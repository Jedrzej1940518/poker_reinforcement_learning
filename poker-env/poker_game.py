from math import inf
import threading
import time

from pokerkit import Automation, NoLimitTexasHoldem, State
from poker_gui import GUI
from game_state import SimpleState, PlayerData


class PokerGame:
    sleep_time = 1

    def __init__(self):
        players = [
            PlayerData("Hans", "????", 1125600, 0),
            PlayerData("Negranu", "????", 553500, 0),
        ]
        self.pokerkit_state = self._init_state(players)
        self.simple_state = SimpleState(players)
        self.simple_state.static_update(self.pokerkit_state)

        self.gui = GUI(self.simple_state)
        self.gui.create_window()
        self.gui.create_table()

        self.thread = threading.Thread(target=self.main_game)
        self.thread.daemon = True
        self.thread.start()

        self.gui.main_loop()

    def main_game(self):
        time.sleep(PokerGame.sleep_time)

        state = self.pokerkit_state

        state.deal_hole("Ac2d")  # Ivey
        self._update_state_event()
        state.deal_hole("7h6h")  # Dwan
        self._update_state_event()

        state.complete_bet_or_raise_to(7000)  # Dwan
        self._update_state_event()
        state.complete_bet_or_raise_to(23000)  # Ivey
        self._update_state_event()
        state.check_or_call()  # Dwan
        self._update_state_event()

        state.burn_card("??")
        self._update_state_event()
        state.deal_board("Jc3d5c")
        self._update_state_event()

        state.complete_bet_or_raise_to(35000)  # Ivey
        self._update_state_event()
        state.check_or_call()  # Dwan
        self._update_state_event()

        state.burn_card("??")
        self._update_state_event()
        state.deal_board("4h")
        self._update_state_event()

        state.complete_bet_or_raise_to(90000)  # Ivey
        self._update_state_event()
        state.complete_bet_or_raise_to(232600)  # Dwan
        self._update_state_event()
        state.complete_bet_or_raise_to(1067100)  # Ivey
        self._update_state_event()
        state.check_or_call()  # Dwan
        self._update_state_event()

        state.burn_card("??")
        self._update_state_event()
        state.deal_board("Jh")
        self._update_state_event()

    def _update_static_state_event(self):
        self.gui.add_event(self.gui.update_state, self.pokerkit_state)
        time.sleep(PokerGame.sleep_time)

    def _update_state_event(self):
        self.gui.add_event(self.gui.update_state, self.pokerkit_state)
        time.sleep(PokerGame.sleep_time)

    def _init_state(self, players: list[PlayerData]) -> State:
        if len(players) != 2:
            print("error bro")
        stacks = [player.stack for player in players]
        return NoLimitTexasHoldem.create_state(
            # Automations
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,  # Uniform antes?
            500,  # Antes
            (1000, 2000),  # Blinds or straddles
            2000,  # Min-bet
            stacks,  # Starting stacks
            len(players),  # Number of players
        )


def example_1():
    state = NoLimitTexasHoldem.create_state(
        # Automations
        (
            Automation.ANTE_POSTING,
            Automation.BET_COLLECTION,
            Automation.BLIND_OR_STRADDLE_POSTING,
            Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
            Automation.HAND_KILLING,
            Automation.CHIPS_PUSHING,
            Automation.CHIPS_PULLING,
        ),
        True,  # Uniform antes?
        500,  # Antes
        (1000, 2000),  # Blinds or straddles
        2000,  # Min-bet
        (1125600, inf, 553500),  # Starting stacks
        3,  # Number of players
    )

    state.deal_hole("Ac2d")  # Ivey
    state.deal_hole("????")  # Antonius
    state.deal_hole("7h6h")  # Dwan

    state.complete_bet_or_raise_to(7000)  # Dwan
    state.complete_bet_or_raise_to(23000)  # Ivey
    state.fold()  # Antonius
    state.check_or_call()  # Dwan

    state.burn_card("??")
    state.deal_board("Jc3d5c")

    state.complete_bet_or_raise_to(35000)  # Ivey
    state.check_or_call()  # Dwan

    state.burn_card("??")
    state.deal_board("4h")

    state.complete_bet_or_raise_to(90000)  # Ivey
    state.complete_bet_or_raise_to(232600)  # Dwan
    state.complete_bet_or_raise_to(1067100)  # Ivey
    state.check_or_call()  # Dwan

    state.burn_card("??")
    state.deal_board("Jh")

    print(state.stacks)  # [572100, inf, 1109500]


if __name__ == "__main__":
    PokerGame()
