from django.test import TestCase, override_settings
from django_ftl import override as ftl_override
from goods.ftl_bundles import goods_bundle

class FluentFilesLoadingTest(TestCase):
    @override_settings(USE_I18N=True)
    def test_ftl_files_are_loaded_without_errors(self):
        for locale in ("en", "uk"):
            with self.subTest(locale=locale):
                with ftl_override(locale):
                    # Спробуємо отримати повідомлення безпосередньо з об'єкта
                    # Якщо goods_bundle — це Bundle, у нього мають бути _messages
                    messages = getattr(goods_bundle, '_messages', None)
                    
                    self.assertIsNotNone(
                        messages, 
                        f"Об'єкт goods_bundle не має атрибута _messages для локалі {locale}"
                    )
                    self.assertTrue(
                        len(messages) > 0, 
                        f"Файли FTL не завантажені або порожні для локалі {locale}"
                    )

class FluentBundleSmokeTest(TestCase):
    @override_settings(USE_I18N=True)
    def test_bundle_has_any_messages(self):
        for locale in ("en", "uk"):
            with self.subTest(locale=locale):
                with ftl_override(locale):
                    # Перевіряємо форматування реального ключа
                    # Замініть 'any-key-from-your-file' на реальний ID з goods.ftl
                    # Наприклад, 'category-title'
                    result = goods_bundle.format('any-key-from-your-file')
                    
                    self.assertNotEqual(result, "???")