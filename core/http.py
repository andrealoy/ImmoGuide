# core/http.py
print("🔥 HttpClient loaded from:", __file__)
import random
import time
import json
import subprocess
from pathlib import Path
import requests

from core.headers import BASE_HEADERS
from core.exceptions import SessionExpiredError


COOKIE_PATH = Path("cookies/seloger_cookies.json")


class BrowserSession:
    def __init__(self):
        self._cookie_cache = None

    def load_cookies(self, force=False) -> str:
        if self._cookie_cache is None or force:
            if not COOKIE_PATH.exists():
                self.refresh_session()

            cookies = json.loads(COOKIE_PATH.read_text())
            self._cookie_cache = "; ".join(
                f"{c['name']}={c['value']}" for c in cookies
            )

        return self._cookie_cache

    def refresh_session(self):
        print("🔄 Session expirée → ouverture du navigateur")
        try:
            subprocess.run(
                ["python3", "tools/get_cookie_headers.py"],
                check=True,
                timeout=60,
            )
            
            # Valider que les cookies ont bien été créés
            if not COOKIE_PATH.exists():
                raise RuntimeError("Cookies file not created after refresh")
            
            # Valider que le fichier contient des données valides
            try:
                cookies = json.loads(COOKIE_PATH.read_text())
                if not cookies or not isinstance(cookies, list):
                    raise ValueError("Invalid cookies format")
            except (json.JSONDecodeError, ValueError) as e:
                raise RuntimeError(f"Invalid cookies file: {e}")
            
            self._cookie_cache = None
            print("✅ Session rafraîchie avec succès")
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Cookie refresh timed out after 60s")
        except Exception as e:
            print(f"❌ Erreur lors du rafraîchissement: {e}")
            raise


class HttpClient:
    def __init__(
        self,
        session: BrowserSession,
        min_delay=1.2,
        max_delay=3.5,
        max_retries=3,
    ):
        self.session = session
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.http = requests.Session()

    def request(self, method, url, *, json_body=None):
        for attempt in range(1, self.max_retries + 1):
            headers = BASE_HEADERS.copy()
            headers["Cookie"] = self.session.load_cookies()

            resp = self.http.request(
                method,
                url,
                headers=headers,
                json=json_body,
                timeout=30,
            )

            if resp.status_code == 403:
                print(f"⚠️ 403 Forbidden (tentative {attempt}/{self.max_retries}) - {url}")
                if attempt < self.max_retries:
                    self.session.refresh_session()
                    time.sleep(2)  # Pause avant retry
                    continue
                else:
                    raise SessionExpiredError(f"403 après {self.max_retries} tentatives")

            # 404 = annonce supprimée, on retourne la réponse pour que l'appelant puisse la gérer
            if resp.status_code == 404:
                time.sleep(random.uniform(self.min_delay, self.max_delay))
                return resp

            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code} - {url}")

            time.sleep(random.uniform(self.min_delay, self.max_delay))
            return resp

        raise SessionExpiredError("Impossible de récupérer une session valide")
