import numpy as np
import random
from collections import Counter


def highest_card(hand):
    return sorted([c[0] for c in hand], reverse=True)[0]

def second_card(hand):
    return sorted([c[0] for c in hand], reverse=True)[1]

def highest_tuple(hand):
    return Counter([c[0] for c in hand]).most_common(1)[0][1]

def second_tuple(hand):
    return Counter([c[0] for c in hand]).most_common(2)[1][1]

def is_color(hand):
    # print('There are', Counter([c[1] for c in hand]).most_common(1)[0][1], Counter([c[1] for c in hand]).most_common(1)[0][0])
    return Counter([c[1] for c in hand]).most_common(1)[0][1]>=4

def is_straight(hand):
    cards = [c[0] for c in hand]
    return (max(cards) - min(cards)) == 4 and len(set(cards)) == 5

def is_flush(hand):
    return is_straight(hand) and is_color(hand)

def is_royal_flush(hand):
    cards = [c[0] for c in hand]
    return is_flush(hand) and 14 in cards


def is_brelan(hand):
    return highest_tuple(hand) == 3 and second_tuple != 2

def is_full(hand):
    return highest_tuple(hand) == 3 and second_tuple == 2

    
def evaluate(hand):
    hand = [card for card in hand if card]
    if is_royal_flush(hand):
        score = (8, 0, 0)
        print("Royal Flush")
    if is_flush(hand):
        score = (7, highest_card(hand), 0)
        print("Straight Flush")
    elif highest_tuple(hand)==4:
        score = (6, Counter([c[0] for c in hand]).most_common(1)[0][0], 0)
        print("Four of a Kind of", score[1])
    elif is_full(hand):
        score = (5, Counter([c[0] for c in hand]).most_common(1)[0][0], Counter([c[0] for c in hand]).most_common(2)[1][0])
        print("Full House of", score[1], "and", score[2])
    elif is_color(hand):
        score = (4, highest_card(hand), second_card(hand))
        print("Flush")
    elif is_brelan(hand):
            score = (3, Counter([c[0] for c in hand]).most_common(1)[0][0], 0)
            print("Three of a Kind of", score[1])
    elif highest_tuple(hand)==2:
        if second_tuple==2:
            pairs = sorted([Counter([c[0] for c in hand]).most_common(1)[0][0], Counter([c[0] for c in hand]).most_common(2)[1][0]])
            score = (2, pairs[1], pairs[0])
            print("Two Pair of", score[1], "and", score[2])
        else:
            score = (1, Counter([c[0] for c in hand]).most_common(1)[0][0], 0)
            print("One Pair of", score[1])
    else:
        score = (0, highest_card(hand), second_card(hand))
        print("Highest card is", score[1])
    return score, 15*15*score[0] + 15*score[1] + score[2]
    
if __name__ == "__main__":
    cards = [[i + 2, card] for i in range(13) for card in ["spades", "heart", "trefle", "square"]] 
    hand = random.sample(cards, 7)
    print(hand, Counter([c[0] for c in hand]).most_common())
    print("score:", evaluate(hand))
