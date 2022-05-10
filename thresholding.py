import numpy as np
import cv2

def page_into_grayscale(self,page):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """


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
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    if not self.is_augmented_help_activated:
        return

    print("Analyse du texte de la page... Veuillez patienter :)")
    self.scanned_text_concatenated=" ".join([self.convert_image_to_text(txt) for txt in self.list_adaptive_threshold]).replace("\n","")
    
    self.scanned_text=self.convert_image_to_text(self.img_adaptive_threshold)

    return
