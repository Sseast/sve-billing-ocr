# Facture OCR Analyst

A command line tool to analyse, extract and rename pages from billing PDFs

# Installation
1. Télécharger le [projet](https://github.com/Sseast/sve-automation/archive/refs/heads/main.zip) 
2. Décompresser l'archive où vous voulez puis ouvrez 
3. Ouvrez un terminal Git Bash à l'endroit où se situe main.py
4. Tapez la commande `pip install -r requirements.txt`
# Pré-requis
1. Assurez-vous que poppler soit installé sur votre ordinateur. Il devrait être situé ici : **C:\Program Files\\poppler-xx.xx.x**
    - Si ça n'est pas le cas, téléchargez la dernière version de [poppler](https://poppler.freedesktop.org/)
    - Décompressez le fichier archive que vous venez de télécharger dans **C:\Program Files\\**
    - Votre répertoire devrait finalement ressembler à cela par exemple **C:\Program Files\poppler-22.04.0**
2. Assurez-vous que **Python** soit installé, pour cela :
    - Ouvrez le dossier qui contient le robot **robot_facture.py**
    - Dans la barre d'addresse du navigateur de fichier, tapez `cmd` puis appuyez sur "Entrée", cela ouvrira un terminal
    - Tapez ensuite `python robot_facture.py`, si cela ne fonctionne pas, essayez `python3 robot_facture.py` ou encore `py robot_facture.py`
    - Si ça ne fonctionne pas, téléchargez et installer [python](https://www.python.org/downloads/) 
    - Lors de la procédure d'installation, veillez à bien cocher > Ajouter Python à PATH

# Utilisation
1. Ouvrez le répertoire qui contient le fichier **robot_facture.py**
2. Dans la barre d'addresse de la fenêtre, tapez **cmd** puis appuyez sur le bouton "Entrée" pour ouvrir un terminal 
3. Depuis le terminal, tapez `python robot_facture.py` (si cela ne fonctionne pas, essayez `python3 robot_facture.py` ou encore `py robot_facture.py`)
4. Le robot va ensuite vous demander d'ouvrir le fichier PDF de la facture que vous souhaitez traiter, vous n'avez plus qu'à suivre les instructions