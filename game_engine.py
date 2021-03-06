import collections # used in register()
import itertools # used in main()
from random import randrange # used in pick() and roll()
import termcolor # used in print_die(); third-party package
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
    the number of dice of a color, and the can from which the dice were picked.
    """
    dice = rerolls
    to_pick = 3 - sum(rerolls)
    
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
    
    return dice, can

def roll(dice):
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
    # Pick all three dice from the can on the first roll, set good to null
    rerolls = [0, 0, 0]
    good_dice = [0, 0, 0]
    
    # Start playing!
    if usestrategy == 0:
        input('Ok, {}, Hit [Enter] to make your first roll!'.format(player[0]))
    
    # Keep rolling until the player busts or chooses to stop
    while keep_rolling:
    
        # Make a roll
        dice, can = pick(can, rerolls)
        results = roll(dice)

        # Count the dice rolled
        rerolls = [0, 0, 0]
        for die in results:
            if die[1] == 0:
                player[3] += 1
                good_dice[die[0]] += 1
            elif die[1] == 1:
                rerolls[die[0]] += 1
            else:
                player[4] += 1
        
        # Put the good dice back in the can if it needs to be refilled
        if (sum(can) + sum(rerolls) < 3):
            can = refill(can, good_dice)
            good_dice = [0, 0, 0]
        
        # Display results of this roll and totals for this turn
        if usestrategy == 0:
            print('Results of this roll:')
            for die in results:
                print_die(die)
            print('Total {} points this turn: {}'.format(faces[0], player[3]))
            print('Total {} damage this turn: {}'.format(faces[2], player[4]))
        
        # The player busts if this roll puts him at or over 3 damage
        if player[4] >= 3: # The player busts
            player[3] = 0
            keep_rolling = False
            if usestrategy == 0:
                print('Sorry! You busted!')
        
        # If the player has not yet reached 3 damage, he decides whether to
        #  roll again.
        else:
            total = player[2] + player[3]
            points = player[3]
            damage = player[4]
            
            # Display the player's turn status and let him choose whether to
            #  continue rolling.
            if usestrategy == 0:
                
                msg = 'If you stop now, you will have {} {} points.'
                print(msg.format(total, faces[0]))
                
                # Allow the user to consult a strategy.
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
                    
                    # Display the strategy's recommendation
                    if continue_rolling(can, rerolls, points, damage, int(strategy), player, players, lastround):
                        print('Strategy {} suggests that you keep rolling!'.format(strategy))
                    else:
                        print('Strategy {} suggests that you stay!'.format(strategy))
                    
                    # Allow the user to consult another strategy
                    get_advice = inquire('Want to check another strategy?')
                    
                # Prompt the user to decide whether to keep rolling
                keep_rolling = inquire('Keep rolling?')
                
                if keep_rolling:
                    print('Ok, rolling again!')
                else:
                    print('Ok, stopping and moving on to the next player!')
            
            else:
                
                # Consult the appropriate strategy to decide whether to keep
                #  rolling.
                keep_rolling = continue_rolling(can, rerolls, points, damage, player[5], player, players, lastround)

    
    # Tally points
    player[2] += player[3]


def print_die(die):
    """Print a die to the terminal or command line
    
    Windows does not support colored text in the command line, so this
    function will print 
    """
    if sys.platform.startswith('win'):
        print('{}: {}'.format(colors[die[0]], faces[die[1]]))
    else:
        print(termcolor.colored(faces[die[1]],colors[die[0]]))


def refill(can, good_dice = [0, 0, 0]):
    # Put all your point dice back in the can and return it
    return [x + y for x, y in zip(can, good_dice)]


def main(games = 1, strats = []):
    # Register the players
    players = register()
    
    # Add command-line arguments as strategies for the players!
    for argument, player in zip(strats, players):
        player[5] = argument
    
    for game in range(games):
        # Start the game
        end_game = False
        for game_round in itertools.count(1):
            
            # Start the round
            print('**** Round {}!'.format(game_round))
            
            #Let each player take a turn
            for player in players:
                turn(player, players, end_game, player[5])
                
                # If a player reaches 13, set the endgame strategy into effect
                if player[2] >= 13:
                    end_game = True
                    msg = '{} has {} {} points! Last round!'
                    print(msg.format(player[0], player[2], faces[0]))
            
            # Rank the players
            scores = [player[2] for player in players]
            
            # If a player has the highest score,...
            high_score = max(scores)
            # ...and it is at least the goal score,...
            if high_score >= 13:
                # ...and no one else has as many points as him,...
                if scores.count(high_score) == 1:
                    # ...he wins!  End the game.
                    break
        
        # Announce the winner
        print('********* Game {} is over!  The game finished in {} rounds.'.format(game + 1, game_round))
        for player in players:
            if player[2] == high_score:
                player[1] += 1
                winner = player[0]
            print('{} with Strategy {}: {} points'.format(player[0], player[5], player[2]))
            player[2] = 0
        print(winner, 'is the winner!  Huzzah!')
    
    print('********* We are done playing!')
    for player in players:
        print('{} won {} games with Strategy {}'.format(player[0], player[1], player[5]))
        
if __name__ == '__main__':
    import sys
    if sys.version.startswith('2'):
        input = raw_input
    
    # If arguments are passed after the filename, pass the first argument as
    #  the number of games, and pass the remaining arguments as strategies to
    #  be used
    if len(sys.argv) > 1:
        main(int(sys.argv[1]), [int(arg) for arg in sys.argv[2:]])
        
    # Otherwise, use the default values
    else:
        main()

