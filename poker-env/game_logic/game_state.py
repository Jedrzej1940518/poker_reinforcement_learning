from dataclasses import dataclass

from pokerkit import State


def split_cards(cards: str):
    return [cards[i : i + 2] for i in range(0, len(cards), 2)]


@dataclass
class PlayerData:
    name: str = "Bot"
    cards: str = "????"
    stack: int = -1
    bet: int = -1
    actor: bool = False

    action: str = ""
    hand: str = "high card"


@dataclass
class SimpleState:
    players_data: list[PlayerData]

    community_cards: str = ""

    pot: int = 0
    middle_pot: int = 0

    big_blind: int = 1

    actor_index: int = 0

    def static_update(self, pokerkit_state: State):
        total_bets = 0
        self.big_blind = pokerkit_state.blinds_or_straddles[1]

        for i, player in enumerate(self.players_data):
            player.stack = pokerkit_state.stacks[i]
            player.bet = pokerkit_state.bets[i]
            total_bets += player.bet

        self.pot = pokerkit_state.total_pot_amount
        self.middle_pot = self.pot - total_bets

    def dynamic_update(self, pokerkit_state: State):
        self.community_cards = ""

        for i, player in enumerate(self.players_data):
            if len(pokerkit_state.hole_cards[i]):
                player.cards = repr(pokerkit_state.hole_cards[i][0]) + repr(
                    pokerkit_state.hole_cards[i][1]
                )
                player.hand = str(pokerkit_state.get_hand(i, 0, 0))

            player.actor = False

        if len(pokerkit_state.actor_indices):
            self.actor_index = pokerkit_state.actor_indices[0]
            self.players_data[pokerkit_state.actor_indices[0]].actor = True

        for board in pokerkit_state.board_cards:
            for card in board:
                self.community_cards += repr(card)

    def update_state(self, pokerkit_state: State):
        self.static_update(pokerkit_state)
        self.dynamic_update(pokerkit_state)

    def save_action(self, action: str, action_actor: int):
        for player in self.players_data:
            player.action = ""

        self.players_data[action_actor].action = action
