/**
 * Vegist - Organic Food & Grocery Theme
 * Frontend JavaScript Controller (AJAX Cart, Wishlist, QuickView, Countdown)
 */

document.addEventListener('DOMContentLoaded', () => {
  initCartDrawer();
  initWishlist();
  initQuickView();
  initCountdownTimer();
  initCategoryToggle();
  initProductTabs();
  initCopyCoupon();
});

// Helper: Get CSRF Cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Toast Notification
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `vegist-toast ${type === 'error' ? 'toast-error' : ''}`;
  const icon = type === 'error' ? 'ri-error-warning-line' : 'ri-checkbox-circle-fill';
  toast.innerHTML = `<i class="${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==========================================
// 1. Cart Drawer & AJAX Cart Operations
// ==========================================
function initCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-drawer-overlay');
  const openBtns = document.querySelectorAll('.js-open-cart');
  const closeBtns = document.querySelectorAll('.js-close-cart');

  if (!drawer || !overlay) return;

  window.openCartDrawer = function() {
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    refreshCartDrawer();
  };

  window.closeCartDrawer = function() {
    drawer.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  openBtns.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openCartDrawer();
  }));

  closeBtns.forEach(btn => btn.addEventListener('click', closeCartDrawer));
  overlay.addEventListener('click', closeCartDrawer);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer.classList.contains('active')) {
      closeCartDrawer();
    }
  });

  // Delegate Add To Cart buttons
  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('.js-add-to-cart');
    if (addBtn) {
      e.preventDefault();
      const productId = addBtn.dataset.productId;
      let qtyInput = addBtn.closest('.deal-action-group, .product-card, .modal-dialog')?.querySelector('.js-qty-input');
      if (!qtyInput) {
        qtyInput = document.querySelector(`.js-qty-input[data-product-id="${productId}"]`);
      }
      const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;
      
      const origContent = addBtn.innerHTML;
      addBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Adding...';
      addBtn.disabled = true;

      fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
      })
      .then(res => res.json())
      .then(data => {
        addBtn.innerHTML = origContent;
        addBtn.disabled = false;
        if (data.success) {
          showToast(data.message || 'Added to cart!');
          updateHeaderCartBadge(data.item_count, data.subtotal);
          renderCartDrawerItems(data);
          openCartDrawer();
        } else {
          showToast(data.message || 'Could not add to cart.', 'error');
        }
      })
      .catch(err => {
        addBtn.innerHTML = origContent;
        addBtn.disabled = false;
        console.error('Cart add error:', err);
        showToast('Sorry, this product is currently out of stock or unavailable.', 'error');
      });
    }
  });
}

function refreshCartDrawer() {
  fetch('/cart/drawer-data/')
    .then(res => res.json())
    .then(data => {
      renderCartDrawerItems(data);
    })
    .catch(err => console.error('Failed to load cart drawer:', err));
}

function renderCartDrawerItems(data) {
  const container = document.getElementById('cart-drawer-items-list');
  const countSpan = document.getElementById('cart-drawer-count');
  const subtotalSpan = document.getElementById('cart-drawer-subtotal');
  const progressFill = document.getElementById('cart-shipping-progress-fill');
  const shippingMsg = document.getElementById('cart-shipping-message');

  if (countSpan) countSpan.textContent = data.item_count || data.items?.length || 0;
  if (subtotalSpan) subtotalSpan.textContent = `₹${parseFloat(data.subtotal || 0).toFixed(2)}`;

  // Update free shipping bar
  if (progressFill && shippingMsg) {
    const progress = data.free_shipping_progress || 0;
    progressFill.style.width = `${progress}%`;
    const remaining = parseFloat(data.free_shipping_remaining || 0);
    if (remaining <= 0) {
      shippingMsg.innerHTML = '<strong style="color:#15803d;"><i class="ri-checkbox-circle-fill"></i> Congratulations! You unlocked Free Shipping!</strong>';
    } else {
      shippingMsg.innerHTML = `Add <strong>₹${remaining.toFixed(2)}</strong> more to get <strong>FREE SHIPPING</strong>!`;
    }
  }

  // Update Header Badges
  updateHeaderCartBadge(data.item_count, data.subtotal);

  if (!container) return;

  const items = data.cart_items || data.items || [];
  if (items.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size: 3.5rem; color: #cbd5e1; margin-bottom: 1rem;"><i class="ri-shopping-basket-line"></i></div>
        <h4 style="font-size: 1.15rem; color: #0f172a; margin-bottom: 0.5rem;">Your Cart is Empty</h4>
        <p style="font-size: 0.875rem; color: #64748b; margin-bottom: 1.5rem;">Explore our fresh organic harvest and add items to your cart!</p>
        <a href="/shop/" class="btn btn-primary" onclick="closeCartDrawer()">Start Shopping</a>
      </div>
    `;
    const footer = document.getElementById('cart-drawer-footer');
    if (footer) footer.style.display = 'none';
    return;
  }

  const footer = document.getElementById('cart-drawer-footer');
  if (footer) footer.style.display = 'block';

  let html = '';
  items.forEach(item => {
    html += `
      <div class="cart-item-row" data-product-id="${item.id}">
        <div class="cart-item-thumb">
          <img src="${item.image_url}" alt="${item.name}">
        </div>
        <div class="cart-item-info">
          <a href="${item.url}" class="cart-item-name">${item.name}</a>
          <div class="cart-item-meta">${item.unit} | ₹${parseFloat(item.price).toFixed(2)}</div>
          <div class="cart-qty-stepper">
            <button type="button" class="qty-btn" onclick="updateItemQty(${item.id}, 'decrement')"><i class="ri-subtract-line"></i></button>
            <span class="qty-val">${item.quantity}</span>
            <button type="button" class="qty-btn" onclick="updateItemQty(${item.id}, 'increment')"><i class="ri-add-line"></i></button>
          </div>
        </div>
        <button type="button" class="cart-item-remove-btn" title="Remove" onclick="removeItemFromCart(${item.id})">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    `;
  });
  container.innerHTML = html;
}

function updateHeaderCartBadge(count, subtotal) {
  const badge = document.querySelector('.header-cart-badge');
  const subtotalEl = document.querySelector('.header-cart-subtotal');
  if (badge) badge.textContent = count || 0;
  if (subtotalEl && subtotal) subtotalEl.textContent = `₹${parseFloat(subtotal).toFixed(2)}`;
}

window.updateItemQty = function(productId, action) {
  const endpoint = action === 'decrement' ? `/cart/decrement/${productId}/` : `/cart/add/${productId}/`;
  const body = action === 'decrement' ? '' : 'quantity=1';

  fetch(endpoint, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body
  })
  .then(res => res.json())
  .then(() => refreshCartDrawer())
  .catch(err => console.error(err));
};

window.removeItemFromCart = function(productId) {
  fetch(`/cart/remove/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(res => res.json())
  .then(data => {
    showToast(data.message || 'Item removed from cart.');
    refreshCartDrawer();
  })
  .catch(err => console.error(err));
};

// ==========================================
// 2. Wishlist AJAX Operations
// ==========================================
function initWishlist() {
  document.addEventListener('click', (e) => {
    const wishBtn = e.target.closest('.js-toggle-wishlist');
    if (wishBtn) {
      e.preventDefault();
      const productId = wishBtn.dataset.productId;

      fetch(`/accounts/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(data.message);
          const badge = document.querySelector('.header-wishlist-badge');
          if (badge) badge.textContent = data.wishlist_count;

          // Toggle active styling on button
          if (data.added) {
            wishBtn.classList.add('active');
            wishBtn.innerHTML = '<i class="ri-heart-fill"></i>';
          } else {
            wishBtn.classList.remove('active');
            wishBtn.innerHTML = '<i class="ri-heart-line"></i>';
          }
        }
      })
      .catch(err => console.error('Wishlist error:', err));
    }
  });
}

// ==========================================
// 3. Quick View Modal AJAX
// ==========================================
function initQuickView() {
  const modal = document.getElementById('quick-view-modal');
  if (!modal) return;

  const closeBtn = modal.querySelector('.modal-close-btn');
  const overlay = modal.querySelector('.modal-backdrop') || modal;

  window.closeQuickView = function() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  };

  if (closeBtn) closeBtn.addEventListener('click', closeQuickView);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeQuickView();
  });

  document.addEventListener('click', (e) => {
    const qvBtn = e.target.closest('.js-quick-view');
    if (qvBtn) {
      e.preventDefault();
      const productId = qvBtn.dataset.productId;

      fetch(`/quick-view/${productId}/`)
        .then(res => res.json())
        .then(data => {
          document.getElementById('qv-title').textContent = data.name;
          document.getElementById('qv-category').textContent = data.category;
          document.getElementById('qv-price').textContent = `₹${parseFloat(data.price).toFixed(2)}`;
          const oldPriceEl = document.getElementById('qv-old-price');
          if (data.old_price) {
            oldPriceEl.textContent = `₹${parseFloat(data.old_price).toFixed(2)}`;
            oldPriceEl.style.display = 'inline';
          } else {
            oldPriceEl.style.display = 'none';
          }
          document.getElementById('qv-desc').textContent = data.short_description;
          document.getElementById('qv-unit').textContent = data.unit;
          document.getElementById('qv-image').src = data.image_url;
          document.getElementById('qv-detail-link').href = data.url;
          document.getElementById('qv-add-btn').dataset.productId = data.id;

          const qvQtyInp = document.getElementById('qv-qty-input');
          if (qvQtyInp) {
            qvQtyInp.value = 1;
            qvQtyInp.dataset.productId = data.id;
          }

          const stockStatus = document.getElementById('qv-stock');
          const qvAddBtn = document.getElementById('qv-add-btn');

          if (stockStatus) {
            stockStatus.innerHTML = data.in_stock 
              ? '<span style="color:#15803d; font-weight:700;"><i class="ri-checkbox-circle-fill"></i> In Stock (Ships Today)</span>' 
              : '<span style="color:#ef4444; font-weight:700;"><i class="ri-close-circle-fill"></i> Sold Out</span>';
          }

          if (qvAddBtn) {
            if (!data.in_stock) {
              qvAddBtn.disabled = true;
              qvAddBtn.style.opacity = '0.6';
              qvAddBtn.style.cursor = 'not-allowed';
              qvAddBtn.innerHTML = '<i class="ri-close-line"></i> Sold Out';
            } else {
              qvAddBtn.disabled = false;
              qvAddBtn.style.opacity = '1';
              qvAddBtn.style.cursor = 'pointer';
              qvAddBtn.innerHTML = '<i class="ri-shopping-basket-fill"></i> Add to Cart';
            }
          }

          modal.classList.add('active');
          document.body.style.overflow = 'hidden';
        })
        .catch(err => console.error('Quick view error:', err));
    }
  });
}

// ==========================================
// 4. Countdown Timer for Deal of the Day
// ==========================================
function initCountdownTimer() {
  const timerContainer = document.querySelector('.deal-countdown-box');
  if (!timerContainer) return;

  const endsAtAttr = timerContainer.dataset.dealEnds;
  let targetDate;
  if (endsAtAttr) {
    targetDate = new Date(endsAtAttr);
    if (isNaN(targetDate.getTime()) || targetDate.getTime() <= Date.now()) {
      targetDate = new Date(Date.now() + 2 * 24 * 3600 * 1000 + 14 * 3600 * 1000);
    }
  } else {
    targetDate = new Date(Date.now() + 2 * 24 * 3600 * 1000 + 14 * 3600 * 1000);
  }

  function update() {
    const now = new Date().getTime();
    const distance = targetDate.getTime() - now;

    if (distance < 0) {
      timerContainer.innerHTML = '<span style="font-weight:700; color: #ef4444;"><i class="ri-alarm-warning-line"></i> Flash Deal Expired</span>';
      return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    const dEl = document.getElementById('timer-days');
    const hEl = document.getElementById('timer-hours');
    const mEl = document.getElementById('timer-mins');
    const sEl = document.getElementById('timer-secs');

    if (dEl) dEl.textContent = String(days).padStart(2, '0');
    if (hEl) hEl.textContent = String(hours).padStart(2, '0');
    if (mEl) mEl.textContent = String(minutes).padStart(2, '0');
    if (sEl) sEl.textContent = String(seconds).padStart(2, '0');
  }

  update();
  setInterval(update, 1000);
}

// ==========================================
// 5. Category Menu Dropdown
// ==========================================
function initCategoryToggle() {
  const toggleBtn = document.querySelector('.categories-toggle-btn');
  const menu = document.querySelector('.categories-dropdown-menu');
  if (!toggleBtn || !menu) return;

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('show');
  });

  document.addEventListener('click', (e) => {
    if (!toggleBtn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('show');
    }
  });
}

// ==========================================
// 6. Interactive Product Showcase Tabs
// ==========================================
function initProductTabs() {
  const tabButtons = document.querySelectorAll('.product-tabs .tab-btn');
  if (!tabButtons.length) return;

  tabButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tabTarget = btn.dataset.tab;
      
      // Update active state on buttons
      tabButtons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      // Update visible pane
      const allPanes = document.querySelectorAll('.product-tab-pane');
      allPanes.forEach(pane => pane.classList.remove('active'));

      const targetPane = document.getElementById(`tab-${tabTarget}`);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });
}

// ==========================================
// 7. Copy Promo Coupon Code
// ==========================================
function initCopyCoupon() {
  const copyBtns = document.querySelectorAll('.js-copy-coupon');
  copyBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const code = btn.dataset.code || 'VEGIST20';
      if (navigator.clipboard) {
        navigator.clipboard.writeText(code).then(() => {
          showToast(`Coupon code ${code} copied! Applied on checkout.`);
        }).catch(() => {
          showToast(`Coupon code: ${code}`);
        });
      } else {
        showToast(`Coupon code: ${code}`);
      }
    });
  });
}
