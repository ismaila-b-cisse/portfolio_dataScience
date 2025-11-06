# import libraries
from bs4 import BeautifulSoup
import asyncio
import csv
import random
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
D_PRODUCT = os.getenv("D_PRODUCT")
D_FAMILY = os.getenv("D_FAMILY")
D_BRAND = os.getenv("D_BRAND")
D_REFERENCE = os.getenv("D_REFERENCE")
D_AVERAGE = os.getenv("D_AVERAGE")
D_REVIEW_NUMBER = os.getenv("D_REVIEW_NUMBER")
D_SELLER = os.getenv("D_SELLER")
D_LABEL = os.getenv("D_LABEL")
D_PRICE_TTC = os.getenv("D_PRICE_TTC")
D_PAGINATION = os.getenv("D_PAGINATION")

# Scrolling et loading...
async def scroll_and_load(page, n):
    
    last_height = await page.evaluate('document.body.scrollHeight')
    i = 1
    products_list_n = []
    while i <= n:
        #await page.wait_for_selector("body", timeout=0)
        #await page.wait_for_load_state("domcontentloaded", timeout=0) #'load'), 'networkidle'
        #await asyncio.sleep(1)
        
        print(f'================================ Page {i}...')

        # du début jusquà une position donnée
        #await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.mouse.wheel(0, random.randint(2000, 7000))
        await page.wait_for_timeout(1500)
        #await asyncio.sleep(1)

        # 
        content_html = await page.content()       
        
        
        prod_locator = page.locator(D_PRODUCT)
        count = await prod_locator.count()
        print("nombre de produits : ", count)

        # BeautifulSoup
        soup = BeautifulSoup(content_html, "html.parser")
        
        products = soup.select(D_PRODUCT)
        #print(products)
        products_list = []
        #print(await page.content())
        for product in products: 
            # Les types de téléphone (ex : smartphone ou iphone)
            family_locator = product.select_one(D_FAMILY)
            if family_locator:
                family = family_locator.text
            else:
                family = None
            brand_locator = product.select_one(D_BRAND)
            # Le nom du produit
            if brand_locator:
                brand = brand_locator.text
            else:
                brand = None
            # la référence du produit
            reference_locator = product.select_one(D_REFERENCE)
            if reference_locator:
                reference = reference_locator.text
            else:
                reference = None
            # La note du produit
            average_locator = product.select_one(D_AVERAGE)
            if average_locator:
                average = average_locator.text
            else:
                average = None
            # Le nombre d'avis 
            review_number_locator = product.select_one(D_REVIEW_NUMBER)
            if review_number_locator:
                review_number = review_number_locator.text
            else:
                review_number = None
            # Le vendeur
            seller_locator = product.select_one(D_SELLER)
            if seller_locator:
                seller = seller_locator.text
            else:
                seller = None
            # Le label du vendeur
            label_locator = product.select_one(D_LABEL)
            if label_locator:
                label = label_locator.text
            else:
                label = None
            # Le prix du produit
            price_ttc_locator = product.select_one(D_PRICE_TTC)
            if price_ttc_locator:
                price_ttc = price_ttc_locator.text
            else:
                price_ttc = None
            # products_list.append({"marque":brand})
            # print(f"brand : {brand}")

            # On récupère la date du scraping
            date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")
            
            products_list.append({"typeTelephone":family,
                                  "marque":brand,
                                  "reference":reference,
                                  "prix":price_ttc,
                                  "note":average,
                                  "nombreAvis":review_number,
                                  "vendeur":seller,
                                  "nomDuVendeur":label,
                                  "date":date
                                  })
            print(f"typeTelephone : {family}\n marque : {brand}\n reference : {reference}\n"+
                  f"prix : {price_ttc}\n note : {average}\n nombreAvis : {review_number}\n"+
                  f"vendeur : {seller}\n nomDuVendeur : {label} date : {date}")

        # On concatène les listes
        products_list_n +=products_list
            
        # position actuelle
        new_height = await page.evaluate('document.body.scrollHeight')
        print("new_height : ", new_height, "\nlast_height : ", last_height, ""+
              "\n diff(new, last) : ", new_height - last_height)
        # chargement - extraction - scrolling - chargement
        if abs(new_height - last_height) < 100000:
            try:                     
                element = page.locator(D_PAGINATION)
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

    # inspecter le dom
    #print(await page.content())
    # with open("darty2.txt", "w") as darty2:
    #         darty2.write(await page.content())

    
    #print("taille : ", len(products_list_n), "\n", products_list_n)
    with open("extracted_data/extracted_darty_data.csv", 'w', newline='', encoding="utf-8") as csvfile:
        #fieldnames = ["marque"]
        fieldnames = ["typeTelephone", "marque", "reference", "note", "nombreAvis", "vendeur", "nomDuVendeur", "prix", "date"]
        #fieldnames = products_list[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products_list_n)
    return products_list