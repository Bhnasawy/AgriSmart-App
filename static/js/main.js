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
  initLanguage();       // ← restore saved language on every page load
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

// ===========================================================================
// Language Toggle — Arabic / English
// ===========================================================================

// ─── Translation Dictionary ───────────────────────────────────────────────
const translations = {
  en: {
    // Navbar
    'nav-home':        'Home',
    'nav-shop':        'Shop',
    'nav-categories':  'Categories',
    'nav-about':       'About',
    'nav-contact':     'Contact',
    'nav-ai':          'AI Tools',
    'nav-crop':        'Crop Recommendation',
    'nav-tomato':      'Tomato Diagnosis',
    'nav-login':       'Login',
    'nav-register':    'Register',
    'nav-profile':     'My Profile',
    'nav-orders':      'My Orders',
    'nav-admin':       'Admin Panel',
    'nav-logout':      'Logout',

    // Hero
    'hero-welcome':    '🌱 WELCOME TO AGRI SMART',
    'hero-title':      'Grow Smarter,',
    'hero-title-span': 'Harvest Better',
    'hero-sub':        'Empowering your farm with a curated selection of premium agricultural supplies, from certified seeds to advanced farming technology. We are your dedicated one-stop smart-farming partner.',
    'hero-btn-shop':   '🛒 Shop Now',
    'hero-btn-browse': '⊞ Browse Categories',
    'hero-stat-1-num': 'Instant',
    'hero-stat-1':     'Disease Diagnosis',
    'hero-stat-2':     'Detection Success Rate',
    'hero-stat-3-num': 'Optimized',
    'hero-stat-3':     'Resource Usage',

    // Section titles (index)
    'sec-category':    'Shop by Category',
    'sec-category-sub':'Explore our wide range of agricultural product categories',
    'sec-featured':    'Featured Products',
    'sec-featured-sub':'Hand-picked products from our collection',
    'sec-why':         'Why Choose Agri Smart?',
    'sec-why-sub':     "We're committed to supporting every farmer with quality and reliability",
    'sec-best':        'Best Sellers',
    'sec-best-sub':    'Most popular products among our farmers',
    'sec-ai':          'AI Smart Farming',
    'sec-ai-sub':      'Leverage the power of machine learning to make smarter farming decisions',

    // Why-us features
    'feat-quality':    'Certified Quality',
    'feat-delivery':   'Fast Delivery',
    'feat-price':      'Best Prices',
    'feat-support':    'Expert Support',

    // AI cards (index)
    'ai-crop-title':   'Crop Recommendation',
    'ai-tomato-title': 'Tomato Disease Diagnosis',
    'ai-crop-btn':     'Open Predictor',
    'ai-tomato-btn':   'Diagnose Tomato Leaf',

    // CTA
    'cta-title':       'Ready to Transform Your Farm?',
    'cta-sub':         'Join thousands of farmers who trust Agri Smart for their agricultural needs.',
    'cta-btn1':        'Get Started Free',
    'cta-btn2':        'Browse Products',

    // Footer
    'footer-about':    'Your trusted online marketplace for quality agricultural products. We connect farmers with the best fertilizers, seeds, tools, and technology for a productive and sustainable harvest.',
    'footer-links':    'Quick Links',
    'footer-cats':     'Categories',
    'footer-contact':  'Contact Info',
    'footer-copy':     '© 2025 Agri Smart. All rights reserved. Built with ❤️ for farmers everywhere.',

    // Shop page
    'shop-title':          'Our Shop',
    'shop-filter':         'Search & Filter',
    'shop-search-label':   'Search Products',
    'shop-category-label': 'Category',
    'shop-all-cats':       'All Categories',
    'shop-apply':          'Apply Filters',
    'shop-clear':          'Clear Filters',
    'shop-browse-cat':     'Browse by Category',
    'shop-all-products':   'All Products',
    'cats-browse':         'Browse',
    'cats-products':       'Products',
    'cats-more':           'more',
    'shop-no-products':    'No Products Found',
    'shop-no-products-sub':'Try adjusting your search or filter criteria.',
    'shop-view-all':       'View All Products',

    // Product card & details
    'prod-add-cart':   'Add to Cart',
    'prod-out-stock':  'Out of Stock',
    'prod-view':       'View Details',
    'prod-in-stock':   'In Stock',
    'badge-featured':  'Featured',
    'badge-bestseller':'Best Seller',
    'prod-detail-units':'units available',
    'prod-detail-out': 'Currently out of stock',
    'prod-view-cart':  'View Cart',
    'prod-detail-warn':'This product is currently out of stock. Please check back later.',
    'feat-returns':    'Easy Returns',
    'feat-secure':     'Secure Payment',
    'prod-related':    'Related Products',

    // About page
    'abt-hero-title':  'About',
    'abt-hero-sub':    'Empowering farmers with quality products, smart technology, and expert knowledge for a more productive and sustainable future.',
    'abt-mission-badge':'Our Mission',
    'abt-mission-title':'Growing Together for a Better Tomorrow',
    'abt-mission-p1':  'Agri Smart was founded with a simple mission: to make quality agricultural products accessible to every farmer, regardless of their location. We believe that when farmers have access to the right tools, seeds, and knowledge, entire communities thrive.',
    'abt-mission-p2':  'From small family farms to large agricultural enterprises, we serve farmers across the region with a carefully curated selection of certified products at competitive prices.',
    'abt-stat-rating': 'Customer Rating',
    'abt-values-title':'Our Core Values',
    'abt-val1-t':      'Quality First',
    'abt-val1-p':      'Every product is rigorously tested and certified before reaching our shelves. We never compromise on quality.',
    'abt-val2-t':      'Farmer-Centric',
    'abt-val2-p':      'We listen to farmers, understand their needs, and constantly improve our product selection based on real feedback.',
    'abt-val3-t':      'Sustainability',
    'abt-val3-p':      'We prioritize eco-friendly products and sustainable farming practices to protect the environment for future generations.',
    'abt-cta-title':   'Ready to Start Farming Smarter?',
    'abt-cta-sub':     'Join Agri Smart today and discover a better way to farm.',
    'abt-cta-btn1':    'Get Started',
    'abt-cta-btn2':    'Contact Us',

    // Categories page
    'cats-title':      'Product Categories',
    'cats-sub':        'Explore our 6 agricultural product categories and find everything your farm needs',

    // AI — Crop page
    'crop-page-title': 'Crop Recommendation',
    'crop-page-sub':   'Enter your soil and climate data to get an AI-powered crop recommendation',
    'crop-n-label':    'Nitrogen (N)',
    'crop-p-label':    'Phosphorus (P)',
    'crop-k-label':    'Potassium (K)',
    'crop-temp-label': 'Temperature (°C)',
    'crop-hum-label':  'Humidity (%)',
    'crop-ph-label':   'Soil pH',
    'crop-rain-label': 'Rainfall (mm)',
    'crop-btn':        'Get Recommendation',
    'crop-result':     'Recommended Crop',
    'crop-soil-section':'Soil Composition',
    'crop-env-section':'Environmental Factors',
    'crop-mode-manual':'Manual Entry',
    'crop-mode-auto':  'Weather Autofill',
    'crop-test-data':  'Test Data',
    'ai-crop-desc':    'Enter your soil\'s nitrogen, phosphorus, potassium levels, temperature, humidity, pH, and rainfall data. Our AI model recommends the most suitable crop for your conditions with high accuracy.',
    'ai-crop-feat1':   '7 environmental parameters',
    'ai-crop-feat2':   '22 crop varieties supported',
    'ai-crop-feat3':   'Weather autofill integration',

    // AI — Tomato page
    'tomato-page-title': 'Tomato Leaf Diagnosis',
    'tomato-page-sub':   'Upload a photo of your tomato leaf to detect diseases instantly',
    'tomato-upload-btn': 'Upload & Diagnose',
    'tomato-result':     'Diagnosis Result',
    'tomato-treatment':  'Treatment',
    'tomato-pesticide':  'Recommended Pesticide',
    'tomato-drop-title': 'Drag & Drop Image Here',
    'tomato-drop-sub':   'or click to browse from your device',
    'tomato-select-btn': 'Select Image',
    'tomato-no-result':  'No Result Yet',
    'tomato-upload-hint':'Upload an image to see the diagnosis',
    'tomato-analyzing':  'Analyzing Image...',
    'tomato-model-running':'Running EfficientNetB3 deep learning model',
    'tomato-diagnose-another':'Diagnose Another Leaf',
    'ai-tom-desc':       'Upload a photo of your tomato leaf and our deep learning model will instantly diagnose any disease, showing confidence score, recommended treatment, and suggested pesticides.',
    'ai-tom-feat1':      '10 disease classes detected',
    'ai-tom-feat2':      'Confidence score provided',
    'ai-tom-feat3':      'Treatment & pesticide advice',

    // Cart page
    'cart-title':      'Your Cart',
    'cart-empty':      'Your cart is empty',
    'cart-checkout':   'Proceed to Checkout',
    'cart-continue':   'Continue Shopping',
    'cart-total':      'Total',
    'cart-qty':        'Quantity',
    'cart-remove':     'Remove',

    // Lang button label (shows target language)
    'lang-label':      'ع',
  },

  ar: {
    // Navbar
    'nav-home':        'الرئيسية',
    'nav-shop':        'المتجر',
    'nav-categories':  'التصنيفات',
    'nav-about':       'عن المنصة',
    'nav-contact':     'تواصل معنا',
    'nav-ai':          'أدوات الذكاء الاصطناعي',
    'nav-crop':        'توصية المحاصيل',
    'nav-tomato':      'تشخيص الطماطم',
    'nav-login':       'تسجيل الدخول',
    'nav-register':    'إنشاء حساب',
    'nav-profile':     'ملفي الشخصي',
    'nav-orders':      'طلباتي',
    'nav-admin':       'لوحة التحكم',
    'nav-logout':      'تسجيل الخروج',

    // Hero
    'hero-welcome':    '🌱 مرحباً بك في أجري سمارت',
    'hero-title':      'ازرع بذكاء،',
    'hero-title-span': 'واحصد أفضل',
    'hero-sub':        'نمكّن مزرعتك بمجموعة مختارة من مستلزمات الزراعة الفاخرة، من البذور المعتمدة إلى تكنولوجيا الزراعة المتقدمة. نحن شريكك الذكي الشامل في عالم الزراعة.',
    'hero-btn-shop':   '🛒 تسوق الآن',
    'hero-btn-browse': '⊞ استعرض التصنيفات',
    'hero-stat-1-num': 'فوري',
    'hero-stat-1':     'تشخيص الأمراض',
    'hero-stat-2':     'معدل نجاح الكشف',
    'hero-stat-3-num': 'مُحسَّن',
    'hero-stat-3':     'استهلاك الموارد',

    // Section titles (index)
    'sec-category':    'تسوق حسب التصنيف',
    'sec-category-sub':'استكشف مجموعتنا الواسعة من تصنيفات المنتجات الزراعية',
    'sec-featured':    'منتجات مميزة',
    'sec-featured-sub':'منتجات مختارة بعناية من مجموعتنا',
    'sec-why':         'لماذا أجري سمارت؟',
    'sec-why-sub':     'نلتزم بدعم كل مزارع بجودة وموثوقية عالية',
    'sec-best':        'الأكثر مبيعاً',
    'sec-best-sub':    'المنتجات الأكثر شعبية بين مزارعينا',
    'sec-ai':          'الزراعة الذكية بالذكاء الاصطناعي',
    'sec-ai-sub':      'استخدم قوة تعلم الآلة لاتخاذ قرارات زراعية أذكى',

    // Why-us features
    'feat-quality':    'جودة معتمدة',
    'feat-delivery':   'توصيل سريع',
    'feat-price':      'أفضل الأسعار',
    'feat-support':    'دعم متخصص',

    // AI cards (index)
    'ai-crop-title':   'توصية المحاصيل',
    'ai-tomato-title': 'تشخيص أمراض الطماطم',
    'ai-crop-btn':     'افتح المحلل',
    'ai-tomato-btn':   'شخّص ورقة الطماطم',

    // CTA
    'cta-title':       'هل أنت مستعد لتحويل مزرعتك؟',
    'cta-sub':         'انضم إلى آلاف المزارعين الذين يثقون بأجري سمارت لتلبية احتياجاتهم الزراعية.',
    'cta-btn1':        'ابدأ مجاناً',
    'cta-btn2':        'استعرض المنتجات',

    // Footer
    'footer-about':    'سوقك الإلكتروني الموثوق لأفضل المنتجات الزراعية. نربط المزارعين بأجود الأسمدة والبذور والأدوات والتكنولوجيا لحصاد منتج ومستدام.',
    'footer-links':    'روابط سريعة',
    'footer-cats':     'التصنيفات',
    'footer-contact':  'معلومات التواصل',
    'footer-copy':     '© 2025 أجري سمارت. جميع الحقوق محفوظة. صُنع بـ ❤️ للمزارعين في كل مكان.',

    // Shop page
    'shop-title':          'متجرنا',
    'shop-filter':         'بحث وتصفية',
    'shop-search-label':   'ابحث عن منتج',
    'shop-category-label': 'التصنيف',
    'shop-all-cats':       'جميع التصنيفات',
    'shop-apply':          'تطبيق الفلتر',
    'shop-clear':          'مسح الفلتر',
    'shop-browse-cat':     'تصفح حسب التصنيف',
    'shop-all-products':   'جميع المنتجات',
    'shop-no-products':    'لا توجد منتجات',
    'shop-no-products-sub':'جرب تعديل معايير البحث أو الفلتر.',
    'shop-view-all':       'عرض جميع المنتجات',

    // Product card & details
    'prod-add-cart':   'أضف للسلة',
    'prod-out-stock':  'نفدت الكمية',
    'prod-view':       'عرض التفاصيل',
    'prod-in-stock':   'متوفر',
    'badge-featured':  'مميز',
    'badge-bestseller':'الأكثر مبيعاً',
    'prod-detail-units':'قطعة متوفرة',
    'prod-detail-out': 'غير متوفر حالياً',
    'prod-view-cart':  'عرض السلة',
    'prod-detail-warn':'هذا المنتج غير متوفر حالياً. يرجى التحقق لاحقاً.',
    'feat-returns':    'إرجاع سهل',
    'feat-secure':     'دفع آمن',
    'cats-browse':     'تصفح',
    'cats-products':   'منتجات',
    'cats-more':       'إضافية',
    'prod-related':    'منتجات ذات صلة',

    // About page
    'abt-hero-title':  'عن',
    'abt-hero-sub':    'نمكّن المزارعين بأفضل المنتجات، والتكنولوجيا الذكية، والخبرات لمستقبل زراعي أكثر إنتاجية واستدامة.',
    'abt-mission-badge':'مهمتنا',
    'abt-mission-title':'ننمو معاً من أجل غدٍ أفضل',
    'abt-mission-p1':  'تأسست أجري سمارت بمهمة بسيطة: جعل المنتجات الزراعية عالية الجودة في متناول كل مزارع، بغض النظر عن موقعه. نحن نؤمن أنه عندما يمتلك المزارعون الأدوات والبذور والمعرفة الصحيحة، فإن المجتمعات بأكملها تزدهر.',
    'abt-mission-p2':  'من المزارع العائلية الصغيرة إلى المؤسسات الزراعية الكبرى، نخدم المزارعين في جميع أنحاء المنطقة بمجموعة مختارة بعناية من المنتجات المعتمدة بأسعار تنافسية.',
    'abt-stat-rating': 'تقييم العملاء',
    'abt-values-title':'قيمنا الأساسية',
    'abt-val1-t':      'الجودة أولاً',
    'abt-val1-p':      'يتم اختبار واعتماد كل منتج بدقة قبل وصوله إلى رفوفنا. نحن لا نساوم أبداً على الجودة.',
    'abt-val2-t':      'المزارع هو المركز',
    'abt-val2-p':      'نستمع إلى المزارعين، ونفهم احتياجاتهم، ونعمل باستمرار على تحسين اختيار منتجاتنا بناءً على الملاحظات الحقيقية.',
    'abt-val3-t':      'الاستدامة',
    'abt-val3-p':      'نحن نعطي الأولوية للمنتجات الصديقة للبيئة والممارسات الزراعية المستدامة لحماية البيئة للأجيال القادمة.',
    'abt-cta-title':   'هل أنت مستعد لبدء الزراعة بذكاء؟',
    'abt-cta-sub':     'انضم إلى أجري سمارت اليوم واكتشف طريقة أفضل للزراعة.',
    'abt-cta-btn1':    'ابدأ الآن',
    'abt-cta-btn2':    'تواصل معنا',

    // Categories page
    'cats-title':      'تصنيفات المنتجات',
    'cats-sub':        'استكشف تصنيفاتنا الستة من المنتجات الزراعية وجد كل ما تحتاجه مزرعتك',

    // AI — Crop page
    'crop-page-title': 'توصية المحاصيل',
    'crop-page-sub':   'أدخل بيانات التربة والمناخ للحصول على توصية محصول بالذكاء الاصطناعي',
    'crop-n-label':    'النيتروجين (N)',
    'crop-p-label':    'الفوسفور (P)',
    'crop-k-label':    'البوتاسيوم (K)',
    'crop-temp-label': 'درجة الحرارة (°م)',
    'crop-hum-label':  'الرطوبة (%)',
    'crop-ph-label':   'درجة حموضة التربة (pH)',
    'crop-rain-label': 'كمية الأمطار (ملم)',
    'crop-btn':        'احصل على التوصية',
    'crop-result':     'المحصول الموصى به',
    'crop-soil-section':'مكونات التربة',
    'crop-env-section':'العوامل البيئية',
    'crop-mode-manual':'إدخال يدوي',
    'crop-mode-auto':  'ملء تلقائي للطقس',
    'crop-test-data':  'بيانات اختبار',
    'ai-crop-desc':    'أدخل مستويات النيتروجين والفوسفور والبوتاسيوم في التربة ودرجة الحرارة والرطوبة ودرجة الحموضة وبيانات هطول الأمطار. يوصي نموذج الذكاء الاصطناعي لدينا بالمحصول الأنسب لظروفك بدقة عالية.',
    'ai-crop-feat1':   '7 معايير بيئية',
    'ai-crop-feat2':   '22 نوعًا من المحاصيل مدعومة',
    'ai-crop-feat3':   'تكامل تلقائي لبيانات الطقس',

    // AI — Tomato page
    'tomato-page-title': 'تشخيص ورقة الطماطم',
    'tomato-page-sub':   'ارفع صورة ورقة الطماطم لاكتشاف الأمراض فوراً',
    'tomato-upload-btn': 'ارفع وشخّص',
    'tomato-result':     'نتيجة التشخيص',
    'tomato-treatment':  'طريقة العلاج',
    'tomato-pesticide':  'المبيد الموصى به',
    'tomato-drop-title': 'اسحب وأفلت الصورة هنا',
    'tomato-drop-sub':   'أو انقر لتصفح جهازك',
    'tomato-select-btn': 'اختر صورة',
    'tomato-no-result':  'لا توجد نتيجة بعد',
    'tomato-upload-hint':'ارفع صورة لرؤية التشخيص',
    'tomato-analyzing':  'جاري تحليل الصورة...',
    'tomato-model-running':'تشغيل نموذج التعلم العميق EfficientNetB3',
    'tomato-diagnose-another':'تشخيص ورقة أخرى',
    'ai-tom-desc':       'قم بتحميل صورة لورقة الطماطم وسيقوم نموذج التعلم العميق الخاص بنا بتشخيص أي مرض على الفور، مع إظهار درجة الثقة والعلاج الموصى به والمبيدات الحشرية المقترحة.',
    'ai-tom-feat1':      'اكتشاف 10 فئات من الأمراض',
    'ai-tom-feat2':      'توفير درجة الثقة',
    'ai-tom-feat3':      'نصائح العلاج والمبيدات',

    // Cart page
    'cart-title':      'سلة التسوق',
    'cart-empty':      'سلتك فارغة',
    'cart-checkout':   'إتمام الشراء',
    'cart-continue':   'مواصلة التسوق',
    'cart-total':      'الإجمالي',
    'cart-qty':        'الكمية',
    'cart-remove':     'حذف',

    // Lang button label (shows target language)
    'lang-label':      'EN',
  }
};

// ─── Apply language to page ────────────────────────────────────────────────
function applyLanguage(lang) {
  const html = document.getElementById('htmlRoot');
  if (!html) return;

  // Set direction and lang
  html.setAttribute('lang', lang === 'ar' ? 'ar' : 'en');
  html.setAttribute('dir',  lang === 'ar' ? 'rtl' : 'ltr');

  const label = translations[lang]['lang-label'];

  // Sync ALL lang button labels (mobile + desktop)
  const mobileLangLabel = document.getElementById('langLabel');
  if (mobileLangLabel) mobileLangLabel.textContent = label;
  document.querySelectorAll('.lang-label-sync').forEach(function(el) {
    el.textContent = label;
  });

  // Translate every element with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(function (el) {
    const key = el.getAttribute('data-i18n');
    const t   = translations[lang];
    if (t && t[key]) el.textContent = t[key];
  });
}

// ─── Toggle between ar ↔ en ───────────────────────────────────────────────
function toggleLanguage() {
  const html    = document.getElementById('htmlRoot');
  const current = html ? html.getAttribute('lang') : 'en';
  const next    = current === 'en' ? 'ar' : 'en';
  
  // Set localStorage as fallback
  localStorage.setItem('agrismart_lang', next);
  
  // Apply visual changes immediately to avoid flash
  applyLanguage(next);
  
  // Also notify server via route to set the cookie for templates (like name_ar)
  fetch(`/set-lang/${next}`)
    .then(() => {
      // Reload page so Flask templates can render correct DB fields
      window.location.reload();
    })
    .catch(err => console.error('Error setting language cookie', err));
}

// ─── Restore saved preference on page load ────────────────────────────────
function initLanguage() {
  const saved = localStorage.getItem('agrismart_lang') || 'en';
  applyLanguage(saved);
}


