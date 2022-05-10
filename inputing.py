
def ask_user_ttc_price(self):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    while True :
        try:
            user_input = float(input("Veuillez indiquer le montant : ").replace(",","."))
            return str(user_input)+"€"
        except ValueError:
            print("La valeur indiquée semble incorrecte. Veuillez réessayer.")

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
    

def manual_input(self,string,list_data):
    """ Loem Ipsum 
    Parameters:
    -----------
    xxx: Loem Ipsum 
    Return:
    -------
    xxx: Loem Ipsum 
    """
    while True:
        user_input=str(input(string).upper())
        possible_matches = [variable_to_find for variable_to_find in list_data if user_input in variable_to_find]

        if possible_matches:
            possible_matches=possible_matches[:5]
            variable_to_find = self.ask_and_return_possible_match(possible_matches,False)
            if variable_to_find:
                return variable_to_find
            else:
                break
        else:
            print("Aucun résultat.")
            if self.ask_user_choices("Pas de résultat : ",["Réessayer","Autre méthode"],has_ignore_answer=False) -1 : 
                return

