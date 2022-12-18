import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()

    mvotes = get_votes(args.file)
    for division, voting in sorted(mvotes.items()):
        produce_division_report(division, voting)


def get_votes(filename):
    with open(filename, 'r') as votes_file:
        lines = [vote_line.strip().lower()
                 for vote_line in votes_file.readlines()
                 if vote_line not in ['', '\n']]
    voting_divisions = {
        'premier': {},
        'intermediate': {},
        'main': {},
        'open': {},
        # 'general': {}
    }

    current_division = ''
    for line in lines:

        dummy = line.split(':')
        category = dummy[0].strip()
        votes = dummy[1].strip()

        if category == 'your team division' or category == 'division (premier/high/intermediate/main/open)':
            current_division = votes
        elif category == 'your team name' or category == 'team name':
            pass
        else:
            #
            # if category in ['best caster']:
            #     current_division, temp_division = 'general', current_division

            if len(votes.split(',')) > 1:
                votes = votes.split(',')
            else:
                votes = [votes]
            votes = [vote.strip() for vote in votes]

            if category not in voting_divisions[current_division]:

                voting_divisions[current_division][category] = []
            voting_divisions[current_division][category] += [votes]

            # if current_division == 'general':
            #     current_division = temp_division

    return voting_divisions


def produce_division_report(division, voting):
    print(division)
    print('=' * len(division))

    for vote_category, ballots in sorted(voting.items()):
        winners = process_votes(ballots)
        print(vote_category + ':', end=' ')
        print(*winners, sep=' and ')


def get_counts(ballots):
    first_votes = dict()
    for vote_set in ballots:
        if len(vote_set) > 0:
            for i, vote in enumerate(vote_set):
                if vote not in first_votes:
                    first_votes[vote] = 0
                if i == 0:
                    first_votes[vote] += 1
    return first_votes


def get_winners(ballots):
    counts = get_counts(ballots)

    max_count = max(counts.values())
    num_counts = sum(counts.values())

    potential_winners = [canidate for (canidate, count) in counts.items()
                         if count == max_count]

    if max_count >= num_counts/2 or len(potential_winners) == len(counts):
        return potential_winners
    else:
        return []


def get_losers(ballots):
    counts = get_counts(ballots)
    min_count = min(counts.values())

    potential_losers = [canidate for (canidate, count) in counts.items()
                        if count == min_count]

    if len(potential_losers) == len(counts):
        return []
    else:
        return potential_losers


def remove_canidate(ballots, canidate):
    for ballot in ballots:
        while canidate in ballot:
            ballot.remove(canidate)


def process_votes(ballots):
    while True:
        winners = get_winners(ballots)
        if winners:
            break

        losers = get_losers(ballots)
        for loser in losers:
            remove_canidate(ballots, loser)
    return winners

main()
