import random
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Informations de connexion
instagram_username = ""
instagram_password = ""

# Liste de mots-clés pour diversifier la recherche
keywords = ["artisan plombier", "électricien", "chauffagiste", "couvreur"]

# Charger les profils déjà contactés à partir d'un fichier JSON
try:
    with open("profils_contactes.json", "r") as f:
        profils_contactes = json.load(f)
except FileNotFoundError:
    profils_contactes = []

driver = webdriver.Chrome()
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(3)

# Connexion
username_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")
username_input.send_keys(instagram_username)
password_input.send_keys(instagram_password)
username_input.send_keys(Keys.RETURN)
time.sleep(5)

# Choisir un mot-clé aléatoire
search_keyword = random.choice(keywords)
print(f"Recherche avec le mot-clé : {search_keyword}")

# Rechercher des profils avec le mot-clé choisi
search_icon = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.x1iyjqo2.xh8yej3 > div:nth-child(2) > span > div > a > div > div > div"))
)
search_icon.click()
search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.x1lugfcp"))
)
search_input.send_keys(search_keyword)
time.sleep(1)
search_input.send_keys(Keys.RETURN)
search_input.send_keys(Keys.RETURN)
time.sleep(3)

# Scrolling pour charger plus de profils
for _ in range(3):  # Ajustez le nombre de scrolls pour obtenir plus de résultats
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Pause pour laisser les profils se charger

# Récupérer les liens de profils et filtrer ceux déjà contactés
profile_links = [
    link.get_attribute('href') for link in WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.xocp1fn a[href^='/']"))
    )
]
profile_links = [link for link in profile_links if link not in profils_contactes]
print("Liens de profils récupérés :", profile_links)

# Limiter les actions à 10 par heure
MAX_ACTIONS_PER_HOUR = 10
actions_count = 0

# Suivre les profils et envoyer un message personnalisé
for profile_link in profile_links:
    if actions_count >= MAX_ACTIONS_PER_HOUR:
        print("Limite d'actions atteinte. Pause d'une heure.")
        time.sleep(3600)  # Pause d'une heure avant de continuer
        actions_count = 0  # Réinitialiser le compteur

    driver.get(profile_link)
    time.sleep(3)  # Pause pour charger le profil

    # Récupérer le nom du profil
    try:
        profile_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2"))
        ).text
        print(f"Nom du profil récupéré : {profile_name}")
    except Exception as e:
        print(f"Erreur lors de la récupération du nom pour le profil {profile_link} : {e}")
        continue

    # Vérification pour voir si le profil est déjà suivi
    try:
        # Rechercher le bouton "Suivre" en utilisant la classe et le texte
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, '_ap3a') and text()='Suivre']"))
        )

        # Afficher le texte du bouton pour débogage
        print(f"Texte du bouton de suivi : '{follow_button.text}' pour le profil {profile_link}")

        # Cliquer uniquement si le texte est "Suivre"
        if follow_button.text == "Suivre":
            follow_button.click()
            print(f"Profil suivi : {profile_link}")
            actions_count += 1
    except Exception as e:
        print(f"Erreur lors de la vérification du suivi pour le profil {profile_link} : {e}")
        continue

    # Étape 2 : Cliquer sur "Contacter" et gérer la fenêtre de notification si elle apparaît
    try:
        # Rechercher le bouton "Contacter"
        contact_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x1i10hfl') and text()='Contacter']"))
        )
        contact_button.click()
        time.sleep(2)

        # Vérifier et fermer la fenêtre de notification si elle apparaît après le clic sur "Contacter"
        try:
            notification_popup = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, '_a9--') and text()='Plus tard']"))
            )
            notification_popup.click()
            print("Fenêtre de notification fermée.")
        except Exception as e:
            print("Pas de fenêtre de notification à fermer.")

        # Étape pour s'assurer que le champ de message est bien prêt
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'xdj266r')]"))
        )

        # Saisir le message personnalisé dans le champ de texte
        message_box.click()
        personalized_message = (
            f"Bonjour {profile_name} ! Je suis Fatou, spécialiste en visibilité en ligne pour les artisans. "
            "En découvrant votre travail, je pense qu’il y aurait de belles opportunités pour attirer davantage de clients en optimisant votre présence en ligne. "
            "Que vous ayez déjà un site ou que vous souhaitiez en créer un, nous pouvons vous accompagner pour rendre votre visibilité plus percutante. "
            "Nous proposons des pages de vente efficaces pour attirer les clients, ainsi que des stratégies d'automatisation pour simplifier votre prospection. "
            "Si cela vous intéresse, je serais ravi d’échanger pour voir comment nous pouvons renforcer votre visibilité et simplifier votre prospection. "
            "À bientôt, l'équipe de Fcs Developer."
        )

        message_box.send_keys(personalized_message)
        message_box.send_keys(Keys.ENTER)  # Utiliser ENTER pour envoyer le message

        print(f"Message envoyé à {profile_name} sur le profil : {profile_link}")

        # Ajouter le profil aux profils contactés et mettre à jour le fichier JSON
        profils_contactes.append(profile_link)
        with open("profils_contactes.json", "w") as f:
            json.dump(profils_contactes, f)

    except Exception as e:
        print(f"Erreur lors de l'envoi du message à {profile_link} : {e}")

    # Pause entre chaque interaction pour respecter la limite d'envois
    time.sleep(random.uniform(300, 360))

# Fermer le navigateur
driver.quit()







