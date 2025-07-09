# Ads vs Organic Search Term Analyzer

🔎 En Streamlit-app til at sammenligne Google Ads-søgetermer med Google Search Console (GSC) data.

---

## 📋 Formål
Denne app hjælper marketingfolk med at identificere muligheder for SEO-optimering ved at vise, hvor Google Ads har høje eksponeringer på søgetermer, der ikke (eller kun lidt) performes organisk.

Med andre ord:
✅ Find søgeord, du betaler for i Ads, men ikke har synlighed for organisk.  
✅ Identificér lavthængende SEO-muligheder.  

---

## ⚡ Funktioner
- Upload Google Ads CSV (søgetermerapport)
- Upload Google Search Console CSV
- Automatisk rensning af data
  - Fjerner summerækker som "I alt konto", "I alt søgetermer" etc.
  - Filtrerer mærkelige tegn i søgeord
- Match på identiske søgetermer (case-insensitive)
- Summerer GSC-impressions på tværs af alle URLs for samme query
- Interaktiv tabel:
  - Filtrering på:
    - Minimum Ads Eksponeringer
    - Minimum Ads Klik
    - **Maximum** GSC Eksponeringer
    - Google Ads Kampagne
  - Sortering
  - Søgning
  - Download som CSV
- Klar, brugervenlig grænseflade

---

## 📂 Inputfiler
✅ Google Ads CSV
- Eksport fra Google Ads
- Med kolonnen **"Søgeterm"** samt matchtype, kampagne osv.
- Filen starter typisk med 2 metadata-linjer → appen håndterer det

✅ Google Search Console CSV
- Eksport fra Search Console
- Header skal inkludere:

- Understøtter flere sider pr. query (impressions summeres automatisk)

---

## 🚀 Hvordan bruger man appen
1. Klik på **Upload Google Ads CSV** og vælg din fil
2. Klik på **Upload Search Console CSV** og vælg din fil
3. Brug filtrene til at analysere
 - Fokusér på Ads-søgetermer med høj eksponering
 - Filtrer væk hvor GSC allerede performer
4. Download dine resultater som CSV

---

## 🛠️ Krav
Python-pakker specificeret i `requirements.txt`:



---

## 🌐 Deployment
Deploy på **Streamlit Community Cloud**:

✅ Skub denne repo til GitHub  
✅ Gå til [https://share.streamlit.io](https://share.streamlit.io)  
✅ Forbind din GitHub  
✅ Vælg repo og app.py → Deploy  

---

## ❤️ Om projektet
Bygget for at hjælpe med at optimere SEM/SEO-investeringer ved at synliggøre hvor betalt trafik kan suppleres med organisk.

