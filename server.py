from flask import Flask, render_template
from flask_socketio import SocketIO
from engineio.async_drivers import gevent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import urllib.request
import time
import os
import shutil
import json
import threading
import sys

if getattr(sys, 'frozen', False):
    ROOT_PATH = sys._MEIPASS
else:
    ROOT_PATH = os.getcwd()

SETTINGS = json.load(open('C:\MJ_SETTINGS.json'))
# SETTINGS['FOLDER_TO_STORE_IMAGE'] = os.path.join(ROOT_PATH, './static/images')
# SETTINGS['FOLDER_TO_STORE_IMAGE'] = "C:/Users/AdrianBenard/Documents/development/perso/midjourney-/static/"

app = Flask(__name__, static_folder=SETTINGS['FOLDER_TO_STORE_IMAGE'])
socketio = SocketIO(app)
driver = webdriver.Chrome()

XPATH_CONVERSATION = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/nav/ul/div[2]/div[3]/div[2]/div[2]/div/div/svg/foreignObject/div/div'
XPATH_INPUT_EMPTY = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/main/form/div/div[1]/div/div[3]/div/div[2]/div'
XPATH_INPUT_NOT_EMPTY = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/main/form/div/div[1]/div/div[3]/div/div/div'
XPATH_PROMPT_EMPTY = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div/main/form/div/div[2]/div/div[2]/div/div/div/span[2]/span[2]/span/span'
XPATH_PROMPT_NOT_EMPTY = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div/main/form/div/div[2]/div/div[2]/div/div/div/span[2]/span[2]/span/span/span'
XPATH_OL_MESSAGES = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[2]/div[2]/main/div[1]/div/div/ol'
XPATH_WHEN_IMAGE_OPEN = '//*[@id="app-mount"]/div[2]/div[1]/div[3]/div[2]/div/div/div/div/img'

DATA = None

THREAD_WAIT = None

MAP_VERSION = {
    "v3": "--v 3",
    "v4a": "--style 4a",
    "v4b": "--style 4b",
    "v4c": "--v 4",
}         

MAP_RATIO = {
    "base": "",
    "2:3": " --aspect 2:3",
    "3:2": " --aspect 3:2",
    "1:2": " --aspect 1:2",
    "2:1": " --aspect 2:1",
    "16:9": " --aspect 16:9",
    "9:16": " --aspect 9:16",
}

MAP_RATIO_FILENAME = {
    "base": "",
    "2:3": " 2_3",
    "3:2": " 3_2",
    "1:2": " 1_2",
    "2:1": " 2_1",
    "16:9": " 16_9",
    "9:16": " 9_16",
}


def connect_selenium():
    driver.get("https://discord.com/login")
    input_username = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="uid_8"]'))
    )
    input_password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="uid_11"]'))
    )
    button_login = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div/div/div/form/div[2]/div/div[1]/div[2]/button[2]'))
    )
    input_username.send_keys(SETTINGS['DISCORD_USERNAME'])
    input_password.send_keys(SETTINGS['DISCORD_PASSWORD'])
    button_login.click()

def wait_response(prompt, version, ratio):
    print("wait_response", prompt, version, ratio)
    reponse_received = {}
    responses_needed = 0
    for v in version:
        reponse_received[v] = {}
        reponse_received[v]['base'] = False
        responses_needed += 1
        for r in ratio:
            responses_needed += 1
            reponse_received[v][r] = False
    all_messages = driver.find_element(By.XPATH, XPATH_OL_MESSAGES)
    while responses_needed > 0:
        time.sleep(5)
        li_messages = all_messages.find_elements(By.TAG_NAME, 'li')
        for li in li_messages:
            # print(li.get_attribute('innerHTML'))
            # Pour chaque combinaison de version et de ratio
            for v in reponse_received:
                for r in reponse_received[v]:
                    # Si la réponse pour cette combinaison de version et de ratio n'a pas encore été reçue
                    if not reponse_received[v][r]:
                        # On construit le XPath pour l'image correspondant à cette combinaison de version et de ratio
                        option = f"{prompt} {MAP_VERSION[v]}{MAP_RATIO[r]}"
                        filename = f"{'_'.join(prompt.split()[:3])} {MAP_VERSION[v]}{MAP_RATIO_FILENAME[r]}"
                        xpath_img = f'.//*[contains(text(), "{option}")]'
                        # print(xpath_img)
                        # On essaie de trouver l'élément <img> correspondant à cette combinaison de version et de ratio
                        try:
                            element = li.find_element(By.XPATH, xpath_img)
                            # Si on trouve l'élément <img>, on cherche son parent pour vérifier s'il est en attente ou en cours de traitement
                            elem_parent = element.find_element(By.XPATH, '..')
                            # print(element.text)
                            # print(elem_parent.text)
                            if f"{prompt} {MAP_VERSION[v]}{MAP_RATIO[r]} -" in elem_parent.text:
                                # print(f"{prompt} {MAP_VERSION[v]}{MAP_RATIO[r]} -")
                                if "(Waiting to start)" in elem_parent.text:
                                    break
                                    print("Waiting to start")
                                elif "%)" in elem_parent.text:
                                    break
                                    print("Processing")
                                else:
                                    # print('---------------------------- ready')
                                    try:
                                        # print(li.get_attribute('outerHTML'))
                                        # img = li.find_element(By.XPATH, '//div[2]/img')
                                        # //img[contains(@class, 'lazyImg-ewiNCh')]
                                        # img = li.find_element(By.XPATH, "//img[@class='lazyImg-ewiNCh']")
                                        # link_img = li.find_element(By.XPATH, "//div[@class='imageWrapper-oMkQl4 imageZoom-3yLCXY clickable-LksVCf lazyImgContainer-3k3gRy']")
                                        # print(link_img.get_attribute('outerHTML'))
                                        image_link = li.find_element(By.XPATH, ".//div[contains(@class,'mageWrapper-oMkQl4 imageZoom-3yLCXY clickable-LksVCf lazyImgContainer-3k3gRy')]//a[contains(@class,'originalLink')]").get_attribute("href")
                                        # print("image_link", image_link)

                                        req = urllib.request.Request(image_link, headers={'User-Agent': 'Mozilla/5.0'})

                                        # Ouvrir l'URL et sauvegarder le contenu dans le fichier local
                                        with urllib.request.urlopen(req) as response, open(f"{filename}.png", 'wb') as out_file:
                                            out_file.write(response.read())

                                        # Vérifier si le fichier existe et n'est pas vide
                                        if os.path.isfile(f"{filename}.png") and os.path.getsize(f"{filename}.png") > 0:
                                            print("L'image a été sauvegardée avec succès!")
                                            shutil.move(f"{filename}.png", os.path.join(SETTINGS['FOLDER_TO_STORE_IMAGE'], f"images/{filename}.png"))
                                        else:
                                            print("La sauvegarde de l'image a échoué.")

                                        reponse_received[v][r] = True
                                        responses_needed -= 1

                                        print(f"Image saved here {SETTINGS['FOLDER_TO_STORE_IMAGE']}/images/{filename}.png")
                                        socketio.emit('receive_image', {
                                            'url': f"./static/images/{filename}.png",
                                            'version': v, 
                                            'ratio': r
                                        })

                                    except Exception as e:
                                        # handle the error when the element is not found
                                        pass
                                
                                # On marque cette combinaison de version et de ratio comme reçue
                        except Exception as e:
                            # Si on ne trouve pas l'élément <img> correspondant à cette combinaison de version et de ratio, on continue la boucle
                            pass


def process_command(version, ratio, prompt):
    # v = version[1:]
    option = f"{prompt} {MAP_VERSION[version]}{MAP_RATIO[ratio]}"
    print("process_command", option)
    input_command = driver.find_element(By.XPATH, XPATH_INPUT_EMPTY)
    input_command.send_keys("/imagine")
    time.sleep(2)
    input_command = driver.find_element(By.XPATH, XPATH_INPUT_NOT_EMPTY)
    input_command.send_keys(Keys.RETURN)
    time.sleep(2)
    input_command = driver.find_element(By.XPATH, XPATH_PROMPT_EMPTY)
    input_command.send_keys(option)
    time.sleep(2)
    input_command = driver.find_element(By.XPATH, XPATH_PROMPT_NOT_EMPTY)
    input_command.send_keys(Keys.RETURN)

# routes

@app.route('/')
def index():
    return render_template('index.html', active={"new_prompt": True})

@app.route('/historic')
def historic():
    return render_template('not_available.html', active={"historic": True})

@app.route('/generate_image')
def generate_image():
    print("generate_image", DATA)
    return render_template(
        'generation.html', 
        active={"none": True}, 
        nb_col=len(DATA["version"])+1,
        nb_row=len(DATA["ratio"])+1,
        data=DATA)

@socketio.on('send_data')
def prompt_data(data):
    global DATA
    DATA = data
    # print("data_received", DATA)
    time.sleep(3)
    for v in DATA["version"]:
        process_command(v, "base", DATA["prompt"])
        for r in DATA["ratio"]:
            process_command(v, r, DATA["prompt"])
    THREAD_WAIT = threading.Thread(target=wait_response, args=(DATA["prompt"], DATA["version"], DATA["ratio"],))
    THREAD_WAIT.start()

if __name__ == '__main__':
    connect_selenium()
    socketio.run(app, debug=False, port=5001)
