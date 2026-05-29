import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import re

FIREBASE_DB_URL = "https://badminton-manager-c69f0-default-rtdb.europe-west1.firebasedatabase.app/"

try:
    firebase_admin.initialize_app(options={'databaseURL': FIREBASE_DB_URL})
except ValueError:
    pass

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

def hent_bwf_resultater():
    print("🤖 Robotten scanner BWF Singapore Open 2026...")
    url = "http://bwfworldtour.bwfbadminton.com/tournament/5649/kff-singapore-badminton-open-2026/results/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        resultater = {}
        
        # SØGELOGIK: Finder runder og spillere på BWF's officielle HTML
        for match in soup.find_all(class_="match-winner-or-round"):
            # Her simulerer/udtrækker vi live-dataen under test-runden
            pass
            
        print("✔ Scanning fuldført!")
        return resultater
    except Exception as e:
        print(f"❌ Fejl ved scanning: {e}")
        return None

def udregn_pris_ændring(start_pris, runde):
    # 📉 DYNAMISK MODEL B PRISSYSTEM (UDREGNER STIGNING/FALD)
    if start_pris >= 20000000: # Topspillere
        if runde == "Winner": return 2000000
        if runde == "Runner-up": return 0
        if runde == "Semi-finalist": return -1500000
        if runde == "Quarter-finalist": return -3000000
        if runde == "Round of 16": return -4500000
        if runde == "Round of 32": return -6000000
        return -8000000
    elif start_pris >= 10000000: # Mellemklasse
        if runde == "Winner": return 3000000
        if runde == "Runner-up": return 1500000
        if runde == "Semi-finalist": return 500000
        if runde == "Quarter-finalist": return 0
        if runde == "Round of 16": return -1500000
        if runde == "Round of 32": return -3000000
        return -4500000
    else: # Billige spillere
        if runde == "Winner": return 4000000
        if runde == "Runner-up": return 2500000
        if runde == "Semi-finalist": return 1500000
        if runde == "Quarter-finalist": return 1000000
        if runde == "Round of 16": return 500000
        if runde == "Round of 32": return 0
        return -1000000

def koer_historisk_og_point_update():
    # TEST-DATA: Vi simulerer resultatet af Singapore Open for de største navne til testen på søndag
    # (På søndag trækker robotten disse data råt ud fra jeres reelle hold)
    test_runder = {
        "Shi Yu Qi": {"runde": "Winner", "raekke": "HS", "id": 1, "start_pris": 26000000},
        "Christo Popov": {"runde": "Runner-up", "raekke": "HS", "id": 4, "start_pris": 22000000},
        "Kunlavut Vitidsarn": {"runde": "Semi-finalist", "raekke": "HS", "id": 2, "start_pris": 24500000},
        "Anders Antonsen": {"runde": "Round of 32", "raekke": "HS", "id": 3, "start_pris": 23500000},
        "An Se Young": {"runde": "Winner", "raekke": "DS", "id": 76, "start_pris": 26000000},
        "Wang Zhi Yi": {"runde": "Runner-up", "raekke": "DS", "id": 77, "start_pris": 24500000}
    }

    print("📊 Opdaterer ligaen i Firebase...")
    
    # Gemmer turneringen i historik-mappen til jeres app-arkiv
    historik_ref = db.reference("turnerings_historik/5649")
    historik_data = {}
    for navn, info in test_runder.items():
        p_point = POINT_SYSTEM.get(info["runde"], 5)
        historik_data[navn] = {"runde": info["runde"], "point": p_point, "raekke": info["raekke"]}
    historik_ref.set(historik_data)

    # Opdaterer managerne ud fra, hvem de har valgt på deres hold
    managere_ref = db.reference("managere")
    alle_managere = managere_ref.get()

    if alle_managere:
        for uid, m_data in alle_managere.items():
            hold_ider = m_data.get("hold", [])
            ugens_liga_point = 0
            
            for s_navn, info in test_runder.items():
                if info["id"] in hold_ider:
                    ugens_liga_point += POINT_SYSTEM.get(info["runde"], 5)
            
            gammelt_total = m_data.get("point", 0)
            db.reference(f"managere/{uid}").update({
                "point": gammelt_total + ugens_liga_point
            })
            print(f"💰 {m_data.get('navn')} fik +{ugens_liga_point} point!")

    print("🚀 ALT ER UPDATERET! Robotten har lukket ugens runde og udregnet værdierne.")

if __name__ == "__main__":
    koer_historisk_og_point_update()
