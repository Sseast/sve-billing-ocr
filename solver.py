from inputing import *

def find_addresse_proprietaire(self,is_augmented_help_activated):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    if self.addresse_proprietaire:
        return
    
    possible_matches=[]
    
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
    
    if not is_augmented_help_activated:
        self.addresse_proprietaire=self.manual_input("Addresse :",self.list_addresse_proprietaire)
        return

    scanned_text =self.scanned_text_concatenated

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

    self.nom_proprietaire=self.manual_input("Addresse :",self.list_nom_proprietaire)
    return

    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    
def find_nom_proprietaire(self,is_augmented_help_activated):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    possible_matches=[]
    nom_proprietaire=None

    #Méthode si variables déjà existantes
    if self.nom_proprietaire:
        return    

    print("\n------------------------------------")
    print("---  Recherche Nom Proprietaire  ---")
    print("------------------------------------")
    if self.numero_mandat_proprietaire:
        self.nom_proprietaire = self.df_mandats.loc[self.df_mandats.MANDAT == str(self.numero_mandat_proprietaire), 'NOM_PROPRIETAIRE'].values.item()
        
        return
    if self.addresse_proprietaire :
        possible_matches = self.df_mandats.loc[self.df_mandats.ADRESSE_LOCATION == self.addresse_proprietaire, 'NOM_PROPRIETAIRE'].values.tolist()
        
        if possible_matches:
            nom_proprietaire = self.ask_and_return_possible_match(possible_matches)
            if nom_proprietaire:
                self.nom_proprietaire=nom_proprietaire
                return
    
    if not is_augmented_help_activated:
        self.nom_proprietaire=self.manual_input("Nom :",self.list_nom_proprietaire)
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
    self.nom_proprietaire = self.manual_input("Nom : ",self.list_nom_proprietaire)

    return

def find_numero_mandat_proprietaire(self,is_augmented_help_activated):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
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

    # if not is_augmented_help_activated:
    self.numero_mandat_proprietaire=self.manual_input("Numéro mandat :",self.list_numero_mandat)
    return
        
def find_prestataire(self,is_augmented_help_activated):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    if self.nom_prestataire:
        return
    
    possible_matches=[]
    scanned_text = self.scanned_text_concatenated

    if not is_augmented_help_activated :
        self.nom_prestataire = self.manual_input("Prestataire :",self.list_nom_prestataire)
        return

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
        if nom_prestataire : 
            self.nom_prestataire=nom_prestataire
            return


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

def find_possible_prix_ttc(self,is_augmented_help_activated):

    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    print("Recherche du prix TTC de la facture.")
    possible_matches_prix=[]

    if not is_augmented_help_activated:
        return ask_user_ttc_price()
    
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
    possible_matches_fine_maille = list(dict.fromkeys([str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", ""))))+"€" for e in re.findall(re_fine, prices,re.IGNORECASE) if float(e.replace(',','.').replace(" ", ""))>0 and float(e.replace(',','.').replace(" ", "")) < 50000 ]))
    possible_matches_fine_maille=possible_matches_fine_maille[:2]

    # Moyenne Maille
    possible_matches_moyenne_maille = list(dict.fromkeys([str('{0:.2f}'.format(float(e.replace(',','.').replace(" ", ""))))+"€" for e in re.findall(re_moyenne, prices,re.IGNORECASE) if float(e.replace(',','.').replace(" ", ""))>0 and float(e.replace(',','.').replace(" ", "")) < 50000 ]))
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
    
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
