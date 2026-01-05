from django.test import TestCase, override_settings
from django_ftl import override as ftl_override
from .ftl_bundles import main_bundle

class FluentInternalTest(TestCase):

    @override_settings(USE_I18N=True)
    def test_translations_loading(self):
        """Перевірка завантаження тексту з FTL файлів додатка"""
        with ftl_override('en'):
            msg = main_bundle.format('welcome-user', {'username': 'Alice'})
            # Використовуємо assertIn, щоб ігнорувати невидимі символи BIDI
            self.assertIn("Welcome,", msg)
            self.assertIn("Alice", msg)

    @override_settings(USE_I18N=True)
    def test_plural_rules(self):
        """Перевірка роботи правил множини (Plural Rules)"""
        with ftl_override('en'):
            # Перевірка [one]
            res_one = main_bundle.format('items-count', {'count': 1})
            self.assertIn("selected", res_one)
            self.assertIn("1", res_one)
            self.assertIn("item", res_one)

            # Перевірка [other]
            res_other = main_bundle.format('items-count', {'count': 5})
            self.assertIn("5", res_other)
            self.assertIn("items", res_other)

    def test_missing_key_behavior(self):
        """Перевірка поведінки, якщо ключа не існує"""
        with ftl_override('en'):
            msg = main_bundle.format('non-existent-key')
            self.assertIn('???', msg)