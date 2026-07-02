/**
 * main.js - Agri Smart Frontend JavaScript
 * Handles cart interactions, UI animations, and general UX
 */

// ===========================================================================
// DOM Ready
// ===========================================================================
document.addEventListener('DOMContentLoaded', function () {
  initFlashMessages();
  initQuantityControls();
  initPaymentOptions();
  initSearchBar();
  initAdminSidebar();
  initProductImageFallback();
  initSmoothAnimations();
  initCategoryFilter();
});

// ===========================================================================
// Flash Messages — Auto-dismiss after 5 seconds
// ===========================================================================
function initFlashMessages() {
  const alerts = document.querySelectorAll('.flash-alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });
}

// ===========================================================================
// Quantity Controls — +/- buttons on cart and product detail pages
// ===========================================================================
function initQuantityControls() {
  // Quantity increment/decrement buttons
  document.querySelectorAll('[data-qty-btn]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const action  = btn.dataset.qtyBtn;         // 'inc' or 'dec'
      const inputId = btn.dataset.target;
      const input   = document.getElementById(inputId);
      if (!input) return;

      let val = parseInt(input.value, 10) || 1;
      if (action === 'inc') {
        val = Math.min(val + 1, parseInt(input.max || 999, 10));
      } else {
        val = Math.max(val - 1, parseInt(input.min || 1, 10));
      }
      input.value = val;

      // Trigger change event for form-auto-submit on cart page
      input.dispatchEvent(new Event('change'));
    });
  });

  // Auto-submit cart update form when quantity changes
  document.querySelectorAll('.cart-qty-input').forEach(function (input) {
    input.addEventListener('change', function () {
      const form = input.closest('form');
      if (form) form.submit();
    });
  });
}

// ===========================================================================
// Payment Options — Highlight selected payment card + show extra fields
// ===========================================================================
function initPaymentOptions() {
  const options = document.querySelectorAll('.payment-option');
  const cardFields = document.getElementById('creditCardFields');
  const vodafoneFields = document.getElementById('vodafoneFields');

  options.forEach(function (opt) {
    opt.addEventListener('click', function () {
      options.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');

      const radio = opt.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;

      // Show/hide extra fields
      const val = radio ? radio.value : '';

      if (cardFields) {
        cardFields.style.display = (val === 'Credit Card') ? 'block' : 'none';
      }
      if (vodafoneFields) {
        vodafoneFields.style.display = (val === 'Vodafone Cash') ? 'block' : 'none';
      }
    });
  });

  // Init: mark first as selected
  if (options.length > 0) {
    options[0].click();
  }
}

// ===========================================================================
// Search Bar — Live URL update on category select
// ===========================================================================
function initSearchBar() {
  const categorySelect = document.getElementById('categoryFilter');
  if (categorySelect) {
    categorySelect.addEventListener('change', function () {
      const form = categorySelect.closest('form');
      if (form) form.submit();
    });
  }
}

// ===========================================================================
// Admin Sidebar — Mobile toggle
// ===========================================================================
function initAdminSidebar() {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('adminSidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
  });

  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }
}

// ===========================================================================
// Product Image Fallback — Replace broken images with placeholder
// ===========================================================================
function initProductImageFallback() {
  document.querySelectorAll('img[data-product-img]').forEach(function (img) {
    img.addEventListener('error', function () {
      img.src = '/static/images/placeholder.svg';
    });
  });
}

// ===========================================================================
// Smooth Scroll Animations — Intersection Observer for fade-in
// ===========================================================================
function initSmoothAnimations() {
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.product-card, .category-card, .feature-card, .stat-card').forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // CSS class added by observer
  const style = document.createElement('style');
  style.textContent = '.animate-in { opacity: 1 !important; transform: translateY(0) !important; }';
  document.head.appendChild(style);
}

// ===========================================================================
// Category Filter on Shop Page
// ===========================================================================
function initCategoryFilter() {
  // Highlight active category in the sidebar filter
  const params = new URLSearchParams(window.location.search);
  const activeCat = params.get('category');

  if (activeCat) {
    const link = document.querySelector(`.cat-filter-link[data-cat-id="${activeCat}"]`);
    if (link) {
      link.classList.add('active');
      link.style.fontWeight = '700';
    }
  }
}

// ===========================================================================
// Confirm Delete — Show confirmation dialog before delete actions
// ===========================================================================
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}

// ===========================================================================
// Cart Count Badge Update (optional AJAX enhancement)
// ===========================================================================
function updateCartBadge(count) {
  const badge = document.querySelector('.cart-count');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }
}

// ===========================================================================
// Admin: Toggle status dropdown on table row
// ===========================================================================
function submitStatusForm(selectEl) {
  const form = selectEl.closest('form');
  if (form) form.submit();
}

// ===========================================================================
// Admin: Image Preview on file input change
// ===========================================================================
const imageFileInput = document.getElementById('image_file');
const imagePreview   = document.getElementById('imagePreview');

if (imageFileInput && imagePreview) {
  imageFileInput.addEventListener('change', function () {
    const file = imageFileInput.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
}

// ===========================================================================
// Navbar scroll effect — add shadow on scroll
// ===========================================================================
window.addEventListener('scroll', function () {
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    if (window.scrollY > 20) {
      navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.25)';
    } else {
      navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.15)';
    }
  }
});
