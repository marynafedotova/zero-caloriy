import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("APIKEY")
BASE_URL = os.getenv("BASE_URL")

def test_token_lifetime():
    url = f"{BASE_URL}/api/1/access_token"
    payload = {"apiLogin": API_KEY}
    response = requests.post(url, json=payload)
    data = response.json()
    token = data["token"]
    print("Отримано токен:", token)

    start_time = time.time()
    print("⏳ Початок тесту...")

    while True:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/api/1/organizations", headers=headers)
        if resp.status_code == 401:
            print("❌ Токен прострочився!")
            break
        time.sleep(10)

    lifetime = time.time() - start_time
    print(f"⌛ Токен жив {int(lifetime)} секунд (~{round(lifetime/60,1)} хвилин)")


if __name__ == "__main__":
    test_token_lifetime()
    