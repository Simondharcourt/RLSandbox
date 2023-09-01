import gym
from gym import spaces
import numpy as np
from evaluate import evaluate

NB_PLAYERS=5
INITIAL_STACK = 20

EPISODES = 1


# why always flush ???
# mettre des limites aux actions.
# pretify the prints (copilot..)

class PokerHoldemEnv(gym.Env):
    def __init__(self):
        
        # Define action and observation spaces
        self.action_space = spaces.Discrete(5)  # Fold, Call, Raise 1x, Raise 2x, All-In
        self.nb_players = NB_PLAYERS
        self.small_blind = 1
        self.observation_space = spaces.Box(low=0, high=1, shape=(15 + 3 * self.nb_players,), dtype=np.float32) # adapt to more players
        
        self.players_stack = [INITIAL_STACK] * self.nb_players
        
        print("Welcome !! We have", self.nb_players, "players. Stacks:" , self.players_stack)


    def reset_deck(self):
        self.deck = [[i + 2, card] for i in range(13) for card in ["spades", "heart", "trefle", "square"]] 

    def deal_initial_hands(self):
        self.players_hand = [[]] * self.nb_players
        for _ in range(2):
            for i in range(self.nb_players):
                if self.players_playing[i]:
                    card = self.deck.pop(np.random.choice(len(self.deck)))
                    self.players_hand[i].append(card)
        self.community_cards = []



    def reset_game(self):
        self.dealer = 0
        self.reset_deck()
        self.players_pot = [0] * self.nb_players  # I think I prefer this state to the following one
        self.players_playing = [self.players_stack[i] > 0 for i in range(self.nb_players)]  # joueurs qui ne sont pas couchés
        self.pot = 0
        self.players_stack = [INITIAL_STACK] * self.nb_players
        
        print("Welcome !! We have", self.nb_players, "players. Stacks:" , self.players_stack)


# States:
# - nb players
# - how many players are still in the game
# - who are you (substract this to other ids - does not count)
# - who is the dealer
# - what is the pot
# - what is your last action
# - what is the next player last action .. (x4)
# - what is your bet
# - what is the next player bet .. (x4)
# - which turn is it?
# - what is your first card
# - what is your second card
# - what is the first card of the pot .. (x3)
# - what is the fourth card of the pot (0 if hidden, x2) (cardeful for evaluation)
# - how much do you still have
# - how much do the next player still have.. (x4)
# bonus:
# - how much do you evaluate your current hand
# - how much do you evaluate your current hand + pot
# - how much do you evaluate your current just the pot (or, hand + pot/just the pot)



    def get_state(self, player, turn):
        state = np.zeros(15 + 3 * self.nb_players)
        state[0] = self.nb_players/5
        state[1] = sum(self.players_playing)/self.nb_players
        state[2] = ((self.dealer - player + self.nb_players)%self.nb_players)/self.nb_players # who is the dealer
        state[3] = (self.pot + sum(self.players_pot))/(INITIAL_STACK*self.nb_players) # what is in the pot
        state[4] = turn/5
        state[5] = evaluate(self.players_hand[player] + self.community_cards)[1]/(15*15*8)
        state[6] = self.players_hand[player][0][0]/15 # use full index
        state[7] = self.players_hand[player][1][0]/15
        state[8] = self.community_cards[0][0]/15 if len(self.community_cards) > 0 else 0
        state[9] = self.community_cards[1][0]/15 if len(self.community_cards) > 1 else 0
        state[10] = self.community_cards[2][0]/15 if len(self.community_cards) > 2 else 0 # and we coud go on to 5
        state[11] = self.players_stack[player]/(INITIAL_STACK*self.nb_players)
        state[12] = self.players_pot[(player - 1 + self.nb_players)%self.nb_players]/(INITIAL_STACK*self.nb_players)
        state[13] = self.players_pot[player]/(INITIAL_STACK*self.nb_players)
        return state
    
    
    def reset_hand(self):
        self.dealer = (self.dealer + 1) % self.nb_players
        print("Dealer is", self.dealer)
        self.reset_deck() # the dealer deals the cards
        self.players_playing = [self.players_stack[i] + self.players_pot[i] > 0 for i in range(self.nb_players)]  # who is playing ?
        print("players:", self.players_playing)
        self.deal_initial_hands() # give the cards to the players
        print("cards:", self.players_hand, len(self.players_hand), len(self.players_hand[0]))
        self.community_cards = []
        return self.get_state((self.dealer + 1) % self.nb_players, 0)


    def end_hand(self):
        all_scores = [evaluate(self.players_hand[i] + self.community_cards)[1] if self.players_playing[i] else 0 for i in range(self.nb_players)]
        winner = np.argmax(all_scores)
        print("winner: ", winner, "of", sum(self.players_pot) + self.pot, "!!!")
        self.players_stack[winner] += sum(self.players_pot) + self.pot
        self.players_pot = [0] * self.nb_players 
        self.pot = 0


    def all_in(self, player):
        self.players_pot[player] += self.players_stack[player]
        self.players_stack[player] = 0
        print("player", player, "does all in !!!!")

        
    def call(self, player):
        print("player", player, "is calling")
        if self.players_pot[player] + self.players_stack[player] > max(self.players_pot):
            self.players_stack[player] += self.players_pot[player] - max(self.players_pot)
            self.players_pot[player] = max(self.players_pot)
        else:
            self.all_in(player)

        
    def raise_bet(self, player, raised_bet):
        self.call(player) # you have to call first to raise
        if self.players_pot[player] + self.players_stack[player] > max(self.players_pot) + self.small_blind * raised_bet:
            self.players_stack[player] -= self.small_blind * raised_bet
            self.players_pot[player] += self.small_blind * raised_bet
            print("player", player, "is raising *", raised_bet)


    def fold(self, player):
        if self.players_pot[player] != max(self.players_pot):
            self.pot += self.players_pot[player]
            self.players_pot[player] = 0
            self.players_playing = [self.players_pot[i] > 0 for i in range(self.nb_players)]  # not playing anymore
            print("player", player, "is folding:", self.players_playing)


    def step(self, player, action): # implement cases if not enough money..
        # Interpret the chosen action and execute the corresponding game logic
        if action == 0:  # Fold
            self.fold(player)
        elif action == 1:  # Call or Check
            self.call(player)
        elif action == 2:  # Raise Half-Pot
            self.raise_bet(player, 1)
        elif action == 3:  # Raise Full-Pot
            self.raise_bet(player, 2)
        elif action == 4:  # All-In
            self.all_in(player)

    def draw_card(self):
        card = env.deck.pop(np.random.choice(len(self.deck)))
        self.community_cards.append(card)    

    def render(self, mode='human'):
        pass
        

class Agent:
    def __init__(self, action_space_size, observation_space_size):
        self.action_space_size = action_space_size
        self.observation_space_size = observation_space_size

    def choose_action(self, state, turn, player, dealer, i):
        if turn == 0 and player in [
            (dealer + 1) % NB_PLAYERS,
            (dealer + 2) % NB_PLAYERS,
        ] and i == 0:
            return 2 # small or big blind
        return np.random.choice(self.action_space_size)  # if possible. Sample from all possible action would be better.




# Create an instance of the environment
if __name__ == "__main__":
    env = PokerHoldemEnv()

    agent = Agent(env.action_space.n, 14)

    for k in range(EPISODES):
        
        print("")
        print("Game: ", k)
        
        state = env.reset_game()
        while len([i for i in env.players_playing if i]) >= 2: # while at least 2 players have money

            turn=0
            
            state = env.reset_hand()
            print("-new_hand")

            while len([i for i in env.players_playing if i]) >= 2 and turn < 5: # while at least 2 players are playing

                i = 0
                print("Turn: ", turn)

                while (
                    (i < env.nb_players
                    or len({j for j in env.players_pot if j > 0}) != 1)
                    and len([i for i in env.players_playing if i]) >= 2 
                    and sum(env.players_stack) > 0
                ):
                    print(len([i for i in env.players_playing if i]), i,  env.players_pot)
                    player = (i + env.dealer + 1) % env.nb_players # start with small blind
                    print(env.players_playing, player)
                    
                    if env.players_playing[player]:                        
                        state = env.get_state(player, turn)

                        action = agent.choose_action(state, turn, player, env.dealer, i//env.nb_players)

                        env.step(player, action)

                        print("--Player: ", player, "choose action: ", action)
                        print()
                    i += 1

                if turn == 0:
                    for _ in range(3):
                        env.draw_card()
                elif turn in {1, 2}: # or all-in has been done ?
                    env.draw_card()    

                turn += 1   
                print()
            env.end_hand()
            print()
        env.render()