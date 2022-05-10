
def clear_variables(self):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    self.numero_mandat_proprietaire=None
    self.addresse_proprietaire=None
    self.nom_proprietaire=None
    self.nom_prestataire=None
    return

def display_found_variables(self):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    print("Valeurs retrouvées : ")
    d=[('N/A' if v is None else v for v in [self.numero_mandat_proprietaire,self.nom_proprietaire,self.addresse_proprietaire,self.prix_ttc,self.nom_prestataire])]
    df = pd.DataFrame(d, columns = ['N°','Nom','Adresse','Prix','Nom Prestataire'])

    print(df.to_string(index=False))
