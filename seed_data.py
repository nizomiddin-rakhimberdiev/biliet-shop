"""Test ma'lumotlar yaratish uchun script."""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from bilet_app.models import Category, Event, TicketType

# Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@biletshop.uz', 'Admin1234!')
    print("✓ Superuser: admin / Admin1234!")

# Test user
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'user@test.uz', 'Test1234!')
    print("✓ Testuser: testuser / Test1234!")

# Kategoriyalar
cats = {
    'Konsert':   'fa-music',
    'Teatr':     'fa-theater-masks',
    'Sport':     'fa-football-ball',
    'Kino':      'fa-film',
    'Festival':  'fa-star',
}

cat_objs = {}
for name, icon in cats.items():
    c, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon})
    cat_objs[name] = c

print(f"✓ {len(cat_objs)} ta kategoriya")

# Tadbirlar
now = timezone.now()

events_data = [
    {
        'title': 'Shaxlo Rajabova konsert kechasi',
        'category': 'Konsert',
        'venue': 'Alisher Navoiy nomidagi Opera va Balet teatri',
        'city': 'Toshkent',
        'event_date': now + timedelta(days=12, hours=19),
        'description': 'O\'zbek estrada musiqasining yulduzlaridan biri Shaxlo Rajabovaning yillik konsert kechasi. Xalq sevimli qo\'shiqlari, jonli musiqa va ajoyib atmosfera.',
        'tickets': [
            ('Partyer', 150000, 200),
            ('Balkon', 80000, 300),
            ('VIP', 350000, 50),
        ]
    },
    {
        'title': 'O\'zbek milliy futbol terma jamoasi: O\'zbekiston — Koreya',
        'category': 'Sport',
        'venue': 'Milliy stadion',
        'city': 'Toshkent',
        'event_date': now + timedelta(days=8, hours=18),
        'description': 'Osiyo chempionati saralash bosqichi. O\'zbekiston terma jamoasi Koreya bilan hal qiluvchi uchrashuv. Stadionni to\'ldiring!',
        'tickets': [
            ('Oddiy sektor', 50000, 10000),
            ('Premium sektor', 120000, 2000),
            ('VIP loyja', 500000, 200),
        ]
    },
    {
        'title': '"Hamlet" — Milliy drama teatri',
        'category': 'Teatr',
        'venue': 'O\'zbek Milliy drama teatri',
        'city': 'Toshkent',
        'event_date': now + timedelta(days=5, hours=18, minutes=30),
        'description': 'Shekspirning o\'lmas asari. Milliy drama teatrining yangi sahnalashtirishi — zamonaviy yondashuv va professional aktyorlar bilan.',
        'tickets': [
            ('Parter', 120000, 150),
            ('Bel etaj', 80000, 100),
            ('Galereya', 40000, 200),
        ]
    },
    {
        'title': 'Tashkent Music Festival 2026',
        'category': 'Festival',
        'venue': 'Navruz bog\'i',
        'city': 'Toshkent',
        'event_date': now + timedelta(days=20, hours=14),
        'description': 'Ikki kunlik ochiq havoda musiqa festivali. 20+ artist, 3 shnа, food kornerlar va ko\'ngilochar dastur.',
        'tickets': [
            ('1 kunlik', 80000, 5000),
            ('2 kunlik', 130000, 3000),
            ('VIP 2 kunlik', 300000, 500),
        ]
    },
    {
        'title': 'Dune: Yangi davr — Premyera',
        'category': 'Kino',
        'venue': 'Cinemark Toshkent City',
        'city': 'Toshkent',
        'event_date': now + timedelta(days=3, hours=20),
        'description': 'Ilmiy-fantastik blokkaster filmning O\'zbekistondagi rasmiy premyerasi. IMAX formatida ko\'rsatish.',
        'tickets': [
            ('Oddiy', 45000, 150),
            ('IMAX', 75000, 100),
            ('VIP IMAX', 120000, 30),
        ]
    },
    {
        'title': 'Samarqand Jazz Festivali',
        'category': 'Konsert',
        'venue': 'Registon maydoni',
        'city': 'Samarqand',
        'event_date': now + timedelta(days=30, hours=17),
        'description': 'Registon oldidagi tarixiy maydonda xalqaro jazz festivali. Dunyo miqyosidagi jazz solistlari va guruhlar ishtirokida.',
        'tickets': [
            ('Standart', 100000, 3000),
            ('VIP', 250000, 300),
        ]
    },
]

for data in events_data:
    if Event.objects.filter(title=data['title']).exists():
        continue
    event = Event.objects.create(
        title=data['title'],
        category=cat_objs[data['category']],
        venue=data['venue'],
        city=data['city'],
        event_date=data['event_date'],
        description=data['description'],
    )
    for name, price, seats in data['tickets']:
        TicketType.objects.create(
            event=event,
            name=name,
            price=price,
            total_seats=seats,
            available_seats=seats,
        )

print(f"✓ {Event.objects.count()} ta tadbir yaratildi")
print("\n=== TAYYOR ===")
print("Admin panel: http://127.0.0.1:8000/admin/")
print("Login: admin / Admin1234!")
print("Test user: testuser / Test1234!")
