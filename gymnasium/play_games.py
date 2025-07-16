import gym

env = gym.make("Breakout-v4", render_mode="human")
observation = env.reset()

for _ in range(1000):
    env.render()
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    if done:
        observation = env.reset()

env.close()
