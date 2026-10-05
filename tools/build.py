#!/usr/bin/env python3
"""
Bouwt de website uit src/ naar de hoofdmap.

    python3 tools/build.py

- src/layout.html       : gedeelde kop, menu, voettekst
- src/pages/*.html      : inhoud per pagina, met bovenaan een JSON-blok met titel,
                          beschrijving, ... in een HTML-commentaar
- js/config.js          : gegevens en prijzen (wordt via node ingelezen)

Resultaat: index.html, eendraadschema.html, ..., sitemap.xml
"""
import datetime
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BASE_URL = "https://www.goedgekeurdschema.be/"


def load_config():
    js = (ROOT / "js/config.js").read_text(encoding="utf-8")
    out = subprocess.run(
        ["node", "-e", "var window={};" + js + ";process.stdout.write(JSON.stringify(window.SITE))"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)


def intl(tel):
    d = re.sub(r"[^0-9+]", "", tel)
    return "+32" + d[1:] if d.startswith("0") else d


def euro(n):
    return "€ " + f"{n:,}".replace(",", ".")


def esc(s):
    return html.escape(str(s), quote=True)


def page_url(path):
    return BASE_URL if path == "index.html" else BASE_URL + path


BERCHEM = (51.195, 4.430)        # middelpunt van het werkgebied
ANTWERPEN = (51.2194, 4.4025)    # Antwerpen-centrum
STRAAL_KM = 30


def km(a, b):
    import math
    dlat = (a[0] - b[0]) * 111.2
    dlon = (a[1] - b[1]) * 111.2 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dlat, dlon)


def slug(naam):
    import unicodedata
    s = unicodedata.normalize("NFKD", naam).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s.replace("'", "")).strip("-")


def load_gemeenten():
    """Gemeenten uit tools/gemeenten.json binnen STRAAL_KM van Berchem, met slug en afstand."""
    f = ROOT / "tools" / "gemeenten.json"
    if not f.exists():
        return []
    gs = [g for g in json.loads(f.read_text(encoding="utf-8")) if km((g["lat"], g["lon"]), BERCHEM) <= STRAAL_KM]
    for g in gs:
        g["slug"] = slug(g["naam"])
        g["km"] = km((g["lat"], g["lon"]), ANTWERPEN)
    return gs


def lijst(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " en " + items[-1]


WONINGEN = {
    "district": "In {n} wonen veel mensen in appartementen en rijwoningen. In oudere panden zijn de schema's vaak verdwenen, of kloppen ze niet meer na een verbouwing.",
    "stad": "In {n} vind je oude stadswoningen naast appartementen en nieuwbouw. Vooral bij oudere panden en na renovaties ontbreken de schema's vaak, of kloppen ze niet meer.",
    "rand": "{n} heeft veel rijwoningen, halfopen bebouwing en appartementen. Is er ooit verbouwd of een kring bijgekomen, dan klopt het oude schema meestal niet meer.",
    "landelijk": "In {n} staan veel vrijstaande woningen, vaak met een garage, tuinhuis of bijgebouw. Ook die kringen moeten op het schema staan, en dat wordt vaak vergeten.",
}


def gemeente_intro(g):
    if g.get("intro"):
        return g["intro"]
    t1 = WONINGEN[g["type"]].format(n=g["naam"])
    waar = f"We komen in heel {g['naam']}" + (f", ook in {lijst(g['deel'])}" if g["deel"] else "") + "."
    afstand = round(g["km"] / 5) * 5
    if g["naam"] == "Antwerpen" or afstand < 5:
        ligging = "De verplaatsing zit altijd in de prijs."
    else:
        ligging = f"{g['naam']} ligt op zo'n {afstand} km van Antwerpen-centrum, en de verplaatsing zit gewoon in de prijs."
    return [t1, f"{waar} {ligging} Je krijgt je eendraad- en situatieschema digitaal, klaar voor de keurder."]


def render_werkgebied(S):
    if not GEMEENTEN:
        return '<ul class="regions">' + "".join(f"<li>{esc(g)}</li>" for g in S["gemeenten"]) + "</ul>"
    regios = {}
    for g in GEMEENTEN:
        regios.setdefault(g["regio"], []).append(g)
    return "".join(
        f'<div class="regio"><h3>{esc(r)}</h3><ul class="regions">'
        + "".join(f'<li><a href="eendraadschema-{g["slug"]}.html">{esc(g["naam"])}</a></li>' for g in gs)
        + "</ul></div>"
        for r, gs in regios.items()
    )


GEMEENTEN = []


def render_cards(S):
    out = []
    for p in S["pakketten"]:
        incl = "".join(f"<li>{esc(i)}</li>" for i in S["inbegrepen"])
        out.append(
            f'<article class="card">'
            f'<span class="card-ico" aria-hidden="true"><svg class="ico"><use href="#i-home"/></svg></span>'
            f'<h3>{esc(p["naam"])}</h3>'
            f'<p class="card-sub">Tot <b>{p["m2"]} m²</b><br>Tot <b>{p["zekeringen"]} zekeringen</b></p>'
            f'<div class="price"><b><sup>€</sup>{p["prijs"]:,}</b><small>Inclusief btw en verplaatsing</small></div>'.replace(",", ".")
            + f'<details class="incl"><summary>Wat zit er allemaal in?</summary>'
            f'<ul class="checks">{incl}</ul></details>'
            f'<a class="btn btn-teal btn-block" href="./#boeken" data-pick="{p["id"]}">Afspraak maken<svg class="ico" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
            f"</article>"
        )
    return '<div class="cards">' + "".join(out) + "</div>"


def keuzes(S):
    k = [
        {"id": p["id"], "naam": p["naam"], "sub": f'tot {p["m2"]} m² · tot {p["zekeringen"]} zekeringen', "prijs": p["prijs"]}
        for p in S["pakketten"]
    ]
    k.append({"id": "groter", "naam": "Groter / anders", "sub": "prijs op maat"})
    k.append({"id": "twijfel", "naam": "Ik twijfel", "sub": "ik stuur een foto van mijn verdeelkast"})
    return k


def render_choices(S):
    out = []
    for i, k in enumerate(keuzes(S)):
        prijs = f' <em>{euro(k["prijs"])}</em>' if "prijs" in k else ""
        out.append(
            f'<label class="chip big"><input type="radio" name="pakket" value="{k["id"]}"{" checked" if i == 0 else ""}>'
            f'<span><b>{esc(k["naam"])}{prijs}</b><small>{esc(k["sub"])}</small></span></label>'
        )
    return "".join(out)


def render_hero_choices(S):
    out = []
    for i, p in enumerate(S["pakketten"]):
        out.append(
            f'<label class="qopt"><input type="radio" name="qtype" value="{p["id"]}" data-prijs="{p["prijs"]}"{" checked" if i == 0 else ""}>'
            f'<span><b>{esc(p["naam"])}</b><small>tot {p["m2"]}\u00a0m², tot {p["zekeringen"]} zekeringen</small></span></label>'
        )
    return "".join(out)


def extra_prijs(x):
    return f"meerprijs vanaf {euro(x['prijs'])}" if x.get("prijs") else "meerprijs, prijs op maat"


def render_extras(S):
    ex = S.get("extras") or []
    if not ex:
        return ""
    rows = "".join(
        f'<li><div><b>{esc(x["naam"])}</b><p>{esc(x.get("uitleg", ""))}</p></div><span class="tag tag-soft">{esc(extra_prijs(x))}</span></li>'
        for x in ex
    )
    return ('<div class="extras"><h3>Extra: differentieel en zekeringen</h3>'
            '<p>Staat er op je keuringsverslag een inbreuk op je differentieel of zekeringen? Dan kunnen we die meteen mee oplossen, tegen een meerprijs. Je krijgt de prijs altijd vooraf.</p>'
            f'<ul class="issues">{rows}</ul>'
            '<p class="more"><a data-wa="Hallo! Ik wil graag een prijs voor het vervangen van mijn differentieel of zekeringen. Ik stuur een foto van mijn verdeelkast / keuringsverslag." href="#">Vraag een prijs via WhatsApp<svg class="ico" aria-hidden="true"><use href="#i-arrow"/></svg></a></p></div>')


def render_extra_choices(S):
    return "".join(
        f'<label class="chip"><input type="checkbox" name="extra" value="{esc(x["naam"])}"><span><b>{esc(x["naam"])}</b><small>{esc(extra_prijs(x))}</small></span></label>'
        for x in (S.get("extras") or [])
    )


def render_reviews(S):
    revs = S.get("reviews") or []
    if not revs:
        return ""
    items = "".join(
        f'<figure class="review"><blockquote>{esc(r["tekst"])}</blockquote>'
        f'<figcaption><b>{esc(r["naam"])}</b>{(" uit " + esc(r["gemeente"])) if r.get("gemeente") else ""}</figcaption></figure>'
        for r in revs
    )
    return ('\n    <!-- REVIEWS -->\n    <section id="reviews" class="section">\n      <div class="wrap">\n'
            '        <div class="sec-head"><h2>Wat klanten zeggen</h2></div>\n'
            f'        <div class="reviews">{items}</div>\n      </div>\n    </section>\n')


def render_fotos(S):
    fotos = S.get("fotos") or []
    if not fotos:
        return ""
    def fig(f):
        srcset = f' srcset="{esc(f["klein"])} 600w, {esc(f["src"])} 1000w" sizes="(max-width: 860px) 92vw, 460px"' if f.get("klein") else ""
        cap = f'<figcaption>{esc(f["tekst"])}</figcaption>' if f.get("tekst") else ""
        return (f'<figure class="foto"><img src="{esc(f["src"])}"{srcset} alt="{esc(f["alt"])}" '
                f'width="600" height="800" loading="lazy" decoding="async">{cap}</figure>')
    veel = " fotos-veel" if len(fotos) > 1 else ""
    return ('\n    <!-- UIT DE PRAKTIJK -->\n    <section id="praktijk" class="section alt">\n      <div class="wrap split">\n'
            '        <div class="split-copy">\n'
            '          <h2>Elke kring krijgt een naam</h2>\n'
            '          <p>Zo hoort een verdeelkast eruit te zien: elke automaat en differentieelschakelaar heeft een duidelijke letter. '
            'Diezelfde letters vind je terug op het eendraadschema en het situatieschema. Zo weten jij, je elektricien en de keurder meteen welke kring waar zit.</p>\n'
            '          <ul class="checks">\n'
            '            <li>Kringen gelabeld in de verdeelkast</li>\n'
            '            <li>Dezelfde letters op je schema\'s</li>\n'
            '            <li>Ook grote kasten, kantoren en handelszaken</li>\n'
            '          </ul>\n        </div>\n'
            f'        <div class="fotos{veel}">{"".join(fig(f) for f in fotos)}</div>\n'
            '      </div>\n    </section>\n')


def render_over(S):
    o = S.get("over") or {}
    if not o.get("tekst"):
        return ""
    foto = f'<img class="over-foto" src="{esc(o["foto"])}" alt="{esc(o.get("naam") or S["naam"])}" width="360" height="360" loading="lazy">' if o.get("foto") else ""
    titel = f'Hallo, ik ben {esc(o["naam"])}' if o.get("naam") else "Over ons"
    return ('\n    <!-- OVER -->\n    <section id="over" class="section">\n'
            f'      <div class="wrap over">{foto}<div><h2>{titel}</h2><p>{esc(o["tekst"])}</p></div></div>\n    </section>\n')


def business(S):
    b = {
        "@type": "Electrician",
        "@id": BASE_URL + "#bedrijf",
        "name": S["naam"],
        "url": BASE_URL,
        "logo": BASE_URL + "img/icon-512.png",
        "image": BASE_URL + "img/og.png",
        "description": "Eendraadschema's en situatieschema's volgens het AREI, aan een vaste prijs. Verplaatsing in " + S["werkgebied"] + " inbegrepen.",
        "areaServed": [{"@type": "City", "name": g} for g in S["gemeenten"]],
        "knowsLanguage": "nl-BE",
        "priceRange": euro(min(p["prijs"] for p in S["pakketten"])) + " - " + euro(max(p["prijs"] for p in S["pakketten"])),
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Eendraadschema + situatieschema",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": f'Eendraad- en situatieschema: {p["naam"]} (tot {p["m2"]} m², tot {p["zekeringen"]} zekeringen)',
                    "price": str(p["prijs"]),
                    "priceCurrency": "EUR",
                    "priceSpecification": {"@type": "PriceSpecification", "price": str(p["prijs"]), "priceCurrency": "EUR", "valueAddedTaxIncluded": True},
                    "itemOffered": {"@type": "Service", "name": "Eendraadschema en situatieschema opmaken"},
                }
                for p in S["pakketten"]
            ],
        },
    }
    if S.get("bedrijfsnaam"):
        b["legalName"] = S["bedrijfsnaam"]
    if S.get("email"):
        b["email"] = S["email"]
    if S.get("telefoon"):
        b["telephone"] = intl(S["telefoon"])
    elif S.get("whatsapp") and S["whatsapp"] != "32470000000":
        b["telephone"] = "+" + S["whatsapp"]
    if S.get("googleReview"):
        b["sameAs"] = [re.sub(r"/review/?$", "", S["googleReview"])]
    if S.get("ondernemingsnummer"):
        b["vatID"] = S["ondernemingsnummer"]
    a = S.get("adres") or {}
    if a.get("straat") and a.get("gemeente"):
        b["address"] = {
            "@type": "PostalAddress", "streetAddress": a["straat"], "postalCode": a.get("postcode", ""),
            "addressLocality": a["gemeente"], "addressCountry": "BE",
        }
    return b


def faq_schema(content):
    items = re.findall(r'<details class="faq-q"><summary>(.*?)</summary>(.*?)</details>', content, re.S)
    if not items:
        return None
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in items
        ],
    }


NAV = [
    ("eendraadschema", "eendraadschema.html", "Eendraadschema"),
    ("situatieschema", "situatieschema.html", "Situatieschema"),
    ("afgekeurd", "keuring-afgekeurd.html", "Keuring afgekeurd"),
    ("verkoop", "keuring-verkoop-woning.html", "Verkoop woning"),
    ("prijzen", "./#prijzen", "Prijzen"),
]


def build():
    global GEMEENTEN
    S = load_config()
    GEMEENTEN = load_gemeenten()
    if GEMEENTEN:
        S["gemeenten"] = [g["naam"] for g in GEMEENTEN]
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    minprijs = min(p["prijs"] for p in S["pakketten"])
    tokens = {
        "{{cards}}": render_cards(S),
        "{{keuzes}}": render_choices(S),
        "{{hero_keuzes}}": render_hero_choices(S),
        "{{reviews}}": render_reviews(S),
        "{{extras}}": render_extras(S),
        "{{extra_keuzes}}": render_extra_choices(S),
        "{{over}}": render_over(S),
        "{{fotos}}": render_fotos(S),
        "{{levertijd}}": str(S["levertijdWerkdagen"]),
        "{{werkgebied}}": esc(S["werkgebied"]),
        "{{gemeenten}}": render_werkgebied(S),
        "{{prijs_vanaf}}": euro(minprijs),
        "{{opAanvraag}}": esc(S["opAanvraag"]),
        "{{email_link}}": f'<a href="mailto:{esc(S["email"])}">{esc(S["email"])}</a>' if S.get("email") else "e-mail",
    }
    for p in S["pakketten"]:
        tokens["{{prijs:" + p["id"] + "}}"] = euro(p["prijs"])

    contact = [f'<a data-wa="Hallo!" href="https://wa.me/{S["whatsapp"]}">WhatsApp</a>']
    if S.get("telefoon"):
        contact.append(f'<a href="tel:{intl(S["telefoon"])}">{esc(S["telefoon"])}</a>')
    if S.get("email"):
        contact.append(f'<a href="mailto:{esc(S["email"])}">{esc(S["email"])}</a>')
    if S.get("googleReview"):
        contact.append(f'<a href="{esc(S["googleReview"])}" target="_blank" rel="noopener">Laat een review achter op Google</a>')
    contact.append(f'Werkgebied: {esc(S["werkgebied"])}')
    legal = [esc(S["naam"]) + (f' is een handelsnaam van {esc(S["bedrijfsnaam"])}' if S.get("bedrijfsnaam") and S["bedrijfsnaam"] != S["naam"] else "")]
    a = S.get("adres") or {}
    if a.get("straat"):
        legal.append(esc(f'{a["straat"]}, {a.get("postcode", "")} {a.get("gemeente", "")}'.strip()))
    if S.get("ondernemingsnummer"):
        legal.append("Ondernemingsnummer " + esc(S["ondernemingsnummer"]))

    # Bronpagina's: de vaste pagina's plus één pagina per gemeente (tools/gemeenten.json)
    bronnen = [(f.name, f.read_text(encoding="utf-8")) for f in sorted((SRC / "pages").glob("*.html"))]
    tpl = (SRC / "gemeente.html").read_text(encoding="utf-8")
    for g in GEMEENTEN:
        buren = sorted((b for b in GEMEENTEN if b is not g), key=lambda b: km((b["lat"], b["lon"]), (g["lat"], g["lon"])))[:4]
        raw = (tpl.replace("{{g_naam}}", esc(g["naam"])).replace("{{g_postcode}}", esc(g["postcode"]))
                  .replace("{{g_intro}}", "".join(f"<p>{esc(t)}</p>" for t in gemeente_intro(g)))
                  .replace("{{g_buren}}", lijst(f'<a href="eendraadschema-{b["slug"]}.html">{esc(b["naam"])}</a>' for b in buren)))
        bronnen.append((f'eendraadschema-{g["slug"]}.html', raw))

    sitemap = []
    for fname, raw in bronnen:
        m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", raw, re.S)
        meta = json.loads(m.group(1))
        content = raw[m.end():]
        for k, v in tokens.items():
            content = content.replace(k, v)
            mv_ = v.replace("€\u00a0", "€")  # in titels en beschrijvingen: "€265"
            meta = {mk: (mv.replace(k, mv_) if isinstance(mv, str) else mv) for mk, mv in meta.items()}
        path = fname
        url = page_url(path)

        graph = [business(S), {"@type": "WebSite", "@id": BASE_URL + "#website", "url": BASE_URL, "name": S["naam"], "inLanguage": "nl-BE", "publisher": {"@id": BASE_URL + "#bedrijf"}}]
        if meta.get("crumb"):
            graph.append({
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL},
                    {"@type": "ListItem", "position": 2, "name": meta["crumb"], "item": url},
                ],
            })
        if meta.get("service"):
            graph.append({
                "@type": "Service",
                "name": meta["service"],
                "serviceType": meta["service"],
                "provider": {"@id": BASE_URL + "#bedrijf"},
                "areaServed": [{"@type": "City", "name": g} for g in ([meta["plaats"]] if meta.get("plaats") else S["gemeenten"])],
                "url": url,
                "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": str(minprijs),
                           "highPrice": str(max(p["prijs"] for p in S["pakketten"])), "offerCount": str(len(S["pakketten"]))},
            })
        fs = faq_schema(content)
        if fs:
            graph.append(fs)
        jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

        current = ' aria-current="page"'
        nav = "".join(
            f'<a href="{href}"{current if key == meta.get("nav") else ""}>{label}</a>'
            for key, href, label in NAV
        )
        crumbs = ""
        if meta.get("crumb"):
            crumbs = f'<nav class="crumbs wrap" aria-label="Kruimelpad"><a href="./">Home</a><span aria-hidden="true">›</span><span>{esc(meta["crumb"])}</span></nav>'

        out = layout
        repl = {
            "{{title}}": esc(meta["title"]),
            "{{description}}": esc(meta["description"]),
            "{{canonical}}": url,
            "{{og_title}}": esc(meta.get("og_title", meta["title"])),
            "{{robots}}": meta.get("robots", "index, follow"),
            "{{base}}": '<base href="/">' if meta.get("base") else "",
            "{{nav}}": nav,
            "{{crumbs}}": crumbs,
            "{{content}}": content,
            "{{jsonld}}": jsonld,
            "{{contact}}": "<br>".join(contact),
            "{{legal}}": " · ".join(legal),
            "{{year}}": str(datetime.date.today().year),
            "{{cta}}": "" if meta.get("no_cta") else (SRC / "cta.html").read_text(encoding="utf-8"),
        }
        for k, v in repl.items():
            out = out.replace(k, v)
        for k, v in tokens.items():
            out = out.replace(k, v)
        if path == "index.html":
            out = out.replace('href="./#', 'href="#')  # op de homepage zelf: blijf op dezelfde pagina
        left = re.findall(r"\{\{[^}]+\}\}", out)
        if left:
            raise SystemExit(f"{fname}: onvervangen tokens {left}")
        (ROOT / path).write_text(out, encoding="utf-8")
        print("gebouwd:", path)
        if meta.get("sitemap", True):
            sitemap.append((url, meta.get("priority", 0.7)))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, prio in sorted(sitemap, key=lambda x: -x[1]):
        xml.append(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>")
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print("gebouwd: sitemap.xml")


if __name__ == "__main__":
    build()
