from rl_environment.environment import PokerEnvironment
from game_logic.poker_game import Action

from stable_baselines3 import DQN


def train(env):
    iters = 0

    while iters < 5:
        iters += 1

        obs, info = env.reset()
        done_or_trunc = False

        while not done_or_trunc:
            obs, reward, terminated, truncated, info = env.step(action=Action.RAISE)
            done_or_trunc = terminated or truncated

        print("reward ", reward)


def train_human_rendering():
    env = PokerEnvironment(render_mode="human")

    def training_looop_func():
        train(env)

    env.init_human_rendering(training_looop_func)


def train_sb3():
    env = PokerEnvironment()
    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000, log_interval=4)
    model.save("dqn_poker")
    del model


def testing_loop(env, model):
    obs, info = env.reset()
    while True:
        print("obs", obs)

        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        print("reward", reward)
        if terminated or truncated:
            obs, info = env.reset()


def test_sb3():
    env = PokerEnvironment(render_mode="human")
    model = DQN.load("dqn_poker")

    def testing_loop_func():
        testing_loop(env, model)

    env.init_human_rendering(testing_loop_func)


if __name__ == "__main__":
    # train_human_rendering()
    # train_sb3()
    test_sb3()
