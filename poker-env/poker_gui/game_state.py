from dataclasses import dataclass

from pokerkit import State


@dataclass
class PlayerData:
    name: str = "Bot"
    cards: str = "????"
    stack: float = -1
    bet: float = -1
    actor: bool = False


@dataclass
class SimpleState:
    players_data: list[PlayerData]  # [todo] add current bet and indexes
    community_cards: str = ""

    pot: float = 0
    middle_pot: float = 0

    big_blind: int = 1

    def static_update(self, pokerkit_state: State):
        total_bets = 0
        self.big_blind = pokerkit_state.blinds_or_straddles[1]

        for i, player in enumerate(self.players_data):
            player.stack = pokerkit_state.stacks[i] / self.big_blind
            player.bet = pokerkit_state.bets[i] / self.big_blind
            total_bets += player.bet

        self.pot = pokerkit_state.total_pot_amount / self.big_blind
        self.middle_pot = self.pot - total_bets

    def dynamic_update(self, pokerkit_state: State):
        self.community_cards = ""

        for i, player in enumerate(self.players_data):
            if len(pokerkit_state.hole_cards[i]):
                player.cards = repr(pokerkit_state.hole_cards[i][0]) + repr(
                    pokerkit_state.hole_cards[i][1]
                )
            player.actor = False

        if len(pokerkit_state.actor_indices):
            self.players_data[pokerkit_state.actor_indices[0]].actor = True

        for board in pokerkit_state.board_cards:
            for card in board:
                self.community_cards += repr(card)

    def update_state(self, pokerkit_state: State):
        self.static_update(pokerkit_state)
        self.dynamic_update(pokerkit_state)
