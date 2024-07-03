from game_logic.game_state import SimpleState, split_cards


def card_to_int(card):
    match card[0]:
        case "0":  # empty community card
            return 0

        case "2":
            return 2
        case "3":
            return 3
        case "4":
            return 4
        case "5":
            return 5
        case "6":
            return 6
        case "7":
            return 7
        case "8":
            return 8
        case "9":
            return 9
        case "T":
            return 10
        case "J":
            return 11
        case "Q":
            return 12
        case "K":
            return 13
        case "A":
            return 14
        case _:
            raise Exception(f"whats that card? {card[0]}")


def make_obs(state: SimpleState, main_actor: int):
    player_cards = split_cards(state.players_data[main_actor].cards)
    community_cards = split_cards(state.community_cards)
    for i in range(5 - len(community_cards)):
        community_cards.append("0x")

    return [card_to_int(card) for card in player_cards] + [
        card_to_int(card) for card in community_cards
    ]
