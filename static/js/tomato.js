/* ==========================================================================
   Tomato Disease Diagnosis - Client Script
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements - Upload Area
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const uploadPrompt = document.getElementById("upload-prompt");
    const previewContainer = document.getElementById("image-preview-container");
    const imagePreview = document.getElementById("image-preview");
    const btnChange = document.getElementById("btn-change");
    const btnPredict = document.getElementById("btn-predict");
    
    // UI Elements - Result Area
    const resultPlaceholder = document.getElementById("result-placeholder");
    const resultLoading = document.getElementById("result-loading");
    const resultError = document.getElementById("result-error");
    const errorMessage = document.getElementById("error-message");
    const btnRetry = document.getElementById("btn-retry");
    const resultSuccess = document.getElementById("result-success");
    const healthBadge = document.getElementById("health-badge");
    const diseaseName = document.getElementById("disease-name");
    const confidenceBar = document.getElementById("confidence-bar");
    const confidenceText = document.getElementById("confidence-text");
    const treatmentText = document.getElementById("treatment-text");
    const pesticideText = document.getElementById("pesticide-text");
    const btnReset = document.getElementById("btn-reset");

    // UI Elements - Recommended Products
    const recommendedSection = document.getElementById("recommended-products-section");
    const recommendedGrid = document.getElementById("recommended-products-grid");
    const noProductsMessage = document.getElementById("no-products-message");

    let selectedFile = null;

    // ─────────────────────────────────────────────
    // File Selection & Drag-Drop
    // ─────────────────────────────────────────────
    
    dropzone.addEventListener("click", (e) => {
        if (e.target.tagName !== "BUTTON" && e.target.tagName !== "I") {
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    function handleFile(file) {
        if (!file.type.startsWith("image/")) {
            showError("Please upload a valid image file.");
            return;
        }

        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadPrompt.classList.add("hidden");
            previewContainer.classList.remove("hidden");
            resetResultView();
        };
        reader.readAsDataURL(file);
    }

    btnChange.addEventListener("click", (e) => {
        e.stopPropagation();
        selectedFile = null;
        fileInput.value = "";
        previewContainer.classList.add("hidden");
        uploadPrompt.classList.remove("hidden");
        resetResultView();
    });

    btnReset.addEventListener("click", () => {
        btnChange.click();
    });

    btnRetry.addEventListener("click", () => {
        btnPredict.click();
    });

    // ─────────────────────────────────────────────
    // Prediction API Call
    // ─────────────────────────────────────────────
    
    document.getElementById("upload-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        // Show loading state
        btnPredict.disabled = true;
        btnChange.disabled = true;
        resultPlaceholder.classList.add("hidden");
        resultError.classList.add("hidden");
        resultSuccess.classList.add("hidden");
        resultLoading.classList.remove("hidden");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/api/tomato/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to analyze image.");
            }

            // Display results
            displayResults(data);
            
        } catch (error) {
            showError(error.message);
        } finally {
            btnPredict.disabled = false;
            btnChange.disabled = false;
        }
    });

    function displayResults(data) {
        resultLoading.classList.add("hidden");
        resultSuccess.classList.remove("hidden");

        diseaseName.textContent = data.disease_display || data.disease;
        
        // Update confidence
        const confPercent = Math.round(data.confidence);
        confidenceText.textContent = `${confPercent}%`;
        confidenceBar.style.width = `${confPercent}%`;

        // Update health status styling
        if (data.is_healthy) {
            healthBadge.className = "badge rounded-pill bg-success";
            healthBadge.innerHTML = `<i class="bi bi-check-circle me-1"></i>Healthy`;
            confidenceBar.className = "progress-bar bg-success";
            confidenceText.className = "ms-2 small fw-700 text-success";
        } else {
            healthBadge.className = "badge rounded-pill bg-danger";
            healthBadge.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i>Disease Detected`;
            confidenceBar.className = "progress-bar bg-danger";
            confidenceText.className = "ms-2 small fw-700 text-danger";
        }

        // Treatments
        treatmentText.textContent = data.treatment || "No specific treatment required.";
        pesticideText.textContent = data.pesticide || "N/A";

        // ── Recommended Products ──────────────────────────────────────
        renderRecommendedProducts(data.recommended_products || [], data.is_healthy);
    }

    // ─────────────────────────────────────────────
    // Recommended Products Rendering
    // ─────────────────────────────────────────────

    function renderRecommendedProducts(products, isHealthy) {
        // Clear previous products
        recommendedGrid.innerHTML = "";
        recommendedSection.classList.add("hidden");
        noProductsMessage.classList.add("hidden");

        // Don't show products section for healthy leaves
        if (isHealthy) return;

        if (products.length === 0) {
            noProductsMessage.classList.remove("hidden");
            return;
        }

        // Show the section
        recommendedSection.classList.remove("hidden");

        // Render each product card
        products.forEach((product, index) => {
            const card = createProductCard(product, index);
            recommendedGrid.innerHTML += card;
        });

        // Attach AJAX event listeners to all "Add to Cart" buttons
        recommendedGrid.querySelectorAll('.btn-ajax-cart').forEach(btn => {
            btn.addEventListener('click', handleAjaxAddToCart);
        });
    }

    function createProductCard(product, index) {
        return `
        <div class="col-auto rec-product-animate" style="animation-delay: ${index * 0.05}s">
            <a href="/product/${product.id}" class="btn btn-outline-success rounded-pill px-3 py-2 shadow-sm d-flex align-items-center gap-2 text-decoration-none">
                <i class="bi bi-bag-check-fill text-success"></i>
                <span class="fw-600">${product.name}</span>
            </a>
        </div>`;
    }

    // ─────────────────────────────────────────────
    // AJAX Add to Cart
    // ─────────────────────────────────────────────

    async function handleAjaxAddToCart(e) {
        const btn = e.currentTarget;
        const productId = btn.dataset.productId;
        const productName = btn.dataset.productName;

        // Show loading state on button
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Adding...`;

        try {
            const response = await fetch(`/api/cart/add/${productId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quantity: 1 })
            });

            if (response.status === 401) {
                // User not logged in
                showToast("Please log in to add items to your cart.", "warning");
                btn.disabled = false;
                btn.innerHTML = originalHtml;
                return;
            }

            const data = await response.json();

            if (data.success) {
                // Update the cart count badge in the navbar
                updateCartBadge(data.cart_count);

                // Show success state on button
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-success");
                btn.innerHTML = `<i class="bi bi-check-circle me-1"></i>Added!`;
                
                showToast(data.message, "success");

                // Reset button after 2 seconds
                setTimeout(() => {
                    btn.classList.remove("btn-success");
                    btn.classList.add("btn-primary");
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                }, 2000);
            } else {
                throw new Error(data.error || "Failed to add to cart.");
            }
        } catch (error) {
            showToast(error.message, "danger");
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    }

    function updateCartBadge(count) {
        // Update the navbar cart badge
        const cartLink = document.getElementById("cartNavLink");
        if (!cartLink) return;

        let badge = cartLink.querySelector(".cart-count");
        if (count > 0) {
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "cart-count";
                cartLink.appendChild(badge);
            }
            badge.textContent = count;
        } else if (badge) {
            badge.remove();
        }
    }

    // ─────────────────────────────────────────────
    // Toast Notifications
    // ─────────────────────────────────────────────

    function showToast(message, type = "success") {
        // Create a flash-style toast notification
        let container = document.querySelector(".flash-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "flash-container";
            document.body.appendChild(container);
        }

        const iconMap = {
            success: "check-circle",
            danger: "exclamation-triangle",
            warning: "exclamation-circle",
            info: "info-circle"
        };

        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible flash-alert`;
        alertDiv.setAttribute("role", "alert");
        alertDiv.innerHTML = `
            <i class="bi bi-${iconMap[type] || 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.appendChild(alertDiv);

        // Auto-dismiss after 4 seconds
        setTimeout(() => {
            alertDiv.style.opacity = "0";
            alertDiv.style.transform = "translateX(100%)";
            alertDiv.style.transition = "all 0.4s ease";
            setTimeout(() => alertDiv.remove(), 400);
        }, 4000);
    }

    // ─────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────

    function showError(msg) {
        resultLoading.classList.add("hidden");
        resultPlaceholder.classList.add("hidden");
        resultSuccess.classList.add("hidden");
        resultError.classList.remove("hidden");
        errorMessage.textContent = msg;
    }

    function resetResultView() {
        resultLoading.classList.add("hidden");
        resultError.classList.add("hidden");
        resultSuccess.classList.add("hidden");
        resultPlaceholder.classList.remove("hidden");
        // Also reset recommended products
        recommendedSection.classList.add("hidden");
        noProductsMessage.classList.add("hidden");
        recommendedGrid.innerHTML = "";
    }
});
