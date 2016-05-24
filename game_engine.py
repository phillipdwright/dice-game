import collections # used in register()
import itertools
from random import randrange # used in pick() and roll()
from termcolor import colored # used in print_die(); third-party package
import sys # used in print_die(), in "if __name__=='__main__':" and in sys.path.append(BASE_DIR)
import os

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
from wrapper import colors, faces
from cli import inquire
from ai_engine import continue_rolling

ODDS = (
    (0, 0, 0, 1, 1, 2), # Easy die
    (0, 1, 1, 2, 2, 2), # Hard die
    (0, 0, 1, 1, 2, 2), # Medium die
)
FULL_CAN = (6, 3, 4)


def register():
    """Returns a list of players based on user input

    Each entry in the *players* list is a list containing the following:
    Name | Wins | Points (game) | Points (turn) | Damage (turn) | Strategy
    """
    names = []
    players = []
    more_players = True
    
    # Ask for user input
    while more_players:
        
        # Get player's name
        name = input("Please enter player {}'s name: ".format(len(names) + 1))
        names.append(name)
        print('Welcome, {}! Good luck!'.format(name))
        
        # See if there are any more players
        more_players = inquire("Are there any other players?")
    
    # Create the players list
    cnt = collections.Counter()
    for name in names:
        cnt[name] += 1
    for name in cnt:
        if cnt[name] == 1:
            players.append([name, 0, 0, 0, 0, 0])
        else:
            for i in range(cnt[name]):
                players.append([name + str(i + 1), 0, 0, 0, 0, 0])
    
    return players

def pick(can, rerolls=[0, 0, 0]):
    """Selects the dice for a roll
    
    *can* is the list representing the can being used this turn. This will be
    updated after the selection is made with the new totals of dice of each
    color. *rerolls* is a list representing the number of dice being rerolled
    in each color. The function returns a list of dice, where each entry is
    the number of dice of a color.
    """
    dice = rerolls
    to_pick = 3 - sum(rerolls)
    
    # If there aren't enough dice to pick, reset the can
    # TODO: Make refill_can() ?
    if to_pick > sum(can):
        # Put all the dice back in the can except those being rerolled
        # TODO: Don't put the shotguns back!
        #can = [x - y - z for x, y, z in zip(FULL_CAN, rerolls, damage)]
        can = [x - y for x, y in zip(FULL_CAN, rerolls)]
    
    # Pick a set of dice
    for die in range(to_pick):
        # Pick a die at random from those remaining in the can
        result = randrange(sum(can))
        
        # Increment *dice* and decrement *can* for the color that was picked
        if result < can[0]:
            dice[0] += 1
            can[0] -= 1
        elif result < can[0] + can[1]:
            dice[1] += 1
            can[1] -= 1
        else:
            dice[2] += 1
            can[2] -= 1
    
    return dice

def roll(dice, can):
    """Rolls dice and returns results
    
    *dice* is a list whose values represent the number of dice of each color
    that are being rolled. The function returns a list of dice, each entry of
    which represents the color and the result of that die's roll.
    """
    
    results = []
    
    # Go color by color and roll the number of dice available in that color
    for color, die_qty in enumerate(dice):
        # Roll each die of this color and append the roll result to *results*
        for die in range(die_qty):
            result = ODDS[color][randrange(6)]
            results.append([color, result])
            
    # TODO: Add can refiller here
    return results

def turn(player, players, lastround, usestrategy=0):
    """Take a turn
    
    *player* is the player taking his turn. This function will take this
    player's input and roll based on his selections, reporting totals after
    each roll. At the end of the player's turn, his number of brains for this
    game is updated.
    
    If *usestrategy* is greater than zero, use the indicated strategy to make
    decisions rather than prompting.
    """
    # Fill up the can
    can = list(FULL_CAN)
    # Set the player's turn scores to 0
    player[3] = player[4] = 0
    # Roll at least once!
    keep_rolling = True
    rolls = 0
    # Pick all three dice from the can on the first roll
    rerolls = [0, 0, 0]
    
    # Start playing!
    if usestrategy == 0:
        input('Ok, {}, Hit [Enter] to make your first roll!'.format(player[0]))
    
    # Keep rolling until the player busts or chooses to stop
    while keep_rolling:
    
        # Make a roll
        dice = pick(can, rerolls)
        results = roll(dice, can)
        
        # Count the dice rolled
        rerolls = [0, 0, 0]
        for die in results:
            if die[1] == 0:
                player[3] += 1
            elif die[1] == 1:
                rerolls[die[0]] += 1
            else:
                player[4] += 1
        
        # Display results of this roll and totals for this turn
        print('Results of this roll:')
        for die in results:
            print_die(die)
        print('Total {} points this turn: {}'.format(faces[0], player[3]))
        print('Total {} damage this turn: {}'.format(faces[2], player[4]))
        
        if player[4] >= 3: # The player busts
            player[3] = 0
            keep_rolling = False
            print('Sorry! You busted!')
            
        else:
            total = player[2] + player[3]
            msg = 'If you stop now, you will have {} {} points.'
            print(msg.format(total, faces[0]))
            points = player[3]
            damage = player[4]
            if usestrategy == 0:
                get_advice = inquire('Get advice?')
                while get_advice:
                    msg = [
                        '\nSelect the strategy to employ:',
                        '==================================',
                        '1 - SJG dumb strategy',
                        '2 - SJG smart strategy',
                        '3 - Cook/Taylor short strategy',
                        '4 - Cook/Taylor long strategy',
                        '\nWhich strategy would you like to check? '
                        ]
                    strategy = input('\n'.join(msg))
                    while strategy not in ['1', '2', '3', '4']:
                        print('Please enter a number from 1 to 4.')
                        strategy = input('\n'.join(msg))
                    
                    if continue_rolling(can, rerolls, points, damage, int(strategy), player, players, lastround):
                        print('Strategy {} suggests that you keep rolling!'.format(strategy))
                    else:
                        print('Strategy {} suggests that you stay!'.format(strategy))
                    get_advice = inquire('Want to check another strategy?')
            
                keep_rolling = inquire('Keep rolling?')
            else:
                keep_rolling = continue_rolling(can, rerolls, points, damage, int(usestrategy), player, players, lastround)
            if keep_rolling:
                print('Ok, rolling again!')
            else:
                print('Ok, stopping and moving on to the next player!')
    
    # Tally points
    player[2] += player[3]

def print_die(die):
    if sys.platform.startswith('win'):
        print('{}: {}'.format(colors[die[0]], faces[die[1]]))
    else:
        print(colored(faces[die[1]],colors[die[0]]))

def main():
    # Register the players
    players = register()
    
    # Add command-line arguments as strategies for the players!
    # for i in range(1,1+min(len(sys.argv)-1,len(players))):
    #    players[i-1][5] = sys.argv[i]
    for argument, player in zip(sys.argv[1:], players):
        player[5] = argument
    
    # Start the game
    end_game = False
    for game_round in itertools.count(1):
        
        # Start the round
        print('Round {}!'.format(game_round))
        
        #Let each player take a turn
        for player in players:
            turn(player, players, end_game, player[5])
            
            # If a player reaches 13, set the endgame strategy into effect
            if player[2] >= 13:
                end_game = True  # This should go here, no?
                msg = '{} has {} {} points! Last round!'
                print(msg.format(player[0], player[2], faces[0]))
        
        # Rank the players
        scores = [player[2] for player in players]
        scores.sort(reverse=True
        
        # If a player reaches the goal score and is alone at the top, he wins
        if scores[0] >= 13:
            # end_game = True  # Moved to earlier in the code
            if scores[1] != scores[0]:
                break
    
    print('Game over!  The game finished in {} rounds.'.format(game_round))
    for player in players:
        print('{}: {} points'.format(player[0], player[2]))
        
if __name__ == '__main__':
    import sys
    if sys.version.startswith('2'):
        input = raw_input
    main()

