(function () {
  const form = document.getElementById("predict-form");
  const submitBtn = document.getElementById("submit-btn");
  const errorEl = document.getElementById("form-error");
  const verdictEl = document.getElementById("verdict");
  const sealProgress = document.getElementById("seal-progress");
  const sealNumber = document.getElementById("seal-number");

  const CIRCUMFERENCE = 603.19;

  // --- Wire up sliders to their live value readouts ---
  document.querySelectorAll(".field").forEach((field, idx) => {
    const input = field.querySelector('input[type="range"]');
    const output = field.querySelector(".field__value");
    if (input && output) {
      input.addEventListener("input", () => {
        output.textContent = input.value;
      });
    }
  });

  // --- Research yes/no toggle ---
  document.querySelectorAll(".toggle").forEach((toggle) => {
    const hiddenInput = toggle.parentElement.querySelector('input[type="hidden"]');
    toggle.querySelectorAll(".toggle__btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        toggle.querySelectorAll(".toggle__btn").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        hiddenInput.value = btn.dataset.val;
      });
    });
  });

  function setSeal(percent) {
    const clamped = Math.max(0, Math.min(100, percent));
    const offset = CIRCUMFERENCE - (clamped / 100) * CIRCUMFERENCE;
    sealProgress.style.strokeDashoffset = offset.toFixed(2);
    sealNumber.textContent = clamped.toFixed(1);

    let color = "#A8792F"; // gold, default
    if (clamped < 40) color = "#A8503A"; // rust — low
    else if (clamped >= 75) color = "#5C7A5E"; // sage — strong
    sealProgress.style.stroke = color;
  }

  function verdictText(percent) {
    if (percent >= 85) return "Strong profile — you're well above the typical admitted range.";
    if (percent >= 65) return "Solid chance — your profile is competitive for most programs.";
    if (percent >= 40) return "Borderline — consider strengthening a few areas of your profile.";
    return "Reach territory — this profile sits below the typical admitted range.";
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.hidden = true;
    submitBtn.disabled = true;
    submitBtn.querySelector("span").textContent = "Calculating…";

    const formData = new FormData(form);
    const payload = {};
    formData.forEach((value, key) => {
      payload[key] = value;
    });

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        errorEl.textContent = (data.errors && data.errors.join(" ")) || "Something went wrong. Please check your inputs.";
        errorEl.hidden = false;
        return;
      }

      setSeal(data.chance_of_admit);
      verdictEl.textContent = verdictText(data.chance_of_admit);
    } catch (err) {
      errorEl.textContent = "Could not reach the prediction server. Please try again.";
      errorEl.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.querySelector("span").textContent = "Estimate my chance";
    }
  });
})();
