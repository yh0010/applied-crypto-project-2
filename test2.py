from utils import *

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
print("----------Pass Into Database------------") 
# Next Alice stores the ciphertext into Carol
createTable() # create table if such table no exist

insertDB(df_head) # insert Pyfhel.PyCtxt.PyCtxt object into Postgres database
# convert it to bytes stores in BYTEA datatype

checkDB(HE) # Pull out all inserted records to confirm information integrity is preserved
# pull out bytes convert it back to Pyfhel.PyCtxt.PyCtxt decrypted object

print(' ')
print("----------Perform Queries------------") 
print(' ')
print("1. Carol, give me the total votes of Hilary and Trump individually") 
queryDB(HE,1)

print(' ')
print("2. Carol, how many republican voted for Hilary?") 
queryDB(HE,2)

print(' ')
print("3. Carol, whats the percentage of republican voted for Hilary?") 
queryDB(HE,3)