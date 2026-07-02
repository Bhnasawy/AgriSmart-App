/* ==========================================================================
   Crop Recommendation System - Client Script
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const btnManual = document.getElementById("btn-manual");
    const btnAutofill = document.getElementById("btn-autofill");
    const weatherCardContainer = document.getElementById("weather-card-container");
    
    const predictionForm = document.getElementById("prediction-form");
    const predictBtn = document.getElementById("predict-btn");
    const predictSpinner = document.getElementById("predict-spinner");
    
    // Inputs
    const inputN = document.getElementById("input-N");
    const inputP = document.getElementById("input-P");
    const inputK = document.getElementById("input-K");
    const inputPh = document.getElementById("input-ph");
    const inputRainfall = document.getElementById("input-rainfall");
    const inputTemp = document.getElementById("input-temp");
    const inputHumidity = document.getElementById("input-humidity");
    
    // Weather autofill elements
    const cityNameInput = document.getElementById("city-name-input");
    const fetchWeatherBtn = document.getElementById("fetch-weather-btn");
    const weatherSpinner = document.getElementById("weather-spinner");
    const weatherInfoDisplay = document.getElementById("weather-info-display");
    const weatherShowCity = document.getElementById("weather-show-city");
    const statTempVal = document.getElementById("stat-temp-val");
    const statHumidityVal = document.getElementById("stat-humidity-val");
    const weatherApiIcon = document.getElementById("weather-api-icon");

    // Result panel elements
    const resultPlaceholder = document.getElementById("result-placeholder");
    const resultLoadingBox = document.getElementById("result-loading-box");
    const resultDisplay = document.getElementById("result-display");
    const resultCropName = document.getElementById("result-crop-name");
    const resultCropImage = document.getElementById("result-crop-image");
    const resultConfidenceText = document.getElementById("result-confidence-text");
    const resultConfidenceBar = document.getElementById("result-confidence-bar");
    const errorAlert = document.getElementById("error-alert");
    const errorAlertMsg = document.getElementById("error-alert-msg");
    const analysisDetails = document.querySelector(".analysis-details .summary-list");

    const resetFormBtn = document.getElementById("reset-form-btn");
    const sampleDataBtn = document.getElementById("sample-data-btn");

    // Initialize Default State
    switchToManualMode();

    btnManual.addEventListener("click", (e) => {
        e.preventDefault();
        switchToManualMode();
    });
    
    btnAutofill.addEventListener("click", (e) => {
        e.preventDefault();
        switchToAutofillMode();
    });

    function switchToManualMode() {
        btnManual.classList.add("active");
        btnAutofill.classList.remove("active");
        weatherCardContainer.classList.add("hidden");
        cityNameInput.value = "";
        weatherInfoDisplay.classList.add("hidden");
    }

    function switchToAutofillMode() {
        btnAutofill.classList.add("active");
        btnManual.classList.remove("active");
        weatherCardContainer.classList.remove("hidden");
    }

    // ─────────────────────────────────────────────
    // Fetch Weather Data
    // ─────────────────────────────────────────────
    fetchWeatherBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        const city = cityNameInput.value.trim();
        if (!city) {
            alert("Please enter a valid city name.");
            return;
        }

        fetchWeatherBtn.disabled = true;
        weatherSpinner.style.display = "block";
        hideError();

        try {
            const response = await fetch(`/weather/${encodeURIComponent(city)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to retrieve weather data.");
            }

            inputTemp.value = data.temperature;
            inputHumidity.value = data.humidity;

            validateField(inputTemp, "err-temp", -10, 50);
            validateField(inputHumidity, "err-humidity", 0, 100);

            weatherShowCity.textContent = city.charAt(0).toUpperCase() + city.slice(1);
            statTempVal.textContent = `${data.temperature} °C`;
            statHumidityVal.textContent = `${data.humidity}%`;

            if (data.temperature > 30) {
                weatherApiIcon.innerHTML = `<i class="bi bi-sun-fill text-warning"></i>`;
            } else if (data.temperature < 15) {
                weatherApiIcon.innerHTML = `<i class="bi bi-snow text-info"></i>`;
            } else {
                weatherApiIcon.innerHTML = `<i class="bi bi-cloud-sun-fill text-secondary"></i>`;
            }

            weatherInfoDisplay.classList.remove("hidden");
        } catch (err) {
            alert(`Weather Error: ${err.message}`);
            weatherInfoDisplay.classList.add("hidden");
        } finally {
            fetchWeatherBtn.disabled = false;
            weatherSpinner.style.display = "none";
        }
    });

    // ─────────────────────────────────────────────
    // Client-Side Input Validations
    // ─────────────────────────────────────────────
    function validateField(inputElement, errorElementId, min, max) {
        const val = parseFloat(inputElement.value);
        const errorSpan = document.getElementById(errorElementId);
        
        if (isNaN(val) || val < min || val > max) {
            inputElement.classList.add("is-invalid");
            if (errorSpan) errorSpan.style.display = "block";
            return false;
        } else {
            inputElement.classList.remove("is-invalid");
            if (errorSpan) errorSpan.style.display = "none";
            return true;
        }
    }

    inputN.addEventListener("input", () => validateField(inputN, "err-N", 0, 150));
    inputP.addEventListener("input", () => validateField(inputP, "err-P", 0, 150));
    inputK.addEventListener("input", () => validateField(inputK, "err-K", 0, 210));
    inputPh.addEventListener("input", () => validateField(inputPh, "err-ph", 0, 14));
    inputRainfall.addEventListener("input", () => validateField(inputRainfall, "err-rainfall", 0, 300));
    inputTemp.addEventListener("input", () => validateField(inputTemp, "err-temp", -10, 50));
    inputHumidity.addEventListener("input", () => validateField(inputHumidity, "err-humidity", 0, 100));

    function validateForm() {
        let isValid = true;
        isValid = validateField(inputN, "err-N", 0, 150) && isValid;
        isValid = validateField(inputP, "err-P", 0, 150) && isValid;
        isValid = validateField(inputK, "err-K", 0, 210) && isValid;
        isValid = validateField(inputPh, "err-ph", 0, 14) && isValid;
        isValid = validateField(inputRainfall, "err-rainfall", 0, 300) && isValid;
        isValid = validateField(inputTemp, "err-temp", -10, 50) && isValid;
        isValid = validateField(inputHumidity, "err-humidity", 0, 100) && isValid;
        return isValid;
    }

    // ─────────────────────────────────────────────
    // Form Submission
    // ─────────────────────────────────────────────
    predictionForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            showError("Please correct the invalid fields in red before predicting.");
            return;
        }

        hideError();
        resultPlaceholder.classList.add("hidden");
        resultDisplay.classList.add("hidden");
        resultLoadingBox.classList.remove("hidden");
        
        predictBtn.disabled = true;
        predictSpinner.style.display = "inline-block";

        const payload = {
            N: parseFloat(inputN.value),
            P: parseFloat(inputP.value),
            K: parseFloat(inputK.value),
            ph: parseFloat(inputPh.value),
            rainfall: parseFloat(inputRainfall.value),
            temperature: parseFloat(inputTemp.value),
            humidity: parseFloat(inputHumidity.value)
        };

        try {
            const response = await fetch("/api/crop/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.error || "Prediction failed.");

            const cropKey = data.crop.toLowerCase();
            const cropTitle = data.crop.charAt(0).toUpperCase() + data.crop.slice(1);
            
            resultCropName.textContent = cropTitle;
            
            // Map crop names to specific images
            const cropImages = {
                "rice": "/static/crops/1.jpg",
                "maize":  "/static/crops/2.jpg",
                "chickpea":  "/static/crops/3.jpg",
                "kidneybeans":  "/static/crops/4.jpg",
                "pigeonpeas":  "/static/crops/5.jpg",
                "mothbeans":  "/static/crops/6.jpg",
                "mungbean":  "/static/crops/7.jpg",
                "blackgram":  "/static/crops/8.jpg",
                "lentil": "/static/crops/9.jpg",
                "pomegranate":  "/static/crops/10.jpg",
                "banana":  "/static/crops/11.jpg",
                "mango": "/static/crops/12.jpg",
                "grapes":  "/static/crops/13.jpg",
                "watermelon":  "/static/crops/14.jpg",
                "muskmelon":  "/static/crops/15.jpg",
                "apple":  "/static/crops/16.jpg",
                "orange":  "/static/crops/17.jpg",
                "papaya":  "/static/crops/18.jpg",
                "coconut": "/static/crops/19.jpg",
                "cotton":  "/static/crops/20.jpg",
                "jute": "/static/crops/21.jpg",
                "coffee":  "/static/crops/22.jpg",
                "unknown": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&auto=format&fit=crop&q=80"
            };
            
            resultCropImage.src = cropImages[cropKey] || cropImages["unknown"];
            
            resultCropImage.onerror = function() {
                this.src = cropImages["unknown"];
            };

            if (data.confidence !== undefined && data.confidence !== null) {
                const confPercent = Math.round(data.confidence * 100);
                resultConfidenceText.textContent = `${confPercent}%`;
                resultConfidenceBar.style.width = `${confPercent}%`;
            } else {
                resultConfidenceText.textContent = "N/A";
                resultConfidenceBar.style.width = "0%";
            }

            analysisDetails.innerHTML = `
                <li><span class="sum-dot"></span> Optimal match for Nitrogen (${payload.N} mg/kg).</li>
                <li><span class="sum-dot"></span> Thrives in pH ${payload.ph} and ${payload.rainfall}mm rainfall.</li>
            `;

            resultLoadingBox.classList.add("hidden");
            resultDisplay.classList.remove("hidden");

        } catch (err) {
            showError(err.message);
            resultLoadingBox.classList.add("hidden");
            resultPlaceholder.classList.remove("hidden");
        } finally {
            predictBtn.disabled = false;
            predictSpinner.style.display = "none";
        }
    });

    function showError(msg) {
        errorAlertMsg.textContent = msg;
        errorAlert.classList.remove("hidden");
    }

    function hideError() {
        errorAlert.classList.add("hidden");
    }

    // ─────────────────────────────────────────────
    // Sample Data
    // ─────────────────────────────────────────────
    const sampleDatasets = [
        { N: 90, P: 42, K: 43, ph: 6.5, rainfall: 202, temperature: 23.5, humidity: 82 },
        { N: 78, P: 48, K: 20, ph: 6.1, rainfall: 85, temperature: 22.0, humidity: 65 },
        { N: 101, P: 28, K: 30, ph: 6.8, rainfall: 150, temperature: 26.0, humidity: 59 }
    ];
    let sampleIndex = 0;

    sampleDataBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const sample = sampleDatasets[sampleIndex % sampleDatasets.length];
        sampleIndex++;

        inputN.value = sample.N;
        inputP.value = sample.P;
        inputK.value = sample.K;
        inputPh.value = sample.ph;
        inputRainfall.value = sample.rainfall;
        inputTemp.value = sample.temperature;
        inputHumidity.value = sample.humidity;

        validateForm();
    });

    resetFormBtn.addEventListener("click", (e) => {
        e.preventDefault();
        predictionForm.reset();
        ["err-N", "err-P", "err-K", "err-ph", "err-rainfall", "err-temp", "err-humidity"].forEach(id => {
            document.getElementById(id).style.display = "none";
        });
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        resultDisplay.classList.add("hidden");
        resultPlaceholder.classList.remove("hidden");
    });
});
