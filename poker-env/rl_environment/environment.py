import threading
import time
import gymnasium as gym
from gymnasium import spaces

import numpy as np
from game_logic.poker_game import PokerGame, Action
from game_logic.game_state import SimpleState, PlayerData
from poker_gui.gui import GUI

from rl_environment.observation import make_obs


class PokerEnvironment(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, init_table_simple_state=None, render_mode=None):
        self.observation_space = spaces.Box(
            np.array([0, 0, 0, 0, 0, 0, 0]).astype(np.int32),
            np.array([14, 14, 14, 14, 14, 14, 14]).astype(np.int32),
        )
        self.action_space = spaces.Discrete(2)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.human_render_initialized = False

        self.main_actor = 1  # [TODO] remove

        self.init_table_simple_state = init_table_simple_state

        if init_table_simple_state is None:
            self.init_table_simple_state = lambda: SimpleState(
                players_data=[
                    PlayerData("Hans", "????", 120000, 0),
                    PlayerData("Negranu", "????", 120000, 0),
                ]
            )

    def _get_obs(self):
        return make_obs(self.game.simple_state, self.main_actor)

    def _get_info(self):
        return {"info": "yeah"}

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        self.game = PokerGame(self.init_table_simple_state())
        self.game.init_hand()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def skip_until_main_actor(self):
        while (
            not self.game.hand_ended()
            and self.game.simple_state.actor_index != self.main_actor
        ):
            if self.render_mode == "human":
                self._render_frame()

            self.game.action(Action.CHECK_OR_CALL)

        if self.render_mode == "human":
            self._render_frame()

    def step(self, action):
        stacks_and_bets = self.game.stacks_plus_bets()

        self.skip_until_main_actor()

        if not self.game.hand_ended():
            self.game.action(action)

        hand_ended = self.game.hand_ended()
        terminated = self.game.table_ended()

        truncated = False
        reward = 0

        if hand_ended:
            reward = (
                self.game.stacks()[self.main_actor] - stacks_and_bets[self.main_actor]
            ) / 10000

        if hand_ended and not terminated:
            self.game.init_hand()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def _render_frame(self):
        if not self.human_render_initialized:
            raise Exception(
                "Call env.init_human_rendering(training_loop_func) after creating env!"
            )

        self.gui.add_event(self.gui.update_state, self.game.simple_state)

        time.sleep(0.5)

    def init_human_rendering(self, training_loop_func):
        self.human_render_initialized = True

        self.gui = GUI()
        self.gui.create_window()
        self.gui.create_table()

        self.thread = threading.Thread(target=training_loop_func)
        self.thread.daemon = True
        self.thread.start()

        self.gui.main_loop()

    def close(self):
        print("[TODO] closing")
