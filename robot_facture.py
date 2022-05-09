from turtle import pos
from pdf2image import convert_from_path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # your path may be different
from pytesseract import image_to_string
import cv2
import numpy as np
import pandas as pd
from fuzzywuzzy import process
import sys, os
import time
import re
import matplotlib.pyplot as plt
import tkinter.filedialog as fd
from PyPDF2 import PdfFileReader, PdfFileWriter
import glob
from pathlib import Path


"""
Goal :
	- Renommer automatiquement les fichiers PDF
	- Supprimer les pages blanches

"""

FILEOPENOPTIONS = dict(defaultextension=".pdf", 
                       filetypes=[('pdf file', '*.pdf')])

frozen = 'not'
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    frozen = 'ever so'
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit


class ScanFacture():
    def __init__(self):
        self.initVariable()
        self.init_dataframe_proprietaire()
        self.init_dataframe_prestataire()

    def initVariable(self):
        self.scanned_text=None
        self.filename_mandats="MANDATS.xlsx"
        self.nom_proprietaire=None
        self.numero_mandat_proprietaire=None
        self.addresse_proprietaire=None
        self.prix_ttc=None

        self.nom_prestataire=None
    
    def init_dataframe_prestataire(self):
        df_prestataire=None
        filename=glob.glob("*frn*")[0]
        df_prestataire = pd.read_excel(filename)



        df_prestataire = df_prestataire[["Unnamed: 1", "Unnamed: 5"]].dropna()
        df_prestataire=df_prestataire.rename(columns={"Unnamed: 1": 'Numéro prestataire', "Unnamed: 5": "Nom préstataire"})
        df_prestataire=df_prestataire.sort_values("Nom préstataire")
        df_prestataire=df_prestataire.replace(to_replace = r'\s\(\d*\)', value ="", regex=True)
        df_prestataire=df_prestataire.drop_duplicates(subset=['Nom préstataire'])

        self.list_numero_prestataire = list(set(df_prestataire['Numéro prestataire']))
        # self.list_numero_prestataire.sort()

        self.list_nom_prestataire = list(set(df_prestataire['Nom préstataire']))
        # self.list_nom_prestataire.sort()

        # print(self.list_nom_prestataire)

        pass

    def init_dataframe_proprietaire(self):
        frozen = 'not'
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            frozen = 'ever so'
            bundle_dir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        df_mandats=None
        try:
            # Si jamais il y a plusieurs fichiers Mandats, on prend le 1er de la liste
            filename=glob.glob("./*mand*.xl*")[0]
            pre = os.getcwd()
            path = os.path.join(pre,filename)
            df_mandats = pd.read_excel(path).astype(str)
            
        except Exception as err:
            print("Il semblerait que le fichier Excel : 'MANDATS.xlsx' soit manquant...")
            print("Assurez-vous de bien le placer dans le même dossier que moi ! :)")
            print("C'est à dire là :")
            print(os.getcwd()+"\ \n")
            # input("Fin de l'exécution...")
            
        self.df_mandats=df_mandats
        self.list_numero_mandat = list(set(self.df_mandats['MANDAT'].astype('int')))
        self.list_numero_mandat.sort()
        # natsorted(self.list_numero_mandat)

        self.list_nom_proprietaire = list(set(df_mandats['NOM_PROPRIETAIRE']))
        self.list_nom_proprietaire.sort()

        self.list_addresse_proprietaire = list(set(df_mandats['ADRESSE_LOCATION']))
        self.list_addresse_proprietaire.sort()
        

    def convert_image_to_text(self,file):
        text = image_to_string(file)
        return text

    def open_pdf(self):
        
        self.pdf=fd.askopenfilename(title="Sélectionnez une facture",**FILEOPENOPTIONS)

        self.directory_pdf='/'.join(self.pdf.split('/')[0:-1])
        self.filename_pdf=self.pdf.split('/')[-1]
        
        if not self.pdf:
            sys.exit()
        self.pdf_file_reader_object = PdfFileReader(self.pdf,strict=False)
        return 

    def show_image(self,img):                
        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.resize(img, (900, 200))
        cv2.imshow("output", img)
        cv2.startWindowThread()
        return
    
    def show_multiple_image(self):  
        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.resize(self.img_normal, (200, 200))
        cv2.imshow("output", self.img_normal)
        # [cv2.imshow('HORIZONTAL'+str(i), img) for i,img in enumerate(self.list_adaptive_threshold)]
        return

    def get_pages_from_any_pdf(self):
        print("Récupération des pages du fichier PDF, merci de patienter...")
        poppler_path = glob.glob("poppler*\\Library\\bin") if  glob.glob("poppler*\\Library\\bin") else glob.glob("C:\\Program Files\\poppler*\\Library\\bin") 
        if not poppler_path:
            print("Mince, l'application poppler est manquante!\nVeuillez la télécharger en suivant ce lien : https://poppler.freedesktop.org/\nUne fois sur le site, téléchargez la dernière archive de poppler (par exemple poppler-22.04.0.tar.xz).\nOuvrez ensuite le fichier archive téléchargé et extrayez son contenu dans le dossier C:\Program Files\\\nDans cet exemple, votre dossier devrait ressembler à ça : C:\Program Files\poppler-22.04.0\nÀ partir de ce moment là, vous pourrez relancer l'application :)")
            quit()
            
        poppler_path.sort(reverse=True)
        poppler_path=poppler_path[0]
        print(self.pdf)
        pages = convert_from_path(self.pdf,poppler_path = poppler_path)
        self.pages = pages 

    def page_into_grayscale(self,page):
        # 1. Load the image
        img = np.asarray(page)
        # 2. Resize the image
        img = cv2.resize(img, None, fx=0.5, fy=0.5)
        # 3. Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 4. Convert image to black and white (using adaptive threshold)
        adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 4)
        
        self.list_adaptive_threshold=[]
        
        # Plus le range est large, plus l'analyse du texte sera poussée mais plus le traitement sera long
        # Les résultats de cette analyse sont contaténés ensemble
        # On prend des ranges impairs car adaptiveThreshold fonctionne avec i impair seulement.add()
        odd_number=[i for i in range(3,10,2)]
        for i in odd_number:
            thres=cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, i, 4)
            self.list_adaptive_threshold.append(thres)

        self.img_normal=img
        self.img_adaptive_threshold=adaptive_threshold

        return 

    def grayscale_to_text(self):
        print("Analyse du texte de la page... Veuillez patienter :)")
        self.scanned_text_concatenated=" ".join([self.convert_image_to_text(txt) for txt in self.list_adaptive_threshold]).replace("\n","")
        
        self.scanned_text=self.convert_image_to_text(self.img_adaptive_threshold)

        return
  
    def get_matches(self,query,choices,limit=3):
        return process.extractOne(query,choices)

    def find_nom_proprietaire(self):
        possible_matches=[]

        #Méthode si variables déjà existantes
        if self.nom_proprietaire:
            return    

        print("\n------------------------------------")
        print("---  Recherche Nom Proprietaire  ---")
        print("------------------------------------")
        if self.numero_mandat_proprietaire:
            self.nom_proprietaire = self.df_mandats.loc[self.df_mandats.MANDAT == str(self.numero_mandat_proprietaire), 'NOM_PROPRIETAIRE'].values.item()
            # self.addresse_proprietaire = self.df_mandats.loc[self.df_mandats.MANDAT == str(self.numero_mandat_proprietaire), 'ADRESSE_LOCATION'].values.item()
            return
        if self.addresse_proprietaire :
            possible_matches = self.df_mandats.loc[self.df_mandats.ADRESSE_LOCATION == self.addresse_proprietaire, 'NOM_PROPRIETAIRE'].values.tolist()
            
            if possible_matches:
                nom_proprietaire = self.ask_and_return_possible_match(possible_matches)
                if nom_proprietaire:
                    self.nom_proprietaire=nom_proprietaire
                    return
        
        #Méthode directe si perfect match
        possible_matches=[]
        for nom_proprietaire in self.list_nom_proprietaire:
            if re.search(r'\b' + nom_proprietaire.upper() + r'\b', self.scanned_text_concatenated.upper()):
                possible_matches.append(nom_proprietaire)
                
        if possible_matches:
            print("J'ai trouvé quelque chose !")
            nom_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if nom_proprietaire:
                self.nom_proprietaire=nom_proprietaire
                return
                
        #Méthode approximative
        lines = [line for line in self.scanned_text_concatenated.splitlines() if len(line)>2 & len(line)<27]
        possible_matches=[]
        for nom_proprietaire in self.list_nom_proprietaire:
            possible_match=self.get_matches(nom_proprietaire,lines)
            if possible_match[1]>=95:
                possible_matches.insert(0,(nom_proprietaire,possible_match[1]))
            elif(possible_match[1]>87):
                possible_matches.append((nom_proprietaire,possible_match[1]))
            
        if possible_matches:
            print("J'ai trouvé quelque chose !")
            possible_matches=sorted(possible_matches, key = lambda x: x[1],reverse=True)
            possible_matches=list(dict.fromkeys(possible_matches))
            possible_matches=possible_matches[:5]

            possible_matches = [tuple[0] for tuple in possible_matches]
            
            nom_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if nom_proprietaire:
                self.nom_proprietaire=nom_proprietaire
                return
        else :
            # print("La recherche approximative n'a rien donné.\n")
            pass

        # Méthode approximation
        print("Essayez vous pour voir ?\n(Vous pouvez écrire approximativement)")
        self.clear_variables()
        while True:
            user_input=str(input("Nom : ").upper())
            possible_matches = [nom_proprietaire for nom_proprietaire in self.list_nom_proprietaire if user_input in nom_proprietaire]
            possible_matches=possible_matches[:5]
            if possible_matches:
                nom_proprietaire = self.ask_and_return_possible_match(possible_matches)
                if nom_proprietaire:
                    self.nom_proprietaire = nom_proprietaire
                    return
                else:
                    break
            else:
                print("Aucun résultat.")
                if self.ask_user_choices("Pas de résultat : ",["Réessayer","Autre méthode"],has_ignore_answer=False) -1 : 
                    return
        return
        
    def find_addresse_proprietaire(self):
        if self.addresse_proprietaire:
            return
        
        possible_matches=[]
        scanned_text =self.scanned_text_concatenated

        print("\n----------------------------------------")
        print("---  Recherche Adresse Proprietaire  ---")
        print("----------------------------------------")

        # Si valeurs déjà connues
        if self.numero_mandat_proprietaire:
            self.nom_proprietaire = self.df_mandats.loc[self.df_mandats.MANDAT == str(self.numero_mandat_proprietaire), 'NOM_PROPRIETAIRE'].values.item()
            self.addresse_proprietaire = self.df_mandats.loc[self.df_mandats.MANDAT == str(self.numero_mandat_proprietaire), 'ADRESSE_LOCATION'].values.item()
            return
        
        elif self.nom_proprietaire :
            possible_matches = self.df_mandats.loc[self.df_mandats.NOM_PROPRIETAIRE == self.nom_proprietaire, 'ADRESSE_LOCATION'].values.tolist()
            if len(possible_matches)==1:
                self.addresse_proprietaire=possible_matches[0]
                return

            addresse_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if addresse_proprietaire :
                self.addresse_proprietaire=addresse_proprietaire
                return

        possible_matches=[]
        for addresse_proprietaire in self.list_addresse_proprietaire:
            if re.search(r'\b' + addresse_proprietaire.upper() + r'\b', scanned_text.upper()):
                possible_matches.append(addresse_proprietaire)
        
        if possible_matches:
            addresse_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if addresse_proprietaire : 
                self.addresse_proprietaire=addresse_proprietaire
                return
            
        # Méthode approximation
        possible_matches=[]
        re_fine = r'(?:\d{0,3}[\/-]?\d{1,4},?\s(?:lieu|rue|place|avenue|route|avenue|avenue|boulevard|quai))[\sa-zA-Z]*'
        possible_matches_regex = list(dict.fromkeys([e for e in re.findall(re_fine, scanned_text,re.IGNORECASE) if len(e)>3 & len(e)<35 ]))
        if possible_matches_regex:
            for addresse_proprietaire in self.list_addresse_proprietaire:
                possible_match=self.get_matches(addresse_proprietaire,possible_matches_regex)
                if possible_match[1]>=95:
                    possible_matches.insert(0,(addresse_proprietaire,possible_match[1]))
                elif(possible_match[1]>89):
                    possible_matches.append((addresse_proprietaire,possible_match[1]))
            possible_matches=list(dict.fromkeys(possible_matches))
            possible_matches=possible_matches[:5]
            possible_matches = [tuple[0] for tuple in possible_matches]
                
            addresse_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if addresse_proprietaire : 
                self.addresse_proprietaire=addresse_proprietaire
                return

        print("Essayez vous pour voir ?\n(Vous pouvez écrire approximativement)")
        self.clear_variables()
        while True:
            user_input=str(input("Tapez l'addresse : ").upper())
            results = [addresse_proprietaire for addresse_proprietaire in self.list_addresse_proprietaire if user_input in addresse_proprietaire]
            results=results[:5]
            
            if results:
                user_input=self.ask_user_choices("Choisissez : ",results)
                if not user_input==len(results):
                    self.addresse_proprietaire = results[user_input-1]
                    return
            if self.ask_user_choices("Pas de résultat : ",["Réessayer","Autre méthode"],has_ignore_answer=False) -1 : 
                return
    
    def ask_and_return_possible_match(self,possible_matches,ask_for_confirmation=True):
        if possible_matches :
            if len(possible_matches)==1 and not ask_for_confirmation:
                value_to_set=str(possible_matches[0])
                return value_to_set
            else:
                input_key=self.ask_user_choices("Choisissez : ",possible_matches)
                if input_key == len(possible_matches):
                    return None
                return str(possible_matches[input_key-1])
        return None
       
    def find_numero_mandat_proprietaire(self):
        possible_matches = [] 
        if self.numero_mandat_proprietaire:
            return

        print("\n----------------------------------------------")
        print("---  Recherche numéro mandat proprietaire  ---")
        print("----------------------------------------------")
        
        if self.nom_proprietaire and self.addresse_proprietaire:
            possible_matches = self.df_mandats.loc[(self.df_mandats['NOM_PROPRIETAIRE'] == str(self.nom_proprietaire) )&(self.df_mandats['ADRESSE_LOCATION'] == str(self.addresse_proprietaire) ),"MANDAT"].values.tolist()

        elif self.nom_proprietaire :
            possible_matches = self.df_mandats.loc[self.df_mandats['NOM_PROPRIETAIRE'] == str(self.nom_proprietaire),"MANDAT"].values.tolist()

        elif self.addresse_proprietaire :
            possible_matches = self.df_mandats.loc[self.df_mandats['ADRESSE_LOCATION'] == str(self.addresse_proprietaire),"MANDAT"].values.tolist()

        if possible_matches:
            if len(possible_matches)==1:
                self.numero_mandat_proprietaire = possible_matches[0]
                return
            else:
                numero_mandat_proprietaire = self.ask_and_return_possible_match(possible_matches)
                if numero_mandat_proprietaire:
                    self.numero_mandat_proprietaire=numero_mandat_proprietaire
                    return

        print("Essayez vous pour voir ?\n(Vous pouvez écrire approximativement)")
        self.clear_variables()
        while True:
            user_input=str(input("Tapez le numéro de mandat : ").upper())
            results = [numero_mandat_proprietaire for numero_mandat_proprietaire in self.list_numero_mandat if user_input in str(numero_mandat_proprietaire)]
            results=results[:5]
            if len(results)==1:
                self.numero_mandat_proprietaire=results[0]
                return
            
            elif len(results)>1:
                user_input=self.ask_user_choices("Choisissez : ",results)
                if not user_input==len(results):
                    self.numero_mandat_proprietaire = results[user_input-1]
                    return
            if self.ask_user_choices("Pas de résultat : ",["Réessayer","Autre méthode"],has_ignore_answer=False) -1 : 
                return
        return

    def split_and_rename(self,i):
        self.addresse_proprietaire=self.addresse_proprietaire.replace("/","-").replace("\\","-")
        self.nom_proprietaire=self.nom_proprietaire.replace("/","-").replace("\\","-")
        timestr = time.strftime("%Y%m%d-%H%M%S")
        time_year = time.strftime("%Y")
        dst = f'{self.directory_pdf}/{time_year}/{self.numero_mandat_proprietaire}/{self.nom_prestataire}/{self.numero_mandat_proprietaire} - {self.nom_proprietaire} - {self.addresse_proprietaire} - {self.prix_ttc} - {timestr}.pdf'
        print("La page traitée a été sauvegardée dans un fichier séparé.\n",dst,"\n")
        
        directory_mandat = self.numero_mandat_proprietaire

        if not os.path.exists(self.directory_pdf+"/"+str(time_year)):
            os.makedirs(self.directory_pdf+"/"+str(time_year))


        if not os.path.exists(self.directory_pdf+"/"+str(time_year)+"/"+str(directory_mandat)):
            os.makedirs(self.directory_pdf+"/"+str(time_year)+"/"+str(directory_mandat))
            
        if not os.path.exists(self.directory_pdf+"/"+str(time_year)+"/"+str(directory_mandat)+"/"+str(self.nom_prestataire)):
            os.makedirs(self.directory_pdf+"/"+str(time_year)+"/"+str(directory_mandat)+"/"+str(self.nom_prestataire))
            
        output = PdfFileWriter()
        output.addPage(self.pdf_file_reader_object.getPage(i))

        with open(dst, "wb") as outputStream:
            output.write(outputStream)

        return

    def clear_variables(self):
        self.numero_mandat_proprietaire=None
        self.addresse_proprietaire=None
        self.nom_proprietaire=None
        return

    def display_found_variables(self):
        print("Valeurs retrouvées : ")
        d=[('N/A' if v is None else v for v in [self.numero_mandat_proprietaire,self.nom_proprietaire,self.addresse_proprietaire,self.prix_ttc,self.nom_prestataire])]
        df = pd.DataFrame(d, columns = ['N°','Nom','Adresse','prix','nom_prestataire'])

        print(df.to_string(index=False))

    def ask_user_ttc_price(self):
        while True :
            try:
                user_input = float(input("Veuillez indiquer le montant : ").replace(",","."))
                return str(user_input)+"€"
            except ValueError:
                print("La valeur indiquée semble incorrecte. Veuillez réessayer.")

    def find_possible_prix_ttc(self):
        print("Recherche du prix TTC de la facture.")
        possible_matches_prix=[]
        prices = self.scanned_text_concatenated
        if self.prix_ttc:
            return

        possible_matches_fine_maille=[]
        possible_matches_moyenne_maille=[]
        possible_matches_grosse_maille=[]
        re_fine=r'(?:montant|tot|net|ttc|tic|itc|iic|t.t.c|t.i.c|i.t.c|i.i.c|t.t.c.|t.i.c.|i.t.c.|i.i.c.)((?:[\s.,]\d+)+[.,]\d{2})'
        re_moyenne=r'((?:[\s]\d+)+[.,]\d{2})'
        re_grosse=r'\d+[.,]+\d{2}'

        # Fine Maille
        possible_matches_fine_maille = list(dict.fromkeys([str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", ""))))+"€" for e in re.findall(re_fine, prices,re.IGNORECASE) if len(str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", "")))))>4 and len(str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", "")))))<13 ]))
        possible_matches_fine_maille=possible_matches_fine_maille[:2]

        # Moyenne Maille
        possible_matches_moyenne_maille = list(dict.fromkeys([str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", ""))))+"€" for e in re.findall(re_moyenne, prices,re.IGNORECASE) if len(str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", "")))))>4 and len(str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", "")))))<13 ]))
        possible_matches_moyenne_maille = list(set(possible_matches_moyenne_maille) - set(possible_matches_fine_maille))
        possible_matches_moyenne_maille.sort(reverse=True)
        possible_matches_moyenne_maille=possible_matches_moyenne_maille[:5]

        possible_matches_prix = possible_matches_fine_maille+possible_matches_moyenne_maille

        if possible_matches_prix:
            possible_matches_prix.append("Saisir le montant")
            input_key=self.ask_user_choices("Quel est le prix ? :",possible_matches_prix, has_ignore_answer=False)
            
            if input_key in range(len(possible_matches_prix)):
                self.prix_ttc=str(possible_matches_prix[input_key-1])
                return
            elif input_key ==(len(possible_matches_prix)):
                self.prix_ttc=self.ask_user_ttc_price()
                return
        else:
            print("Je n'ai pas trouvé le prix TTC.")
            self.prix_ttc=self.ask_user_ttc_price()
            return
        return
        
    def ask_user_choices(self,question,choices,has_ignore_answer=True,display_choices=True):
        print(question)
        if(has_ignore_answer):
            ignore_option="Ignorer suggestion"
            if len(choices)>1:
                ignore_option+="s"
            choices.append(ignore_option)
        if display_choices:
            [print(str(i+1) + " - " + str(x)) for i,x in enumerate(choices)]
        while True :
            try:
                user_input = int(input(""))
                if user_input in range(1,len(choices)+1):
                    return user_input
                else:
                    print("La valeur indiquée semble incorrecte. Veuillez réessayer.")
            except ValueError:
                print("La valeur indiquée semble incorrecte. Veuillez réessayer.")
        
    def rename_used_pdf(self):
        used_pdf_directory = self.directory_pdf+"/PDF traités"
        
        if not os.path.exists(str(used_pdf_directory)):
            os.makedirs(str(used_pdf_directory))

        timestr = time.strftime("%Y%m%d-%H%M%S")
        
        new_directory_and_filename=used_pdf_directory+"/"+self.filename_pdf+" traitée "+timestr+".pdf"
        
        os.rename(self.pdf, new_directory_and_filename)
        
        print("Fichier traité et déplacé !\n",new_directory_and_filename,"\n")
        pass
            
    def find_prestataire(self):
        if self.nom_prestataire:
            return
        
        possible_matches=[]
        scanned_text = self.scanned_text_concatenated

        print("\n----------------------------------------")
        print("---------  Recherche Prestataire  ---------")
        print("----------------------------------------")

        # Méthode match direct
        possible_matches=[]

        regex = ''
        for nom_prestataire in self.list_nom_prestataire:
            if re.search(r'' + nom_prestataire.upper() + r'', self.scanned_text.upper()):
            # if re.search(r'.EDF.', scanned_text.upper()):
                possible_matches.append(nom_prestataire)


        if possible_matches:
            possible_matches=possible_matches[:5]
            nom_prestataire = self.ask_and_return_possible_match(possible_matches)
            print(nom_prestataire)
            if nom_prestataire : 
                self.nom_prestataire=nom_prestataire
                return

        # Méthode approximation
        if False:
            #Méthode approximative
            lines = [line for line in self.scanned_text.splitlines() if len(line)>2 & len(line)<27]
            possible_matches=[]
            print(lines)
            print(len(lines))
            for nom_prestataire in self.list_nom_prestataire:
                possible_match=self.get_matches(nom_prestataire,lines)
                if possible_match[1]>=95:
                    print(possible_match[0])
                    possible_matches.insert(0,(nom_prestataire,possible_match[1]))
                # elif(possible_match[1]>87):
                #     possible_matches.append((nom_prestataire,possible_match[1]))
                
            if possible_matches:
                print("J'ai trouvé quelque chose !")
                possible_matches=sorted(possible_matches, key = lambda x: x[1],reverse=True)
                possible_matches=list(dict.fromkeys(possible_matches))
                possible_matches=possible_matches[:5]

                possible_matches = [tuple[0] for tuple in possible_matches]
                
                nom_prestataire = self.ask_and_return_possible_match(possible_matches)
                if nom_prestataire:
                    self.nom_prestataire=nom_prestataire
                    return
            else :
                # print("La recherche approximative n'a rien donné.\n")
                pass


        print("Essayez vous pour voir ?\n(Vous pouvez écrire approximativement)")
        # self.clear_variables()
        while True:
            user_input=str(input("Tapez le nom du prestataire : ").upper())
            results = [nom_prestataire for nom_prestataire in self.list_nom_prestataire if user_input in nom_prestataire]
            results=results[:10]
            
            if results:
                user_input=self.ask_user_choices("Choisissez : ",results)
                if not user_input==len(results):
                    self.nom_prestataire = results[user_input-1]
                    return
            if self.ask_user_choices("Pas de résultat : ",["Réessayer","Autre méthode"],has_ignore_answer=False) -1 : 
                return
    

    def apply(self):
        while True :
            self.open_pdf()
            self.get_pages_from_any_pdf()
            for i in range(len(self.pages)):
                print("Traitement de la page",str(i+1)+"/"+str(len(self.pages)),"du fichier PDF.")
                self.page_into_grayscale(self.pages[i])
                plt.imshow(self.img_normal)
                self.show_multiple_image()
                
                #On demande s'il s'agit d'une facture pour passer ou non à la page suivante
                if self.ask_user_choices("Cette page est-elle une facture ? : ",["Oui","Non"],has_ignore_answer=False) -1 : 
                    continue
                
                self.grayscale_to_text()
                
                self.find_possible_prix_ttc()

                while True:
                    self.display_found_variables()
                    self.find_nom_proprietaire()
                    
                    self.display_found_variables()
                    self.find_addresse_proprietaire()
                    
                    self.display_found_variables()
                    self.find_numero_mandat_proprietaire()
                    
                    self.display_found_variables()
                    self.find_prestataire()
                    if self.nom_proprietaire and self.addresse_proprietaire and self.numero_mandat_proprietaire :
                        self.display_found_variables()
                        user_input=self.ask_user_choices("Est-ce correct ? : ",["Oui","Non"],has_ignore_answer=False)
                        if user_input == 1:
                            break
                        elif user_input == 2:
                            self.clear_variables()
                
                self.split_and_rename(i)
                
                cv2.destroyAllWindows()
                self.clear_variables()
                self.prix_ttc=None
            print("Fin de traitement du fichier PDF !")
            
            self.rename_used_pdf()
            user_input=self.ask_user_choices("Souhaitez-vous traiter un autre fichier ?",["Oui","Non"],has_ignore_answer=False)
            if user_input -1 :
                print("J'espère avoir pu vous aider, bonne journée :) !")
                time.sleep(3)
                break

def check_missing_modules():
    poppler_path = glob.glob("poppler*\\Library\\bin") if  glob.glob("poppler*\\Library\\bin") else glob.glob("C:\\Program Files\\poppler*\\Library\\bin") 
    
    if not poppler_path:
        print("Mince, l'application poppler est manquante!\nVeuillez la télécharger en suivant ce lien : https://poppler.freedesktop.org/\nUne fois sur le site, téléchargez la dernière archive de poppler (par exemple à poppler-22.04.0.tar.xz).\nOuvez ensuite le fichier archive téléchargé et extrayez son contenu dans le dossier C:\Program Files\\\nDans cet exemple, votre dossier devrait ressembler à ça : C:\Program Files\poppler-22.04.0\nÀ partir de ce moment là, vous pourrez relancer l'application :)")
        quit()
class DataReader():
    def __init__(self):
        pass
    def open_qpr(self):
        pass
    def open_xlsx(self):
        try:
            # Si jamais il y a plusieurs fichiers Mandats, on prend le 1er de la liste
            filename=glob.glob("*frn*")[0]
            print(filename)
            
            file_path = Path(filename)
            file_extension = file_path.suffix.lower()[1:]

            pre = os.getcwd()
            path = os.path.join(pre,filename)

            # df_mandats = pd.read_excel(path).astype(str)
                        
            file_extension = file_path.suffix.lower()[1:]
            print(file_extension)
            if file_extension == 'xlsx':
                df = pd.read_excel(filename, header=1,usecols=['item_type', 'order id', 'order date', 'state', 'priority'])
            elif file_extension == 'xls':
                print("------   ----------------------------------------------------------")
                # df = pd.read_excel(filename, engine='xlrd')
                # df = pd.read_excel(filename, header=None)
                # df.to_excel(filename, index=False, header=False)
                # df = pd.read_excel(filename,  engine='openpyxl')
                print("------   ----------------------------------------------------------")
                
            elif file_extension == 'csv':
                df = pd.read_csv(filename)
            else:
                raise Exception("File not supported")

            print(df)
        except Exception as err:
            print(err)
            
        pass

def main():
    print("Lancement de l'application, veuillez patienter...")

    # qpr = DataReader()
    # qpr.open_xlsx()

    scanner = ScanFacture()
    scanner.apply()
       
if __name__ == "__main__":
    main()
    
