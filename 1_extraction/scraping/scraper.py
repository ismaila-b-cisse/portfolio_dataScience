from playwright.async_api import async_playwright, TimeoutError
import asyncio
import os
from dotenv import load_dotenv
from scraping import darty_scraping as darty
from scraping import temu_scraping as temu
from scraping import amazon_scraping as amazon
from scraping import moviles_scraping as moviles

load_dotenv()
ARGS = os.getenv("ARGS")
D_BANNER_BUTTON = os.getenv("D_BANNER_BUTTON")
D_BUTTON_TEXT = os.getenv("D_BUTTON_TEXT")
T_BANNER_BUTTON = os.getenv("T_BANNER_BUTTON")
T_BUTTON_TEXT = os.getenv("T_BUTTON_TEXT")
M_BANNER_IFRAME = os.getenv('M_BANNER_IFRAME')
M_BANNER_BUTTON = os.getenv("M_BANNER_BUTTON")


"""
    Cette méthode lance le navigateur et appelle la fonction scroll_and_load.
    Elle prend 
            - l'url, 
            - le nom du site sur lequel on fait l'extraction, 
            - le nombre de pages qu'on souhaite extraire les données. Il est par défaut égale à 0.
"""
async def scraper(url, website_name, number_of_page=0):
    
    async with async_playwright() as pw:
        # créer une instance de browser
        browser = await pw.chromium.launch(
            headless=False,
            args=[ARGS]
        )
        # Créer un contexte
        context = await browser.new_context()
        # Créer la page
        page = await context.new_page()
        
        print(website_name)
        
        # Pour darty
        if website_name=="darty":
            # Ouvrir le navigateur, attendre que le réseau soit soit inactif et ne pas limiter le temps
            await page.goto(url, timeout=0, wait_until="networkidle")
            await asyncio.sleep(1)
            
            print("loading...")
            await page.wait_for_selector(D_BANNER_BUTTON, timeout=0)
            await page.click(D_BUTTON_TEXT)
            await asyncio.sleep(1)
            await darty.scroll_and_load(page, number_of_page)
        
        # pour temu
        elif website_name=="temu":
            await page.goto(url ,timeout=0, wait_until="networkidle")
            await asyncio.sleep(1)
            
            print("loading...")
            button = await page.wait_for_selector(T_BANNER_BUTTON, timeout=0)
            await page.click(T_BUTTON_TEXT)
            await asyncio.sleep(1)
            await temu.scroll_and_load(page, number_of_page)

        # pour amazon
        elif website_name=="amazon":
            # Ouvrir le navigateur, attendre que la page html soit chargé et limiter le temps à 10s
            await page.goto(url, timeout=10000, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            print("loading...")
            await amazon.scroll_and_load(page, number_of_page)

        # Pour moviles
        elif website_name=="moviles":
            await page.goto(url ,timeout=0, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            try:
                locator = page.frame_locator(M_BANNER_IFRAME).locator(M_BANNER_BUTTON)
                await locator.click()
                await asyncio.sleep(1)
            except TimeoutError:
                pass
            
            print("loading...")
            await moviles.scroll_and_load(page, number_of_page)
            
        else:
            print("Ce site n'est pas pris en charge ! veuillez réessayer un un autre nom.")
        
        await asyncio.sleep(1)
        await context.close()
        await browser.close()