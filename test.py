import numpy as np
from Pyfhel import Pyfhel
from utils import *

votes_raw = get_votes_raw()
votes_count = get_votes_count()

print(votes_count)

#encode candidates : {HC - 1, DT - 0}
enc_candidate = encoded_candidate()
print(enc_candidate.value_counts())