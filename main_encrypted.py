from utils import *
from time import time

print("----------Data Cleaning and Encoding------------")

df = encode_vote()

print(' ')
print("----------Homomorphic Encryption------------")
# Alice wants confidentiality so she encrypts her dataset before sending out to Carol
# First Alice generates an Homomorphic Encryption object HE
HE = HE_object()

# Then Alice encrypts accordingly
# for efficiency purpose I'm only using the head of df to continue
df_head = df.head(50)
print("Before Encryption")
print(df_head)
for i, row in df_head.iterrows():
    ctxt = HE_encryption(int(row['PARTY_AGENDAS_rand_2016']), HE)
    df_head.loc[i,'PARTY_AGENDAS_rand_2016'] = ctxt
    ctxt = HE_encryption(int(row['presvote16post_2016']), HE)
    df_head.loc[i,'presvote16post_2016'] = ctxt
print(' ')
print("After Encryption")
print(df_head)

print(' ')
print("A full Pyfhel object sample: ")
vote = np.array([1], dtype=np.int64)#32?
vote_ctxt = HE.encryptInt(vote) #encrypt it with using the public key
print(vote_ctxt)

print(' ')
print("----------Pass Into Database------------")
# Next Alice stores the ciphertext into Carol
deleteTable() # resetting table for testing purposes
createTable() # create table if such table no exist

insertDB(df_head) # insert Pyfhel.PyCtxt.PyCtxt object into Postgres database
# convert it to bytes stores in BYTEA datatype

checkDB(HE) # Pull out all inserted records to confirm information integrity is preserved
# pull out bytes convert it back to Pyfhel.PyCtxt.PyCtxt decrypted object

print(' ')
print("----------Perform Queries------------")
print("1. [Addition] Carol, give me the total votes of Hillary and Trump individually")
start = time()
queryDB(HE,1)
query1_time = time() - start

print(' ')
print("2. [Conditional Addition] Carol, how many republican voted for Hillary?")
start = time()
queryDB(HE,2)
query2_time = time() - start

print(' ')
print("3. [Conditional Division] Carol, whats the percentage of republican voted for Hillary?")
start = time()
queryDB(HE,3)
query3_time = time() - start

print(' ')
print("----------Execution Time for Each Query------------")
print(f"Query 1: {query1_time:.3f} seconds")
print(f"Query 2: {query2_time:.3f} seconds")
print(f"Query 3: {query3_time:.3f} seconds")
