import base as clss


def main():
    clss.sys_clear(OnScreen=clss.payout)

    NR_OF_CARDS = 5
    suits = {'Spades': '♠', 'Diamonds': '♦', 'Hearts': '♥', 'Clubs': '♣', 'Joker': '§'}

    bet = clss.Bet(balance=100)

    while True:
        clss.sys_clear(OnScreen=clss.payout)
        print(f"  Balance: {clss.bcolors.GREEN}{bet.balance}{clss.bcolors.ENDC} coins\n")

        # Get a valid bet
        while True:
            raw = input(f"  Enter bet (1–{bet.balance}): ").strip()
            try:
                amount = int(raw)
                if bet.place_bet(amount):
                    break
                print(f"  Bet must be between 1 and {bet.balance}.")
            except ValueError:
                print("  Please enter a whole number.")

        # Deal initial hand
        cards  = clss.Cards(NR_OF_CARDS, suits)
        front_ascii_cards, hand, used_cards = cards.create_cards(NR_OF_CARDS)

        dealer   = clss.Dealer(NR_OF_CARDS, suits)
        the_flop = dealer.shuffles(front_ascii_cards, hand)
        dealer.deals_cards(the_flop, NR_OF_CARDS)

        # Player selects cards to replace
        player   = clss.Select(front_ascii_cards, hand, NR_OF_CARDS, suits, used_cards)
        selected = player.highlight_card()

        # Replace selected cards and redisplay
        if selected:
            new_hand, new_ascii, used_cards = player.replace_select(selected, used_cards)
        else:
            new_hand, new_ascii = hand, front_ascii_cards

        new_flop = dealer.shuffles(new_ascii, new_hand)
        clss.sys_clear(OnScreen=clss.payout)
        for line in new_flop:
            print(clss.Cards.MARGIN_LEFT + line)

        # Evaluate and pay out
        hand_name, multiplier = clss.evaluate_hand(new_hand)
        winnings = bet.payout(multiplier)

        print(f"\n  {clss.bcolors.BOLD}{hand_name}{clss.bcolors.ENDC}", end='')
        if winnings > 0:
            print(
                f"  —  {clss.bcolors.GREEN}+{winnings} coins"
                f"{clss.bcolors.ENDC} (×{multiplier})"
            )
        else:
            print(f"  —  {clss.bcolors.RED}no win{clss.bcolors.ENDC}")

        print(f"  Balance: {clss.bcolors.GREEN}{bet.balance}{clss.bcolors.ENDC} coins")

        if bet.balance <= 0:
            print(f"\n  {clss.bcolors.RED}Out of coins — game over.{clss.bcolors.ENDC}")
            break

        again = input("\n  Play again? (y/n): ").strip().lower()
        if again != 'y':
            print(f"\n  Final balance: {bet.balance} coins. Thanks for playing!")
            break


if __name__ == "__main__":
    main()
