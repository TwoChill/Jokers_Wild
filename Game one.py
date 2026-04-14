from pynput import keyboard
import copy
import platform
import random
import time
import os

class bcolors:
    BLUE = '\033[95m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    BLACK = '\033[30m'
    GREY = '\33[90m'
    BLINK1 = '\33[5m'
    BLINK2 = '\33[6m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Cards(object):
    def __init__(self, NR_OF_CARDS, suits, all_card_combinations):
        self.NR_OF_CARDS = NR_OF_CARDS
        self.MARGIN_BETWEEN = ' ' * 2
        self.MARGIN_LEFT = ' ' * 2
        self.MARGIN_HITME = ' ' * ((len(payout[payout.find('┏'):payout.find('┓')])) // 6)
        self.suits = suits
        self.set_cards_suits = set()
        self.all_card_combinations = all_card_combinations

    def create_cards(self, NR_OF_CARDS):
        """Create Cards
        Creates card combinations and returns ASCII-type cards based on the given index
        """
        card_index = [i for i in range(NR_OF_CARDS)]
        front_ascii_cards = {}
        set_cards_suits = set()

        for line_index in range(NR_OF_CARDS):
            while len(set_cards_suits) < NR_OF_CARDS:
                card_nr = random.randint(1, 14)
                suit_sym = random.randint(0, 3)

                if (card_nr, suit_sym) in set_cards_suits:
                    continue

                set_cards_suits.add((card_nr, suit_sym))
                card_lines = self.generate_card_lines(card_nr, suit_sym)
                front_ascii_cards[card_index[line_index]] = card_lines

        return front_ascii_cards, set_cards_suits

    def generate_card_lines(self, card_nr, suit_sym):
        """Generate the lines for a single card"""
        lines = []
        space = ' ' * 4

        if card_nr == 1:
            card_nr = 'A'
        elif card_nr == 11:
            card_nr = 'J'
        elif card_nr == 12:
            card_nr = 'Q'
        elif card_nr == 13:
            card_nr = 'K'
        elif card_nr == 14:
            card_nr = 'Joker'
            suit_sym = 4
            space = ''

        for i in range(9):
            if card_nr == 'Joker':
                if i == 1 or i == 7:
                    line = '║{}    {}║'.format(card_nr, space)
                elif i == 4:
                    line = '║    {}    ║'.format(list(self.suits.values())[suit_sym].upper())
                else:
                    line = '║         ║'
            else:
                if i == 1 or i == 7:
                    line = '║{}    {}║'.format(card_nr, space)
                elif i == 4:
                    line = '║    {}    ║'.format(list(self.suits.values())[suit_sym].upper())
                else:
                    line = '║         ║'
            lines.append('╔═════════╗' if i == 0 else line)
        lines.append('╚═════════╝')
        return lines


class Dealer(Cards):
    """Everything related to dealing cards"""

    def __init__(self, NR_OF_CARDS, suits, all_card_combinations):
        super().__init__(NR_OF_CARDS, suits, all_card_combinations)
        self.DoubleDown = False
        self.winning_multipliers = {
            "Five of a Kind": 100,
            "Royal Flush": 50,
            "Straight Flush": 30,
            "Four of a Kind": 20,
            "Full House": 10,
            "Flush": 8,
            "Straight": 7,
            "Three of a Kind": 5,
            "Two Pair": 3,
            "One Pair": 1
        }

    def colorize_card(self, card):
        color = bcolors.RED if any(suit in card for suit in ['Hearts', 'Diamonds']) else bcolors.GREY
        if 'Joker' in card and 'mJoker' not in card:
            color = bcolors.ORANGE
        return f"{color}{card}{bcolors.ENDC}"

    def shuffles(self, front_ascii_cards):
        colored_cards = [
            "".join([self.colorize_card(card_part) for card_part in
                     [ascii_line[i:i + 22] for i in range(0, len(ascii_line), 22)] if card_part])
            for ascii_line in front_ascii_cards.values()]
        return colored_cards

    def deals_cards(self, the_flop):
        hit_me = f"""
{self.MARGIN_HITME}{bcolors.RED}
██╗  ██╗██╗████████╗    ███╗   ███╗███████╗
██║  ██║██║╚══██╔══╝    ████╗ ████║██╔════╝
███████║██║   ██║       ██╔████╔██║█████╗
██╔══██║██║   ██║       ██║╚██╔╝██║██╔══╝
██║  ██║██║   ██║       ██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝╚═╝   ╚═╝       ╚═╝     ╚═╝╚══════╝
{bcolors.ENDC}
{self.MARGIN_HITME}
{self.MARGIN_HITME}
{self.MARGIN_HITME}
{self.MARGIN_HITME}"""

        while the_flop:
            os.system('clear')
            sys_clear(OnScreen=hit_me)
            hit_me = f"{hit_me[:133]}{the_flop[0][:84]}{hit_me[133 + len(the_flop[0][:84]):]}"
            the_flop[0] = the_flop[0][84:]
            time.sleep(0.1)

        os.system('clear')
        sys_clear(OnScreen=hit_me)


class Select(Cards):

    def __init__(self, the_flop, NR_OF_CARDS, suits, all_card_combinations):
        Cards.__init__(self, NR_OF_CARDS, suits, all_card_combinations)
        self.the_flop = the_flop
        self.the_flop_copy = copy.deepcopy(the_flop)

    def highlight_card(self, the_flop):
        global start_a, end_a, start_b, end_b, end_c, index_line, card_position
        start_a, end_a, start_b, end_b, end_c, index_line, card_position = 0, 11, 0, 1, 19, 0, 1

        while True:
            sys_clear(OnScreen=payout)
            # Inside the `highlight_card` method of the `Select` class
            for card_item in the_flop:
                if card_item[start_a:end_a] == self.the_flop[0][start_a:end_a]:
                    self.update_line(0, bcolors.BLUE)
                elif card_item[start_a:end_a] == self.the_flop[1][start_a:end_a]:
                    self.update_line(1, bcolors.GREEN)
                elif card_item[start_a:end_a] == self.the_flop[2][start_a:end_a]:
                    self.update_line(2, bcolors.ORANGE)
                elif card_item[start_a:end_a] == self.the_flop[3][start_a:end_a]:
                    self.update_line(3, bcolors.RED)
                elif card_item[start_a:end_a] == self.the_flop[4][start_a:end_a]:
                    self.update_line(4, bcolors.PURPLE)

            for card_item in self.the_flop:
                print(self.MARGIN_LEFT + card_item)  # Print the whole card item on a new line

            if card_position < self.NR_OF_CARDS:
                self.listen_for_keys(on_press)
            else:
                self.listen_for_keys(on_press)

    def update_line(self, line_index, color):
        line = self.the_flop_copy[line_index]
        start_a_idx = (start_a, end_a)
        start_b_idx = (start_b, end_b)
        end_c_idx = (end_c, end_c + 1)

        if line[start_a_idx[0]:start_a_idx[1]] == self.the_flop[line_index][start_a_idx[0]:start_a_idx[1]]:
            self.the_flop_copy.remove(self.the_flop_copy[line_index])
            updated_line = color + line[start_a_idx[0]:start_a_idx[1]] + bcolors.ENDC + line[end_c_idx[1]:]

            if card_position >= 2:
                updated_line = self.the_flop[line_index][:start_a_idx[0]] + updated_line

            self.the_flop_copy.insert(line_index, updated_line)

    def listen_for_keys(self, on_press):
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()


def on_press(key):
    global start_a, end_a, start_b, end_b, end_c, index_line, card_position

    if key == keyboard.Key.right and card_position <= 4:
        card_position += 1
        start_a, end_a = start_a + 13, end_a + 13
        start_b, end_b = start_b + 22, end_b + 22
        end_c += 22
        index_line = 0
    elif key == keyboard.Key.left and card_position >= 2:
        card_position -= 1
        start_a, end_a = start_a - 13, end_a - 13
        start_b, end_b = start_b - 22, end_b - 22
        end_c -= 22
        index_line = 0


def sys_clear(OnScreen=None):
    ''' Clears terminal screen for different OS's '''
    import os

    if 'ipad' in platform.platform().lower():
        import console
        console.clear()
    elif 'linux' or 'Darwin' in platform.platform().lower():
        os.system('cls' if os.name == 'nt' else 'clear')
    elif 'windows' in platform.platform().lower():
        os.system('cls')
    else:
        print(f"Sorry, OS: {platform.platform()} is not known to me yet.")

    if OnScreen is not None:
        print(f'{OnScreen}')


payout = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Payout ━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃\t\t\t\t\t\t\t\t  ┃
┃\tFive of a Kind\tx 100\t\tFlush\t\tx 7\t  ┃
┃ \tRoyal Flush\tx 50\t\tStraight\tx 5\t  ┃

┃ \tStraight Flush\tx 20\t\tThree of a Kind\tx 3\t  ┃
┃ \tFour of a Kind\tx 10\t\tTwo Pair\tx 2\t  ┃
┃ \tFull House\tx 8\t\tOne Pair\tx 1\t  ┃
┃\t\t\t\t\t\t\t\t  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
"""


if __name__ == "__main__":
    NR_OF_CARDS = 5
    card_nrs = [i for i in range(1, 15)]
    suits = {'Spades': '♠', 'Diamonds': '♦', 'Hearts': '♥', 'Clubs': '♣', 'Joker': '§'}
    suits.pop('Joker')
    all_card_combinations = {k: list(suits.keys()) for k in card_nrs}
    all_card_combinations[len(card_nrs) + 1] = ['Joker' for i in range(len(suits))]
    suits['Joker'] = '§'

    cards = Cards(NR_OF_CARDS, suits, all_card_combinations)
    dealer = Dealer(NR_OF_CARDS, suits, all_card_combinations)
    front_ascii_cards, set_cards_suits = cards.create_cards(NR_OF_CARDS)
    colored_cards = dealer.shuffles(cards.create_cards(NR_OF_CARDS)[0])
    player = Select(colored_cards, NR_OF_CARDS, suits, all_card_combinations)

    sys_clear(OnScreen=payout)
    player.highlight_card(player.the_flop_copy)