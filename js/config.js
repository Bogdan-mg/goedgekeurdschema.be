/*
 * ─────────────────────────────────────────────────────────────
 *  INSTELLINGEN — pas hier je gegevens en prijzen aan.
 *  Na een wijziging op GitHub bouwt de site zichzelf opnieuw op
 *  (zie .github/workflows/build.yml). Lokaal: python3 tools/build.py
 * ─────────────────────────────────────────────────────────────
 */
window.SITE = {
  naam: "Goedgekeurd Schema",

  // WhatsApp-nummer in internationaal formaat, zonder +, spaties of 0 vooraan.
  // Voorbeeld: 0470 12 34 56  →  "32470123456"
  whatsapp: "32489413589",

  // Zichtbaar telefoonnummer en e-mail (mag leeg blijven: "")
  telefoon: "0489 41 35 89",
  email: "info@goedgekeurdschema.be",

  // Afspraken via e-mail (verstuurd via FormSubmit.co, gratis, zonder account).
  // De eerste aanvraag stuurt een activatiemail naar boekingEmail: klik op "Activate Form".
  // Tip: FormSubmit geeft je daarna een willekeurige code; die mag je hier invullen
  // in plaats van je e-mailadres, zodat je adres niet zichtbaar is in de website.
  boekingEmail: "giurgeab@gmail.com",
  boekingCc: "info@goedgekeurdschema.be",   // krijgt een kopie (mag leeg blijven)

  // Wettelijk verplicht op een Belgische bedrijfswebsite:
  // officiële naam, adres en ondernemingsnummer (KBO / btw).
  bedrijfsnaam: "Voltra",      // officiële naam; "Goedgekeurd Schema" is de handelsnaam
  ondernemingsnummer: "BE 1042.544.914",
  adres: { straat: "", postcode: "", gemeente: "" },

  // Levertijd en werkgebied
  levertijdWerkdagen: 10,
  werkgebied: "Antwerpen en omgeving",
  // Gemeenten die op de site vermeld worden (ook voor Google).
  // Let op: tools/gemeenten.json heeft voorrang. Daar staan alle gemeenten binnen 30 km van Berchem,
  // en per gemeente maakt de site automatisch een pagina (eendraadschema-<gemeente>.html).
  gemeenten: [
    "Antwerpen", "Berchem", "Borgerhout", "Deurne", "Ekeren", "Hoboken", "Merksem", "Wilrijk",
    "Mortsel", "Edegem", "Kontich", "Aartselaar", "Hove", "Boechout", "Wommelgem", "Wijnegem",
    "Schoten", "Brasschaat", "Kapellen", "Stabroek", "Zwijndrecht", "Hemiksem", "Schelle", "Ranst",
  ],

  // Pakketten: eendraadschema + situatieschema. Prijzen in euro, incl. btw en verplaatsing.
  pakketten: [
    { id: "app",   naam: "Appartement",            m2: 110, zekeringen: 12, prijs: 265 },
    { id: "won",   naam: "Woning / duplex",        m2: 110, zekeringen: 12, prijs: 310 },
    { id: "w250",  naam: "Woning tot 250 m²", m2: 250, zekeringen: 25, prijs: 450 },
    { id: "w450",  naam: "Woning tot 450 m²", m2: 450, zekeringen: 40, prijs: 680 },
  ],

  // Tijdelijke actie: korting in euro op elk pakket. Verdwijnt vanzelf na de datum "tot".
  // Zet promo op null om de actie te stoppen.
  promo: { naam: "Najaarsactie", korting: 50, tot: "2026-11-30" },

  // Wat zit er in elk pakket?
  inbegrepen: [
    "Bezoek en opmeting ter plaatse",
    "Eendraadschema volgens het AREI",
    "Situatieschema van alle verdiepingen",
    "Legende met gebruikte symbolen",
    "Digitaal (PDF) in je mailbox",
    "Verplaatsing in Antwerpen en omgeving",
  ],

  // Extra werk tegen meerprijs. prijs: null = "prijs op maat", of bv. 95 = "vanaf € 95".
  extras: [
    { id: "diff", naam: "Differentieelschakelaar plaatsen of vervangen",
      uitleg: "Bv. een ontbrekende of verkeerde differentieel (30 mA of 300 mA, type A).", prijs: null },
    { id: "zek", naam: "Zekeringen (automaten) vervangen of bijplaatsen",
      uitleg: "Bv. een verkeerd kaliber, verouderde smeltzekeringen of een extra kring.", prijs: null },
  ],

  // Link van je Google Bedrijfsprofiel om een review te vragen ("Vragen om reviews").
  // Ook bereikbaar via de korte link www.goedgekeurdschema.be/review (zie vercel.json).
  googleReview: "https://g.page/r/CXQrOEXrI0F9EBM/review",

  // Reviews van echte klanten (verschijnen pas op de site als je er toevoegt).
  // Voorbeeld: { naam: "Voornaam N.", gemeente: "Berchem", tekst: "..." }
  reviews: [],

  // Foto's van je werk (blok "Uit de praktijk" op de homepage; verschijnt enkel als er foto's zijn).
  // src: grote versie, klein: kleinere versie voor gsm (mag weg). Staand formaat (3:4) werkt het best.
  fotos: [
    { src: "img/werk/verdeelkast-1-1000.webp", klein: "img/werk/verdeelkast-1-600.webp",
      alt: "Grote verdeelkast met automaten en differentieelschakelaars, elke kring gelabeld met een letter",
      tekst: "Elke kring een duidelijke letter, ook in grote kasten." },
  ],

  // Over jou (het blok verschijnt pas als 'tekst' ingevuld is).
  // foto: bv. "img/over.jpg" (vierkant, minstens 600x600 px)
  over: { naam: "", tekst: "", foto: "" },

  // Groter of anders → op aanvraag
  opAanvraag: "Groter dan 450 m², meer dan 40 zekeringen, een handelszaak of een appartementsgebouw? Stuur ons een berichtje voor een prijs op maat.",
};
