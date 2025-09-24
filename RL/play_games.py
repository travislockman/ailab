import gymnasium as gym
import ale_py  # required for ALE/ env registration

env = gym.make("ALE/Breakout-v5", render_mode="human")
obs, info = env.reset()
for _ in range(2000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()
env.close()