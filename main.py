#1. Scrape top christmas songs from here
import time
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from pathlib import Path
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wish_gen import *
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "ppl.json"


header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
url = "https://toptunetales.com/top-100-christmas-songs-of-all-time/"
response = requests.get(url=url, headers=header)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")
song_names = [a.getText(strip=True) for a in soup.find_all('h3', class_='wp-block-heading')]
print(song_names)

# 2. create Spotify Playlist
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "https://example.com/"

scope = "playlist-modify-public"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                              redirect_uri=SPOTIPY_REDIRECT_URI))

USER_ID = sp.current_user()["id"]

songs = []

for i in song_names:
    result = sp.search(q=i, type="track")
    if result["tracks"]["items"]:
        song_uri = result["tracks"]["items"][0]["uri"]
        songs.append(song_uri)
    else:
        print(f"{i} cannot be found on Spotify")

playlist = sp.user_playlist_create(user=USER_ID, public=True, name=f"Top 100 SONGS CHRISTMAS SONGS",
                                   collaborative=False, description=f"Christmas Melodies from Wei Jun")
sp.playlist_add_items(playlist["id"], songs, position=None)

#3. ============================================================================================have a list of ppl to send to
with open(JSON_PATH , "r", encoding="utf-8") as f:
    data = json.load(f)
# print(data["messenger"][0]["Type"])
#4. ============================================================================================Generate Christmas wish, one for each person
messengerWish = []
whatsappWish = []
instagramWish = []
for i in range(0,len(data["messenger"])):
    messengerWish.append(wish(data["messenger"][i]["Type"], data["messenger"][i]["Name"]))
for i in messengerWish:
    print(i)
for i in range(0,len(data["whatsapp"])):
    whatsappWish.append(wish(data["whatsapp"][i]["Type"], data["whatsapp"][i]["Name"]))
for i in whatsappWish:
    print(i)
for i in range(0,len(data["instagram"])):
    instagramWish.append(wish(data["instagram"][i]["Type"], data["instagram"][i]["Name"]))
for i in instagramWish:
    print(i)




#5. ==================================================================================Selenium send to Messenger, Whatsapp, Instagram
# Messenger
chrome_options = Options()
script_dir = os.path.dirname(os.path.abspath(__file__))
profile_path = os.path.join(script_dir, "messenger_profile")
chrome_options.add_experimental_option("detach",True)

chrome_options.add_argument(f"--user-data-dir={profile_path}")

# Optional: specify a profile name (default is 'Default')
chrome_options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.messenger.com")

time.sleep(5)

for i in range(0, len(data["messenger"])):
    search_bar = driver.find_element(By.XPATH,"//input[@aria-label='Search Messenger']")
    search_bar.send_keys(data["messenger"][i]["Name"], Keys.ENTER)

    wait = WebDriverWait(driver, 10)

    selectp = wait.until(EC.element_to_be_clickable((By.XPATH, "(//ul[@role='listbox']//li[@role='option'])[2]//a")))
    driver.execute_script("arguments[0].click();", selectp)


    time.sleep(3)

    wish = driver.find_element(By.XPATH, "//div[@role='textbox' and @aria-label='Message']")
    wish.send_keys(messengerWish[i], Keys.ENTER)
time.sleep(5)
driver.quit()
# Whatsapp
chrome_options = Options()

script_dir = os.path.dirname(os.path.abspath(__file__))
user_data_path = os.path.join(script_dir, "whatsapp_session")
lock_file = os.path.join(user_data_path, "SingletonLock")
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
    except:
        print("Could not remove lock file. Is Chrome still open?")
chrome_options.add_experimental_option("detach",True)
chrome_options.add_argument(f"--user-data-dir={user_data_path}")
chrome_options.add_argument("--profile-directory=Default")
# Highly recommended: Use a custom User-Agent to avoid being flagged as a bot
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://web.whatsapp.com")

time.sleep(15)
for i in range(0, len(data["whatsapp"])):
    # if i!=0:
    #     exitButton = driver.find_element(By.XPATH,"//button[@aria-label='Cancel Search']")
    #     exitButton.click()
    #     time.sleep(2)
#//*[@id="side"]/div[1]/div/div[2]/span/button
    search_bar = driver.find_element(By.XPATH,"//div[@aria-label='Search input textbox']")
    search_bar.send_keys(data["whatsapp"][i]["Name"], Keys.ENTER)

    # wait = WebDriverWait(driver, 10)

    # selectp = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@aria-label='Search results.']//div[@role='button'])[1]")))
    # driver.execute_script("arguments[0].click();", selectp)

    time.sleep(5)

    wish = driver.find_element(By.XPATH, "//div[@aria-placeholder='Type a message']")
    wish.send_keys(whatsappWish[i], Keys.ENTER)
time.sleep(5)
driver.quit()

#Instagram
for i in range(0, len(data["instagram"])):
    chrome_options = Options()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_path = os.path.join(script_dir, "instagram_session")
    chrome_options.add_experimental_option("detach",True)
    chrome_options.add_argument(f"--user-data-dir={user_data_path}")
    chrome_options.add_argument("--profile-directory=Default")
    # Highly recommended: Use a custom User-Agent to avoid being flagged as a bot
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.instagram.com/")

    time.sleep(5)

    messages = driver.find_element(By.XPATH,"//a[contains(@aria-label, 'Direct messaging')]//span[text()='Messages']")
    try:
        messages.click()
    except:
        driver.execute_script("arguments[0].click();", messages)

    time.sleep(8)
    print(1)
    time.sleep(2)
    search_bar = driver.find_element(By.XPATH,"//input[@placeholder='Search']")
    search_bar.send_keys(data["instagram"][i]["Name"], Keys.ENTER)
    print(2)
    wait = WebDriverWait(driver, 5)
    selectp = wait.until(EC.element_to_be_clickable((By.XPATH, "//h2[contains(text(), 'More accounts')]/following::div[@role='button'][1]")))
    driver.execute_script("arguments[0].click();", selectp)
    print(3)
    time.sleep(3)

    wish = driver.find_element(By.XPATH, "//div[@aria-placeholder='Message...']")
    wish.send_keys(instagramWish[i], Keys.ENTER)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    time.sleep(1)
    driver.quit()

