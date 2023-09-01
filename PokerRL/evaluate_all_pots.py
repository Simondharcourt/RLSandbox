
import numpy as np
import random
from evaluate import evaluate
from collections import Counter

cards = [[i + 2, card] for i in range(13) for card in ["spades", "heart", "trefle", "square"]] 
scores = []
hand = random.sample(cards, 3)

for i in range(10000):
    my_hand = random.sample(cards, 2) + hand
    scores.append(evaluate(my_hand)[1])
print(cards, ':', sum(scores)/len(cards))

# anyway, it should be possible to evaluate hands. (your hand, and the pot)