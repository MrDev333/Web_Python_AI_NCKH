import base64
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.urls import reverse
from django.utils.http import urlencode

try:
	from google.oauth2.credentials import Credentials
	from googleapiclient.discovery import build
	from googleapiclient.errors import HttpError
except Exception:
	Credentials = None
	build = None
	HttpError = Exception

logger = logging.getLogger(__name__)


def _get_gmail_service(user):
	"""Return (service, error_message). If Google libraries missing or token missing, return (None, msg)."""
	if Credentials is None or build is None:
		return None, "Google client libraries not installed (google-auth, google-api-python-client)"

	account = SocialAccount.objects.filter(user=user, provider="google").first()
	if not account:
		return None, {"msg": "No connected Google account found. Please sign in with Google.", "reauth_url": reverse('account_login')}

	token = SocialToken.objects.filter(account=account).first()
	if not token:
		# Build a re-auth url that forces consent and offline access
		params = {'process': 'connect'}
		# After reauth we want to return to the scanner page
		params['next'] = '/app/scanner/'
		reauth = reverse('socialaccount_login', args=['google']) + '?' + urlencode(params)
		return None, {"msg": "No social token found for Google account. Please reconnect Google to grant permissions.", "reauth_url": reauth}

	# Try to find refresh token in a couple of places
	refresh_token = token.token_secret or account.extra_data.get("refresh_token") if hasattr(account, 'extra_data') else None

	try:
		app = SocialApp.objects.get(provider="google")
		client_id = app.client_id
		client_secret = app.secret
	except SocialApp.DoesNotExist:
		client_id = None
		client_secret = None

	creds = Credentials(
		token=token.token,
		refresh_token=refresh_token,
		client_id=client_id,
		client_secret=client_secret,
		token_uri="https://oauth2.googleapis.com/token",
	)

	try:
		service = build("gmail", "v1", credentials=creds)
	except Exception as e:
		logger.exception("Failed to build Gmail service")
		return None, {"msg": str(e)}

	return service, None


@login_required
def inbox_view(request):
	return render(request, "email_scan/inbox.html")


def api_list_messages(request):
	# Return JSON errors for AJAX clients instead of redirecting
	if not request.user.is_authenticated:
		return JsonResponse({"error": "User not authenticated", "login_url": reverse('account_login')}, status=401)

	service, err = _get_gmail_service(request.user)
	if not service:
		if isinstance(err, dict):
			return JsonResponse({"error": err.get('msg'), "reauth_url": err.get('reauth_url')}, status=403)
		return JsonResponse({"error": err}, status=500)
	try:
		resp = service.users().messages().list(userId="me", maxResults=50).execute()
		items = resp.get("messages", [])
		out = []
		for item in items:
			try:
				msg = service.users().messages().get(userId="me", id=item["id"], format="metadata", metadataHeaders=["Subject", "From", "Date"]).execute()
				headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
				out.append({
					"id": item["id"],
					"snippet": msg.get("snippet"),
					"subject": headers.get("Subject", ""),
					"from": headers.get("From", ""),
					"date": headers.get("Date", ""),
				})
			except HttpError as e:
				logger.exception("Error fetching message metadata %s", item)
		return JsonResponse({"messages": out})
	except HttpError as e:
		logger.exception("Gmail API list error")
		return JsonResponse({"error": str(e)}, status=400)


def _decode_b64(data: str) -> str:
	if not data:
		return ''
	# Fix padding
	rem = len(data) % 4
	if rem:
		data += '=' * (4 - rem)
	try:
		return base64.urlsafe_b64decode(data).decode(errors='ignore')
	except Exception:
		try:
			return base64.b64decode(data).decode(errors='ignore')
		except Exception:
			return ''


def _extract_bodies(payload):
	"""Traverse payload and return a dict with 'text' and 'html' (strings)."""
	text_parts = []
	html_parts = []

	def walk(part):
		if not part:
			return
		if isinstance(part, dict):
			mime = part.get('mimeType', '')
			body = part.get('body', {})
			data = body.get('data')
			if data:
				decoded = _decode_b64(data)
				if mime == 'text/plain':
					text_parts.append(decoded)
				elif mime == 'text/html':
					html_parts.append(decoded)
			# some parts may have filename and attachment, skip attachments
			for p in part.get('parts', []) or []:
				walk(p)
		elif isinstance(part, list):
			for p in part:
				walk(p)

	walk(payload)
	return {'text': '\n\n'.join(text_parts).strip(), 'html': '\n\n'.join(html_parts).strip()}


def api_fetch_message(request, msg_id: str):
	if not request.user.is_authenticated:
		return JsonResponse({"error": "User not authenticated", "login_url": reverse('account_login')}, status=401)

	service, err = _get_gmail_service(request.user)
	if not service:
		if isinstance(err, dict):
			return JsonResponse({"error": err.get('msg'), "reauth_url": err.get('reauth_url')}, status=403)
		return JsonResponse({"error": err}, status=500)
	try:
		msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
		payload = msg.get("payload", {})
		bodies = _extract_bodies(payload)

		return JsonResponse({"id": msg_id, "snippet": msg.get("snippet", ""), "text": bodies.get('text', ''), "html": bodies.get('html', '')})
	except HttpError as e:
		logger.exception("Gmail API get message error %s", msg_id)
		return JsonResponse({"error": str(e)}, status=400)
