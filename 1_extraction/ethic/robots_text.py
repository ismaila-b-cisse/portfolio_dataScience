# import libraries
import requests

# Préalables pour le web scraping
# analyse du fichier robots
def robots_file_analysis(base_url):
    """
        Le fichier robots.txt contient des chemins que les bots ou robots
        ne doivent pas utiliser. Ce paneau d'attention est parfois addressé
        à tout robot, parfois à des robots spécifiques pour leur dire de ne pas
        emprunter ces chemin. Ainsi, ici, j'analyse les chemins que le site ne veulent
        pas mon programme emprunte pour y extraire des données. Ces chemins contiennent des 
        mots clés qui nous intéressent dans notre scraping. S'ils y sont présent, et que c'est 
        qu'ils sont précédés par un "Disallow", on pourrait ne pas estraire ces données. En revanche, 
        s'ils sont précédés par un "Allow", alors on pourrait les extraire de ce site.
        Par exemple, dans notre présent projet, nous voulons extraire du site les produits et certains de 
        leur caractérisques. ALors "produit" est un mot clé pour nous. Si un chemin contient ce mot clé dans 
        le fichier robots.txt, alors notre programme le détecte et l'affiche. Une fois qu'on a ce chemin, on peut
        voir s'il s'agit de tous les produits ou certains de ces caractéristiques.
        
        Cette fonction --robots_file_analysis-- prend l'URL de base du site qu'on souhaite extraire ces données, on y ajoute 
        le chemin vers le fichier "/robots.txt" qu'on souhaite analyser, et renvoie un dictionnaire
        contenant les user-agent, comme clés, et les chemins comme valeurs.
 
    """
    
    headers = {"user-agnet":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"}

    #response = requests.get("https://httpbin.io/user-agent")
    # Envoi d'une requête au site
    response = requests.get(base_url+"/robots.txt", headers=headers)

    # On construit une liste des lignes du fichier robots
    robots_lines_list = response.text.lower().splitlines()
    #print(robots_text_lines)
    
    # On récupère tous les user-agent du robots.txt
    userAgent_list = []
    for i, agent in enumerate(robots_lines_list):
        userAgent_indice = agent.find("user-agent")
        if userAgent_indice != -1:
            userAgent_list.append(agent)
    # print(userAgent_list)
    
    # On construit un dictionnaire avec comme key le user-agent et value
    # l'item qui ne doit être aspiré
    robots_text_dict = {}
    # On construit un dictionnaire avec comme key le user-agent et value
    # l'item qui ne doit être aspiré
    for i, userAgent in enumerate(userAgent_list):
        start = robots_lines_list.index(userAgent)+1
        
        if i+1 < len(userAgent_list):
            end = robots_lines_list.index(userAgent_list[i+1])
            robots_text_dict[userAgent] = robots_lines_list[start:end]
        else:
            robots_text_dict[userAgent] = robots_lines_list[start:]
    
    return robots_text_dict


def robots_results(base_url, robots_keywords_list):
    """
        Cette fonction -- robots_results -- appelle la --robots_file_analysis--. Elle aussi prend 
        l'URL de base du site, avec le chemin robots.txt, et une liste de mots clés. Elle renvoie 
        les résultats dans un dictionnaire contenant les user-agent, comme clés, concatenés avec le mot clé recherché, 
        séparés par un "_", et comme valeurs les chemins trouvés dans lesquels il y a le mot clé qu'on
        recherche.       
        
        J'ai paramétré le mots clés, car nous ne chercons pas forcément à extraire les mêmes choses. 
        Ainsi, l'utilisateur peut mettre les mots sur lesquels il souhaite travailler. Pour moi, par exemple,
        parmi les mots qui m'interresse figurent "produit", "product", "catalogue", ...
    """
    results_dic = robots_file_analysis(base_url)
    
    results = {}
    for i, item in enumerate(results_dic.items()):
        # On affiche les keywords présent dans les values de la clé
        for robots_keyword in robots_keywords_list:
            for j, robots_keyword_path in enumerate(item[1]):
                if robots_keyword in robots_keyword_path:
                    results.setdefault((item[0]+"_"+robots_keyword).replace(" ", ""), []).append(robots_keyword_path)
                else:
                    continue
                    
    return results
    

def display_robots_results(base_url, robots_keywords_list):
    
    """
        Cette méthode -- display_robots_results -- appelle la fonction -- robots_results -- 
        et permet d'afficher les résultats obtenus. Si aucun des mots clés n'est trouvé, elle
        nous affiche le message "Aucun de ces mots clés que vous cherchez n'est trouvé dans le fichier /robots.txt !"
    """
    
    results_dic = robots_results(base_url, robots_keywords_list)
    
    #print(results_dic)
    #print(results_dic.keys())
    if results_dic == {}:
        print("Aucun de ces mots clés que vous cherchez n'est trouvé dans le fichier /robots.txt !")
    else :
        userAgent_list = []
        for key, values in results_dic.items():
            userAgent_key = key.split("_") # le key avec split à partir "_" -> liste de deux mots : user-agent et le mot clé qui est cherché 
            if userAgent_key[0] not in userAgent_list:
                userAgent_list.append(userAgent_key[0])
        print(userAgent_list)        
           
        for key, values in results_dic.items():
            userAgent_key = key.split("_")
            
            if userAgent_key[0] in userAgent_list:
                print(f"{userAgent_key[0]}")
                userAgent_list.remove(userAgent_key[0])
                
            print(f"\t {userAgent_key[1]} est bien présent dans : ")
            
            for i, robots_keyword_path in enumerate(values):
                print("\t\t", robots_keyword_path)
                
    # lien vers robots.txt et les CGU
    print("Pour plus d'informations, vous pouvez consulter : ", base_url+"/robots.txt")