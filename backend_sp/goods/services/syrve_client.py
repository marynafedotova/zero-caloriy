import os
import sys
import requests
import time
import uuid
from django.utils.text import slugify
from dotenv import load_dotenv, find_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_sp.settings')
django.setup()


from goods.models import Product, ProductCategory, Group, GroupModifier, GroupModifierChild, ProductSize


load_dotenv(find_dotenv())

class SyrveClient:
    def __init__(self):
        self.api_key = os.getenv("APIKEY")
        self.base_url = os.getenv("BASE_URL")
        self.org_id = os.getenv("ORG_ID")
        self.term_grp = os.getenv("TERMINAL_GROUP_ID")
        self.org_id_cache = None 
        self.token_cache = None
        self.token_created_at = None
        self.token_ttl = 3600

    def get_token(self):
        # якщо токен ще живий — повертаємо кешований
        if self.token_cache and (time.time() - self.token_created_at) < self.token_ttl:
            return self.token_cache

        # якщо ні — отримуємо новий
        url = f"{self.base_url}/api/1/access_token"
        payload = {"apiLogin": self.api_key}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            self.token_cache = token
            self.token_created_at = time.time()
            return token
        else:
            raise Exception(f"Syrve auth error: {response.status_code} {response.text}")


    def get_token(self):
        url = f"{self.base_url}/api/1/access_token"
        payload = {"apiLogin": self.api_key}
        response = requests.post(url, json=payload)


        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            return token
        else:
            raise Exception(f"Syrve auth error: {response.status_code} {response.text}")


    def get_menu(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        body = {
            "organizationId": self.org_id,
            "startRevision": 0
        }

        
        response = requests.post(
            f"{self.base_url}/api/1/nomenclature",
            headers=headers,
            json=body
        )

        print("Status code:", response.status_code)
        print("Response text:", response.text)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Помилка запиту меню: {response.status_code} {response.text}")
        

    def save_menu_from_db(self):
        data = self.get_menu()

        #Категорії
        categories = [ cat for cat in data.get("productCategories", []) if not cat.get("isDeleted")] 

        for cat in categories:
            ProductCategory.objects.update_or_create(
                id=cat["id"],
                defaults={
                    "name": cat["name"]
                }
            )
        #Розміри
        sizes = data.get("sizes", [])
        for s in sizes:
            ProductSize.objects.update_or_create(
                id=s["id"],
                defaults={
                    "name": s["name"],
                    "is_default": s.get("isDefault", False)
                }
            )
        

        #Групи
        groups = [gr for gr in data.get("groups", []) if not gr.get("isDeleted")]
        for gr in groups:
            group_obj = Group.objects.filter(id=gr["id"]).first()
            slug = group_obj.slug if group_obj else self.generate_unique_slug(Group, gr.get("name", ""))

            Group.objects.update_or_create(
                id=gr["id"],
                defaults={
                    "name": gr.get("name", ""),
                    "slug": slug,
                    "parent_id": gr.get("parentGroup"),
                    "order": gr.get("order", 0),
                    "is_included_in_menu": gr.get("isIncludedInMenu", True),
                    "is_group_modifier": gr.get("isGroupModifier") is True,
                    "description": gr.get("description"),
                    "additional_info": gr.get("additionalInfo"),
                    "code": gr.get("code", ""),
                    "image_links": gr.get("imageLinks", []),
                    "tags": gr.get("tags", []),
                    "seo_title": gr.get("seoTitle"),
                    "seo_description": gr.get("seoDescription"),
                    "seo_text": gr.get("seoText"),
                    "seo_keywords": gr.get("seoKeywords"),

                }
            )

    
        #Позиції
        products = [p for p in data.get("products", []) if not p.get("isDeleted")]
        product_ids = []

        for p in products:
            product_obj = Product.objects.filter(id=p["id"]).first()
            product_ids.append(p["id"])

            # Ціна та розмір
            current_price = 0.0
            size_id = None
            if p.get("sizePrices"):
                sp = p["sizePrices"][0]
                current_price = sp.get("price", {}).get("currentPrice", 0.0)
                size_id = sp.get("sizeId")

            # Slug
            slug = product_obj.slug if product_obj else self.generate_unique_slug(Product, p.get("name", ""))

            Product.objects.update_or_create(
                id=p["id"],
                defaults={
                    "code": p.get("code", ""),
                    "name_uk": p.get("name", ""),
                    "slug": slug,
                    "description_uk": p.get("description"),
                    "additional_info_uk": p.get("additionalInfo"),
                    "group_id": p.get("parentGroup"),
                    "product_category_id": p.get("productCategoryId"),
                    "type": p.get("type", Product.DISH),
                    "measure_unit_uk": p.get("measureUnit", ""),
                    "weight": p.get("weight", 0.0),
                    "order": p.get("order", 0),
                    "image_url": p["imageLinks"][0] if p.get("imageLinks") else None,
                    "price": current_price,
                    "size_id": size_id,
                    "is_included_in_menu": p.get("isIncludedInMenu", True) # Або логіка з sizePrices
                }
            )   

    # МОДИФІКАТОРИ (Другий прохід: зв'язки)
        for p in products:
            if not p.get("groupModifiers"):
                continue
        
            for gm in p["groupModifiers"]:
                group_mod, _ = GroupModifier.objects.update_or_create(
                    id=gm["id"],
                    defaults={
                        "product_id": p["id"],
                        "modifier_group_name": gm.get("modifierSchemaName", ""),
                        "min_amount": gm.get("minAmount", 0),
                        "max_amount": gm.get("maxAmount", 1),
                        "required": gm.get("required", False)
                    }
                )

                for child in gm.get("childModifiers", []):
                    # Перевіряємо чи існує модифікатор як продукт в базі
                    if Product.objects.filter(id=child["id"]).exists():
                        GroupModifierChild.objects.update_or_create(
                            id=child.get("id"), # У iiko зазвичай childModifier має свій ID або використовує ID продукту
                            group_modifier=group_mod,
                            modifier_id=child["id"],
                            defaults={
                                "min_amount": child.get("minAmount", 0),
                                "max_amount": child.get("maxAmount", 0),
                                "default_amount": child.get("defaultAmount", 0),
                            }
                        )

        

    def generate_unique_slug(self, model, name):
        """Генерує унікальний url з назви"""
        base_slug = slugify(name, allow_unicode=False)

        if not base_slug:
            base_slug = f"item-{uuid.uuid4().hex[:8]}"

        slug = base_slug
        counter = 1


        while model.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
    


    def get_stop_lists(self):
        token = self.get_token()
        url = f"{self.base_url}/api/1/stop_lists"
        payload = {"organizationIds": [self.org_id]}
        headers = {"Authorization": f"Bearer {token}"}
    
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()  # ПОВЕРТАЄМО ВЕСЬ JSON
            else:
                print(f"Syrve API error: {response.text}")
                return {}
        except Exception as e:
            print(f"Request failed: {e}")
            return {}
        

    def create_order(self, order_data):
        """Відправка замовлення в Syrve"""
        token = self.get_token()
        url = f"{self.base_url}/api/1/deliveries/create"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(url, json=order_data, headers=headers)
            # Ми повертаємо JSON відповіді, щоб обробити результат у view
            return response.json(), response.status_code
        except Exception as e:
            print(f"Критична помилка при відправці замовлення: {e}")
            return {"errorDescription": str(e)}, 500
        
    def check_order_status(self, correlation_id):
        """Перевірка, чи замовлення потрапило на касу"""
        token = self.get_token()
        url = f"{self.base_url}/api/1/deliveries/by_id"
        payload = {
            "organizationId": self.org_id,
            "orderIds": [correlation_id]
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


def run():
    """Точка входу для manage.py runscript"""
    client = SyrveClient()
    client.save_menu_from_db()
    print("✅ Меню успішно збережено у базу")

if __name__ == "__main__":
    run()















