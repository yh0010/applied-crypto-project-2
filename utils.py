import csv

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
