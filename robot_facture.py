from turtle import pos
from kiwisolver import Solver
from pdf2image import convert_from_path
import pytesseract
from pytesseract import image_to_string
import cv2
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

from thresholding import *
from solver import *
from inputing import *
from utils import *
"""
Goal :
	- Renommer automatiquement les fichiers PDFx&
	- Supprimer les pages blanches

"""

# pytesseract.pytesseract.tesseract_cmd = 'T:\\INFORMATIQUE\\Rex Rotary\\Robot Analyse Facture\\Tesseract-OCR\\tesseract.exe'

def filter_dirs(dirs=[]):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    result = []
    for dir in dirs:
        try:
            files = os.listdir(dir)
        except:
            continue
        tesseract = 'tesseract.exe' in files
        if tesseract:
            result.append(dir+"\\tesseract.exe")
    return result[0]

pytesseract.pytesseract.tesseract_cmd = filter_dirs(['T:\\INFORMATIQUE\\Rex Rotary\\Robot Analyse Facture\\Tesseract-OCR', 'C:\\Program Files\\Tesseract-OCR'])


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
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def show_exception_and_exit(exc_type, exc_value, tb):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit


class ScanFacture():
    def __init__(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        self.initVariable()
        self.init_dataframe_proprietaire()
        self.init_dataframe_prestataire()

    def initVariable(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        self.is_augmented_help_activated=True
        self.scanned_text=None
        self.scanned_text_concatenated=None
        self.filename_mandats="MANDATS.xlsx"
        self.nom_proprietaire=None
        self.numero_mandat_proprietaire=None
        self.addresse_proprietaire=None
        self.prix_ttc=None

        self.nom_prestataire=None
    
    def init_dataframe_prestataire(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        df_prestataire=None
        filename=glob.glob("./input/*ourniss*")[0]
        df_prestataire = pd.read_excel(filename)


        df_drop_na = df_prestataire[["Unnamed: 1", "Unnamed: 5"]].dropna()
        df_rename=df_drop_na.rename(columns={"Unnamed: 1": 'Numéro prestataire', "Unnamed: 5": "Nom préstataire"})
        df_sort=df_rename.sort_values("Nom préstataire")

        df_regex=df_sort.replace(r'\s*\(.*\).*', "", regex=True)
        df_regex=df_regex.replace(r'EDF\s.*', "EDF", regex=True)
        df_regex=df_regex.replace(r'FONCIA\s.*', "FONCIA", regex=True)
        df_regex=df_regex.replace(r'CITY\s.*', "CITY", regex=True)
        df_regex=df_regex.replace(r'CITYA\s.*', "CITYA", regex=True)
        df_regex=df_regex.drop_duplicates(subset=['Nom préstataire'])

        self.list_numero_prestataire = list(set(df_regex['Numéro prestataire']))
        self.list_nom_prestataire = list(set(df_regex['Nom préstataire']))

        return

    def init_dataframe_proprietaire(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
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
            filename=glob.glob("./input/*mand*.xl*")[0]
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
        self.list_numero_mandat = list(set(self.df_mandats['MANDAT']))
        self.list_numero_mandat.sort()
        # natsorted(self.list_numero_mandat)

        self.list_nom_proprietaire = list(set(df_mandats['NOM_PROPRIETAIRE']))
        self.list_nom_proprietaire.sort()

        self.list_addresse_proprietaire = list(set(df_mandats['ADRESSE_LOCATION']))
        self.list_addresse_proprietaire.sort()
        

    def convert_image_to_text(self,file):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        text = image_to_string(file)
        return text

    def open_pdf(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        print("Veuillez ouvrir un fichier PDF dans la fenêtre qui vient d'apparaitre.")
        self.pdf=fd.askopenfilename(title="Sélectionnez une facture",**FILEOPENOPTIONS)

        self.directory_pdf='/'.join(self.pdf.split('/')[0:-1])
        self.filename_pdf=self.pdf.split('/')[-1]
        
        if not self.pdf:
            sys.exit()
        self.pdf_file_reader_object = PdfFileReader(self.pdf,strict=False)
        return 

    def show_image(self,img):                
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.resize(img, (900, 200))
        cv2.imshow("output", img)
        cv2.startWindowThread()
        return
    
    def show_multiple_image(self):  
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.resize(self.img_normal, (200, 200))
        cv2.imshow("output", self.img_normal)
        # [cv2.imshow('HORIZONTAL'+str(i), img) for i,img in enumerate(self.list_adaptive_threshold)]
        return

    def get_pages_from_any_pdf(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        print("Récupération des pages du fichier PDF, merci de patienter...")
        poppler_path = glob.glob("poppler*\\bin") if  glob.glob("poppler*\\bin") else glob.glob("C:\\Program Files\\poppler*\\Library\\bin") 
        print(poppler_path)
        if not poppler_path:
            print("Mince, l'application poppler est manquante!\nVeuillez la télécharger en suivant ce lien : https://poppler.freedesktop.org/\nUne fois sur le site, téléchargez la dernière archive de poppler (par exemple poppler-22.04.0.tar.xz).\nOuvrez ensuite le fichier archive téléchargé et extrayez son contenu dans le dossier C:\Program Files\\\nDans cet exemple, votre dossier devrait ressembler à ça : C:\Program Files\poppler-22.04.0\nÀ partir de ce moment là, vous pourrez relancer l'application :)")
            quit()
            
        poppler_path.sort(reverse=True)
        poppler_path=poppler_path[0]
        print(poppler_path)
        print(self.pdf)
        time.sleep(1)
        pages = convert_from_path(self.pdf,poppler_path = poppler_path)
        self.pages = pages 

    def get_matches(self,query,list_of_strings):
        """ Returns best fuzzy matching between a string and a list of string associated with probability
        Parameters:
        -----------
        query: the string that we are looking upon
        list_of_strings: a list of string that may contain the query 
        Return:
        -------
        best_match: returns the most probable match between query and list_of_strings
        """
        best_match = process.extractOne(query,list_of_strings)
        return best_match

    def split_and_rename(self,i):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
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

    def rename_used_pdf(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        used_pdf_directory = self.directory_pdf+"/PDF traités"
        
        if not os.path.exists(str(used_pdf_directory)):
            os.makedirs(str(used_pdf_directory))

        timestr = time.strftime("%Y%m%d-%H%M%S")
        
        new_directory_and_filename=used_pdf_directory+"/"+self.filename_pdf+" traitée "+timestr+".pdf"
        
        os.rename(self.pdf, new_directory_and_filename)
        
        print("Fichier traité et déplacé !\n",new_directory_and_filename,"\n")
        pass
    def set_is_augmented_help_activated(self):
        """ Loem Ipsum 
        Parameters:
        -----------
        xxx: Loem Ipsum 
        Return:
        -------
        xxx: Loem Ipsum 
        """
        if ask_user_choices(self,"Souhaitez-vous activer l'aide intelligente ?",["Oui","Non"],False) == 2:
            self.is_augmented_help_activated=False
        return

    def apply(self):
        self.set_is_augmented_help_activated()
        while True :
            self.open_pdf()
            self.get_pages_from_any_pdf()
            for i in range(len(self.pages)):
                print("Traitement de la page",str(i+1)+"/"+str(len(self.pages)),"du fichier PDF.")

                page_into_grayscale(self,self.pages[i])
                plt.imshow(self.img_normal)
                self.show_multiple_image()
                
                #On demande s'il s'agit d'une facture pour passer ou non à la page suivante
                if ask_user_choices(self,"Cette page est-elle une facture ? : ",["Oui","Non"],has_ignore_answer=False) -1 : 
                    continue
                
                grayscale_to_text(self)
                self.prix_ttc=find_possible_prix_ttc(self, self.is_augmented_help_activated)

                while True:
                    display_found_variables(self)
                    self.nom_proprietaire=find_nom_proprietaire(self, self.is_augmented_help_activated)
                    
                    display_found_variables(self)
                    self.addresse_proprietaire=find_addresse_proprietaire(self, self.is_augmented_help_activated)
                    
                    display_found_variables(self)
                    self.numero_mandat_proprietaire=find_numero_mandat_proprietaire(self, self.is_augmented_help_activated)
                    
                    display_found_variables(self)
                    if self.nom_proprietaire and self.addresse_proprietaire and self.numero_mandat_proprietaire :
                        find_prestataire(self, self.is_augmented_help_activated)
                        display_found_variables(self)
                        user_input=ask_user_choices(self,"Est-ce correct ? : ",["Oui","Non"],has_ignore_answer=False)
                        if user_input == 1:
                            break
                        elif user_input == 2:
                            clear_variables(self)
                
                self.split_and_rename(i)
                
                cv2.destroyAllWindows()
                clear_variables(self)
                self.prix_ttc=None
            print("Fin de traitement du fichier PDF !")
            
            self.rename_used_pdf()
            user_input=ask_user_choices(self,"Souhaitez-vous traiter un autre fichier ?",["Oui","Non"],has_ignore_answer=False)
            if user_input -1 :
                print("Fermeture de l'application.\nBonne journée :) !")
                time.sleep(3)
                break

def main():
    print("Lancement de l'application, veuillez patienter...")
    scanner = ScanFacture()
    scanner.apply()
       
if __name__ == "__main__":
    main()
    
