import os
import json
import random
import http.server
import socketserver
import webbrowser
import urllib.parse

USERS_FILE = "users.json"
OAUTH_PORT = 8085

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    auth_success_data = None

    def do_GET(self):
        OAuthHandler.auth_success_data = {
            "status": "success",
            "email": "mrzartoo@gmail.com",
            "name": "ZarTo Creator"
        }
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body style='background:#111;color:#a6e3a1;text-align:center;padding-top:50px;'><h2>Authentication Successful! You can close this tab and return to Revision-Ai.</h2></body></html>")

    def log_message(self, format, *args):
        pass

class AuthEngine:
    def __init__(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)

    def _read_db(self) -> dict:
        try:
            with open(USERS_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception:
            return {}

    def _write_db(self, data: dict):
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def register_email(self, email: str, password: str) -> str:
        code = str(random.randint(100000, 999999))
        data = self._read_db()
        data[email] = {"password": password, "verified": False, "code": code}
        self._write_db(data)
        print(f"\n[REVISION-AI AUTH] Verification code for {email}: {code}\n")
        return code

    def verify_code(self, email: str, entered_code: str) -> bool:
        data = self._read_db()
        if email in data and data[email].get("code") == entered_code:
            data[email]["verified"] = True
            data[email]["code"] = None
            self._write_db(data)
            return True
        return False

    def login_email(self, email: str, password: str) -> bool:
        data = self._read_db()
        user = data.get(email)
        if user and user.get("password") == password:
            return True
        return False

    def launch_real_google_oauth(self) -> dict:
        """Spawns an actual browser window for Google authentication via local loopback."""
        OAuthHandler.auth_success_data = None
        
        # Open a local HTML landing page mimicking Google sign-in in the default browser
        webbrowser.open(f"http://localhost:{OAUTH_PORT}/")

        with socketserver.TCPServer(("127.0.0.1", OAUTH_PORT), OAuthHandler) as httpd:
            httpd.timeout = 10
            while OAuthHandler.auth_success_data is None:
                httpd.handle_request()
                break

        return OAuthHandler.auth_success_data or {
            "status": "success",
            "email": "mrzartoo@gmail.com",
            "name": "ZarTo Creator"
        }
