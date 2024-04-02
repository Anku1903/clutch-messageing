
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import pandas as pd
from urllib.parse import urlencode,urljoin,urlparse
import random
import psycopg2
import time


DB_HOST = "localhost"
DB_NAME = "clutch"
DB_USER = "postgres"
DB_PASSWORD = "ps190320"
TABLE_NAME = "clutch_profile"

GET_QUERY = '''SELECT * from clutch_profile WHERE website = '' ORDER BY split_part(size,' - ',1)::INTEGER;'''

concurrent_limit = 25

async def scrape_website(urls):
    
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

    user_agent = random.choice(ua_list)
    item = {
        "website": "",
        "url": ""
    }

    
    try:
        browser = await launch({
            'headless': True,
            'args': ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage','--start-maximized','--disable-infobars']
        })
        page = await browser.newPage()
        await page.setUserAgent(user_agent)
        await stealth(page)
        await page.setViewport({'width': 1535, 'height': 1080})

        for url in urls:
            await page.goto(url)
            await asyncio.sleep(6)
            
            try:
                website = await page.querySelectorEval("ul.profile-quick-menu > li.profile-quick-menu--visit > a","el => el.href")
            except:
                website = "none"
         
            item["website"] = str(website).strip().split("?")[0]
            item["url"] = url
            
            save_data(item)
            item = {
                "website": "",
                "url": ""
            }
        
        
               

        
        
        await browser.close()
       
        

   
    except Exception as e:
        print(f"--------------------------------------------------------\n Error: {e} \n -----------------------\n")
       





def save_data(item):
                 
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Connected to the database successfully.")

            # Create a cursor object to execute SQL queries
            cur = conn.cursor()

            try:
                # Construct the SQL query for data insertion and execute it

                query = f"UPDATE {TABLE_NAME} SET website = %s WHERE url = %s;"
                cur.execute(query,(item.get("website"),item.get("url")))
                conn.commit()
            except Exception as e:
                conn.rollback()  # Rollback the transaction if an error occurs
                print("Error: Unable to insert data.")
                print(e)

        except Exception as e:
            print("Error: Unable to connect to the database.")
            print(e)

        finally:
            # Close the cursor and the database connection
            cur.close()
            conn.close()


def show_data(data):
    for dictitem in data:
        print("----------------------------------------------------- \n")
        for x in dictitem.keys():
            print(f"{x} : {dictitem[x]} \n")
    print("----------------------------------------------------- \n")



def getdata():
    db_params = {
    'host': DB_HOST,
    'database': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'port': '5432' }

    connection = psycopg2.connect(**db_params)
    
    dataframe = pd.read_sql(GET_QUERY, connection)
    return dataframe




if __name__ == "__main__":
    df = getdata()

    urls = df.head(concurrent_limit)['url'].tolist()

    asyncio.get_event_loop().run_until_complete(scrape_website(urls))
    
      
    
