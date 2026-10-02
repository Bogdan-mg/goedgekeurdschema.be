# goedgekeurdschema.be

Statische website voor het opmaken van eendraadschema's en situatieschema's,
met boeken via WhatsApp.

## Pagina's

| Bestand | Doel / zoektermen |
|---|---|
| `index.html` | Homepage: prijzen, werkwijze, boeken |
| `eendraadschema.html` | "eendraadschema laten opmaken", prijs, uitleg |
| `situatieschema.html` | "situatieschema laten tekenen", verschil met eendraadschema |
| `keuring-afgekeurd.html` | "elektrische keuring afgekeurd", termijnen, herkeuring |
| `keuring-verkoop-woning.html` | "elektrische keuring bij verkoop" |
| `privacy.html` | Privacybeleid (AVG/GDPR) |
| `404.html` | Pagina niet gevonden |

## Aanpassen

**Gegevens en prijzen** staan in `js/config.js`: WhatsApp-nummer, telefoon, e-mail,
bedrijfsnaam, adres, ondernemingsnummer, pakketten en prijzen.

**Teksten** staan in `src/pages/*.html`; de gedeelde kop en voettekst in `src/layout.html`.

De `.html`-bestanden in de hoofdmap worden daaruit **gebouwd**. Pas die niet rechtstreeks aan.

- Op GitHub gebeurt dat automatisch: pas je `js/config.js` of iets in `src/` aan,
  dan bouwt de workflow *Website bouwen* (`.github/workflows/build.yml`) de site opnieuw.
- Lokaal: `python3 tools/build.py` (vereist Python 3 en Node).

## Afspraken ontvangen

Klanten kiezen onderaan het formulier **WhatsApp** of **E-mail**.

- **WhatsApp**: opent WhatsApp met een ingevuld bericht naar `whatsapp` uit `js/config.js`.
- **E-mail**: de aanvraag wordt via [FormSubmit](https://formsubmit.co) (gratis, geen account)
  naar `boekingEmail` gestuurd, met een kopie naar `boekingCc`. De klant krijgt automatisch
  een bevestigingsmail.
  - **Eenmalig activeren:** doe na het online zetten zelf een testaanvraag via e-mail.
    FormSubmit stuurt dan een mail naar `boekingEmail` → klik op **Activate Form**.
    Vanaf dan komen alle aanvragen binnen (kijk de eerste keer ook in je spam).
  - Wil je je e-mailadres niet zichtbaar in de website? FormSubmit geeft je na de activatie
    een willekeurige code; vul die in bij `boekingEmail` in plaats van je adres.

## Online zetten (GitHub Pages)

0. **De repository moet openbaar zijn.** Met een gratis GitHub-account werkt Pages niet voor
   privé-repositories. *Settings* → *General* → helemaal onderaan *Danger Zone* →
   *Change visibility* → *Change to public*. (Er staat niets geheims in: alles is sowieso
   zichtbaar op de website.)
1. *Settings* → *Pages* → *Deploy from a branch* → kies de branch, map `/ (root)`.
2. `CNAME` bevat al `goedgekeurdschema.be`.
3. DNS bij je domeinregistrar:
   - 4 `A`-records voor `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME`-record `www` → `<gebruikersnaam>.github.io`
4. Vink *Enforce HTTPS* aan zodra het domein werkt.

## Gevonden worden op Google

Op de site zelf is alles voorzien: titels en beschrijvingen per pagina,
gestructureerde gegevens (schema.org: bedrijf, diensten, prijzen, FAQ, kruimelpad),
`sitemap.xml`, `robots.txt`, deelafbeelding (`img/og.png`), snelle laadtijd zonder
externe scripts of cookies.

Wat je zelf nog moet doen (dit heeft de grootste impact):

1. **Google Search Console** — <https://search.google.com/search-console>
   - Voeg een *domeineigendom* toe voor `goedgekeurdschema.be` en bevestig via het TXT-record bij je registrar.
   - Menu *Sitemaps* → dien `sitemap.xml` in.
2. **Google Bedrijfsprofiel** — <https://business.google.com>
   - Maak een profiel aan als *servicegebied-bedrijf* (je adres hoeft niet zichtbaar te zijn),
     met als servicegebied Antwerpen en de omliggende gemeenten.
   - Categorie bv. "Elektricien" of "Adviesbureau elektrotechniek", werkgebied, openingsuren,
     link naar de website en je WhatsApp-nummer.
   - Vraag elke tevreden klant om een **Google-review**. Reviews zijn de belangrijkste factor om
     lokaal bovenaan te staan.
3. **Bing Webmaster Tools** — <https://www.bing.com/webmasters> (kan je Search Console-gegevens importeren).
4. **Vermeldingen**: zet je bedrijf met dezelfde naam, website en telefoon op o.a. Gouden Gids,
   Facebook en eventueel platformen voor vakmannen. Vraag makelaars en notarissen met wie je werkt
   om naar je site te linken.
5. **Wettelijke info**: vul `bedrijfsnaam`, `adres` en `ondernemingsnummer` in `js/config.js` in —
   dat is verplicht op een Belgische bedrijfswebsite en versterkt ook het vertrouwen bij Google.

## Skills voor Claude

In `.claude/skills/` staan skills die Claude automatisch gebruikt bij werk aan deze site:

| Skill | Bron | Waarvoor |
|---|---|---|
| `taste-skill` | Leonxlnx/taste-skill (MIT) | Mooie, niet-generieke ontwerpen |
| `image-to-code` | Leonxlnx/taste-skill (MIT) | Ontwerp vanuit (gegenereerde) afbeeldingen naar code |
| `web-design-guidelines` | vercel-labs/agent-skills | UI-controle op toegankelijkheid en best practices |
| `awesome-design-md` | VoltAgent/awesome-design-md (MIT) | 70+ design systems als inspiratie |
| `playwright-cli` | microsoft/playwright-cli (Apache-2.0) | Site testen in een echte browser |

## Foto's van je werk

In `js/config.js` staat de lijst `fotos`. Elke foto verschijnt in het blok "Uit de praktijk" op de homepage.
Zet de afbeelding in `img/werk/` (staand formaat 3:4, liefst WebP van ongeveer 1000 px breed) en voeg een regel toe met `src`, `alt` (korte beschrijving voor Google en schermlezers) en eventueel `tekst` (onderschrift).
Let op: geen adressen, namen of gezichten van klanten op de foto zonder hun toestemming.
