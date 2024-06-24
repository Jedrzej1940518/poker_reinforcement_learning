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
            np.array([0, 0, 0, 0, 0, 0, 0]).astype(np.int32),
            np.array([14, 14, 14, 14, 14, 14, 14]).astype(np.int32),
        )
        self.action_space = spaces.Discrete(2)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.human_render_initialized = False

        self.main_actor = 1  # [TODO] remove

    def _get_obs(self):
        return make_obs(self.game.simple_state)

    def _get_info(self):
        return {"info": "yeah"}

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        players = [
            PlayerData("Hans", "????", 120000, 0),
            PlayerData("Negranu", "????", 120000, 0),
        ]

        self.game = PokerGame(SimpleState(players))
        self.starting_stacks = self.game.stacks()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self.game.action(action)

        hand_ended = not self.game.pokerkit_state.actor_indices

        while not hand_ended and self.game.simple_state.actor_index != self.main_actor:
            if self.render_mode == "human":
                self._render_frame()

            self.game.action(Action.CHECK_OR_CALL)
            hand_ended = not self.game.pokerkit_state.actor_indices

        terminated = hand_ended and any(
            [player.stack <= 0 for player in self.game.simple_state.players_data]
        )

        truncated = False
        reward = 0

        if hand_ended:
            current_stacks = self.game.stacks()

            reward = (
                self.starting_stacks[self.main_actor] - current_stacks[self.main_actor]
            ) / 10000
            self.starting_stacks = current_stacks

        if not terminated and hand_ended:
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
