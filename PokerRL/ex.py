

import gym
from gym import spaces
import numpy as np
import random



cards = [[i + 2, card] for i in range(13) for card in ["spades", "heart", "trefle", "square"]] 
hand = random.sample(cards, 5)
    
    
NB_PLAYERS = 5

played_cards = random.sample(cards, 5 + 2*NB_PLAYERS)

