
import os
import sys
import django
from decimal import Decimal

def setup_django():
    # Přidání cesty k projektu do sys.path a nastavení DJANGO_SETTINGS_MODULE
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoparts_omega.settings')
    django.setup()

def seed_data():
    from django.utils.text import slugify
    from store.models import Category, Product

    print("Mazání starých dat...")
    # Product.objects.all().delete() # Pro čistý start, ale pro MVP je get_or_create bezpečnější
    # Category.objects.all().delete()

    print("Vytvářím kategorie...")
    categories_data = [
        "Brzdy", "Filtry", "Motorové díly", "Podvozek", "Výfukové systémy"
    ]
    categories = {}
    for cat_name in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slugify(cat_name)}
        )
        categories[cat_name] = category
        if created:
            print(f"- Vytvořena kategorie: {cat_name}")

    print("\nVytvářím produkty...")
    products_data = [
        {'cat': "Brzdy", 'name': "Brzdové destičky OmegaPro", 'price': 1250.00, 'stock': 50, 'desc': 'Vysoce výkonné keramické brzdové destičky.'},
        {'cat': "Brzdy", 'name': "Brzdový kotouč 320mm", 'price': 2100.50, 'stock': 30, 'desc': 'Vnitřně chlazený brzdový kotouč pro sportovní vozy.'},
        {'cat': "Filtry", 'name': "Olejový filtr Mann", 'price': 350.00, 'stock': 120, 'desc': 'Prémiový olejový filtr pro většinu evropských vozů.'},
        {'cat': "Filtry", 'name': "Vzduchový filtr sportovní K&N", 'price': 1800.00, 'stock': 45, 'desc': 'Zvyšuje výkon motoru a má dlouhou životnost.'},
        {'cat': "Motorové díly", 'name': "Sada rozvodového řemene Contitech", 'price': 4500.00, 'stock': 15, 'desc': 'Kompletní sada včetně kladek a vodní pumpy.'},
        {'cat': "Motorové díly", 'name': "Zapalovací svíčka NGK Iridium", 'price': 420.00, 'stock': 200, 'desc': 'Iridiová svíčka pro optimální zapalování a výkon.'},
        {'cat': "Podvozek", 'name': "Tlumič pérování Sachs", 'price': 2800.00, 'stock': 40, 'desc': 'Kvalitní plynový tlumič pro komfortní i sportovní jízdu.'},
        {'cat': "Výfukové systémy", 'name': "Koncový díl výfuku Remus", 'price': 8990.00, 'stock': 10, 'desc': 'Nerezový sportovní výfuk s homologací.'},
    ]

    for data in products_data:
        product, created = Product.objects.get_or_create(
            slug=slugify(data['name']),
            defaults={
                'category': categories[data['cat']],
                'name': data['name'],
                'description': data['desc'],
                'price': Decimal(str(data['price'])),
                'stock': data['stock'],
                'image_url': f"https://via.placeholder.com/400x300.png/1a1a1a/ff4500?text={slugify(data['name'])}"
            }
        )
        if created:
            print(f"- Vytvořen produkt: {data['name']}")
    
    print("\nNaplnění databáze dokončeno.")

if __name__ == '__main__':
    setup_django()
    seed_data()
