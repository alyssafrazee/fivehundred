## 500 game in python, creating a game class so as to avoid scope problems!
## AF June 24 2013

# create a deck of cards
def build_deck():
    deck = []
    for num in range(4,11)+["J","Q","K","A"]:
        for suit in 'spades','clubs','diamonds','hearts':
            deck.append(Card(suit=suit, number=num))
    deck.append(Card(suit='none', number='joker'))
    return deck

# create the dictionary to keep score: (bid class defined later)
def build_score_table():
    score_dict = {}
    for num in range(7, 11):
        for i, suit in enumerate(['spades','clubs','diamonds','hearts','notrump']):
            score_dict[Bid(num, suit)] = 140 + (20 * i) + 100 * (num - 7)
    return score_dict

# low bower helper function
def get_low_bower(trump):
    low_bower = {
                "hearts" : Card(suit = "diamonds", number = "J"),
                "diamonds" : Card(suit = "hearts", number = "J"),
                "spades" : Card(suit = "clubs", number = "J"),
                "clubs" : Card(suit = "spades", number = "J"),
                "notrump" : None,
                }

    try:
        return low_bower[trump]
    except KeyError:
        import sys
        print "invalid suit in get_low_bower"
        sys.exit()


# the game class
class Game(object):
    def __init__(self):
        self.score_table = build_score_table()
        self.deck = build_deck()
        self.score = [0, 0]
        self.trick_score = [0, 0]
        self.dealer = 4
        self.high_bid = False
        self.bid_winner = False
    
    def shuffle_deal(self, handsize = 10):
        import random
        random.shuffle(self.deck)
        self.hands = {}
        hand_names = [str(i) for i in range(1,5)] + ['kitty']
        for i, hand in enumerate(hand_names):
            self.hands[hand] = self.deck[i*handsize:(i+1)*handsize]
    
    def get_high_bid(self):
        first_bidder = self.dealer+1
        players = [str(get_player(x)) for x in range(first_bidder, first_bidder+4)]
        bid_winner = 0
    
        current_bid = Bid(0,'spades')
        for p in players:
            print "\nPlayer", p, "- here is your hand.  It's your bid.\n" 
            self.hands[p].sort()
            for c in self.hands[p]:
                print c
            player_p_bid = False
            while not player_p_bid:
                bid_input = raw_input("\nWhat would you like to bid? ")
                player_p_bid = validate_bid(self, bid_input, current_bid)
            if player_p_bid.number != 0:
                current_bid = player_p_bid
                bid_winner = p
    
        self.high_bid = current_bid
        self.bid_winner = bid_winner
    
     
    def check_winning_bid(self):
        if self.high_bid.number == 0 or self.high_bid.number == 6:
            self.dealer += 1
            if self.high_bid.number == 0:
                message = "everyone has passed. deal passes to player " + str(get_player(self.dealer))
            else:
                message = "house rules: we don't play 6 bids. deal passes to player "+str(get_player(self.dealer))
            return True, message
        else: 
            return False, None
    
    
    def pick_up_kitty(self):
        print "\n"
        print "player",self.bid_winner, "wins the bid with", self.high_bid
        print "player",self.bid_winner, "- here is the kitty:"
    
        # sort hands and kitty with trump information:
        for k in self.hands.keys():
            if self.high_bid.suit != "notrump":
                for c in self.hands[k]:
                    if c.suit == self.high_bid.suit:
                        c.trump = True
                    else:  
                        if c == get_low_bower(self.high_bid.suit):
                            c.trump = True
                            c.lowBower = True
                        elif c.number == 'joker':
                            c.suit = self.high_bid.suit
            self.hands[k].sort()
    
        for c in self.hands['kitty']:
            print c
        print "and again, here is your hand:"
        for c in self.hands[str(self.bid_winner)]:
            print c
        new_hand = []
        newcard = 0
        print "\nof these 15 cards, choose the 10 you would like to keep."
        for newcard in range(10):
            prompt = "card "+str(newcard+1)+": "
            choose_from = self.hands[str(self.bid_winner)] + self.hands['kitty']
            new_hand.append(validate_card(self, prompt, choose_from, self.high_bid.suit, new_hand))
        new_hand.sort()
        self.hands[str(self.bid_winner)] = new_hand
    
    def play_tricks(self):
        lead_player = int(self.bid_winner)
        for trick in range(10):
            play_order = [str(get_player(x)) for x in range(lead_player, lead_player+4)]
            cards_played = []
            for p in play_order:
                print "player "+p+": it's your turn. Here is your hand: "
                for c in self.hands[p]:
                    print c
                valid_move = False
                while not valid_move:
                    selected_card = validate_card(self, "Which card would you like to play? ", self.hands[p], self.high_bid.suit, False)
                    valid_move = validate_move(selected_card, self.high_bid.suit, p, self.hands, cards_played)
                cards_played.append(selected_card)
                self.hands[p].remove(selected_card)

            contenders = [x for x in cards_played if x.suit==cards_played[0].suit or x.trump]
            winning_card = max(contenders)
            winning_player = int(play_order[cards_played.index(winning_card)])
            print "player", winning_player, "wins with", winning_card
            print "\n"
            
            # increment hand scores:
            if winning_player==1 or winning_player==3:
                self.trick_score[0] += 1
            else:
                self.trick_score[1] += 1
            
            # pass lead to winning player
            lead_player = winning_player
    
    def reset_trump(self):
        for c in self.deck:
            if c.number != 'joker':
                c.trump = False
                c.lowBower = False
            else:
                c.suit = 'none'
    
    def score_hand(self):
        if self.bid_winner == 1 or self.bid_winner == 3:
            if self.trick_score[0] >= self.high_bid.number:
                print "players 1 and 3 have made their bid!"
                self.score[0] += self.score_table[self.high_bid]
            else:
                print "players 1 and 3 have been set."
                self.score[0] -= self.score_table[self.high_bid]
        else:
            if self.trick_score[1] >= self.high_bid.number:
                print "players 2 and 4 have made their bid!"
                self.score[1] += self.score_table[self.high_bid]
            else:
                print "players 2 and 4 have been set."
                self.score[1] -= self.score_table[self.high_bid]
        self.trick_score = [0, 0]
    
    def print_score(self):
        print "Players 1 and 3 have",self.score[0],"points"
        print "Players 2 and 4 have",self.score[1],"points"
        if self.bid_winner:
            print "Player",self.bid_winner,"has won the bid, with",self.high_bid
        else:
            print "The bid has not yet been won."
        if self.trick_score == [0, 0]:
            print "No one has taken any tricks yet"
        else:
            print "This hand:"
            print "Players 1 and 3 have taken",self.trick_score[0],"tricks"
            print "Players 2 and 4 have taken",self.trick_score[1],"tricks"
    
    def print_trick(self):
        print "trick printing not yet implemented, but we can access it!"
    
    def end_game_message(self):
        if self.score[0] >= 500:
            print "players 1 and 3 win!"
        elif self.score[0] <= -500:
            print "players 2 and 4 win, because players 1 and 3 lose!"
        elif self.score[1] >= 500:
            print "players 2 and 4 win!"
        else:
            print "players 1 and 3 win, because players 2 and 4 lose!"
        print "thank you for playing!"    


#### the card and bid classes:
class Card(object):
    def __init__(self, suit, number, trump=False, lowBower=False):
        self.suit = suit
        self.number = number
        self.trump = trump
        self.lowBower = lowBower
        
    def __cmp__(self, other):
        if self.suit == other.suit and self.number == other.number:
            return 0
        elif self.number=="joker":
            return 1
        elif other.number=="joker":
            return -1
        elif self.trump and not other.trump:
            return 1
        elif not self.trump and other.trump:
            return -1
        elif self.trump and other.trump:
            if self.number == "J" and other.number == "J":
                if self.lowBower:
                    return -1 #other is the high bower
                else:
                    return 1 #other is the low bower
            else:
                numOrder = range(4,11)+["Q","K","A","J"]
                if numOrder.index(self.number) > numOrder.index(other.number):
                    return 1
                else:
                    return -1
        elif self.suit == other.suit:
            numOrder = range(4,11)+["J","Q","K","A"]
            if numOrder.index(self.number) > numOrder.index(other.number):
                return 1
            else:
                return -1
        else: 
            suitOrder = ['spades','clubs','diamonds','hearts','none']
            if suitOrder.index(self.suit) > suitOrder.index(other.suit):
                return 1
            else:
                return -1
                
    def __str__(self):
        if self.number == 'joker':
            return 'joker [trump]'
        else:
            shown = str(self.number)+" "+self.suit
            if self.trump:
                shown = shown+" [trump]"
            return shown
        
class Bid(object):
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
    
    def __cmp__(self, other):
        suitOrder = ['spades','clubs','diamonds','hearts','notrump']
        if self.suit == other.suit and self.number == other.number:
            return 0
        elif self.number > other.number:
            return 1
        elif other.number > self.number:
            return -1
        elif suitOrder.index(self.suit) > suitOrder.index(other.suit):
            return 1
        else:
            return -1
    
    def __str__(self):
        if self.number == 0:
            return 'pass'
        else:
            return str(self.number)+' '+self.suit
    
    def __hash__(self):
        return hash(str(self))

def get_player(x):
    while x > 4:
        x -= 4
    return x

#### the validators
def validate_bid(game, bid_input, current_bid):
    if bid_input == 'score':
        game.print_score()
        return False

    if bid_input == 'pass':
        return Bid(0, 'spades')
    
    else:
        bid_input = bid_input.split(' ')
        
        if len(bid_input) != 2 or bid_input[0] not in ['6','7','8','9','10'] or bid_input[1] not in ['spades','hearts','diamonds','clubs','notrump']:
            print "invalid bid!"
            return False
        else:
            bid_input = Bid(number=int(bid_input[0]), suit=bid_input[1])
            if bid_input <= current_bid:
                print "you must bid higher than the current bid ("+str(current_bid)+")"
                return False
            else:
                return bid_input

# helper function for choosing and playing cards:
def validate_card(game, message, hand, trump, new_hand):
    card = raw_input(message)
    
    if card == "score":
        game.print_score()
        message = "choose card: "
        theCard = validate_card(game, message, hand, trump, new_hand)
    
    card_values = ['4','5','6','7','8','9','10','J','Q','K','A']
    card_suits = ['spades','hearts','diamonds','clubs']
    
    if card == "joker":
        theCard = Card(suit=trump, number="joker", trump=True)
    
    else:
        card_val_and_suit = card.split(' ')
        
        if len(card_val_and_suit) != 2 or card_val_and_suit[0] not in card_values or card_val_and_suit[1] not in card_suits:
            message = "invalid card - try again: "
            theCard = validate_card(game, message, hand, trump, new_hand)
        else:
            card_value, card_suit = card_val_and_suit
            try:
                card_value = int(card_value)
            except ValueError: # face card
                pass
            theCard = Card(suit=card_suit, number=card_value, trump = (card_suit==trump) )
            if theCard == get_low_bower(trump):
                theCard.trump = True
                theCard.lowBower = True
        
    if theCard not in hand:
        message = "you don't have this card, please enter another card: "
        theCard = validate_card(game, message, hand, trump, new_hand)
        
    if new_hand:
        if theCard in new_hand:
            message = "you have already chosen this card, please choose a different one: "
            theCard = validate_card(game, message, hand, trump, new_hand)
        
    return theCard

# function to check whether you can actually play a card from your hand
def validate_move(selectedCard, trump, p, hands, cardsPlayed):
    # selectedCard must already be validated for hands[p]
    
    if cardsPlayed == []:
       return True

    else:
        if cardsPlayed[0] == get_low_bower(trump):
            ledSuit = trump
        else:
            ledSuit = cardsPlayed[0].suit

        suitsInHand = {c.suit for c in hands[p] if c != get_low_bower(trump)}
        if get_low_bower(trump) in hands[p]:
            suitsInHand.add(trump)

        if selectedCard.suit != ledSuit:
            if selectedCard == get_low_bower(trump) and ledSuit == trump:
               return True
            else:
                if ledSuit in suitsInHand:
                    print "Follow suit!"
                    return False
                else:
                    return True
        else:
            if selectedCard == get_low_bower(trump) and ledSuit in suitsInHand:
                print "Follow suit! (low bower is a trump card)"
                return False
            else:
                return True


#### FUNCTION TO PLAY GAME!
def play500():
    print "Welcome to python 500!\n\n"
    game = Game()
    
    while all(-500 < s < 500 for s in game.score):
        # shuffle and deal:
        game.shuffle_deal()
        print "player",get_player(game.dealer),"is dealing."
        
        # have players bid:
        print "bidding"
        game.get_high_bid()
        
        # check whether bid is high enough:
        print "checking bids"
        bid_failed, message = game.check_winning_bid()
        if bid_failed:
            print message
            game.high_bid = False
            game.bid_winner = False
            continue
        
        # have bid winner pick up the kitty:
        game.pick_up_kitty()
        
        # play tricks
        game.play_tricks()
        
        # calculate the score:
        game.score_hand(bid_winner)
        
        # reset trump and bids:
        game.reset_trump()
        game.high_bid = False
        game.bid_winner = False
        
        # pass deal
        game.dealer += 1
    
    end_game_message()



if __name__ == '__main__':
    play500()
    

    
    
    
    
    


