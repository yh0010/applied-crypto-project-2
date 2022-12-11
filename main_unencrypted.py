from utils import *

print("----------Data Cleaning and Encoding------------")

df = encode_vote()

df_head = df.head(50)
print("Before Encryption")
print(df_head)


print(' ')
print("----------Pass Into Database------------")
# Alice stores data in plaintext
deleteTable_Unencrypted() # resetting table for testing purposes
createTable_Unencrypted() # create table if such table no exist

insertDB_Unencrypted(df_head)

checkDB_Unencrypted()

print(' ')
print("----------Perform Queries------------")
print(' ')
print("1. [Addition] Carol, give me the total votes of Hillary and Trump individually")
queryDB_Unencrypted(1)

print(' ')
print("2. [Conditional Addition] Carol, how many republican voted for Hillary?")
queryDB_Unencrypted(2)

print(' ')
print("3. [Conditional Division] Carol, whats the percentage of republican voted for Hillary?")
queryDB_Unencrypted(3)
