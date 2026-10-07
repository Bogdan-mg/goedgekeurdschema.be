(function () {
  "use strict";
  var S = window.SITE;
  var euro = function (n) { return "€ " + n.toLocaleString("nl-BE"); };
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  // Tijdelijke actie: geldig tot en met de datum in config.js
  var vandaag = new Date();
  var iso = vandaag.getFullYear() + "-" + ("0" + (vandaag.getMonth() + 1)).slice(-2) + "-" + ("0" + vandaag.getDate()).slice(-2);
  var promo = S.promo && iso <= S.promo.tot ? S.promo : null;
  var prijs = function (p) { return promo ? p.prijs - promo.korting : p.prijs; };

  // Actie voorbij maar de pagina nog niet opnieuw opgebouwd: toon de gewone prijzen
  if (!promo) {
    $$(".promo-balk").forEach(function (el) { el.remove(); });
    $$(".price[data-oud]").forEach(function (el) {
      var o = el.querySelector(".oud"); if (o) o.remove();
      el.querySelector("b").innerHTML = "<sup>€</sup>" + el.dataset.oud;
      el.querySelector("small").textContent = "Inclusief btw en verplaatsing";
    });
  }

  // Cookies: de Google-tag staat in de pagina (Consent Mode), maar plaatst pas cookies na toestemming
  var meet = function (naam, extra) { if (window.gtag) window.gtag("event", naam, extra || {}); };
  (function () {
    if (!S.googleTag) return;
    var banner = $("#cookie");
    var lees = function () { try { return localStorage.getItem("cookies"); } catch (e) { return null; } };
    var bewaar = function (v) { try { localStorage.setItem("cookies", v); } catch (e) {} };
    var zet = function (ja) {
      var c = ja ? "granted" : "denied";
      if (window.gtag) window.gtag("consent", "update", { ad_storage: c, ad_user_data: c, ad_personalization: c, analytics_storage: c });
    };
    var k = lees();
    if (k !== "ja" && k !== "nee" && banner) banner.hidden = false;
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-cookie]");
      if (b) {
        bewaar(b.dataset.cookie);
        banner.hidden = true;
        zet(b.dataset.cookie === "ja");
        return;
      }
      if (e.target.closest("[data-cookie-keuze]")) { e.preventDefault(); if (banner) banner.hidden = false; }
    });
  })();

  // Contactklikken meten (enkel als cookies aanvaard zijn)
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    var h = a.getAttribute("href") || "";
    if (a.hasAttribute("data-wa") || h.indexOf("wa.me") > -1) meet("whatsapp_klik");
    else if (h.indexOf("tel:") === 0) meet("telefoon_klik");
    else if (h.indexOf("mailto:") === 0) meet("email_klik");
  });

  // Bedankpagina: extra uitleg bij WhatsApp
  if (/via=whatsapp/.test(location.search)) $$("[data-via-wa]").forEach(function (el) { el.hidden = false; });

  function waLink(text) {
    return "https://wa.me/" + S.whatsapp + "?text=" + encodeURIComponent(text);
  }

  // Alle WhatsApp-knoppen met een vaste tekst
  $$("[data-wa]").forEach(function (a) {
    a.href = waLink(a.getAttribute("data-wa"));
    a.target = "_blank";
    a.rel = "noopener";
  });

  // Menu op gsm
  var menuBtn = $(".menu-btn"), topbar = $(".topbar");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = topbar.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.setAttribute("aria-label", open ? "Menu sluiten" : "Menu openen");
    });
    $$("#nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        topbar.classList.remove("open");
        menuBtn.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Prijswidget bovenaan de homepage
  var quote = $("#quote");
  if (quote) {
    var syncQuote = function () {
      var r = $('input[name="qtype"]:checked', quote);
      if (!r) return;
      var pk = S.pakketten.filter(function (p) { return p.id === r.value; })[0];
      $("#quotePrice").textContent = euro(pk ? prijs(pk) : +r.dataset.prijs);
      $("#quoteCta").dataset.pick = r.value;
    };
    quote.addEventListener("change", syncQuote);
    quote.addEventListener("submit", function (e) { e.preventDefault(); });
    syncQuote();
  }

  // Boekingsformulier (enkel op de homepage)
  var form = $("#bookForm");
  if (form) {
    var keuzes = S.pakketten.map(function (p) {
      return { id: p.id, naam: p.naam, sub: "tot " + p.m2 + " m² · tot " + p.zekeringen + " zekeringen", prijs: prijs(p) };
    }).concat([
      { id: "groter", naam: "Groter / anders", sub: "prijs op maat" },
      { id: "twijfel", naam: "Ik twijfel", sub: "ik stuur een foto van mijn verdeelkast" },
    ]);

    var state = function () {
      var fd = new FormData(form);
      var k = keuzes.filter(function (x) { return x.id === fd.get("pakket"); })[0];
      return { fd: fd, keuze: k, total: k && k.prijs ? k.prijs : null };
    };
    var updateTotal = function () {
      var st = state();
      $("#totalPrice").textContent = st.total === null ? "Op maat" : euro(st.total);
      $("#totalNote").textContent = st.total === null
        ? (st.keuze && st.keuze.id === "twijfel" ? "we bepalen het samen via een foto" : "prijs op aanvraag")
        : "incl. btw & verplaatsing";
      if (st.fd.getAll("extra").length) $("#totalNote").textContent += " + extra's (meerprijs, prijs op maat)";
    };
    form.addEventListener("change", updateTotal);
    updateTotal();

    // "Maak afspraak" op een prijskaart kiest dat pakket in het formulier
    document.addEventListener("click", function (e) {
      var a = e.target.closest("[data-pick]");
      if (!a) return;
      var r = $('#pkgChoices input[value="' + a.dataset.pick + '"]');
      if (r) { r.checked = true; updateTotal(); }
    });

    var err = $("#formErr");
    var showErr = function (html, field) {
      err.innerHTML = html;
      if (field) field.focus();
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var via = (e.submitter && e.submitter.value) || "wa";
      var st = state(), fd = st.fd;
      var v = function (k) { return (fd.get(k) || "").toString().trim(); };
      var naam = v("naam"), gem = v("gemeente"), mail = v("email"), tel = v("telefoon"), opm = v("opmerking");
      if (!naam || !gem) {
        return showErr("Vul je naam en gemeente in, dan kunnen we je meteen verder helpen.", naam ? form.gemeente : form.naam);
      }
      if (via === "mail" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail)) {
        return showErr("Vul je e-mailadres in, zodat we je kunnen antwoorden.", form.email);
      }
      err.textContent = "";

      var extras = fd.getAll("extra").join(", ");
      var type = st.keuze ? st.keuze.naam + " (" + st.keuze.sub + ")" : "-";
      var prijsTekst = st.total === null ? "op maat" : euro(st.total) + " (incl. btw" + (promo ? ", " + promo.naam.toLowerCase() : "") + ")";

      if (via === "wa") {
        var lines = [
          "Hallo! Ik wil graag een afspraak boeken via goedgekeurdschema.be.",
          "",
          "👤 Naam: " + naam,
          "📍 Gemeente: " + gem,
        ];
        if (tel) lines.push("📞 Telefoon: " + tel);
        if (mail) lines.push("✉️ E-mail: " + mail);
        lines.push("🏠 Type: " + type);
        if (extras) lines.push("➕ Extra (meerprijs): " + extras);
        lines.push("🎯 Waarvoor: " + fd.get("reden"), "🗓️ Voorkeur: " + fd.get("moment"));
        if (opm) lines.push("💬 Opmerking: " + opm);
        lines.push("", st.total === null ? "Graag een prijs op maat." : "💶 Prijs volgens de website: " + prijsTekst);
        meet("generate_lead", { method: "whatsapp" });
        window.open(waLink(lines.join("\n")), "_blank", "noopener");
        setTimeout(function () { location.href = "bedankt.html?via=whatsapp"; }, 400);
        return;
      }

      // Versturen per e-mail via FormSubmit
      var data = {
        "Naam": naam,
        "Gemeente": gem,
        "email": mail,
        "Telefoon": tel || "-",
        "Type woning": type,
        "Prijs volgens website": prijsTekst,
        "Extra (meerprijs)": extras || "-",
        "Waarvoor": fd.get("reden"),
        "Voorkeur moment": fd.get("moment"),
        "Opmerking": opm || "-",
        _subject: "Nieuwe afspraak: " + naam + " (" + gem + ")",
        _replyto: mail,
        _template: "table",
        _honey: v("_honey"),
        _autoresponse: "Bedankt voor je aanvraag bij " + S.naam + "! We hebben ze goed ontvangen en nemen zo snel mogelijk contact met je op om een moment af te spreken. Je vaste prijs: " + prijsTekst + ".",
      };
      if (S.boekingCc) data._cc = S.boekingCc;

      var btn = e.submitter;
      btn.disabled = true;
      var oldLabel = btn.innerHTML;
      btn.innerHTML = "Bezig met versturen…";
      var fallback = function () {
        var body = Object.keys(data).filter(function (k) { return k.charAt(0) !== "_"; })
          .map(function (k) { return k + ": " + data[k]; }).join("\n");
        var to = S.boekingEmail.indexOf("@") > -1 ? S.boekingEmail : S.email;
        return "mailto:" + to + "?subject=" + encodeURIComponent(data._subject) +
          (S.boekingCc ? "&cc=" + encodeURIComponent(S.boekingCc) : "") + "&body=" + encodeURIComponent(body);
      };

      fetch("https://formsubmit.co/ajax/" + S.boekingEmail, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(data),
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok || String(res.j.success) !== "true") throw new Error(res.j.message || "Versturen mislukt");
          meet("generate_lead", { method: "e-mail" });
          form.hidden = true;
          setTimeout(function () { location.href = "bedankt.html?via=email"; }, 300);
        })
        .catch(function () {
          btn.disabled = false;
          btn.innerHTML = oldLabel;
          showErr('Het versturen is niet gelukt. Probeer het opnieuw, stuur ons een WhatsApp of <a href="' + fallback() + '">mail ons rechtstreeks</a>.');
        });
    });
  }

  // Zwevende knop en mobiele balk verbergen zolang de grote knoppen bovenaan
  // of het afsprakenformulier in beeld zijn (dubbele knoppen = extra keuzestress)
  var fab = $(".fab"), mbar = $(".mbar");
  var watch = $$(".hero-cta, .page-hero .hero-cta, #boeken");
  if ("IntersectionObserver" in window && watch.length) {
    var zichtbaar = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.isIntersecting ? zichtbaar.add(en.target) : zichtbaar.delete(en.target); });
      var verberg = zichtbaar.size > 0;
      if (fab) fab.classList.toggle("hide", verberg);
      if (mbar) mbar.classList.toggle("hide", verberg);
    });
    watch.forEach(function (el) { io.observe(el); });
  }
})();
