import re
import os
import json
import logging
import base64
import requests
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialToken, SocialAccount


def email_scan_view(request):

    return render(request, "email_scan/email_scan.html")

@login_required
def gmail_inbox_api(request):
    """Return a JSON list of messages (id, subject, from, snippet, internalDate).
    Supports an optional query param `pageToken` for pagination and `maxResults` (max 100).
    """
    try:
        token = SocialToken.objects.get(account__user=request.user, account__provider='google')
    except SocialToken.DoesNotExist:
        return JsonResponse({'error': 'Google account not connected'}, status=403)

    max_results = int(request.GET.get('maxResults', 25))
    max_results = min(max_results, 100)
    page_token = request.GET.get('pageToken')

    headers = {'Authorization': f'Bearer {token.token}'}
    params = {'maxResults': max_results}
    if page_token:
        params['pageToken'] = page_token

    r = requests.get('https://gmail.googleapis.com/gmail/v1/users/me/messages', headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return JsonResponse({'error': 'Failed to list messages', 'detail': r.text}, status=500)

    body = r.json()
    messages_list = body.get('messages', []) or []
    next_page_token = body.get('nextPageToken')

    inbox = []
    # fetch lightweight metadata for each message (subject, from, snippet)
    for m in messages_list:
        mid = m.get('id')
        try:
            mr = requests.get(f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}', headers=headers, params={'format': 'metadata', 'metadataHeaders': ['Subject', 'From']}, timeout=10)
            if mr.status_code != 200:
                continue
            md = mr.json()
            headers_list = md.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers_list if h['name'].lower() == 'subject'), '(No subject)')
            sender = next((h['value'] for h in headers_list if h['name'].lower() == 'from'), '(Unknown)')
            snippet = md.get('snippet', '')
            internalDate = md.get('internalDate')
            inbox.append({
                'id': mid,
                'subject': subject,
                'from': sender,
                'snippet': snippet,
                'internalDate': internalDate,
            })
        except Exception:
            continue

    return JsonResponse({'messages': inbox, 'nextPageToken': next_page_token})


@login_required
def gmail_message_api(request, msg_id):
    """Return decoded email body (plaintext preferred, fallback to HTML)."""
    try:
        token = SocialToken.objects.get(account__user=request.user, account__provider='google')
    except SocialToken.DoesNotExist:
        return JsonResponse({'error': 'Google account not connected'}, status=403)

    headers = {'Authorization': f'Bearer {token.token}'}
    r = requests.get(f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}', headers=headers, params={'format': 'full'}, timeout=10)
    if r.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch message', 'detail': r.text}, status=500)

    msg = r.json()
    payload = msg.get('payload', {})
    body_text = ''

    def extract_from_part(part):
        mime = part.get('mimeType', '')
        data = part.get('body', {}).get('data')
        if data:
            try:
                return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8', errors='ignore')
            except Exception:
                return ''
        return ''

    # Walk parts if exist
    if payload.get('parts'):
        # prefer text/plain
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                t = extract_from_part(part)
                if t:
                    body_text = t
                    break
        if not body_text:
            # fallback to first text/html
            for part in payload['parts']:
                if part.get('mimeType') == 'text/html':
                    t = extract_from_part(part)
                    if t:
                        body_text = t
                        break
    else:
        data = payload.get('body', {}).get('data')
        if data:
            try:
                body_text = base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8', errors='ignore')
            except Exception:
                body_text = ''

    return JsonResponse({'id': msg_id, 'body': body_text, 'snippet': msg.get('snippet', '')})