
import pandas as pd

import psycopg2,os


DB_HOST = "localhost"
DB_NAME = "clutch"
DB_USER = "postgres"
DB_PASSWORD = "ps190320"
TABLE_NAME = "clutch_profile"

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

                placeholder = ','.join(['%s']*len(item[0]))

                query = f"INSERT INTO {TABLE_NAME} VALUES ({placeholder});"
                # values = [[item.get("email"),str(item.get("website")).split('//')[1]] for item in results]

                cur.executemany(query,item)
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

    csv_path = os.path.abspath('clutch.csv')
    df = pd.read_csv(csv_path)

    df = df.astype(str)
    df.fillna('',inplace=True)
    df.replace('nan','',inplace=True)

    records = df.to_records(index=False)
    save_data(records)
