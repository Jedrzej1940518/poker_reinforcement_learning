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

    def __init__(self, render_mode=None):
        self.observation_space = spaces.Box(
            np.array([2, 2]).astype(np.int32), np.array([14, 14]).astype(np.int32)
        )
        self.action_space = spaces.Discrete(2)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.human_render_initialized = False

        self.main_actor = 1  # [TODO] remove

    def _get_obs(self):
        return make_obs(self.simple_state)

    def _get_info(self):
        return {"info": "yeah"}

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        players = [
            PlayerData("Hans", "????", 120000, 0),
            PlayerData("Negranu", "????", 120000, 0),
        ]

        self.simple_state = SimpleState(players)
        self.game = PokerGame(self.simple_state)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self.game.action(action)
        terminated = not self.game.pokerkit_state.actor_indices

        while not terminated and self.game.simple_state.actor_index != self.main_actor:
            self.game.action(Action.CHECK_OR_CALL)
            terminated = not self.game.pokerkit_state.actor_indices

        truncated = False
        reward = 0

        if terminated:
            reward = (
                self.game.simple_state.players_data[self.main_actor].stack
                - 120000 / self.simple_state.big_blind
            ) / 5.25

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
