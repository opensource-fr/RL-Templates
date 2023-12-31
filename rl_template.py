import gym
from gym import spaces
import numpy as np
import argparse
from stable_baselines3 import A2C, PPO
from stable_baselines3.common.vec_env import DummyVecEnv

def target_function(x):
    return -((x[0] - 1) **2 + (x[1] + 1)**2 - 0.1*np.sin(5 * x[0]) * 0.1*np.sin(5 * x[1]))

class CustomEnv(gym.Env):
    def __init__(self, initial_state):
        super(CustomEnv, self).__init__()

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(2,))

        # Initialize state with the initial_state argument
        self.state = np.array(initial_state)

    def step(self, action):
        self.state += action
        reward = target_function(self.state)
        done = False
        return self.state, reward, done, {}

    def reset(self):
        self.state = np.zeros(2)
        return self.state

def get_model(model_name, env):
    if model_name.lower() == "ppo":
        return PPO('MlpPolicy', env, ent_coef=0.01, verbose=1, tensorboard_log="./ppo_tensorboard/")
    elif model_name.lower() == "a2c":
        return A2C('MlpPolicy', env, entropy_coef=0.01, verbose=1, tensorboard_log="./a2c_tensorboard/")
    else:
        raise ValueError(f"Unknown model name {model_name}, please choose either 'ppo' or 'a2c'")

def main():
    parser = argparse.ArgumentParser(description="Train an agent to maximize a function.")
    parser.add_argument("--model", help="The model to use, either 'ppo' or 'a2c'", type=str, default="ppo")
    parser.add_argument("--max_timesteps", help="The maximum number of timesteps to train for", type=int, default=100000)

    # Add argparse arguments for the initial states of x and y coordinates
    parser.add_argument("--initial_x", help="The initial value of the x coordinate", type=float, default=0.0)
    parser.add_argument("--initial_y", help="The initial value of the y coordinate", type=float, default=0.0)

    args = parser.parse_args()

    # Create the custom environment with the initial state
    env = CustomEnv([args.initial_x, args.initial_y])

    env = DummyVecEnv([lambda: env])
    model = get_model(args.model, env)
    model.learn(total_timesteps=args.max_timesteps)
    print("Final values of the parameters: ", env.envs[0].state)

    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, _, _, _ = env.step(action)

    model.save("agent_model")

if __name__ == "__main__":
    main()

