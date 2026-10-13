import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vegist_project.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product, Review
from cart.models import Coupon
from accounts.models import Profile


def seed():
    print("[*] Starting Vegist Organic Store Seeding...")

    # 1. Create Superuser & Customer
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@vegist.com', 'admin123')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'Vegist'
        admin_user.save()
        print("[OK] Superuser created: admin / admin123")

    customer, created = User.objects.get_or_create(
        username='customer@vegist.com',
        defaults={
            'email': 'customer@vegist.com',
            'first_name': 'Aarav',
            'last_name': 'Sharma',
        }
    )
    if created or customer:
        customer.set_password('customer123')
        customer.save()
        profile, _ = Profile.objects.get_or_create(user=customer)
        profile.phone = '+91 98765 43210'
        profile.address = '742, 12th Main Road, HAL 2nd Stage, Indiranagar'
        profile.city = 'Bengaluru'
        profile.state = 'Karnataka'
        profile.postal_code = '560038'
        profile.country = 'India'
        profile.save()
        print("[OK] Demo customer created/updated: customer@vegist.com / customer123")

    # 2. Coupons
    coupons_data = [
        ('VEGIST20', 20),
        ('ORGANIC15', 15),
        ('FRESH10', 10),
        ('FARM50', 50),
    ]
    for code, discount in coupons_data:
        Coupon.objects.get_or_create(
            code=code,
            defaults={
                'discount_percent': discount,
                'active': True,
                'valid_to': timezone.now() + timedelta(days=90)
            }
        )
    print("[OK] Coupons created: VEGIST20 (20%), ORGANIC15 (15%), FRESH10 (10%)")

    # 3. Categories
    categories_data = [
        {
            'name': 'Fresh Vegetables',
            'slug': 'fresh-vegetables',
            'icon': 'veg-carrot',
            'image': 'categories/cat_vegetables.jpg',
            'description': 'Farm-picked crisp green vegetables, organic root produce, and fresh herbs grown without synthetic chemicals.'
        },
        {
            'name': 'Organic Fruits',
            'slug': 'organic-fruits',
            'icon': 'veg-apple',
            'image': 'categories/cat_fruits.jpg',
            'description': 'Sun-ripened orchard fruits, berries, and citrus brimming with natural sweet vitamins and antioxidants.'
        },
        {
            'name': 'Farm Dairy & Eggs',
            'slug': 'farm-dairy-eggs',
            'icon': 'veg-milk',
            'image': 'categories/cat_dairy.jpg',
            'description': 'Pasture-raised cow and buffalo milk, cultured artisan butter, and organic free-range farm eggs.'
        },
        {
            'name': 'Cold-Pressed Juices',
            'slug': 'cold-pressed-juices',
            'icon': 'veg-juice',
            'image': 'categories/promo_juice.jpg',
            'description': '100% raw unpasteurized cold-pressed fruit and vegetable elixir shots and cleanse juices.'
        },
        {
            'name': 'Artisan Bakery',
            'slug': 'artisan-bakery',
            'icon': 'veg-bread',
            'image': 'categories/cat_bakery.jpg',
            'description': 'Slow-fermented wild yeast sourdough breads, whole grain loaves, and organic seed pastries.'
        },
        {
            'name': 'Harvest Bundles & Deals',
            'slug': 'harvest-bundles',
            'icon': 'veg-box',
            'image': 'categories/deal_bundle.jpg',
            'description': 'Curated weekly farm harvest boxes offering the ultimate variety and family savings.'
        },
    ]

    cat_map = {}
    for cat in categories_data:
        c, _ = Category.objects.update_or_create(
            slug=cat['slug'],
            defaults=cat
        )
        cat_map[c.slug] = c
    print(f"[OK] Created {len(cat_map)} Categories")

    # 4. Products (in Indian Rupees - ₹)
    products_data = [
        # Fresh Vegetables
        {
            'category': cat_map['fresh-vegetables'],
            'name': 'Crisp Organic Garden Broccoli Crown',
            'slug': 'organic-garden-broccoli',
            'short_description': 'Hand-harvested vibrant green broccoli rich in Vitamin C, fiber, and sulforaphane.',
            'description': 'Our organic broccoli crowns are harvested at dawn to ensure maximum freshness and crisp texture. Free from all synthetic pesticides, non-GMO, and packed with vital phytonutrients. Ideal for steaming, roasting with garlic and olive oil, or adding to fresh green salads.',
            'price': Decimal('89.00'),
            'old_price': Decimal('120.00'),
            'unit': '500g',
            'stock': 45,
            'image': 'products/cat_vegetables.jpg',
            'badge': '25% OFF',
            'rating': Decimal('4.9'),
            'reviews_count': 28,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '34 kcal', 'Protein': '2.8g', 'Carbs': '6.6g', 'Fiber': '2.6g', 'Vitamin C': '148% DV'}
        },
        {
            'category': cat_map['fresh-vegetables'],
            'name': 'Organic Sweet Dutch Baby Carrots',
            'slug': 'organic-sweet-baby-carrots',
            'short_description': 'Crunchy tender sweet baby carrots with leafy greens attached.',
            'description': 'Naturally sweet baby carrots pulled from rich loam soil. Their natural sweetness makes them a favorite for snacking, juicing, and oven roasting with a drizzle of pure organic honey.',
            'price': Decimal('65.00'),
            'old_price': Decimal('85.00'),
            'unit': '1 kg Bunch',
            'stock': 60,
            'image': 'products/cat_vegetables.jpg',
            'badge': 'ORGANIC',
            'rating': Decimal('4.8'),
            'reviews_count': 19,
            'is_featured': True,
            'is_trending': False,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '41 kcal', 'Beta-Carotene': '8285 µg', 'Carbs': '9.6g', 'Fiber': '2.8g', 'Vitamin A': '104% DV'}
        },
        {
            'category': cat_map['fresh-vegetables'],
            'name': 'Farm Fresh Red Bell Sweet Pepper',
            'slug': 'farm-fresh-red-bell-pepper',
            'short_description': 'Plump, glossy red bell peppers with sweet and crisp juicy walls.',
            'description': 'Sun-drenched organic sweet peppers ripened on the vine for deep red pigment and extraordinary sweet crunch. Perfect for fajitas, roasting, stuffing, or raw snacking with hummus.',
            'price': Decimal('75.00'),
            'old_price': Decimal('95.00'),
            'unit': '3 Pcs Pack',
            'stock': 35,
            'image': 'products/cat_vegetables.jpg',
            'badge': 'BESTSELLER',
            'rating': Decimal('4.7'),
            'reviews_count': 15,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '31 kcal', 'Vitamin C': '213% DV', 'Carbs': '6.0g', 'Fiber': '2.1g'}
        },
        {
            'category': cat_map['fresh-vegetables'],
            'name': 'Heritage Heirloom Vine Tomatoes',
            'slug': 'heritage-heirloom-vine-tomatoes',
            'short_description': 'Aromatic ruby red tomatoes left to ripen on the vine for peak flavor.',
            'description': 'Rich, juicy, and sweetly acidic. These vine-ripened tomatoes carry the authentic nostalgic heirloom aroma that supermarket greenhouse tomatoes lack. Best in Caprese salads and pasta sauces.',
            'price': Decimal('48.00'),
            'old_price': Decimal('65.00'),
            'unit': '1 kg',
            'stock': 40,
            'image': 'products/hero_banner.jpg',
            'badge': 'HOT',
            'rating': Decimal('5.0'),
            'reviews_count': 34,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '18 kcal', 'Lycopene': '2573 µg', 'Potassium': '237 mg', 'Vitamin C': '28% DV'}
        },

        # Organic Fruits
        {
            'category': cat_map['organic-fruits'],
            'name': 'Sweet Mountain Organic Strawberries',
            'slug': 'sweet-organic-strawberries',
            'short_description': 'Luscious, ruby-red organic strawberries bursting with natural sweetness.',
            'description': 'Pesticide-free organic strawberries grown with sustainable mountain aquifer irrigation. Plump, fragrant, and hand-selected at optimal ripeness. Perfect for desserts, breakfast bowls, or guilt-free snacking.',
            'price': Decimal('179.00'),
            'old_price': Decimal('240.00'),
            'unit': '450g Clamshell',
            'stock': 50,
            'image': 'products/cat_fruits.jpg',
            'badge': 'TOP RATED',
            'rating': Decimal('4.9'),
            'reviews_count': 42,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '32 kcal', 'Vitamin C': '98% DV', 'Carbs': '7.7g', 'Fiber': '2.0g', 'Sugar': '4.9g'}
        },
        {
            'category': cat_map['organic-fruits'],
            'name': 'Wild Organic Super Antioxidant Blueberries',
            'slug': 'wild-organic-blueberries',
            'short_description': 'Plump indigo berries with a natural powdery silver bloom.',
            'description': 'Deep blue, sweet-tart superfruits loaded with anthocyanins and dietary fiber. Harvested from organic certified berry orchards and immediately chilled to maintain crisp bursting texture.',
            'price': Decimal('249.00'),
            'old_price': Decimal('320.00'),
            'unit': '300g Pack',
            'stock': 30,
            'image': 'products/cat_fruits.jpg',
            'badge': 'ANTIOXIDANTS',
            'rating': Decimal('4.9'),
            'reviews_count': 38,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '57 kcal', 'Anthocyanins': '163 mg', 'Carbs': '14g', 'Fiber': '2.4g'}
        },
        {
            'category': cat_map['organic-fruits'],
            'name': 'Juicy Valencia Organic Sweet Oranges',
            'slug': 'juicy-valencia-organic-oranges',
            'short_description': 'Thin-skinned sun-kissed citrus bursting with pure refreshing juice.',
            'description': 'Sweet, fragrant Valencia oranges grown in sunny pesticide-free groves. Exceptional for juicing or peeling into fresh segments.',
            'price': Decimal('95.00'),
            'old_price': Decimal('130.00'),
            'unit': '1.5 kg Bag',
            'stock': 55,
            'image': 'products/promo_fruits.jpg',
            'badge': 'VITAMIN C',
            'rating': Decimal('4.8'),
            'reviews_count': 22,
            'is_featured': False,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '47 kcal', 'Vitamin C': '89% DV', 'Carbs': '11.8g', 'Fiber': '2.4g'}
        },
        {
            'category': cat_map['organic-fruits'],
            'name': 'Crisp Organic Granny Smith & Gala Apples',
            'slug': 'crisp-organic-mixed-apples',
            'short_description': 'Tart green and sweet red apples hand-picked in local orchards.',
            'description': 'No wax coating, no synthetic sprays. Just pure unadulterated crunch and vibrant natural flavor that refreshes your palate with every bite.',
            'price': Decimal('145.00'),
            'old_price': Decimal('180.00'),
            'unit': '1 kg Bag',
            'stock': 40,
            'image': 'products/promo_fruits.jpg',
            'badge': 'NO WAX',
            'rating': Decimal('4.7'),
            'reviews_count': 18,
            'is_featured': True,
            'is_trending': False,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '52 kcal', 'Fiber': '2.4g', 'Carbs': '13.8g', 'Potassium': '107 mg'}
        },

        # Farm Dairy & Eggs
        {
            'category': cat_map['farm-dairy-eggs'],
            'name': 'Pasture-Raised Organic Whole Milk',
            'slug': 'pasture-raised-organic-whole-milk',
            'short_description': 'Cream-top non-homogenized whole milk from grass-fed cows.',
            'description': 'Bottled in nostalgic eco-glass. Our cows graze happily on certified organic open pastures 365 days a year, producing rich milk with natural golden cream floating on top. Free of hormones and antibiotics.',
            'price': Decimal('68.00'),
            'old_price': Decimal('85.00'),
            'unit': '1 Liter Bottle',
            'stock': 30,
            'image': 'products/cat_dairy.jpg',
            'badge': 'GRASS FED',
            'rating': Decimal('5.0'),
            'reviews_count': 56,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '149 kcal', 'Protein': '7.7g', 'Calcium': '276 mg', 'Fat': '8g'}
        },
        {
            'category': cat_map['farm-dairy-eggs'],
            'name': 'Free-Range Organic Farm Brown Eggs',
            'slug': 'free-range-organic-brown-eggs',
            'short_description': 'Large brown eggs with vibrant deep orange yolks from pasture-roaming hens.',
            'description': 'Hen welfare is at the heart of our partner farms. Hens forage outdoors freely on organic clover pastures and certified organic grain feed, delivering rich, nutrient-dense eggs with thick shells and vivid yolks.',
            'price': Decimal('115.00'),
            'old_price': Decimal('140.00'),
            'unit': 'Dozen (12 Eggs)',
            'stock': 45,
            'image': 'products/cat_dairy.jpg',
            'badge': 'PASTURE ROAMED',
            'rating': Decimal('4.9'),
            'reviews_count': 64,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '72 kcal', 'Protein': '6.3g', 'Choline': '147 mg', 'Omega-3': '180 mg'}
        },
        {
            'category': cat_map['farm-dairy-eggs'],
            'name': 'Cultured Organic Farmhouse Sea Salt Butter',
            'slug': 'cultured-organic-farmhouse-butter',
            'short_description': 'Slow-churned European-style cultured butter with delicate sea salt crystals.',
            'description': 'Churned in small batches from pasture-grazed sweet cream cultured for 24 hours. Rich 84% butterfat delivers unmatchable flaky pastry laminations and luscious morning toast spreads.',
            'price': Decimal('185.00'),
            'old_price': Decimal('220.00'),
            'unit': '250g Block',
            'stock': 25,
            'image': 'products/cat_dairy.jpg',
            'badge': 'ARTISAN',
            'rating': Decimal('4.9'),
            'reviews_count': 31,
            'is_featured': False,
            'is_trending': False,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '102 kcal / tbsp', 'Butterfat': '84%', 'Sodium': '90 mg'}
        },

        # Cold Pressed Juices
        {
            'category': cat_map['cold-pressed-juices'],
            'name': 'Green Vitality Cold-Pressed Detox Elixir',
            'slug': 'green-vitality-cold-pressed-detox',
            'short_description': 'Hydrating blend of organic kale, crisp cucumber, celery, lemon & mint.',
            'description': 'Over 2 lbs of organic leafy greens squeezed into every single bottle using gentle hydraulic cold-press technology. No added water, sugar, or preservatives. Alkalizing, detoxifying, and ultra-refreshing.',
            'price': Decimal('149.00'),
            'old_price': Decimal('189.00'),
            'unit': '500ml Bottle',
            'stock': 28,
            'image': 'products/promo_juice.jpg',
            'badge': 'RAW & FRESH',
            'rating': Decimal('4.8'),
            'reviews_count': 35,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '90 kcal', 'Sugars (Natural)': '11g', 'Chlorophyll': 'High', 'Vitamin K': '240% DV'}
        },
        {
            'category': cat_map['cold-pressed-juices'],
            'name': 'Golden Glow Turmeric Carrot Ginger Juice',
            'slug': 'golden-glow-turmeric-carrot-juice',
            'short_description': 'Invigorating immunity booster made with fresh turmeric root and sweet organic carrots.',
            'description': 'A warming, zesty immunity powerhouse. Fresh raw ginger and earthy golden turmeric root blended with sweet carrot and cold-pressed citrus.',
            'price': Decimal('139.00'),
            'old_price': Decimal('179.00'),
            'unit': '500ml Bottle',
            'stock': 32,
            'image': 'products/promo_juice.jpg',
            'badge': 'IMMUNITY',
            'rating': Decimal('4.9'),
            'reviews_count': 27,
            'is_featured': False,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '110 kcal', 'Curcumin': 'Active', 'Beta-Carotene': 'High', 'Vitamin C': '85% DV'}
        },
        {
            'category': cat_map['cold-pressed-juices'],
            'name': 'Ruby Red Beetroot & Wild Berry Cleanse',
            'slug': 'ruby-red-beetroot-berry-cleanse',
            'short_description': 'Nitrate-rich organic beetroot, crisp apple, wild blueberries and lemon.',
            'description': 'Natural stamina and cardiovascular boost. Deep red pigments indicate abundant betalains, supporting natural liver cleansing and post-workout circulation.',
            'price': Decimal('149.00'),
            'old_price': Decimal('189.00'),
            'unit': '500ml Bottle',
            'stock': 20,
            'image': 'products/promo_juice.jpg',
            'badge': 'STAMINA',
            'rating': Decimal('4.7'),
            'reviews_count': 19,
            'is_featured': False,
            'is_trending': False,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '125 kcal', 'Nitrates': 'Naturally Occurring', 'Iron': '15% DV'}
        },

        # Artisan Bakery
        {
            'category': cat_map['artisan-bakery'],
            'name': 'Stoneground Organic Sourdough Boule',
            'slug': 'stoneground-organic-sourdough-boule',
            'short_description': 'Naturally leavened with 48-hour slow fermentation and blistered crunchy crust.',
            'description': 'Baked fresh daily at 4 AM using certified organic stoneground ancient grain flours, well water, and sea salt. Crisp caramelized crust yields to an airy, chewy, slightly sour crumb that is exceptionally gut-friendly.',
            'price': Decimal('145.00'),
            'old_price': Decimal('180.00'),
            'unit': '750g Loaf',
            'stock': 22,
            'image': 'products/cat_bakery.jpg',
            'badge': 'FRESH BAKED',
            'rating': Decimal('5.0'),
            'reviews_count': 49,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '160 kcal / slice', 'Protein': '6g', 'Fiber': '3g', 'No Added Sugar': '100%'}
        },
        {
            'category': cat_map['artisan-bakery'],
            'name': 'Seeded Ancient Grain Sourdough Baguette',
            'slug': 'seeded-ancient-grain-baguette',
            'short_description': 'Crusted with toasted organic sesame, poppy, flax, and sunflower seeds.',
            'description': 'Aromatic nutty seeds toasted into the crust during baking. Perfect companion for farm cheese boards, organic butter, or dipping in extra virgin olive oil.',
            'price': Decimal('99.00'),
            'old_price': Decimal('130.00'),
            'unit': '2 Baguettes Pack',
            'stock': 30,
            'image': 'products/cat_bakery.jpg',
            'badge': 'SEEDED',
            'rating': Decimal('4.8'),
            'reviews_count': 23,
            'is_featured': False,
            'is_trending': False,
            'is_deal_of_the_day': False,
            'nutrition_facts': {'Calories': '180 kcal / portion', 'Omega-3 Fatty Acids': 'Rich', 'Protein': '7g'}
        },

        # Harvest Bundles & Deals (Deal of the Day Featured!)
        {
            'category': cat_map['harvest-bundles'],
            'name': 'Organic Farm Harvest Family Box (12kg)',
            'slug': 'organic-farm-harvest-family-box',
            'short_description': 'Our flagship weekly farm box packed with seasonal veggies, fruits, sourdough loaf & farm honey.',
            'description': 'The ultimate zero-waste organic farm experience! Includes heirloom Romanesco broccoli, baby carrots, vine tomatoes, crisp green apples, fresh herbs, pasture-raised butter, raw wildflower honey, and our artisan sourdough boule. Sourced within 50 miles of your doorstep.',
            'price': Decimal('1199.00'),
            'old_price': Decimal('1699.00'),
            'unit': '12 kg Harvest Box',
            'stock': 18,
            'image': 'products/deal_bundle.jpg',
            'badge': '30% OFF',
            'rating': Decimal('5.0'),
            'reviews_count': 82,
            'is_featured': True,
            'is_trending': True,
            'is_deal_of_the_day': True,
            'deal_discount_percent': 30,
            'deal_ends_at': timezone.now() + timedelta(days=3, hours=14, minutes=45),
            'nutrition_facts': {'Total Items': '14 Varieties', 'Servings': 'Family of 4 (1 Week)', 'Certified': '100% USDA Organic'}
        },
        {
            'category': cat_map['harvest-bundles'],
            'name': 'Green Smoothie & Detox Morning Crate',
            'slug': 'green-smoothie-detox-morning-crate',
            'short_description': 'Curated box of organic avocados, baby spinach, kale, green apples, and lemons.',
            'description': 'Everything you need for 7 mornings of glowing green smoothies! Packed with freshly washed organic baby greens, buttery hass avocados, crisp tart apples, and zesty lemons.',
            'price': Decimal('749.00'),
            'old_price': Decimal('999.00'),
            'unit': '7-Day Cleanse Box',
            'stock': 25,
            'image': 'products/hero_banner.jpg',
            'badge': 'DETOX DEAL',
            'rating': Decimal('4.9'),
            'reviews_count': 41,
            'is_featured': True,
            'is_trending': False,
            'is_deal_of_the_day': True,
            'deal_discount_percent': 25,
            'deal_ends_at': timezone.now() + timedelta(days=2, hours=8, minutes=20),
            'nutrition_facts': {'Smoothie Yield': '7 Large 600ml Glasses', 'Nutrients': 'High Alkalizing Minerals'}
        }
    ]

    for pdata in products_data:
        prod, created = Product.objects.update_or_create(
            slug=pdata['slug'],
            defaults=pdata
        )

    print(f"[OK] Created/Updated {len(products_data)} organic products")

    # 5. Add sample verified reviews
    sample_reviews = [
        ('Sarah Jenkins', 'sarah@example.com', 5, 'The freshness is simply unbeatable! The heirloom tomatoes taste like real tomatoes from my childhood garden. The packaging was eco-friendly and fully recyclable.'),
        ('Michael Chang', 'michael@example.com', 5, 'Delivery arrived in 3 hours crisp and chilled. The sourdough loaf crust had incredible blister and aroma. Vegist is now our primary grocery provider!'),
        ('Elena Rostova', 'elena@example.com', 5, 'The Family Harvest Box saved us at least ₹500 compared to local supermarkets, and the quality is noticeably superior. Highly recommend!'),
        ('David Miller', 'david@example.com', 4, 'Great produce, especially the baby carrots and broccoli. Fresh, crunchy, and very sweet. Will reorder next Tuesday.'),
    ]

    first_prod = Product.objects.get(slug='organic-farm-harvest-family-box')
    for name, email, rating, comment in sample_reviews:
        Review.objects.get_or_create(
            product=first_prod,
            user_name=name,
            defaults={
                'user_email': email,
                'rating': rating,
                'comment': comment
            }
        )

    print("[SUCCESS] Vegist database seeding completed successfully!")


if __name__ == '__main__':
    seed()

