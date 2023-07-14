__author__ = "Adam A. Smith"
__license__ = "MIT"
__date__ = "September 2019"

import sys
import random
from functools import partial

DEFAULT_AI_FILE = "connect4player"
DEFAULT_AI_LEVEL = 4

# ANSI ESCAPE SEQUENCES TO MAKE ASCII MODE IN COLOR--MAY NOT ALWAYS WORK
P1_ESCAPE = "\33[91m\33[1m"
P2_ESCAPE = "\33[34m\33[1m"
END_ESCAPE = "\33[0m"
BOARD_ESCAPE = "\33[90m"

################################################################################
# HUMAN PLAYER CLASS
################################################################################
class HumanPlayer:
    pass
################################################################################
# FUNCTIONS
################################################################################

def load_player(player_id, module_name = None, level = 1):
    """
    Load up a ComputerPlayer class from the given module. A module of None means 
    a human player.
    """
    class_name = "Player" +str(player_id)+ "Class"

    # if module_name is None, that means we have a human player
    if module_name == None:
        exec(class_name + " = HumanPlayer", globals())
        return HumanPlayer()

    # look for the file specified, see if we have a proper ComputerPlayer
    try:
        exec("from " +module_name+ " import ComputerPlayer as " +class_name, globals())
    except ImportError:
        print("Could not find ComputerPlayer in file \"" +module_name+ ".py\". Exiting.", file=sys.stderr)
        sys.exit(1)

    # make a local pointer to the ComputerPlayer class, and return a new instance
    exec("Player = " +class_name)
    return locals()["Player"](player_id, level)

def parse_command_line_args(args):
    """
    Search the command-line args for the various options (see the help function).
    """
    print(args)
    # print help message
    if "-h" in args or "--help" in args: print_help = True
    else: print_help = False

    # AI file
    if "-f" in args: ai_file = args[args.index("-f") + 1].rstrip(".py")
    else: ai_file = DEFAULT_AI_FILE
    
    # number of players
    if "-0" in args: players = (ai_file, ai_file)
    elif "-2" in args: players = (None, None)
    else: players = (None, ai_file)

    # level of players
    if "-l" in args:
        levels = args[args.index("-l") + 1].split(',')
        print(levels)
        if len(levels) == 1: levels = (int(levels[0]), int(levels[0]))
        else: levels = (int(levels[0]), int(levels[1]))
    else: levels = (DEFAULT_AI_LEVEL, DEFAULT_AI_LEVEL)
    print(levels)

    # colors
    if "-c" in args:
        color_string = args[args.index("-c") + 1]
        colors = color_string.split(',')
    else: colors = None
        
    # manually turn off the graphics
    if "-n" in args or "--nographics" in args: graphics_wanted = False
    else: graphics_wanted = True
    
    return (print_help, players, levels, colors, graphics_wanted)

def print_help(output = sys.stderr):
    """
    Print out a help screen for the user (probably to stderr).
    """
    
    print("Usage: python3 " +sys.argv[0]+ " <options>", file=output)
    print("Options include:", file=output)
    print("\t-0\t0-player (computer-v-computer)", file=output)
    print("\t-1\t1-player (human-v-computer)", file=output)
    print("\t-2\t2-player (human-v-human)", file=output)
    print("\t-c\tuse colors (RRGGBB,RRGGBB)", file=output)
    print("\t-f\tuse a non-standard AI file", file=output)
    print("\t-h\tprint this help", file=output)
    print("\t-l\tset AI level (#,#)", file=output)
    print("\t-n\tnon-graphics mode", file=output)

def play_game_in_ascii(player1, player2):
    """
    ASCII game. Boring. May not implement this.
    """
    rack = make_rack()
    players = (None, player1, player2)

    current_player = random.randrange(1,3)
    winning_quartet = None

    while not winning_quartet:
        current_player = 3 - current_player
        if current_player == 1: player_escape = P1_ESCAPE
        else: player_escape = P2_ESCAPE

        # print out rack state
        print(player_escape + "Player " + str(current_player) + ":" + END_ESCAPE)
        print_rack(rack)

        if not exists_legal_move(rack): break

        if type(players[current_player]) == HumanPlayer: move = do_human_turn(rack, players[current_player])
        else: move = do_computer_turn(rack, players[current_player])
        print()
        place_disc(rack, current_player, move)
        winning_quartet = find_win(rack, move)

    print_rack(rack)
    if winning_quartet:
        print(player_escape + "Player " + str(current_player)+ " wins!!!" +END_ESCAPE)
        
    else:
        print("It was a tie!")

def do_human_turn(rack, player):
    while True:
        print("Your move? ", end="")
        user_input = input()
        try:
            column = int(user_input) - 1 # -1 for 0/1 based counting
        except ValueError:
            column = -1

        if column >= 0 and column < len(rack) and rack[column][-1] == 0: return column
        else: print("INVALID")
    
        
def do_computer_turn(rack, player):
    # pass the player a tuple (so it can't mess with the original rack)
    rack_tuple = tuple([tuple(column) for column in rack])
    move = player.pick_move(rack_tuple)

    # checks to make sure that the AI has made a valid move
    assert move >=0 and move < len(rack)
    assert rack[move][-1] == 0

    return move
    
def place_disc(rack, player_number, column):
    # figure out where the thing drops to
    row = 0
    while rack[column][row] != 0: row += 1
    rack[column][row] = player_number
        
# return True if there exists at least 1 valid move
def exists_legal_move(rack):
    for c in range(len(rack)):
        if rack[c][-1] == 0: return True
    return False

def make_rack(num_columns = 7, num_rows = 6):
    """
    Create the basic rack object. (Just a list, really.)
    """
    rack = [[0 for x in range(num_rows)] for y in range(num_columns)]
    return rack

def print_rack(rack):
    # print numbers on top (doesn't work with 100 or more columns)
    if len(rack) >= 10:
        print("                  ", end="")
        for i in range(9, len(rack)): print(str((i+1)//10), end=" ")
        print()

    for i in range(len(rack)): print(str((i+1)%10), end=" ")
    print()

    # print the rack itself
    for r in range(len(rack[0])-1, -1, -1):
        for c in range(len(rack)):
            if rack[c][r] == 1: print(P1_ESCAPE + "X" + END_ESCAPE, end=" ")
            elif rack[c][r] == 2: print(P2_ESCAPE + "O" + END_ESCAPE, end=" ")
            else: print(BOARD_ESCAPE + "." + END_ESCAPE, end=" ")
        print()

def find_win(rack, column = None):
    # if no column explicitly given, do them all recursively
    if column == None:
        for c in range(len(rack)):
            win = find_win(c)
            if win: return win
        return None

    num_cols = len(rack)
    num_rows = len(rack[0])
    
    # figure out where the disc was dropped
    row = num_rows - 1
    while row > -1 and rack[column][row] == 0: row -= 1
    if row == -1: return None            

    player = rack[column][row]

    # check for vertical win
    if row >= 3:
        subrack = rack[column]
        if subrack[row] == subrack[row-1] and subrack[row] == subrack[row-2] and subrack[row] == subrack[row-3]:
            return ((column, row-3), (column, row))

    # check for horizontal win
    c = d = column
    while c > 0 and rack[c-1][row] == player: c -= 1
    while d < (num_cols-1) and rack[d+1][row] == player: d += 1
    if (d-c) >= 3: return ((c, row), (d, row))

    # check for forward-diagonal win
    c = d = column
    r = s = row
    while c > 0 and r > 0 and rack[c-1][r-1] == player: c -= 1; r -= 1
    while d < (num_cols-1) and s < (num_rows-1) and rack[d+1][s+1] == player: d += 1; s+=1
    if (d-c) >= 3: return ((c, r), (d, s))
    
    # check for backward-diagonal win
    c = d = column
    r = s = row
    while c > 0 and r < (num_rows-1) and rack[c-1][r+1] == player: c -= 1; r += 1
    while d < (num_cols-1) and s > 0 and rack[d+1][s-1] == player: d += 1; s-=1
    if (d-c) >= 3: return ((c, r), (d, s))

    # no win detected--return None
    return None
    

################################################################################
# MAIN(): PARSE COMMAND LINE & START PLAYING
################################################################################

if __name__ == "__main__":

    # look at the command line for what the user wants
    do_print_help, player_files, levels, colors, graphics_wanted = parse_command_line_args(sys.argv[1:])
    
    # help message for user, if -h or --help
    if do_print_help:
        print_help()
        sys.exit(1)

    # load up the player classes
    players = (load_player(1, player_files[0], levels[0]), load_player(2, player_files[1], levels[1]))

    play_game_in_ascii(players[0], players[1])
        #print("Sorry--this game is not implemented yet in ASCII.", file=sys.stderr)
