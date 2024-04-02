import asyncio
from pyppeteer import launch
import random,psycopg2,os,json
import pandas as pd
from pyppeteer_stealth import stealth

import psycopg2
import re
import time

DB_HOST = "localhost"
DB_NAME = "clutch"
DB_USER = "postgres"
DB_PASSWORD = "ps190320"
TABLE_NAME = "clutch_profile"

GET_QUERY = '''SELECT * from clutch_profile WHERE send = '' and size = '2 - 9';'''

async def sign_in_clutch(urls):

    ua_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YaBrowser/21.6.4.787 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 BIDUBrowser/2.x Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Iron Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Comodo_Dragon/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Amigo/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Vivaldi/4.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Maxthon/6.1.3.2000 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Qutebrowser/2.1.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Coc_Coc_browser/100.2.175 Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Whale/2.10.115.42 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Sleipnir/6.5.16 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YandexBrowser/21.6.4.146 Yowser/2.5 Safari/537.36"
    ]

    
  
        
    try:
        browser = await launch({
            'headless': False,
            'args': ['--start-maximized','--disable-infobars']
        })
        page = await browser.newPage()
        await page.setUserAgent(random.choice(ua_list))
        await stealth(page)
        await page.setViewport({'width': 1600, 'height': 1080})
     
    except Exception as e:
        return 1
    
    try:
        
        try:
            await load_cookies(page)
            print("Cookies loaded, attempting to visit the site...")
            
        except FileNotFoundError:
            print("No cookies found, performing initial login...")
        

        baseurl = 'https://clutch.co/'

        email = 'dhainiksuthar@gmail.com'

        password = 'Ankur@1903'

        await page.goto(baseurl)
        await asyncio.sleep(8000)  # Wait for 10 seconds

        # Click on the Sign In button
        sign_in_button_selector = '#sign-in-link'
        await page.click(sign_in_button_selector)
        await asyncio.sleep(5)

        base_selector = "div.sg-modal__window > div.sg-modal__contents > div.main-flow > div.sign-in"

        # Fill in the email address and password using full CSS selectors
        email_selector = f"{base_selector} div.custom-input:nth-of-type(1) input[type='text']"
        password_selector = f"{base_selector} div.custom-input:nth-of-type(2) input[type='password']"
        await page.type(email_selector,email)  # Replace with your actual email
        await page.type(password_selector,password)  # Replace with your actual password

        # Check the "Stay logged in" checkbox
        stay_logged_in_checkbox_selector = f"{base_selector} div.sign-in__forgot input[type='checkbox']#stay"
        await page.click(stay_logged_in_checkbox_selector)

        # Click on the Sign In button in the modal
        sign_in_button_selector = f"{base_selector} button.sign-in__send-button"
        await page.click(sign_in_button_selector)

        # Wait for some time to observe the logged-in state or for further processing
        await page.waitFor(7000)

        print('sign in complete successfully... \n\n')

        cookies = await page.cookies()
        save_cookies(cookies)

        await page.goto(urls[0])
        await asyncio.sleep(5)

        # Close the browser
        await browser.close()
    
    except Exception as e:
        print(str(e))



async def load_cookies(page):
    cookie_path = os.path.abspath('clutch_cookies.json')
    with open(cookie_path, 'r') as f:
        cookies = json.load(f)
        f.close()
    for cookie in cookies:
        await page.setCookie(cookie)

def save_cookies(cookies):
    cookie_path = os.path.abspath('clutch_cookies.json')
    with open(cookie_path, 'w') as f:
        json.dump(cookies, f)
        f.close()

        print('Cookies saved...')




def get_data(database_name, query):
    # PostgreSQL connection parameters
    conn_params = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "dbname": database_name
    }

    # Establish a connection to the PostgreSQL database
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch all data from the query result
        data = cursor.fetchall()

        # Get column names
        col_names = [desc[0] for desc in cursor.description]

        # Create a Pandas DataFrame
        df = pd.DataFrame(data, columns=col_names)

        # Close cursor and connection
        cursor.close()
        conn.close()

        return df

    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None
    
        


if __name__ == "__main__":

    df = get_data(database_name=DB_NAME,query=GET_QUERY)
    print(df)

    url_limit = 5

    urls = df.head(url_limit)['url'].tolist()

    asyncio.get_event_loop().run_until_complete(sign_in_clutch(urls))