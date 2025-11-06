# import libraries
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError
import asyncio
from rich import print

# fonction pour supprimer les balises html
def remove_tags(soup_find_all_list):
    texts_list = []
    for text in soup_find_all_list:
        text = text.get_text(strip=True)
        texts_list.append(text)

    return texts_list


async def cgu_analysis_auto(base_url, cgu_path, keywords_list):
    """
        Cette fonction prend la base de l'url d'un site web, le chemin relatif
        de l'url des conditions générales d'utilisation et une list de de mots clés,
        pour vérifier si ces dernisers sont présents ou pas dans le contenu des cgu.
        Elle récupère le contenu d'une page html, notamment les cgu, et retourne 
        un dictionnaire avec le mot clé et le paragraphe dans lequel il se trouve.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        #browser = await pw.firefox.launch(headless=False)
        page = await browser.new_page()
        
        async def handle_response(response):
            url = response.url
            try:                
                if "api" in url or url.endswith("json"):
                    data = await response.json
                    print("API trouvé : ", url)
                    print(data)
            except:
                pass
                #print("Pas d'API trouvé !")

        # La page écoute l'évenenment "response", si le navigateur reçoit des réponses, 
        # elle appelle un callback en l'occurrence handle_response qui traite les responses reçues et 
        # les trie selon qu'ils soient .json ou non
        #page.on("response", handle_response)
        page.on("response", f=lambda response: handle_response(response))

        
        # La réponse de la navigation
        response = await page.goto(base_url+cgu_path, wait_until="networkidle")
        #response = await page.goto(base_url+cgu_path, {timeout:0}, wait_until="networkidle")
        page.set_default_navigation_timeout(0)
        status = response.status if response else None
        print("Status HTTP : ", status)
        
        if status != 200:
            print("Une erreur est survenue ! \nVeuillez réssayer plus tard" +
            "\nou accédez au lien ", base_url+cgu_path)

        #print(response.url)
        #print(response.json)
        await page.wait_for_selector("body")
        content = await page.content()
        #print(content) # [:2000]

        # On récupère le texte des cgu avec BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        #print(soup.get_text())
        await asyncio.sleep(5)
        #await browser.close()
        
        
        # vérifier si un keyword est présent dans les titre ou sous-titres
        # vérifier si un keyword est présent dans les paragraphes
        h2_titles_list = soup.find_all("h2")
        #print(h2_titles_list)
        h3_titles_list = soup.find_all("h3")
        p_list = soup.find_all("p")
        li_list = soup.find_all("li")

        # tags deletion
        h2titles_list = remove_tags(h2_titles_list)
        h3titles_list = remove_tags(h3_titles_list)
        paragraphs_list = remove_tags(p_list)
        puces_list = remove_tags(li_list)
        

        keywords_dic = {}
        for keyword in keywords_list:
            for paragraph in paragraphs_list:
                if keyword in paragraph:                    
                    keywords_dic.setdefault(keyword, []).append(paragraph)
            for puce in puces_list:
                if keyword in puce:
                    keywords_dic.setdefault(keyword, []).append(puce)

        return keywords_dic


async def display_cgu_results(base_url, cgu_path, keywords_list):
    """
        Affichage des mots clés trouvés dans les cgu de l'url et 
        leurs paragraphes
    """
    keywords_dic = await cgu_analysis_auto(base_url, cgu_path, keywords_list)

    # On met les mots clés qui sont présent dans le passage des cgu
            # en gras et de couleur rouge 
    values_list = [] #list(keywords_dic.values())
    for key, values in keywords_dic.items():
        #print(type(values), "-- ", values)
        #print("***","[bold]"+key+"[/bold]", " ---> ", values)
        print("***","[bold]"+key+"[/bold]", " ---> ")

        for value in values:
            value = value.replace(key, "[bold red]"+key+"[/bold red]")
            print("\t", value)
  
    #     print()

    print("Pour plus d'informations, vous pouvez consulter : ", base_url+cgu_path)

    # print("Pour plus d'informations, vous pouvez consulter : ", base_url+cgu_path) 


# Si vous mettez un nombre important de à chercher, vous aurez beaucoup de passages. 
# Egalement, si vous mettez un mot clé seul qui est abondamment cité dans les cgu, 
# comme licence ou utilisation, vous aurez beaucoup de passages avec ces mots, qui peuvent
# ne pas être pertinents pour votre recherche. Donc, l'idéal c'est de combiner les mots clés
# importants. Par exemple, on peut associer "utilisation" et ..., extraction et données en 
# "extraction de données" pour avoir des passages pertients.
# En revance, certains mots clés sont à eux seuls pertients dans la recherche, comme "scraping", 
# "scraper", "robot" (bon, on suppose qu'on ne va pas parler de robots de cusine dans les cgu),
# "bot", ...

# Enfin, bien que ce programme facilite la recherche d'un mot clés dans les cgu et leur lecture, 
# il est toujours intéressant de se rapporter sur le lien des cgu que nous affichons dans les réponse
# pour de plus amples informations, peut-être sur les passage qui sont affichés. Si vous ne trouvez pas un mot, cela ne veut pas forcément dire qu'il n'exite pas dans les cgu.
# peut-être les passages des cgu contenant le mot que vous cherché est inclus dans d'autres balises 
# différents de ceux qui sont habituellement utilisés pour un texte. D'où l'importance de jetter un coup
# d'oeil sur l'url des cgu que nous affichons pour plus d'informations.

async def analyse_cgu(url, page, keywords_list): 
    relevant_list = ["robot", "extraction", "scraping"]
    content = await page.content()
    #print(content)
    await asyncio.sleep(1)

    soup = BeautifulSoup(content, "html.parser")
    cgu_title_selector = soup.select_one("h1") ##GUID-602FA6E8-D724-4317-89F6-E78834F9BA58__GUID-2C1DF364-8FA3-4387-BCDB-2A63B7C51B64")
    print(cgu_title_selector.text)

    #cgu_subtitles_selector = soup.select("h2")# donne la liste de tous les h2 #.sectiontitle")
    #cgu_subtitles_selector = soup.select_one("h2")# donne un h2
    #cgu_subtitles_selector = soup.select("section")
    cgu_sections_selector = soup.find_all("section")
    #print("---- ", cgu_subtitles_selector, " ----")
    
    
    for section in cgu_sections_selector: 
        sectiontitle_selector = section.select_one("h2") # on met find car un seul title dans chaque section 
        # avec comme classe .sectiontitle, dans le cas d'amazon
        section_paragraphs_selector = section.find_all("p") 
        #print("=== " , subtitle_paragraphs_selector," === ")
        for paragraph_selector in section_paragraphs_selector:
            found_keywords =  [] # les keywords trouvés dans le paragraphes
            
            paragraph = paragraph_selector.text
            # On vérifie que chaque mot clé de notre existe dans la paragraphe de la section
            for keyword in keywords_list:
                if keyword in paragraph:
                    found_keywords.append(keyword) 

            # si un 
            if found_keywords != []:
                # Pour rendre la recherche pertinente, si la liste a un élement que 
                # ce n'est pas robot, extraction, scraping, on n'affiche pas
                if len(found_keywords) == 1 and found_keywords[0] not in relevant_list:
                    pass
                else:
                    print("Mots clés ")

                
                for found_key in found_keywords:
                    # Pour rendre la recherche pertinente, si la liste a un élement que 
                    # ce n'est pas robot, extraction, scraping, on n'affiche pas
                    if len(found_keywords) == 1 and found_keywords[0] not in relevant_list:
                        pass
                    else:
                        print("[bold]"+found_key+"[/bold]")
                        paragraph = paragraph.replace(found_key, "[bold red]"+found_key+"[/bold red]")                
                
                # Pour rendre la recherche pertinente, si la liste a un élement que 
                # ce n'est pas robot, extraction, scraping, on n'affiche pas
                if len(found_keywords) == 1 and found_keywords[0] not in relevant_list:
                    pass
                else:
                    print("trouvés dans la sections : ---> ")
                    #print("\t", sectiontitle_selector.get_text())
                    #print("\t", type(sectiontitle_selector))
                    try:
                        print("\t", sectiontitle_selector.text)
                    except AttributeError: # cette erreur, au cas, l'attribut sectiontitle n'est pas trouvé, s'il n'y a pas de h2
                        pass
                    print("\t", paragraph)
            else:
                #print("mot clé non trouvé !")
                pass

    print("Pour plus d'informations, vous pouvez consulter : ", url) #base_url+cgu_path)
            

async def cgu_analysis(url, keywords_list):
    async with async_playwright() as pw : 
        # On lance un navigateur
        browser = await pw.chromium.launch(headless=False 
                                           #args=["--disable-blink-features=AutomationControlled"]
                                          )
        
        context = await browser.new_context()
        # On ouvre une page sur cette navigateur
        page = await context.new_page()

        # On passe l'url sur sur la barre d'adresse de la page
        await page.goto(url, wait_until="networkidle", timeout=0)# wait_until="networkidle", "domcontentloaded"
        #page.set_default_navigation_timeout(0)
        await asyncio.sleep(1)

        # Faire des screeshots
        #await page.screenshot(path=url+".png", full_page=True)

        # appel 
        await analyse_cgu(url, page, keywords_list)
        
        
        await asyncio.sleep(1)
        await context.close()
        await browser.close()