import json, argparse
from io import *

# Syntax
# python3 parse_votes_new.py -f votes.txt
# python3 parse_votes_new.py -f votes.txt -d

# -d just adds the score to the end of the vote, for debugging purposes.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help='File to read votes from', required=True)
    parser.add_argument('--debug', '-d', help='Debug mode', action='store_true')
    parser.add_argument('--nocap', '-c', help='Don\'t cap to 3 awards', action='store_true')
    args = parser.parse_args()
    global debug
    debug = args.debug
    global dontcap
    dontcap = args.nocap
    # If the file doesnt exist, exit
    rawvotes = dict()
    try:
        with open(args.file, 'r') as votes_file:
            rawvotes = parse_votes(votes_file)

    #   for k       , v      in sorted(rawvotes.items()):
        for division, voting in sorted(rawvotes.items()):
            produce_division_report(division, voting)

    except FileNotFoundError:
        print("File not found")
        exit(1)

def parse_votes(votes_file: TextIOWrapper):
    # Read the file by line
    lines = [vote_line.strip().lower()
             for vote_line in votes_file.readlines()
             if vote_line not in ['', '\n']]
    voting_divisions = {
    }
    i = 0
    current_division = ''
    for line in lines:
        i+=1
        # Process each line of the votes dump.
        separator = line.split(':')
        try:
            question = separator[0].strip()
            response = separator[1].strip()
        except IndexError:
            print(f'[[ERROR]]: Malformed line {i} : {line}')
            print(f'[[FATAL]]: Correct this error before continuing.')
            exit(1)



        if question == 'your team division' or question == 'division (premier/high/intermediate/main/open)':
            current_division = response
        elif question == 'your team name' or question == 'team name':
            # End of previous teams votes. In the event of the first team, nothing preceeded this so nothing happened.
            pass
        else:
            # The response is a comma separated list of votes, in theory.
            # Assuming that the response has been pre-santized, we can split it by commas.
            if len(response.split(',')) > 1:
                response = response.split(',')
            else:
                response = [response]
            # warn if more than 3 votes are given.
            if len(response) > 3:
                print(f'[[WARNING]]: Too many votes given for line {i} : {line}')

            # Do we know of this division?
            if current_division not in voting_divisions:
                voting_divisions[current_division] = {}

            # What category is this vote for?
            if question not in voting_divisions[current_division]:
                voting_divisions[current_division][question] = []

            # Add the votes to the list of votes for this category.
            voting_divisions[current_division][question] += [response]

    return voting_divisions

def produce_division_report(division, voting):
    print(division)
    print('=' * len(division))

    # loop through categories
    for vote_category, ballots in sorted(voting.items()):
        # Voting works by scoring 3 points to the first vote, 2 to the second and 1 to the third.
        # These are then summed up to give a total score.
        scores = {}
        for ballot in ballots:
            for i, vote in enumerate(ballot):
                vote = vote.strip()
                if vote not in scores:
                    scores[vote] = 0
                scores[vote] += 3 - min(i,3) # 3, 2, 1, and then don't count anything after
        # sort the scores and get the top 3
        winners = sorted(scores, key=scores.get, reverse=True)
        if !nocap:
            winners = winners[:3]
        printstring = vote_category + ': '
        for winner in winners:
            if debug:
                printstring += f'{winner} ({scores[winner]}), '
            else:
                printstring += f'{winner}, '
        print(printstring[:-2])

if __name__ == '__main__':
    main()

