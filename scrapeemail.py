import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import pandas as pd
from urllib.parse import urlencode,urljoin,urlparse
import random
import psycopg2
import re
import time

DB_HOST = "localhost"
DB_NAME = "clutch"
DB_USER = "postgres"
DB_PASSWORD = "ps190320"
TABLE_NAME = "clutch_profile"
GET_QUERY = '''SELECT * from clutch_profile WHERE email = '' ORDER BY split_part(size,' - ',1)::INTEGER;'''


async def scrape_email(url):

    # ua_path = pathlib.Path(__file__).parent/"ua.csv"
    # df = pd.read_csv(ua_path)
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

    
    item = {}
    item['website'] = url
    custom_headers = {
        "authority": "www.facebook.com",
        "scheme": "https",
        "Accept": "/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded"
    }
  
        
    try:
        browser = await launch({
            'headless': True,
            'args': ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage','--start-maximized','--disable-infobars']
        })
        page = await browser.newPage()
        await page.setUserAgent(random.choice(ua_list))
        await stealth(page)
        await page.setViewport({'width': 1535, 'height': 1080})
        #await page.setExtraHTTPHeaders(custom_headers)
        #page.setDefaultNavigationTimeout(40000)
    except Exception as e:
        print(f"Error: {str(e)}")
        item['email'] = "None"
        save_data(item)

        await page.close()
        await browser.close()
        return item


    try:
        await page.goto(url)
        await asyncio.sleep(12)
        
        pattern = r'\b[A-Za-z][A-Za-z0-9]*@[A-Za-z0-9.-]+\.(?!png|jpg|jpeg|gif)[A-Za-z]{2,4}\b'
        

        first_page_content = await page.content()

        try:
            fb_page_url = await page.querySelectorEval('a[href*="facebook.com"]', "el => el.href")
        except Exception as e:
            fb_page_url = None
        
        try:
            contact_page = await page.querySelectorEval('a[href*="contact"]', "el => el.href")
        except Exception as e:
            contact_page = None
        
        
        if fb_page_url:
            
            await page.goto(fb_page_url)
            await asyncio.sleep(15)
            try:
                await page.click('div[aria-label="Close"]')
            except:
                pass

            content = await page.content()
            email_match_fb = re.findall(pattern, content)
            
            if len(email_match_fb)>0:
                
                item["email"] = email_match_fb[0]
                save_data(item)
                        
                await page.close()
                await browser.close()
                return item
            else:
                
                item["email"] = "None"
            
        
        if contact_page:
            
            await page.goto(contact_page)
            await asyncio.sleep(15)


            try:
                
                email_tag = await page.querySelectorEval('a[href*="mailto"]', "el => el.href")
                item['email'] = str(email_tag).replace('mailto:','')
                save_data(item)
                
                
                await page.close()
                await browser.close()
                return item
            except Exception as e:
                
                email_tag = None
            
            contact_page_content = await page.content()

            if item.get('email','-1') != 'None': 
                
                try:
                    
                    fb_page_url = await page.querySelectorEval('a[href*="facebook.com"]', "el => el.href")
                    await page.goto(fb_page_url)
                    await asyncio.sleep(15)
                    # for closing unwanted pop ups
                    try:
                        await page.click('div[aria-label="Close"]')
                    except:
                        pass

                    content = await page.content()
                    email_match_fb = re.findall(pattern, content)
                    if len(email_match_fb)>0:
                        
                        item["email"] = email_match_fb[0]
                        save_data(item)
                                
                        await page.close()
                        await browser.close()
                        return item
                    else:
                        
                        item["email"] = "None"
                except Exception as e:
                    
                    fb_page_url = None
                    item["email"] = "None"

            if item.get('email','-1') == 'None':

                email_match_regex = re.findall(pattern,contact_page_content)
                email_match_first_page = re.findall(pattern,first_page_content)
                if len(email_match_regex)>0:
                    
                    item['email'] = email_match_regex[0]
                elif len(email_match_first_page)>0:

                    item['email'] = email_match_first_page[0]
                else:
                    
                    item['email'] = 'None'
                save_data(item)
                
                await page.close()
                await browser.close()
                return item
        
        else:
            
            item['email'] = "None"
            save_data(item)
        
            await page.close()
            await browser.close()
            return item


        


    except Exception as e:
        
        
        item['email'] = 'None'
        item['website'] = url
        save_data(item)

        await page.close()
        await browser.close()
        return item
        

    




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
            
                query = f"UPDATE {TABLE_NAME} SET email = %s WHERE website = %s;"
                # values = [[item.get("email"),str(item.get("website")).split('//')[1]] for item in results]

                cur.execute(query,(item.get("email"),item.get("website")))
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

async def scrape_multiple_urls(urls):
    
    tasks = [scrape_email(url) for url in urls]
    await asyncio.gather(*tasks)
        
        
        


if __name__ == "__main__":

    start_time = time.perf_counter()
    df = get_data(database_name=DB_NAME,query=GET_QUERY)


    chunk_size = 8
    urls = df.head(chunk_size)['website'].tolist()
    urls = [str(url).split('?')[0] for url in urls]

    
    asyncio.get_event_loop().run_until_complete(scrape_multiple_urls(urls))

    
    
    end_time = time.perf_counter()
    print(f"Execution time: ------ {end_time-start_time} secs")
    


