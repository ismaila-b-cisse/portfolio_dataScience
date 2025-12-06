# import libraries
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import asyncio
import csv
import random
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
M_BRAND_TITLES = os.getenv("M_BRAND_TITLES")
M_BRAND_LINK = os.getenv("M_BRAND_LINK")
M_BRAND_PAGE_BANNER_BUTTON = os.getenv("M_BRAND_PAGE_BANNER_BUTTON")
M_BRAND_ITEM_LINK = os.getenv("M_BRAND_ITEM_LINK")
M_BRAND_ITEM = os.getenv("M_BRAND_ITEM")
M_BRAND_MODEL = os.getenv("M_BRAND_MODEL")
M_PAGINATION = os.getenv("M_PAGINATION")


"""
    Cette fonction scrolle et charge les données.
    Elle prend en entrée :
            - la page,  
            - le nombre de pages qu'on souhaite extraire les données. Il est par défaut égale à 0.
    Elle renvoie en sortie :
            - une liste des données extraites
    Les données extraites sur le site moviles sont des données supplémentaires constituant une sorte de 
    référentiel des modèles de marques de mobiles pour les données déjà extraites sur les sites darty, 
    temu et amazon.
    Ces données seront traitées dans la partie Préparation des données.
"""
# Scrolling et loading...
async def scroll_and_load(page, n=0):
    
    brand_list = ['samsung', 'apple', 'xiaomi', 'blackview', 'reborn', 'oppo', 'google', 'oukitel', 
                   'honor', 'oneplus', 'artfone', 'oscal', 'fossibot', 'cubot', 'nubia', 'doogee', 
                   'doro', 'vivo', 'huawei', 'hotwav', 'crosscall', 'lagoona', 'olympia', 'generique', 
                   'asus', 'motorola', 'beafon', 'realme', 'iiif150', 'viqee', 'fvh', 'xgody', 
                   'rainbuvvy', 'astarry']
    brand_list = sorted([x.lower() for x in brand_list])
    
    product_list_nplus = []
    product_list_n = []
    
    # Récupère toutes les marques
    brands = await page.locator(M_BRAND_TITLES).all_inner_texts()
    brands = list(map(lambda x : x.lower(), brands))
    
    for brand in brand_list:
        if brand in brands:
            print('--- Marque "',brand,'"')
            try:
                await page.click(M_BRAND_LINK+" a[href='https://fr.moviles.com/"+brand+"']")
                await asyncio.sleep(1)
            except TimeoutError:
                await page.goto("https://fr.moviles.com/"+brand)
                await asyncio.sleep(1)
                
            try:
                await page.wait_for_selector(M_BRAND_PAGE_BANNER_BUTTON)
                await page.click(M_BRAND_PAGE_BANNER_BUTTON)
                await asyncio.sleep(1)
            except TimeoutError:
                pass
    
            try:
                await page.click(M_BRAND_ITEM_LINK+" a[href='https://fr.moviles.com/"+brand+"/tous']")
                await asyncio.sleep(1)
            except TimeoutError:
                await page.goto("https://fr.moviles.com/"+brand+"/tous")
                await asyncio.sleep(1)
                
            
            try:
                # Le nombre total de pages des modèles d'une marque donnée
                n = await page.locator("div.pagination span.numpag strong").nth(1).inner_text()
                n = int(n)
                print("nombre de page : ", n)
            except TimeoutError:
                pass
            last_height = await page.evaluate('document.body.scrollHeight')
            i = 1
            
            while i <= n:
                
                #print(f'================================ page {i}...')
                
                # On scrolle avec la souris entre 0 et un nombre aléattoire entre 2000 et 7000
                await page.mouse.wheel(0, random.randint(2000, 7000))
                await page.wait_for_timeout(1500)
        
                # 
                content_html = await page.content()       
                
                prod_locator = page.locator(M_BRAND_ITEM)
                count = await prod_locator.count()
                #print("nombre de modèles : ", count)
        
                # BeautifulSoup
                soup = BeautifulSoup(content_html, "html.parser")
    
                # Les items (modeles) de la marque
                products = soup.select(M_BRAND_ITEM)
                product_list = []
                
                for product in products: 
                    # Le nom du modèle de la marque
                    model_selector = product.select_one(M_BRAND_MODEL)
                    if model_selector:
                        model = model_selector.text
                    else:
                        model = None
                        
                    # On récupère la date du scraping
                    date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")
                    
                    product_list.append({"marque":brand,
                                          "modele":model,
                                          "date":date
                                          })
                    # print(f"reference : {typeRef}\n prix : {price_ttc}\n"+
                    #       f"nombreVentes : {sales_number}\n note : {average}\n"+
                    #       f"nombreAvis : {review_number}\n date:{date}")
        
                # On concatène les listes
                product_list_n +=product_list
                # position actuelle
                new_height = await page.evaluate('document.body.scrollHeight')
                # print("new_height : ", new_height, "\nlast_height : ", last_height, ""+
                #       "\n diff(new, last) : ", new_height - last_height)
                # chargement - extraction - scrolling - chargement
                if abs(new_height - last_height) < 100000:
                    try:
                        # On sélectionne le bouton et son texte
                        element = page.locator(M_PAGINATION)
                        # Si on scrolle jusqu'à la fin de la page, alors le texte
                        # qu'on souhaite cliquer est déjà visible
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await element.click()
                        await asyncio.sleep(1)
                        try:
                            await asyncio.sleep(1)
                        except TimeoutError:
                            continue                                
                    except TimeoutError:
                        print('Limite atteinte.')
                        #break
                        pass
                else:
                    print("fin scroll")
                    break
                # On réinitialise last_height pour la page suivante
                last_height = new_height        
                i+=1
            print(f'================================ page {i-1} chargée')
           
        else:
            print("'",brand,"' n'est pas dans les marques de mobiles répertoriées par le site moviles")

    product_list_nplus += product_list_n 
    
    with open("extracted_data/additional_data/extracted_moviles_data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["marque", "modele", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_list_nplus)

    print('================================ Données chargées ================================')
    return product_list_nplus



""" 
    On redéfinit la fonction scroll_and_load, en y ajoutant une liste des marques à extraire.

    Cette fonction scrolle et charge les données.
    Elle prend en entrée :
            - la page, 
            - une liste des marques qu'on souhaite extraire leurs modèles est ajouté comme
              paramètre. Il est par défaut vide.
            - le nombre de pages qu'on souhaite extraire les données. Il est par défaut égale à 0.
    Elle renvoie en sortie :
            - une liste des données extraites
    Les données extraites sur le site moviles sont des données supplémentaires constituant une sorte de 
    référentiel des modèles de marques de mobiles pour les données déjà extraites sur les sites darty, 
    temu et amazon.
    Ces données seront traitées dans la partie Préparation des données.
"""
# Scrolling et loading...
async def scroll_and_load(page, brand_list, n=0):
    
    brand_list = sorted([x.lower() for x in brand_list])
    
    product_list_nplus = []
    product_list_n = []
    
    # Récupère toutes les marques
    brands = await page.locator(M_BRAND_TITLES).all_inner_texts()
    brands = list(map(lambda x : x.lower(), brands))
    
    for brand in brand_list:
        if brand in brands:
            print('--- Marque "',brand,'"')
            try:
                # brand_url = "https://fr.moviles.com/"+brand
                # print("brand_url : ", brand_url)
                if brand=='honor':
                    await page.click(M_BRAND_LINK+" a[href='https://fr.moviles.com/hihonor']")
                    await asyncio.sleep(1)
                else:
                    await page.click(M_BRAND_LINK+" a[href='https://fr.moviles.com/"+brand+"']")
                    await asyncio.sleep(1)
            except TimeoutError:
                if brand=='honor':
                    await page.goto("https://fr.moviles.com/hihonor")
                    await asyncio.sleep(1)
                else:
                    await page.goto("https://fr.moviles.com/"+brand)
                    await asyncio.sleep(1)
                
            try:
                await page.wait_for_selector(M_BRAND_PAGE_BANNER_BUTTON)
                await page.click(M_BRAND_PAGE_BANNER_BUTTON)
                await asyncio.sleep(1)
            except TimeoutError:
                pass
    
            try:
                if brand=='honor':
                    await page.click(M_BRAND_ITEM_LINK+" a[href='https://fr.moviles.com/hihonor/tous']")
                    await asyncio.sleep(1)
                else:
                    await page.click(M_BRAND_ITEM_LINK+" a[href='https://fr.moviles.com/"+brand+"/tous']")
                    await asyncio.sleep(1)
            except TimeoutError:
                if brand=='honor':
                    await page.goto("https://fr.moviles.com/hihonor/tous")
                    await asyncio.sleep(1)
                else:
                    await page.goto("https://fr.moviles.com/"+brand+"/tous")
                    await asyncio.sleep(1)
                    
                
            
            try:
                # Le nombre total de pages des modèles d'une marque donnée
                n = await page.locator("div.pagination span.numpag strong").nth(1).inner_text()
                n = int(n)
                print("nombre de page : ", n)
            except TimeoutError:
                pass
            last_height = await page.evaluate('document.body.scrollHeight')
            i = 1
            
            while i <= n:
                
                #print(f'================================ page {i}...')
                
                # On scrolle avec la souris entre 0 et un nombre aléattoire entre 2000 et 7000
                await page.mouse.wheel(0, random.randint(2000, 7000))
                await page.wait_for_timeout(1500)
        
                # 
                content_html = await page.content()       
                
                prod_locator = page.locator(M_BRAND_ITEM)
                count = await prod_locator.count()
                #print("nombre de modèles : ", count)
        
                # BeautifulSoup
                soup = BeautifulSoup(content_html, "html.parser")
    
                # Les items (modeles) de la marque
                products = soup.select(M_BRAND_ITEM)
                product_list = []
                
                for product in products: 
                    # Le nom du modèle de la marque
                    model_selector = product.select_one(M_BRAND_MODEL)
                    if model_selector:
                        model = model_selector.text
                    else:
                        model = None
                        
                    # On récupère la date du scraping
                    date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")
                    
                    product_list.append({"marque":brand,
                                          "modele":model,
                                          "date":date
                                          })
                    # print(f"reference : {typeRef}\n prix : {price_ttc}\n"+
                    #       f"nombreVentes : {sales_number}\n note : {average}\n"+
                    #       f"nombreAvis : {review_number}\n date:{date}")
        
                # On concatène les listes
                product_list_n +=product_list
                # position actuelle
                new_height = await page.evaluate('document.body.scrollHeight')
                # print("new_height : ", new_height, "\nlast_height : ", last_height, ""+
                #       "\n diff(new, last) : ", new_height - last_height)
                # chargement - extraction - scrolling - chargement
                if abs(new_height - last_height) < 100000:
                    try:
                        # On sélectionne le bouton et son texte
                        element = page.locator(M_PAGINATION)
                        # Si on scrolle jusqu'à la fin de la page, alors le texte
                        # qu'on souhaite cliquer est déjà visible
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await element.click()
                        await asyncio.sleep(1)
                        try:
                            await asyncio.sleep(1)
                        except TimeoutError:
                            continue                                
                    except TimeoutError:
                        print('Limite atteinte.')
                        #break
                        pass
                else:
                    print("fin scroll")
                    break
                # On réinitialise last_height pour la page suivante
                last_height = new_height        
                i+=1
            print(f'================================ page {i-1} chargée')
           
        else:
            print("'",brand,"' n'est pas dans les marques de mobiles répertoriées par le site moviles")

    product_list_nplus += product_list_n 
    
    with open("extracted_data/additional_data/extracted_moviles_data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["marque", "modele", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_list_nplus)

    print('================================ Données chargées ================================')
    return product_list_nplus