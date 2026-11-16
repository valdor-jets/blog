/* Valdor waitlist form. Any element with data-waitlist becomes a signup form.
   Optional: data-role="operator" preselects the role. */
(function () {
  var ENDPOINT = "https://valdor-waitlist.valdorjets.workers.dev/signup";

  var html =
    '<form class="wl-form" novalidate>' +
      '<label>Email<input type="email" name="email" autocomplete="email" required placeholder="you@example.com"></label>' +
      '<div class="wl-row">' +
        '<label><span>Name <span class="opt">(optional)</span></span><input type="text" name="name" autocomplete="name" maxlength="80"></label>' +
        '<label><span>I am a… <span class="opt">(optional)</span></span><select name="role">' +
          '<option value="">Choose one</option>' +
          '<option value="flyer">Flyer: I book private flights</option>' +
          '<option value="operator">Operator: I run aircraft</option>' +
          '<option value="broker">Broker / travel advisor</option>' +
          '<option value="curious">Just curious</option>' +
        '</select></label>' +
      '</div>' +
      '<label><span>Home airport or usual routes <span class="opt">(optional)</span></span><input type="text" name="airport" maxlength="120" placeholder="e.g. TEB, or Miami ↔ New York"></label>' +
      '<label class="wl-check"><input type="checkbox" name="surveys" value="1"> Yes, you can reach out to me for a few quick surveys about private travel.</label>' +
      '<div class="wl-hp" aria-hidden="true"><label>Company website<input type="text" name="company_website" tabindex="-1" autocomplete="off"></label></div>' +
      '<button class="wl-btn" type="submit">Join the waitlist</button>' +
      '<p class="wl-msg" role="status" aria-live="polite"></p>' +
      '<p class="wl-fine">We\'ll email you about early access. Unsubscribe any time. See our <a href="https://valdorjets.com/privacy">privacy policy</a>.</p>' +
    '</form>';

  function done(box) {
    box.innerHTML = '<div class="wl-done"><div class="mark">✦</div><h3>You\'re on the list.</h3>' +
      '<p>Check your inbox for a welcome note from Valdor Jets.</p></div>';
  }

  function mount(box) {
    box.innerHTML = html;
    var form = box.querySelector("form"), msg = box.querySelector(".wl-msg"), btn = box.querySelector("button");
    var started = Date.now();
    var role = box.getAttribute("data-role");
    if (role) form.role.value = role;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      msg.className = "wl-msg"; msg.textContent = "";
      var email = form.email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        msg.className = "wl-msg err"; msg.textContent = "Please enter a valid email address."; form.email.focus(); return;
      }
      btn.disabled = true; btn.textContent = "Joining…";
      var payload = {
        email: email, name: form.name.value.trim(), role: form.role.value, airport: form.airport.value.trim(),
        surveys: form.surveys.checked, company_website: form.company_website.value,
        elapsed_ms: Date.now() - started, source: location.pathname
      };
      fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j.ok) { done(box); return; }
          throw new Error(res.j.error || "Something went wrong.");
        })
        .catch(function (err) {
          btn.disabled = false; btn.textContent = "Join the waitlist";
          msg.className = "wl-msg err";
          msg.textContent = (err && err.message && err.message !== "Failed to fetch") ? err.message
            : "We couldn't reach the server. Please try again in a minute.";
        });
    });
  }

  function init() { Array.prototype.forEach.call(document.querySelectorAll("[data-waitlist]"), mount); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
