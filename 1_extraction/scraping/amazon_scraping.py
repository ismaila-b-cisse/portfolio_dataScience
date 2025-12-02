# import libraries
from bs4 import BeautifulSoup
import asyncio
import csv
import random
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
A_PRODUCT = os.getenv("A_PRODUCT")
A_REFERENCE = os.getenv("A_REFERENCE")
A_AVERAGE = os.getenv("A_AVERAGE")
A_REVIEW_NUMBER = os.getenv("A_REVIEW_NUMBER")
A_SALES_NUMBER = os.getenv("A_SALES_NUMBER")
A_PRICE = os.getenv("A_PRICE")
A_PAGINATION = os.getenv("A_PAGINATION")

"""
    Cette fonction scrolle et charge les données.
    Elle prend en entrée :
            - la page,  
            - le nombre de pages qu'on souhaite extraire les données. Il est par défaut égale à 0.
    Elle renvoie en sortie :
            - une liste des données extraites
"""
# Scrolling et loading...
async def scroll_and_load(page, n):
    
    last_height = await page.evaluate('document.body.scrollHeight')
    i = 1
    products_list_n = []
    while i <= n:        
        print(f'================================ Page {i}...')

        # du début jusquà une position donnée
        #await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        
        # On scrolle avec la souris entre 0 et un nombre aléattoire entre 2000 et 7000
        await page.mouse.wheel(0, random.randint(2000, 7000))
        await page.wait_for_timeout(1500)

        # 
        content_html = await page.content()       
        
        prod_locator = page.locator(A_PRODUCT)
        count = await prod_locator.count()
        print("nombre de produits : ", count)

        # BeautifulSoup
        soup = BeautifulSoup(content_html, "html.parser")
    
        products = soup.select(A_PRODUCT)
        #print(products)
        products_list = []
        #print(await page.content())
        for product in products: 
            # Les types et la référence de téléphone (ex : smartphone galaxy S56 ou iphone apple ...)
            typeRef_selector = product.select_one(A_REFERENCE)
            if typeRef_selector:
                typeRef = typeRef_selector.text
            else:
                typeRef = None
                
            # La note du produit            
            average_selector = product.select_one(A_AVERAGE)
            if average_selector:
                average = average_selector.text
            else:
                average = None
            # Le nombre d'avis
            review_number_selector = product.select_one(A_REVIEW_NUMBER)
            if review_number_selector:
                review_number = review_number_selector.text
            else:
                review_number = None
                
            # Le nombre de vente
            sales_number_selector = product.select_one(A_SALES_NUMBER)
            if sales_number_selector:
                sales_number = sales_number_selector.text
            else:
                sales_number = None
            # Le prix du produit            
            price_ttc_selector = product.select_one(A_PRICE)
            if price_ttc_selector:
                price_ttc = price_ttc_selector.text
            else:
                price_ttc = None

            # On récupère la date du scraping
            date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")
            
            products_list.append({"reference":typeRef,
                                  "prix":price_ttc,
                                  "nombreVentes":sales_number,
                                  "note":average,
                                  "nombreAvis":review_number,
                                  "date":date
                                  })

        # On concatène les listes
        products_list_n +=products_list
            
        # position actuelle
        new_height = await page.evaluate('document.body.scrollHeight')
        
        if abs(new_height - last_height) < 100000:
            try:
                # On sélectionne le bouton et son texte
                element = page.locator(A_PAGINATION)
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
                break
                #pass
        else:
            print("fin scroll")
            break
        # On réinitialise last_height pour la page suivante
        last_height = new_height        
        i+=1


    with open("extracted_data/extracted_amazon_data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["reference", "prix", "nombreVentes", "note", "nombreAvis", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products_list_n)

    print('================================ Données amazon chargées ================================')
    return products_list_n