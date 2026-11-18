
import json
import ipaddress
import socket
from urllib.parse import urlparse

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from browser.session_manager import browser_manager


def validate_target_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed")

    if not parsed.hostname:
        raise ValueError("Invalid URL")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed")

    # Development MVP: only permit the local test server.
    hostname = parsed.hostname.lower()

    if hostname not in ("localhost", "127.0.0.1"):
        raise ValueError(
            "For this MVP, use a local test website on localhost."
        )

    return url


@csrf_exempt
@require_POST
def inspect_job(request):
    try:
        payload = json.loads(request.body)

        url = payload.get("url", "").strip()
        instruction = payload.get("instruction", "").strip()

        if not url or not instruction:
            return JsonResponse(
                {"error": "URL and instruction are required"},
                status=400,
            )

        validate_target_url(url)

        result = browser_manager.inspect(
            url=url,
            instruction=instruction,
        )

        return JsonResponse(result)

    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    except Exception as exc:
        return JsonResponse(
            {"error": f"Inspection failed: {exc}"},
            status=500,
        )


@csrf_exempt
@require_POST
def fill_job(request, job_id):
    try:
        payload = json.loads(request.body)

        if payload.get("approved") is not True:
            return JsonResponse(
                {"error": "Explicit approval is required"},
                status=400,
            )

        result = browser_manager.fill(job_id)
        return JsonResponse(result)

    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    except Exception as exc:
        return JsonResponse(
            {"error": f"Form filling failed: {exc}"},
            status=500,
        )


def test_form(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebForm Agent Test Form</title>
        <style>
            body {
                font-family: Arial;
                max-width: 600px;
                margin: 40px auto;
            }
            input, select, textarea {
                display: block;
                width: 100%;
                padding: 10px;
                margin: 8px 0 18px;
                box-sizing: border-box;
            }
        </style>
    </head>
    <body>
        <h1>WebForm Agent Test Form</h1>

        <form>
            <label>Full Name</label>
            <input name="full_name" type="text" required>

            <label>Email Address</label>
            <input name="email" type="email" required>

            <label>Country</label>
            <select name="country" required>
                <option value="">Select country</option>
                <option value="india">India</option>
                <option value="usa">USA</option>
            </select>

            <label>
                <input name="newsletter" type="checkbox">
                Subscribe to newsletter
            </label>

            <p>Preferred contact method</p>
            <label>
                <input type="radio" name="contact" value="email">
                Email
            </label>
            <label>
                <input type="radio" name="contact" value="phone">
                Phone
            </label>

            <label>Message</label>
            <textarea name="message"></textarea>

            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """

    return HttpResponse(html)
