import params
import psycopg2
import sql

conn = psycopg2.connect(
    host=params.DB_HOST,
    database=params.DB,
    user=params.USER,
    password=params.PASSWORD,
    port=params.PORT)


def insert(source):
    """ Connect to the PostgreSQL database server """
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        
        # create a cursor
        cur = conn.cursor()
        
    # execute a statement
        for query in sql.queries:
            cur.execute(query.format(source=source))
        print('Insertion données effectuée')            
       
    # close the communication with the PostgreSQL DB
        cur.close()

        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

#raw_input car python2
source=input("Quelle est la base de données source ?")

if __name__ == '__main__':
    insert(source)