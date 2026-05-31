import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

FIREBASE_DB_URL = "https://badminton-manager-c69f0-default-rtdb.europe-west1.firebasedatabase.app/"

try:
    cred = credentials.Certificate("firebase-nogle.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })
    print("🟢 STATUS: Forbindelse til Firebase er aktiv og klar!")
except Exception as e:
    print(f"❌ FEJL: Kunne ikke oprette forbindelse: {e}")

if __name__ == "__main__":
    print("🤖 Robotten kører i baggrunden. Alt styres nu direkte fra dit visuelle Admin Panel i index.html!")
