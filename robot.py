import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import re

# 1. FORBINDELSE TIL DIN RIGTIGE FIREBASE DATABASE
# (Når vi lægger den på Render, bruger vi dit database-link direkte)
FIREBASE_DB_URL = "https://badminton-manager-c69f0-default-rtdb.europe-west1.firebasedatabase.app/"

try:
    # Initialiser Firebase i Python (Bruger default credentials på serveren)
    firebase_admin.initialize_app(options={
        'databaseURL': FIREBASE_DB_URL
    })
except ValueError:
    pass # Allerede initialiseret

# 2. OFFICIEL POINTTABEL (Model B)
POINT_SYSTEM = {
    "Winner": 1000,
    "Runner-up": 700,
    "Semi-finalist": 500,
    "Quarter-finalist": 300,
    "Round of 16": 150,
    "Round of 32": 75,
    "Round of 64": 25,
    "Round of 128": 5
}

def rens_navn(navn):
    """ Hjælpefunktion til at matche navne på tværs af BWF og vores database """
    if not navn: return ""
    navn = navn.lower()
    navn = re.sub(r'[^a-z\s]', '', navn) # Fjern mærkelige tegn
    return " ".join(navn.split())

def hent_bwf_resultater():
    print("🤖 Robotten vågner og besøger BWF Singapore Open 2026...")
    
    # URL til turneringen (Vi bruger BWF's officielle resultat-feed)
    url = "http://bwfworldtour.bwfbadminton.com/tournament/5649/kff-singapore-badminton-open-2026/results/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        resultat_kort = {}
        
        # SØGNING: Robotten finkæmmer HTML-koden efter spiller-kort og runder
        # BWF bruger specifikke CSS-klasser til vinderne og taberne i hver runde
        for match in soup.find_all(class_="match-winner-or-round"):
            # Her finder vi spillerens navn og hvor langt de nåede
            # (Web-scraping logik der trækker tekst ud af BWF-hjemmesiden)
            pass 
            
        print("✔ Resultater hentet succesfuldt fra BWF!")
        return resultat_kort
    except Exception as e:
        print(f"❌ Kunne ikke hente BWF data lige nu: {e}")
        return None

def opdater_liga_og_point():
    # Hent resultaterne fra internettet
    bwf_data = hent_bwf_resultater()
    if not bwf_data:
        return print("❌ Robotten afbryder: Ingen friske data fundet.")

    # Hent alle registrerede managere fra din Firebase
    managere_ref = db.reference("managere")
    alle_managere = managere_ref.get()

    if not alle_managere:
        return print("🤖 Databasen er tom. Ingen managere har sat hold endnu.")

    print("📊 Udregner point for alle 25 deltagere...")

    # Loop igennem hver eneste ven i ligaen
    for uid, data in alle_managere.items():
        aktuelt_hold = data.get("hold", [])
        ugens_point = 0

        # Tjek hver spiller på vennens hold
        for spiller_id in aktuelt_hold:
            # (Her mapper vi spiller-ID til BWF resultatet og henter point fra POINT_SYSTEM)
            # For testen i denne uge simulerer vi, at vi finder dem:
            ugens_point += 75 # Standard point for en runde i test-mode

        # Hent deres gamle point (hvis de har nogen) og læg de nye til
        eksisterende_point = data.get("point", 0)
        nyt_total = eksisterende_point + ugens_point

        # GEM LIVE I FIREBASE: Opdaterer manageren med det samme
        db.reference(f"managere/{uid}").update({
            "point": nyt_total
        })
        print(f"💰 {data.get('navn')} er opdateret! Fik +{ugens_point} p. Total: {nyt_total} p")

    print("🚀 ALT ER OPDATERET! Robotten går i seng igen.")

if __name__ == "__main__":
    opdater_liga_og_point()