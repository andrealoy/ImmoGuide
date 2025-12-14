# tools/get_cookie_headers.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import json
import time
import os


SELOGER_URL = "https://www.seloger.com/"
OUTPUT_PATH = Path("cookies/seloger_cookies.json")


def get_cookie_headers():
    """
    Ouvre SeLoger dans un vrai Chrome,
    permet la résolution du CAPTCHA,
    sauvegarde UNIQUEMENT les cookies.
    """

    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    # Masquer webdriver
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
        },
    )

    driver.get(SELOGER_URL)

    print("\n" + "=" * 60)
    print("🔒 Si un CAPTCHA apparaît :")
    print("👉 Résous-le MANUELLEMENT")
    print("👉 Attends que la page soit chargée")
    print("👉 Puis patiente 10 secondes")
    print("=" * 60 + "\n")

    time.sleep(10)

    cookies = driver.get_cookies()
    driver.quit()

    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(cookies, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("✅ Cookies sauvegardés")
    print(f"📄 {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    get_cookie_headers()
