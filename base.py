try:
    from pynput import keyboard
except ImportError:
    print("Missing dependency: pynput. Run: pip install pynput")
    raise SystemExit(1)

import platform
import random
import time
import os
from collections import Counter

# Source: Idea Inspiration: https://codereview.stackexchange.com/questions/82103/ascii-fication-of-playing-cards

payout = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━ Joker's Wild ━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃\t\t\t\t\t\t\t\t  ┃
┃\tNatural Royal Flush\tx 800\t\t\t\t\t  ┃
┃\tFive of a Kind\tx 100\t\tFlush\t\tx 7\t  ┃
┃ \tRoyal Flush *\tx 50\t\tStraight\tx 5\t  ┃
┃ \tStraight Flush\tx 20\t\tThree of a Kind\tx 3\t  ┃
┃ \tFour of a Kind\tx 10\t\tTwo Pair\tx 2\t  ┃
┃ \tFull House\tx 8\t\tOne Pair\tx 1\t  ┃
┃\t\t\t\t  * with Joker\t\t\t  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
"""

# Suit symbols indexed 0=Spades, 1=Diamonds, 2=Hearts, 3=Clubs, 4=Joker #1, 5=Joker #2
_SUIT_SYMBOLS = ['♠', '♦', '♥', '♣', '§', '§']


class bcolors:
    BLUE   = '\033[94m'
    GREEN  = '\033[92m'
    ORANGE = '\033[93m'
    RED    = '\033[91m'
    GREY   = '\33[90m'
    ENDC   = '\033[0m'
    BOLD   = '\033[1m'
    UNDERLINE = '\033[4m'


def _value_str(value):
    mapping = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 14: 'Joker'}
    return mapping.get(value, str(value))


def evaluate_hand(hand):
    """Classify a 5-card poker hand. Joker (value=14) is wild.
    Returns (hand_name, multiplier).
    """
    joker_count = sum(1 for v, _ in hand if v == 14)
    regular     = [(v, s) for v, s in hand if v != 14]
    values      = [v for v, _ in regular]
    suits       = [s for _, s in regular]

    val_counts = Counter(values)
    counts = sorted(val_counts.values(), reverse=True)

    # Add wild jokers to the best grouping
    if joker_count:
        if counts:
            counts[0] += joker_count
        else:
            counts = [joker_count]

    top    = counts[0] if counts else 0
    second = counts[1] if len(counts) > 1 else 0

    # Flush: all non-joker cards share one suit, jokers fill the rest
    is_flush = len(set(suits)) <= 1 and (len(suits) + joker_count == 5)

    # Straight: works for both A-low (A=1) and A-high (A=14)
    def _straight_ok(vals, wilds):
        if not vals:
            return wilds >= 5
        unique = sorted(set(vals))
        span   = unique[-1] - unique[0]
        gaps   = span - (len(unique) - 1)
        return span <= 4 and gaps <= wilds

    def has_straight():
        if _straight_ok(values, joker_count):
            return True
        if 1 in values:
            high = [14 if v == 1 else v for v in values]
            return _straight_ok(high, joker_count)
        return False

    is_straight = has_straight()

    # Royal Flush: A-high straight flush (A, 10, J, Q, K)
    def is_royal():
        if not is_flush or not is_straight:
            return False
        if 1 not in values:
            return False
        non_ace_max = max((v for v in values if v != 1), default=0)
        return non_ace_max >= 10

    # Classify hand
    if top == 5:
        name = "Five of a Kind"
    elif is_flush and is_straight:
        if is_royal():
            name = "Natural Royal Flush" if joker_count == 0 else "Royal Flush"
        else:
            name = "Straight Flush"
    elif top == 4:
        name = "Four of a Kind"
    elif top == 3 and second == 2:
        name = "Full House"
    elif is_flush:
        name = "Flush"
    elif is_straight:
        name = "Straight"
    elif top == 3:
        name = "Three of a Kind"
    elif top == 2 and second == 2:
        name = "Two Pair"
    elif top == 2:
        name = "One Pair"
    else:
        name = "High Card"

    multipliers = {
        "Natural Royal Flush": 800,
        "Five of a Kind": 100, "Royal Flush": 50,  "Straight Flush": 20,
        "Four of a Kind": 10,  "Full House":   8,   "Flush":           7,
        "Straight":        5,  "Three of a Kind": 3, "Two Pair":        2,
        "One Pair":        1,  "High Card":     0,
    }
    return name, multipliers.get(name, 0)


class Cards:
    MARGIN_LEFT    = '  '
    MARGIN_BETWEEN = '  '

    def __init__(self, NR_OF_CARDS, suits):
        self.NR_OF_CARDS = NR_OF_CARDS
        self.suits = suits

    def create_cards(self, n, used_cards=None):
        """Draw n unique cards from the deck.
        Returns (front_ascii_cards, hand, used_cards).
          front_ascii_cards: {card_index: [9 line strings]}
          hand:              [(value, suit_idx), ...]
          used_cards:        set of (value, suit_idx) already dealt
        """
        if used_cards is None:
            used_cards = set()
        hand             = []
        front_ascii_cards = {}

        for i in range(n):
            while True:
                # Two Jokers exist in the 54-card deck: (14,4) and (14,5)
                r = random.randint(1, 54)
                if r == 1:
                    value, suit_idx = 14, 4
                elif r == 2:
                    value, suit_idx = 14, 5
                else:
                    value    = random.randint(1, 13)
                    suit_idx = random.randint(0, 3)
                if (value, suit_idx) not in used_cards:
                    used_cards.add((value, suit_idx))
                    hand.append((value, suit_idx))
                    front_ascii_cards[i] = self._make_card_lines(value, suit_idx)
                    break

        return front_ascii_cards, hand, used_cards

    def _make_card_lines(self, value, suit_idx):
        v     = _value_str(value)
        suit  = _SUIT_SYMBOLS[suit_idx]
        inner = 9
        return [
            '╔═════════╗',
            '║' + v.ljust(inner)    + '║',
            '║' + ' ' * inner       + '║',
            '║' + ' ' * inner       + '║',
            '║' + suit.center(inner) + '║',
            '║' + ' ' * inner       + '║',
            '║' + ' ' * inner       + '║',
            '║' + v.rjust(inner)    + '║',
            '╚═════════╝',
        ]

    def _suit_color(self, value, suit_idx):
        if value == 14:
            return bcolors.ORANGE
        if suit_idx in (1, 2):    # Diamonds, Hearts
            return bcolors.RED
        return bcolors.GREY        # Spades, Clubs


class Dealer(Cards):
    """Handles dealing and displaying the cards."""

    MARGIN_HITME = ' ' * 11

    def __init__(self, NR_OF_CARDS, suits):
        super().__init__(NR_OF_CARDS, suits)

    def shuffles(self, front_ascii_cards, hand):
        """Interleave card rows into 9 display strings, colored by suit."""
        the_flop = []
        for row in range(9):
            parts = []
            for i in range(self.NR_OF_CARDS):
                color = self._suit_color(*hand[i])
                parts.append(color + front_ascii_cards[i][row] + bcolors.ENDC)
            the_flop.append(self.MARGIN_BETWEEN.join(parts))
        return the_flop

    def deals_cards(self, the_flop, NR_OF_CARDS):
        """Animate card backs one-by-one, then reveal the hand."""
        M = self.MARGIN_HITME
        hit_me = (
            f'\n{M}' + bcolors.RED +
            f'\n{M}██╗  ██╗██╗████████╗    ███╗   ███╗███████╗'
            f'\n{M}██║  ██║██║╚══██╔══╝    ████╗ ████║██╔════╝'
            f'\n{M}███████║██║   ██║       ██╔████╔██║█████╗  '
            f'\n{M}██╔══██║██║   ██║       ██║╚██╔╝██║██╔══╝  '
            f'\n{M}██║  ██║██║   ██║       ██║ ╚═╝ ██║███████╗'
            f'\n{M}╚═╝  ╚═╝╚═╝   ╚═╝       ╚═╝     ╚═╝╚══════╝' +
            bcolors.ENDC +
            f'\n\n{M}    ' + bcolors.UNDERLINE + 'Press Enter' + bcolors.ENDC
        )

        back_card = [
            '╔═════════╗',
            '║' + bcolors.RED + '░░░░░░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░░░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░X░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░X░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░X░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░░░░░░' + bcolors.ENDC + '║',
            '║' + bcolors.RED + '░░░░░░░░░' + bcolors.ENDC + '║',
            '╚═════════╝',
        ]

        input(hit_me)

        for nr in range(1, NR_OF_CARDS + 1):
            time.sleep(0.09)
            sys_clear(OnScreen=payout)
            for row_line in back_card:
                print(self.MARGIN_LEFT + self.MARGIN_BETWEEN.join([row_line] * nr))

        time.sleep(2)
        sys_clear(OnScreen=payout)
        for line in the_flop:
            print(self.MARGIN_LEFT + line)
        time.sleep(1.5)


class Select(Cards):
    """Handles player card selection and replacement."""

    def __init__(self, front_ascii_cards, hand, NR_OF_CARDS, suits, used_cards):
        super().__init__(NR_OF_CARDS, suits)
        self.front_ascii_cards = front_ascii_cards
        self.hand              = hand
        self.used_cards        = used_cards

    def highlight_card(self):
        """Let the player choose cards to replace.
        Arrow keys navigate; Space toggles selection; Enter confirms.
        Returns a set of card indices selected for replacement.
        """
        state = {'cursor': 0, 'selected': set()}

        def redraw():
            sys_clear(OnScreen=payout)
            for line in self._build_display(state['cursor'], state['selected']):
                print(self.MARGIN_LEFT + line)
            print(
                f"\n  {bcolors.BLUE}←/→{bcolors.ENDC} navigate  "
                f"{bcolors.ORANGE}Space{bcolors.ENDC} select/deselect  "
                f"{bcolors.GREEN}Enter{bcolors.ENDC} confirm draw"
            )

        def on_key(key):
            if key == keyboard.Key.right:
                state['cursor'] = min(self.NR_OF_CARDS - 1, state['cursor'] + 1)
            elif key == keyboard.Key.left:
                state['cursor'] = max(0, state['cursor'] - 1)
            elif key == keyboard.Key.space:
                c = state['cursor']
                if c in state['selected']:
                    state['selected'].discard(c)
                else:
                    state['selected'].add(c)
            elif key == keyboard.Key.enter:
                return False   # stops the listener
            else:
                return         # ignore all other keys
            redraw()

        redraw()
        with keyboard.Listener(on_press=on_key) as listener:
            listener.join()

        return state['selected']

    def _build_display(self, cursor, selected):
        """Return 10 strings: 9 card rows + 1 marker row."""
        lines = []
        for row in range(9):
            parts = []
            for i in range(self.NR_OF_CARDS):
                card_line = self.front_ascii_cards[i][row]
                if i in selected:
                    color = bcolors.ORANGE
                elif i == cursor and row in (0, 8):
                    color = bcolors.BLUE
                else:
                    color = self._suit_color(*self.hand[i])
                parts.append(color + card_line + bcolors.ENDC)
            lines.append(self.MARGIN_BETWEEN.join(parts))

        # Marker row beneath the cards
        markers = []
        for i in range(self.NR_OF_CARDS):
            if i in selected:
                markers.append(bcolors.ORANGE + bcolors.BOLD + '[SWAP]'.center(11) + bcolors.ENDC)
            elif i == cursor:
                markers.append(bcolors.BLUE + '[  ]'.center(11) + bcolors.ENDC)
            else:
                markers.append(' ' * 11)
        lines.append(self.MARGIN_BETWEEN.join(markers))
        return lines

    def replace_select(self, selected, used_cards):
        """Draw new cards for each selected position.
        Returns (new_hand, new_front_ascii_cards, used_cards).
        """
        new_hand  = list(self.hand)
        new_ascii = dict(self.front_ascii_cards)

        for i in selected:
            while True:
                if random.randint(1, 53) == 1:
                    value, suit_idx = 14, 4
                else:
                    value    = random.randint(1, 13)
                    suit_idx = random.randint(0, 3)
                if (value, suit_idx) not in used_cards:
                    used_cards.add((value, suit_idx))
                    new_hand[i]  = (value, suit_idx)
                    new_ascii[i] = self._make_card_lines(value, suit_idx)
                    break

        return new_hand, new_ascii, used_cards


class Bet:
    """Tracks balance and handles bet placement and payout."""

    def __init__(self, balance=100):
        self.balance     = balance
        self.current_bet = 0

    def place_bet(self, amount):
        """Deduct bet from balance. Returns False if invalid."""
        if amount <= 0 or amount > self.balance:
            return False
        self.current_bet  = amount
        self.balance     -= amount
        return True

    def payout(self, multiplier):
        """Add winnings to balance. Returns the amount won."""
        winnings      = self.current_bet * multiplier
        self.balance += winnings
        return winnings


class DoubleDown:
    pass


def sys_clear(OnScreen=None):
    """Clear the terminal screen across platforms."""
    if 'ipad' in platform.platform().lower():
        try:
            import console
            console.clear()
        except ImportError:
            pass
    elif os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    if OnScreen is not None:
        print(OnScreen)
