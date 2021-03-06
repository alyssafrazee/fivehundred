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
        self.cards_played = []
    
    def shuffle_deal(self, handsize = 10):
        import random
        random.shuffle(self.deck)
        self.hands = {}
        hand_names = [str(i) for i in range(1,5)] + ['kitty']
        for i, hand in enumerate(hand_names):
            self.hands[hand] = self.deck[i*handsize:(i+1)*handsize]
    
    def validate_bid(self, bid_input, current_bid):
        if bid_input == 'score':
            self.print_score()
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
                player_p_bid = self.validate_bid(bid_input, current_bid)
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

    def validate_card(self, card, p, choosing_kitty, new_hand):
       
        trump = self.high_bid.suit
                    
        if card == "score" or card == "trick":
            if card == "score":
                self.print_score()
            else:
                self.print_trick()
            return False
        
        elif card == "joker":
            chosen_card = Card(suit=trump, number="joker", trump=True)
        
        else:
            card_values = ['4','5','6','7','8','9','10','J','Q','K','A']
            card_suits = ['spades','hearts','diamonds','clubs']
            card_val_and_suit = card.split(' ')

            if len(card_val_and_suit) != 2 or card_val_and_suit[0] not in card_values or card_val_and_suit[1] not in card_suits:
                print "invalid card - try again: "
                return False
            else:
                card_value, card_suit = card_val_and_suit
                try:
                    card_value = int(card_value)
                except ValueError: # face card
                    pass
                chosen_card = Card(suit=card_suit, number=card_value, trump = (card_suit==trump) )
                if chosen_card == get_low_bower(trump):
                    chosen_card.trump = True
                    chosen_card.lowBower = True
        
        if chosen_card not in self.hands[p]:
            if not choosing_kitty:
                print "you don't have this card."
                return False
            else:
                if chosen_card not in self.hands['kitty']:
                    print "you don't have this card."
                    return False
        
        if choosing_kitty and chosen_card in new_hand:
            print "you have already chosen this card, please choose a different one: "
            return False
        
        if choosing_kitty:
            return chosen_card
        
        else:
            # if you get to this point, you're playing a trick and have the card.
            if self.cards_played == []:
                return chosen_card
            
            else:
                if self.cards_played[0] == get_low_bower(trump):
                    led_suit = trump
                else:
                    led_suit = self.cards_played[0].suit
    
                suits_in_hand = {c.suit for c in self.hands[p] if c != get_low_bower(trump)}
                if get_low_bower(trump) in self.hands[p]:
                    suits_in_hand.add(trump)

                if chosen_card.suit != led_suit:
                    if chosen_card == get_low_bower(trump) and led_suit == trump:
                        return chosen_card
                    else:
                        if led_suit in suits_in_hand:
                            print "Follow suit!"
                            return False
                        else:
                            return chosen_card
                else:
                    if chosen_card == get_low_bower(trump) and led_suit in suits_in_hand:
                        print "Follow suit! (low bower is a trump card)"
                        return False
                    else:
                        return chosen_card
    
    def pick_up_kitty(self):
        print "\n"
        print "player",self.bid_winner, "wins the bid with", self.high_bid
        print "\nplayer",self.bid_winner, "- here is the kitty: \n"
    
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
        print "\nand again, here is your hand:"
        for c in self.hands[str(self.bid_winner)]:
            print c
        new_hand = []
        newcard = 0
        print "\nof these 15 cards, choose the 10 you would like to keep. \n"
        for newcard in range(10):
            prompt = "card "+str(newcard+1)+": "
            selected_card = False
            while not selected_card:
                card_input = raw_input(prompt)
                selected_card = self.validate_card(card_input, str(self.bid_winner), True, new_hand)
            new_hand.append(selected_card)
        new_hand.sort()
        self.hands[str(self.bid_winner)] = new_hand
    
    def play_tricks(self):
        lead_player = int(self.bid_winner)
        for trick in range(10):
            play_order = [str(get_player(x)) for x in range(lead_player, lead_player+4)]
            for p in play_order:
                print "\nplayer "+p+": it's your turn. Here is your hand: "
                for c in self.hands[p]:
                    print c
                selected_card = False
                valid_move = False
                while not selected_card:
                    card_input = raw_input("\nWhich card would you like to play? ")
                    selected_card = self.validate_card(card_input, p, False, None)
                self.cards_played.append(selected_card)
                self.hands[p].remove(selected_card)

            contenders = [x for x in self.cards_played if x.suit==self.cards_played[0].suit or x.trump]
            winning_card = max(contenders)
            winning_player = int(play_order[self.cards_played.index(winning_card)])
            print "\nplayer", winning_player, "wins with", winning_card,"\n"
            
            # increment hand scores:
            if winning_player==1 or winning_player==3:
                self.trick_score[0] += 1
            else:
                self.trick_score[1] += 1
            
            # clear the table:
            self.cards_played = []
            
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
        if self.bid_winner == "1" or self.bid_winner == "3":
            if self.trick_score[0] >= self.high_bid.number:
                print "players 1 and 3 have made their bid!"
                self.score[0] += self.score_table[self.high_bid]
            else:
                print "players 1 and 3 have been set."
                self.score[0] -= self.score_table[self.high_bid]
            self.score[1] += 10*self.trick_score[1]
        else:
            if self.trick_score[1] >= self.high_bid.number:
                print "players 2 and 4 have made their bid!"
                self.score[1] += self.score_table[self.high_bid]
            else:
                print "players 2 and 4 have been set."
                self.score[1] -= self.score_table[self.high_bid]
            self.score[0] += 10*self.trick_score[0]
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
        if self.cards_played == []:
            print "\nno cards have been played on this trick yet"
        elif len(self.cards_played)==1:
            print "\n",self.cards_played[0], "was led.  It's your turn.  Your partner has not yet played."
        elif len(self.cards_played)==2:
            print "\nYour partner led",self.cards_played[0]
            print "Opposing team played", self.cards_played[1]
        else:
            print "\nOpposing team led",self.cards_played[0]
            print "Your partner played",self.cards_played[1]
            print "Opposing team played",self.cards_played[2]
    
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

# the card and bid classes:
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


# tiny helper player ID function
def get_player(x):
    while x > 4:
        x -= 4
    return x
    

#### FUNCTION TO PLAY GAME!
def play500():
    print "Welcome to python 500!\n\n"
    game = Game()
    
    while all(-500 < s < 500 for s in game.score):
        # shuffle and deal:
        game.shuffle_deal()
        print "player",get_player(game.dealer),"is dealing."
        
        # have players bid:
        game.get_high_bid()
        
        # check whether bid is high enough:
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
        game.score_hand()
        
        # reset trump and bids:
        game.reset_trump()
        game.high_bid = False
        game.bid_winner = False
        
        # pass deal
        game.dealer += 1
    
    end_game_message()



if __name__ == '__main__':
    play500()
    

    
    
    
    
    

