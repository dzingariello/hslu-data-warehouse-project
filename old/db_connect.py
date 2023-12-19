import psycopg2
import os


def db_connect(destinations):

    conn = psycopg2.connect(
        host=os.environ['DB_STAG_ENDPOINT'],
        user=os.environ['DB_STAG_USER'],
        password=os.environ['DB_STAG_PW'],
        database=os.environ['DB_STAG_NAME']
    )

    # Create a cursor object
    cursor = conn.cursor()

    table_name = "destinations"

    # Create a table
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute(f"CREATE TABLE {table_name} (id serial PRIMARY KEY, name VARCHAR);")

    # Insert the names from the list into the table
    for destination in destinations:
        cursor.execute(f"INSERT INTO {table_name} (name) VALUES ('{destination}')")

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
