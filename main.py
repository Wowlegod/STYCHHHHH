from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from datetime import datetime, timedelta
from twilio.rest import Client

options = Options()
options.add_argument("--headless=new")  # mode sans interface
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


account_sid = "ACf11393f366afacc01774744f09984446"   # à remplir
auth_token = "b82b297463c47d1199052e4abe0b8f93"     # à remplir
twilio_whatsapp = "whatsapp:+14155238886"  # numéro WhatsApp Twilio (sandbox)
mon_whatsapp = "whatsapp:+33778312009"     # ton numéro validé (format international)
client = Client(account_sid, auth_token)

def send_whatsapp(message):
    client.messages.create(
        body=message,
        from_=twilio_whatsapp,
        to=mon_whatsapp
    )

import time

# 1. Initialisation du navigateur
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.stych.fr/connexion")

# 2. Attendre et remplir l'email
email_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "email"))  # À adapter si le name est différent
)
email_field.send_keys("pouzetquentin2@gmail.com")

# 3. Attendre et remplir le mot de passe
password_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "mdp"))  # Utilise l'ID trouvé
)
password_field.send_keys("Quentin28$")

# 4. Soumettre le formulaire
password_field.submit()
time.sleep(5)  # Attendre la connexion

# Suite du script (filtres, créneaux, etc.)

# 3. Accéder au planning
driver.get("https://www.stych.fr/elearning/formation/conduite/reservation/planning")
time.sleep(30)

# 4. Cliquer sur le bouton "Filtrer"
filter_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-filters-popup-full"))
)
driver.execute_script("arguments[0].scrollIntoView();", filter_button)
driver.execute_script("arguments[0].click();", filter_button)
print("Bouton 'Filtrer' cliqué avec succès.")
time.sleep(2)  # Attendre l'ouverture des filtres

# 5. Cliquer sur "Afficher tous les enseignants"
try:
    show_all_teachers_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'link-show-all') and contains(@class, 'show-all-moniteurs')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", show_all_teachers_button)
    driver.execute_script("arguments[0].click();", show_all_teachers_button)
    print("Liste complète des enseignants affichée.")
    time.sleep(3)  # Attendre que la liste se charge

    # Vérifier que la liste des enseignants est bien chargée
    try:
        enseignant_test = driver.find_element(By.XPATH, "//label[contains(text(), 'CHLOE S')]")
        print("La liste des enseignants est bien chargée.")
    except NoSuchElementException:
        print("La liste des enseignants ne s'est pas chargée correctement.")
except TimeoutException:
    print("Le bouton 'Afficher tous les enseignants' n'a pas été trouvé.")

# 6. Sélectionner la monitrice
try:
    monitrice_label = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//label[@for='moniteur_1329702']"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", monitrice_label)
    driver.execute_script("arguments[0].click();", monitrice_label)
    print("Monitrice sélectionnée avec succès.")
    time.sleep(3)  # Attendre la mise à jour des créneaux
except Exception as e:
    print(f"Erreur lors de la sélection de la monitrice : {e}")
# 7. Cliquer sur le bouton "Afficher les [nombre] cours"
try:
    afficher_cours_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "submit-filters"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", afficher_cours_button)
    driver.execute_script("arguments[0].click();", afficher_cours_button)
    print("Bouton 'Afficher les cours' cliqué avec succès.")
    time.sleep(5)  # Attendre que les créneaux se chargent
except Exception as e:
    print(f"Erreur lors du clic sur le bouton 'Afficher les cours' : {e}")
# 8. Récupérer les créneaux disponibles
message_final = "📢 Créneaux disponibles dans les 28 prochains jours :\n\n"
today = datetime.today().date()
limit_date = today + timedelta(days=31)

try:
    creneaux = driver.find_elements(By.CSS_SELECTOR, 'div.course[data-nb-credit="1"]')
    count = 0
    for creneau in creneaux:
        day_element = creneau.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'course-day')]")
        date_str = day_element.get_attribute("data-date")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if today <= date_obj <= limit_date:
            time_slot = creneau.find_element(By.CLASS_NAME, "course-time").text
            address = creneau.find_element(By.CLASS_NAME, "course-address").text
            message_final += f"📅 {date_str} 🕒 {time_slot} - {address}\n"
            count += 1

    if count == 0:
        message_final = "❌ Aucun créneau disponible dans les 28 prochains jours."

    # Envoi WhatsApp
    send_whatsapp(message_final)
    print("✅ Message envoyé sur WhatsApp")
except Exception as e:
    print(f"Erreur lors de la récupération des créneaux : {e}")
# 8. Fermer le navigateur
driver.quit()
