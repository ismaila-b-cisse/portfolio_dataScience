from playwright.async_api import async_playwright, TimeoutError
import asyncio
import os
from dotenv import load_dotenv
from scraping import darty_scraping as darty
from scraping import temu_scraping as temu

load_dotenv()
D_BANNER_BUTTON = os.getenv("D_BANNER_BUTTON")
D_BUTTON_TEXT = os.getenv("D_BUTTON_TEXT")
T_BANNER_BUTTON = os.getenv("T_BANNER_BUTTON")
T_BUTTON_TEXT = os.getenv("T_BUTTON_TEXT")

async def scraper(url, website_name, number_of_page): #BANNER_BUTTON="", BUTTON_TEXT=""): #, text_bandeau="", selector):
    async with async_playwright() as pw:
        # create browser instance
        browser = await pw.chromium.launch(
            # we can choose either headful (with GUI) or headless mode:
            headless=False,
            #devtools=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        # create context
        # Using context we can define page properties like viewport dimensions
        context = await browser.new_context(
            # most commun desktop viewport is 1920x1080
            viewport={"width":1920, "height":1080}
        )
        # create page aka browser tab wich we'll be using to do everything
        page = await context.new_page()

        # enable for intercepting for this page, **/* enable for all request
        # page.on("**/*", intercept_route) # actif quand je loadais sur darty
        
        # go to url
        #await page.goto("https://twitch.tv/directory/game/Art")
        await page.goto(url ,timeout=0, wait_until="networkidle")
        await asyncio.sleep(1)

        # Pour darty
        if website_name=="darty":
            await page.wait_for_selector(D_BANNER_BUTTON, timeout=0)
            await page.click(D_BUTTON_TEXT)
            await asyncio.sleep(1)
            await darty.scroll_and_load(page, number_of_page) #"Voir plus de produits")
        
        # pour temu
        elif website_name=="temu": 
            button = await page.wait_for_selector(T_BANNER_BUTTON, timeout=0)
            await page.click(T_BUTTON_TEXT)
            #await button.dispatch_event('click')
            await asyncio.sleep(1)
            await temu.scroll_and_load(page, number_of_page)
        else:
            print("Ce site n'est pas pris en charge ! veuillez réessayer un autre un autre nom.")
        
        await asyncio.sleep(1)
        # await asyncio.sleep(300)
        await context.close()
        await browser.close()