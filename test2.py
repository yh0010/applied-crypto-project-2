from utils import *
import base64


print("----------Data Cleaning and Encoding------------")

df = encode_vote()

print(' ')
print("----------Homomorphic Encryption------------") 
# Alice wants confidentiality so she encrypts her dataset before sending out to Carol
# First Alice generates an Homomorphic Encryption object HE
HE = HE_object()

# Then Alice encrypts accordingly
# for efficiency purpose I'm only using the head of df to continue
df_head = df.head()
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
createDB()

#testing in progress below are drafts
c = HE_encryption(2, HE)
print(c)
# message_bytes = bytes(str(c), 'utf-8')
# base64_bytes = base64.b64encode(message_bytes)
# base64_message = base64_bytes.decode('utf-8')

# print(base64_message)
#print(c.__bytes__())
# x = c.to_bytes()
# y = c.__bytes__()
x = c.to_bytes()
y = HE.encryptInt(np.array([-1], dtype=np.int64))
y.from_bytes(x)

print(HE.decryptInt(c),HE.decryptInt(y))





# Carol will use Homomorphic Encryption to encrypt all the encoded information and stores it its database
# here the database I use postgres



