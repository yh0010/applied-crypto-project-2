import csv
import category_encoders as ce
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
from Pyfhel import Pyfhel
import psycopg2
import copy
from psycopg2.extensions import register_adapter, AsIs
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)


def get_votes_count():
    CSV_FILE = 'voter_data.csv'     # I've renamed the csv file in this directory for better readability
    vote_count = {}
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
    for row in reader:
        candidate = row['presvote16post_2016']
        if candidate in vote_count:
            vote_count[candidate] += 1
        else:
            vote_count[candidate] = 1
    return vote_count

def get_votes_raw():
    CSV_FILE = 'voter_data.csv'     # I've renamed the csv file in this directory for better readability
    votes = []
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            candidate = row['presvote16post_2016']
            votes.append(candidate)
    return votes

def encode_vote():
    df = pd.read_csv("voter_data.csv")
    print(' ')
    print("1. to learn what columns we want")
    print(df.head())

    print(' ')
    print("2. select only desired columns into new pandas frame")
    df_new = df[["case_identifier","PARTY_AGENDAS_rand_2016","presvote16post_2016"]]
    print(df_new.head())

    print(' ')
    print("3. restrict candidates to be only Hillary or Trump and remove NaN value")
    print(df_new['presvote16post_2016'].value_counts())

    df_new.replace(" ", float("NaN"), inplace=True)
    print(df_new.describe(include='all'))
    df_HT = df_new[df_new['presvote16post_2016'].isin(['Hillary Clinton','Donald Trump'])]
    df_HT.reset_index(inplace=True, drop=True)
    df_HT.info()
    print(df_HT["presvote16post_2016"].value_counts())

    print(' ')
    print("4. encode two candidates into 1-Hillary and 0-Trump")
    print("encode two parties into 1-Democratic and 0-Republican")
    df_HT['presvote16post_2016'] = df_HT['presvote16post_2016'].map({'Hillary Clinton':1,'Donald Trump':0})
    df_HT['PARTY_AGENDAS_rand_2016'] = df_HT['PARTY_AGENDAS_rand_2016'].map({'Democratic Party':1,'Republican Party':0})

    print(df_HT)
    print(' ')
    print("=> party count")
    print(df_HT['PARTY_AGENDAS_rand_2016'].value_counts())
    print(' ')
    print("=> candidate count")
    print(df_HT['presvote16post_2016'].value_counts())
    #df_HT = df_HT.reset_index()
    return df_HT

def HE_object():
    HE = Pyfhel()           # Creating empty Pyfhel object
    HE.contextGen(scheme='bfv', n=2**14, t_bits=20)#scheme?
    # Generate context for 'bfv'/'ckks' scheme
    # The n defines the number of plaintext slots.
    HE.keyGen() #generae a pair of public and secret keys
    return HE #return HE object

def HE_encryption(val, HE):
    vote = np.array([val], dtype=np.int64)#32?
    vote_ctxt = HE.encryptInt(vote) #encrypt it with using the public key
    return vote_ctxt

def HE_decryption(val, HE):
    vote_dtxt = HE.decryptInt(val)
    return vote_dtxt

def createTable():
    # Connect to the Database Server, now with the created DB
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres") #change your credential
    except (Exception, psycopg2.Error) as error:
        print("Connection not established", error)


    # Check if test_run Table Exists
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='votedata')")
    if bool(cursor.fetchone()[0]):
        print('Table exists. Moving On.')
    else:
        print('Table does not exist. Creating the Table now.')
        cursor.execute("CREATE TABLE votedata (id serial PRIMARY KEY, caseid integer, party bytea, candidate bytea);")
        connection.commit()

def deleteTable():
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres") #change your credential
    except (Exception, psycopg2.Error) as error:
        print("Connection not established", error)

    # Check if table exists
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='votedata')")
    if bool(cursor.fetchone()[0]):
        print('Table exists. Deleting Table.')
        cursor.execute("DROP TABLE votedata")
        connection.commit()

def insertDB(df_head):
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
        cursor = connection.cursor()

        for i, row in df_head.iterrows():
            postgres_insert_query = """ INSERT INTO votedata (caseid, party, candidate) VALUES (%s,%s,%s)"""
            record_to_insert = (row['case_identifier'], row['PARTY_AGENDAS_rand_2016'].to_bytes(), row['presvote16post_2016'].to_bytes())
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()

        count = cursor.rowcount
        print(count, "Record inserted successfully into table")

        print(' ')
        print("Before decryption - A sample on how info is stored inside database")
        print("this is only a fraction of the bytes, the length of bytes will be over millions of chars")
        print(df_head['presvote16post_2016'][0].to_bytes()[:20])

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def checkDB(HE):
    try:
                connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
                cursor = connection.cursor()

                postgres_extract_query = """ SELECT * FROM votedata """
                cursor.execute(postgres_extract_query)

                record = cursor.fetchall()

                print(' ')
                print("After decryption")
                x = HE.encryptInt(np.array([-1], dtype=np.int64))
                y = copy.deepcopy(x)
                for item in record:
                    x.from_bytes(bytes(item[2]))
                    y.from_bytes(bytes(item[3]))
                    print(item[0], item[1], HE.decryptInt(x), HE.decryptInt(y))
                connection.commit()
                count = cursor.rowcount
                print(count, "pulled.")

    except (Exception, psycopg2.Error) as error:
                print("Failed.", error)

    finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")

def queryDB(HE, val):
    col_names = ['id', 'caseid', 'party', 'candidate']
    ls = []
    try:
                connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
                cursor = connection.cursor()

                postgres_extract_query = """ SELECT * FROM votedata"""
                cursor.execute(postgres_extract_query)

                record = cursor.fetchall()
                x = HE.encryptInt(np.array([-1], dtype=np.int64))
                y = copy.deepcopy(x)
                for item in record:
                    x.from_bytes(bytes(item[2]))
                    y.from_bytes(bytes(item[3]))
                    ls.append([item[0], item[1], HE.decryptInt(x), HE.decryptInt(y)])

                df = pd.DataFrame(ls, columns=col_names)

                if val == 1:
                    hillary_total = df['candidate'].sum()
                    trump_total = df['candidate'].count() - df['candidate'].sum()
                    print("Hillary: ", hillary_total.item(0))
                    print("Trump: ", trump_total.item(0))

                elif val == 2:
                    count = 0
                    for i, r in df.iterrows():
                        if r['party'].item(0) == 0 and r['candidate'].item(0) == 1:
                            count += 1
                            # print(count, r)
                    print("The total count is: ",count)

                elif val == 3:
                    count = 0
                    for i, r in df.iterrows():
                        if r['party'].item(0) == 0 and r['candidate'].item(0) == 1:
                            count += 1
                    print(round(float(count/(df['candidate'].count() - df['candidate'].sum()).item(0)) * 100, 2), "%")
                    # query = """drop table votedata"""
                    # cursor.execute(query)
                    # connection.commit()


    except (Exception, psycopg2.Error) as error:
                print("Failed.", error)

    finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    # print("PostgreSQL connection is closed")


##########################################################
### SAME FUNCTIONS AS ABOVE, BUT FOR UNENCRYPTED TABLE ###
##########################################################
def createTable_Unencrypted():
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres") #change your credential
    except (Exception, psycopg2.Error) as error:
        print("Connection not established", error)

    # Check if test_run Table Exists
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='votedata_unencrypted')")
    if bool(cursor.fetchone()[0]):
        print('Unencrypted Table exists. Moving On.')
    else:
        print('Unencrypted Table does not exist. Creating the Table now.')
        cursor.execute("CREATE TABLE votedata_unencrypted (id serial PRIMARY KEY, caseid integer, party int, candidate int);")
        connection.commit()

def deleteTable_Unencrypted():
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres") #change your credential
    except (Exception, psycopg2.Error) as error:
        print("Connection not established", error)

    # Check if table exists
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='votedata_unencrypted')")
    if bool(cursor.fetchone()[0]):
        print('Unencrypted Table exists. Deleting Table.')
        cursor.execute("DROP TABLE votedata_unencrypted")
        connection.commit()

def insertDB_Unencrypted(df_head):
    try:
        connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
        cursor = connection.cursor()

        for i, row in df_head.iterrows():
            postgres_insert_query = """ INSERT INTO votedata_unencrypted (caseid, party, candidate) VALUES (%s,%s,%s)"""
            record_to_insert = (row['case_identifier'], row['PARTY_AGENDAS_rand_2016'], row['presvote16post_2016'])
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()

        count = cursor.rowcount
        print(count, "Record inserted successfully into unencrypted table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into unencrypted table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

def checkDB_Unencrypted():
    try:
                connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
                cursor = connection.cursor()

                postgres_extract_query = """ SELECT * FROM votedata_unencrypted """
                cursor.execute(postgres_extract_query)

                record = cursor.fetchall()
                for item in record:
                    print(item[0], item[1], item[2], item[3])

                connection.commit()
                count = cursor.rowcount
                print(count, "pulled.")

    except (Exception, psycopg2.Error) as error:
                print("Failed.", error)

    finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    # print("PostgreSQL connection is closed")

def queryDB_Unencrypted(val):
    col_names = ['id', 'caseid', 'party', 'candidate']
    ls = []
    try:
                connection = psycopg2.connect("host=localhost password=qqqq dbname=enc_vote user=postgres")
                cursor = connection.cursor()

                postgres_extract_query = """ SELECT * FROM votedata_unencrypted"""
                cursor.execute(postgres_extract_query)

                record = cursor.fetchall()
                for item in record:
                    ls.append([item[0], item[1], item[2], item[3]])

                df = pd.DataFrame(ls, columns=col_names)

                if val == 1:
                    hillary_total = df['candidate'].sum()
                    trump_total = df['candidate'].count() - df['candidate'].sum()
                    print("Hillary: ", hillary_total.item(0))
                    print("Trump: ", trump_total.item(0))

                elif val == 2:
                    count = 0
                    for i, r in df.iterrows():
                        if r['party'].item(0) == 0 and r['candidate'].item(0) == 1:
                            count += 1
                            # print(count, r)
                    print("The total count is: ",count)

                elif val == 3:
                    count = 0
                    for i, r in df.iterrows():
                        if r['party'].item(0) == 0 and r['candidate'].item(0) == 1:
                            count += 1
                    print(round(float(count/(df['candidate'].count() - df['candidate'].sum()).item(0)) * 100, 2), "%")
                    # query = """drop table votedata_unencrypted"""
                    # cursor.execute(query)
                    # connection.commit()
    except (Exception, psycopg2.Error) as error:
                print("Failed.", error)

    finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    # print("PostgreSQL connection is closed")
