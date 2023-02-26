import urllib.request
import os

# URL de l'image
image_link = "https://cdn.discordapp.com/attachments/1078621166765363213/1079001582609367081/adrian_dev_zaza_0bb2e0f2-03d2-4c5a-97c0-0c391a7c7990.png"

# Nom de fichier local
filename = "image"

# Créer une requête avec un header User-Agent
req = urllib.request.Request(image_link, headers={'User-Agent': 'Mozilla/5.0'})

# Ouvrir l'URL et sauvegarder le contenu dans le fichier local
with urllib.request.urlopen(req) as response, open(f"{filename}.png", 'wb') as out_file:
    out_file.write(response.read())

# Vérifier si le fichier existe et n'est pas vide
if os.path.isfile(f"{filename}.png") and os.path.getsize(f"{filename}.png") > 0:
    print("L'image a été sauvegardée avec succès!")
else:
    print("La sauvegarde de l'image a échoué.")