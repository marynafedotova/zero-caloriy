import os
import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class LokoClient:
    def __init__(self):
        self.base_url = os.getenv("LOKO_BASE_URL")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.company_id = os.getenv("COMPANY_ID")

    def get_access_token(self):
        """
        Отримання токена з виводом діагностики в консоль.
        """
        cache_key = "loko_access_token"
        token = cache.get(cache_key)

        if token:
            print(f"DEBUG: [Loko] Використовуємо токен з КЕШУ Redis")
            return token

        print(f"DEBUG: [Loko] КЕШ порожній. Запитуємо новий токен у {self.base_url}/token")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        try:
            url = f"{self.base_url}/token"
            # OAuth2 вимагає передачу через Form Data (data=), а не JSON
            response = requests.post(url, data=payload, timeout=(5, 15))
            
            # Виводимо статус відповіді
            print(f"DEBUG: [Loko] Статус відповіді: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            new_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # Час життя в секундах

            if new_token:
                # Виводимо інформацію про токен
                print(f"DEBUG: [Loko] Токен отримано успішно!")
                print(f"DEBUG: [Loko] Час життя токена (expires_in): {expires_in} сек. (~{expires_in // 60} хв.)")
                
                # Зберігаємо в Redis, резервуємо 5 хвилин (300 сек) на "про запас"
                cache_timeout = max(expires_in - 300, 60)
                cache.set(cache_key, new_token, timeout=cache_timeout)
                
                print(f"DEBUG: [Loko] Токен збережено в Redis на {cache_timeout} секунд")
                return new_token

        except requests.exceptions.HTTPError as e:
            print(f"ERROR: [Loko] Помилка HTTP: {e.response.status_code}")
            print(f"ERROR: [Loko] Деталі: {e.response.text}")
            logger.error(f"Loko Auth HTTP Error: {e.response.text}")
        except Exception as e:
            print(f"ERROR: [Loko] Критична помилка: {str(e)}")
            logger.error(f"Loko Auth Exception: {str(e)}")
        
        return None