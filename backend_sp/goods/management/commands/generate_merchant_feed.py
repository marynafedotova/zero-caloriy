# goods/management/commands/generate_merchant_feed.py
from django.core.management.base import BaseCommand
from django.utils.translation import activate
from xml.etree.ElementTree import Element, SubElement, tostring
from goods.models import Product
import xml.dom.minidom
import os
from pathlib import Path

class Command(BaseCommand):
    help = "Generate Google Merchant Center XML feed"

    def handle(self, *args, **options):
        # Устанавливаем язык для мультиязычных полей
        activate('uk')

        root = Element('rss', attrib={'version': '2.0', 'xmlns:g': 'http://base.google.com/ns/1.0'})
        channel = SubElement(root, 'channel')
        SubElement(channel, 'title').text = "Зеро калорій"
        SubElement(channel, 'link').text = "https://zerokaloriy.com/"
        SubElement(channel, 'description').text = "Фід товарів для Google Merchant Center"

        products = Product.objects.filter(is_visible=True)

        for product in products:
            item = SubElement(channel, 'item')
            SubElement(item, 'g:id').text = str(product.id)
            SubElement(item, 'g:title').text = product.name
            SubElement(item, 'g:description').text = product.description or product.additional_info or ""
            SubElement(item, 'g:link').text = f"https://zerokaloriy.com{product.get_absolute_url()}"
            if product.image_url:
                SubElement(item, 'g:image_link').text = product.image_url
            SubElement(item, 'g:availability').text = "in stock" if product.is_included_in_menu else "out of stock"
            SubElement(item, 'g:price').text = f"{product.price:.2f} UAH"
            SubElement(item, 'g:condition').text = "new"
            SubElement(item, 'g:product_type').text = product.group.name if product.group else ""
            SubElement(item, 'g:google_product_category').text = product.product_category.name if product.product_category else ""

        # Преобразуем в красиво отформатированный XML
        xml_bytes = tostring(root, encoding='utf-8')
        dom = xml.dom.minidom.parseString(xml_bytes)
        pretty_xml_as_str = dom.toprettyxml(indent="  ", encoding='utf-8')

        # Путь до корня проекта
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

        # Сохраняем в static, чтобы был доступен по URL
        output_path = BASE_DIR / 'static' / 'merchant_feed.xml'
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(pretty_xml_as_str)

        self.stdout.write(self.style.SUCCESS(f"Feed generated: {output_path}"))
