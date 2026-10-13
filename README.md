# 🥦 Vegist - Organic Food & Grocery eCommerce Supermarket

A full-stack, state-of-the-art Python & Django eCommerce web application inspired by the **Vegist Vegetables & Organic Food Shopify Theme**.

Built with a focus on fresh organic aesthetics, instant AJAX interactions, clean architecture, and comprehensive grocery store workflows.

---

## 🌟 Key Features

### 🛒 1. Customer Shopping & Catalog
* **Modern Organic Theme**: Curated emerald green & harvest amber palette, Outfit & Plus Jakarta Sans typography, and organic farm imagery.
* **Top Announcement Bar**: Free shipping tracker notification, customer helpline (+1 800 555-VEGI), and daily deal alerts.
* **Smart Header**: Instant search bar with Category selector dropdown, live wishlist count badge, and dynamic shopping cart trigger.
* **Mega Menu & Categories**: "All Farm Categories" dropdown navigation with live item counts.
* **Deal of the Day**: Interactive countdown timer (Days : Hours : Mins : Secs) with live stock inventory progress bar.
* **Interactive Product Cards**:
  - Discount badges (`-25%`, `HOT`, `100% ORGANIC`, `BESTSELLER`)
  - Instant AJAX Heart Wishlist toggle
  - Quick View Modal popup with nutritional facts and pack size
  - Quick Add to Cart button with animated feedback

### ⚡ 2. Slide-In AJAX Cart & Drawer
* **Flyout Side Drawer**: Slides in smoothly without reloading the page.
* **Free Delivery Progress Tracker**: Live progress bar showing how much more to add to unlock Free Shipping ($50 threshold).
* **Quantity Controls**: Instant `+` / `-` steppers and remove item actions.
* **Promotional Coupon System**: Apply promo vouchers (e.g. `VEGIST20` for 20% OFF).

### 💳 3. Checkout & Order Management
* **Multi-Step Checkout**: Billing address form, order notes, and prefill for logged-in members.
* **Payment Gateways**:
  - **Razorpay Online Gateway**: Full integration supporting UPI (Google Pay, PhonePe, Paytm, QR), Credit & Debit Cards (Visa, Mastercard, RuPay), and NetBanking via official Razorpay Checkout SDK with backend cryptographic signature verification (`verify_payment_signature`).
  - **Cash on Delivery (COD)**: Doorstep cash or UPI delivery option with 1-click fallback from Razorpay.

### 👤 4. User Accounts & Dashboard
* **Customer Authentication**: Register, Login, and Logout with validation.
* **Profile Management**: Saved delivery address and phone number.
* **Order History**: Real-time order status tracking (`Order Placed`, `Processing`, `Out for Delivery`, `Delivered`).
* **Wishlist Page**: Saved items grid with instant 1-click cart addition.

### 🛠️ 5. Django Admin Portal
* Customized admin branding (`Vegist Organic Supermarket Admin`).
* Inline product management, stock monitoring, coupon creation, and order status updates.

---

## 🔑 Demo Credentials

| Role | Username / Email | Password |
|---|---|---|
| **Admin Superuser** | `admin` | `admin123` |
| **Demo Customer** | `customer@vegist.com` | `customer123` |

### 🎟️ Active Promo Coupon Codes
* `VEGIST20` - **20% OFF**
* `ORGANIC15` - **15% OFF**
* `FRESH10` - **10% OFF**

### 💳 Razorpay Configuration (Optional)
To use your own Razorpay live or test credentials, configure these environment variables or update `vegist_project/settings.py`:
```bash
set RAZORPAY_KEY_ID="rzp_test_your_key_id"
set RAZORPAY_KEY_SECRET="your_key_secret"
```
*(If unconfigured, the system automatically runs in Development Test Mode with simulated instant payment verification).*

---

## 🚀 Running the Project

1. **Activate Server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
2. **Open in Browser**:
   - Storefront: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Shop Catalog: [http://127.0.0.1:8000/shop/](http://127.0.0.1:8000/shop/)
   - Deals of the Day: [http://127.0.0.1:8000/deals/](http://127.0.0.1:8000/deals/)
   - Admin Portal: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📁 Project Architecture

```
new project/
├── manage.py
├── seed_data.py               # Preloads 6 categories, 18 products, coupons & users
├── vegist_project/            # Django root configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                     # Storefront, Catalog, Search, Reviews, Pages
│   ├── models.py              # Category, Product, Review, NewsletterSubscriber
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── cart/                      # Cart session handler, AJAX drawer, Coupons
│   ├── cart.py
│   ├── models.py              # Coupon model
│   ├── views.py
│   ├── urls.py
│   └── context_processors.py
├── orders/                    # Checkout, Orders, Receipts
│   ├── models.py              # Order, OrderItem
│   ├── views.py
│   └── urls.py
├── accounts/                  # User Auth, Profiles, Wishlists
│   ├── models.py              # Profile, WishlistItem
│   ├── views.py
│   └── urls.py
├── static/
│   ├── css/vegist.css         # Complete bespoke Vegist styling
│   ├── js/vegist.js           # AJAX cart, drawer, quick-view, countdown timer
│   └── images/                # High-res organic farm assets
└── templates/                 # Semantic HTML5 templates & components
    ├── base.html
    ├── components/            # Header, Footer, Cart Drawer, Quick View Modal
    ├── store/                 # Home, Shop, Product Detail, Deals, About, Contact
    ├── cart/                  # Cart detail page
    ├── orders/                # Checkout & Order Success Invoice
    └── accounts/              # Login, Register, Profile, Wishlist
```
