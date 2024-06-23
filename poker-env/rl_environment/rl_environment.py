import gymnasium as gym
from gymnasium import spaces


class PokerEnvironment(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode=None):
        self.observation_space = spaces.Box([0, 0], [1, 1])
        self.action_space = spaces.Discrete(2)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def _get_obs(self):
        return [0.5, 0.5]

    def _get_info(self):
        return {"info": "yeah"}

    def reset(self, seed=None, options=None):
        print("[TODO] resetting")
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        print("[TODO] stepping")

        terminated = False
        truncated = False
        reward = 1 if terminated else 0  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def _render_frame(self):
        print("[TODO] rendering frame")

    def close(self):
        print("[TODO] closing")
