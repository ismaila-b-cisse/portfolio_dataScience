# import libraries
from bs4 import BeautifulSoup
import asyncio
import csv
import random
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
T_PRODUCT = os.getenv("T_PRODUCT")
T_REFERENCE = os.getenv("T_REFERENCE")
T_BRAND = os.getenv("T_BRAND")
T_AVERAGE = os.getenv("T_AVERAGE")
T_REVIEW_NUMBER = os.getenv("T_REVIEW_NUMBER")
T_SALES_NUMBER = os.getenv("T_SALES_NUMBER")
T_PRICE = os.getenv("T_PRICE")
T_PAGINATION = os.getenv("T_PAGINATION")

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
    product_list_n = []
    while i <= n:        
        print(f'================================ Page {i}...')
        
        # On scrolle avec la souris entre 0 et un nombre aléattoire entre 2000 et 7000
        await page.mouse.wheel(0, random.randint(2000, 7000))
        await page.wait_for_timeout(1500)

        # 
        content_html = await page.content()       
        
        prod_locator = page.locator(T_PRODUCT)
        count = await prod_locator.count()
        print("nombre de produits : ", count)

        # BeautifulSoup
        soup = BeautifulSoup(content_html, "html.parser")
    
        products = soup.select(T_PRODUCT)
        #print(products)
        product_list = []
        for product in products: 
            # Les types et la référence de téléphone (ex : smartphone galaxy S56 ou iphone apple ...)
            typeRef_selector = product.select_one(T_REFERENCE)
            if typeRef_selector:
                typeRef = typeRef_selector.text
            else:
                typeRef = None

            # La marque du produit            
            brand_selector = product.select_one(T_BRAND)
            if brand_selector:
                # on a marque : marqueTelephone, on supprime les espaces, sépare les mots 
                # à partir des ":" et enfin on récupère le second élément
                brand = brand_selector.text #
            else:
                brand = None
                
            # La note du produit            
            average_selector = product.select_one(T_AVERAGE)
            if average_selector:
                average = average_selector.text
            else:
                average = None
            # Le nombre d'avis
            review_number_selector = product.select_one(T_REVIEW_NUMBER)
            if review_number_selector:
                review_number = review_number_selector.text
            else:
                review_number = None
                
            # Le nombre de vente
            sales_number_selector = product.select_one(T_SALES_NUMBER)
            if sales_number_selector:
                sales_number = sales_number_selector.text
            else:
                sales_number = None
            # Le prix du produit            
            price_ttc_selector = product.select_one(T_PRICE)
            if price_ttc_selector:
                price_ttc = price_ttc_selector.text
            else:
                price_ttc = None

            # On récupère la date du scraping
            date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")
            
            product_list.append({"typeRefTelephone":typeRef,
                                  "marque":brand,
                                  "prix":price_ttc,
                                  "nombreVentes":sales_number,
                                  "note":average,
                                  "nombreAvis":review_number,
                                  "date":date
                                  })
            print(f"typeRefTelephone : {typeRef}\n marque : {brand}\n"+
                  f"prix : {price_ttc}\n nombreVentes : {sales_number}\n"+ 
                  f"note : {average}\n nombreAvis : {review_number}\n date:{date}")

        # On concatène les listes
        product_list_n +=product_list
            
        # position actuelle
        new_height = await page.evaluate('document.body.scrollHeight')
        print("new_height : ", new_height, "\nlast_height : ", last_height, ""+
              "\n diff(new, last) : ", new_height - last_height)
        
        if abs(new_height - last_height) < 100000:
            try:
                # On sélectionne le bouton et son texte
                element = page.locator(T_PAGINATION)
                # Si on scrolle jusqu'à la fin de la page, alors le texte
                # qu'on souhaite cliquer est déjà visible
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await element.click()
                await asyncio.sleep(1)
                try:
                    print(f"{await element.text_content()} est bien cliqué...")
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

    with open("extracted_data/extracted_temu_data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["typeRefTelephone", "marque", "prix", "nombreVentes", "note", "nombreAvis", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(product_list_n)

    print('================================ Données temu chargées ================================')
    return product_list_n