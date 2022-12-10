import csv
import category_encoders as ce

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

def encoded_candidate():
    df = pd.read_csv("VOTER_Survey_December16_Release1.csv")
    print(df.head()) #to learn what columns we want

    #select only desired columns into new pandas frame
    df_new = df[["case_identifier","PARTY_AGENDAS_rand_2016","inputstate_2016","presvote16post_2016"]]
    print(df_new.head())

    print(df_new['presvote16post_2016'].value_counts())

    df_new.replace(" ", float("NaN"), inplace=True)
    print(df_new.describe(include='all'))

    #restrict candidates to be only Hilary or Trump
    df_HT = df_new[df_new['presvote16post_2016'].isin(['Hillary Clinton','Donald Trump'])]
    df_HT.reset_index(inplace=True, drop=True)
    df_HT.info()
    print(df_HT["presvote16post_2016"].value_counts())

    #encode two candidates into 1 and 0
    y = df_HT['presvote16post_2016'].map({'Hillary Clinton':1,'Donald Trump':0})
    print(y.value_counts())
    return y
