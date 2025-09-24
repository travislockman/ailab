#!/usr/bin/env python3
# frozenlake_qlearn_viz.py
# Baby-steps RL with Q-learning + visualizations for FrozenLake-v1

import argparse
import time
from typing import Tuple
import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt


def make_env(is_slippery: bool, render: str | None = None):
    """
    render:
      - None         -> no rendering (fast training)
      - "ansi"       -> text frames you can print in terminal
      - "human"      -> not used for FrozenLake (text env)
    """
    return gym.make(
        "FrozenLake-v1",
        map_name="4x4",
        is_slippery=is_slippery,
        render_mode=render,
    )


def epsilon_greedy(Q: np.ndarray, state: int, n_actions: int, eps: float) -> int:
    if np.random.random() < eps:
        return np.random.randint(n_actions)
    return int(np.argmax(Q[state]))


def train_q_learning(
    episodes: int = 5000,
    alpha: float = 0.8,
    gamma: float = 0.95,
    eps_start: float = 1.0,
    eps_end: float = 0.05,
    eps_decay: float = 0.9995,
    is_slippery: bool = False,
    seed: int = 0,
) -> Tuple[np.ndarray, list[float]]:
    rng = np.random.default_rng(seed)
    env = make_env(is_slippery, render=None)
    n_states = env.observation_space.n
    n_actions = env.action_space.n

    Q = np.zeros((n_states, n_actions), dtype=np.float32)
    eps = eps_start
    rewards: list[float] = []

    for ep in range(episodes):
        state, _ = env.reset(seed=int(rng.integers(0, 1_000_000)))
        done = False
        ep_reward = 0.0

        while not done:
            action = epsilon_greedy(Q, state, n_actions, eps)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            best_next = np.max(Q[next_state])
            td_target = reward + (0.0 if done else gamma * best_next)
            td_error = td_target - Q[state, action]
            Q[state, action] += alpha * td_error

            state = next_state
            ep_reward += reward

        rewards.append(ep_reward)
        eps = max(eps_end, eps * eps_decay)

        if (ep + 1) % max(1, (episodes // 10)) == 0:
            recent = np.mean(rewards[-100:]) if len(rewards) >= 100 else np.mean(rewards)
            print(f"[{ep+1}/{episodes}] ε={eps:.3f}  recent win-rate≈{recent:.2f}")

    env.close()
    return Q, rewards


def moving_average(x: list[float], k: int = 100) -> np.ndarray:
    if len(x) == 0:
        return np.array([])
    k = max(1, min(k, len(x)))
    c = np.cumsum([0.0] + x)
    ma = (c[k:] - c[:-k]) / k
    # Pad to match length
    pad = np.concatenate([np.full(k - 1, ma[0] if len(ma) else 0.0), ma]) if len(ma) else np.zeros_like(x, dtype=float)
    return pad


def plot_learning_curve(rewards: list[float], title: str = "FrozenLake Q-learning"):
    ma = moving_average(rewards, k=100)
    plt.figure(figsize=(7, 4.5))
    plt.plot(rewards, label="Reward (1 if success else 0)")
    plt.plot(ma, label="Moving Avg (100-ep)")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def print_policy(Q: np.ndarray, is_slippery: bool):
    """
    Show best action per state on the 4x4 grid.
    Actions: 0:Left, 1:Down, 2:Right, 3:Up
    """
    arrows = {0: "←", 1: "↓", 2: "→", 3: "↑"}
    env = make_env(is_slippery, render=None)
    desc = env.unwrapped.desc.astype(str)  # array of S/F/H/G characters
    policy = np.full((4, 4), "·", dtype=object)

    for s in range(env.observation_space.n):
        r, c = divmod(s, 4)
        cell = desc[r, c]
        if cell in ("H", "G"):  # holes & goal: leave as is
            policy[r, c] = cell
        else:
            a = int(np.argmax(Q[s]))
            policy[r, c] = arrows[a]

    print("\nPolicy (arrows = greedy action; H=hole, G=goal):")
    for r in range(4):
        print(" ".join(policy[r]))
    env.close()


def rollout(Q: np.ndarray, is_slippery: bool, delay: float = 0.2, max_steps: int = 100):
    """
    Runs one episode with the greedy policy and prints a live text animation.
    Uses render_mode='ansi' to get frame strings.
    """
    env = make_env(is_slippery, render="ansi")
    state, _ = env.reset()
    done = False
    steps = 0
    total_reward = 0.0

    print("\nGreedy rollout (live):")
    while not done and steps < max_steps:
        # Render current frame
        frame = env.render()
        if hasattr(frame, "strip"):
            print("\033[2J\033[H", end="")  # clear screen
            print(frame, end="")
        else:
            print(frame)

        # Greedy action
        action = int(np.argmax(Q[state]))
        state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        total_reward += reward
        steps += 1
        time.sleep(delay)

    print(f"\nEpisode finished: steps={steps}, reward={total_reward}\n")
    env.close()


def evaluate(Q: np.ndarray, episodes: int = 200, is_slippery: bool = False) -> float:
    env = make_env(is_slippery, render=None)
    wins = 0
    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = int(np.argmax(Q[state]))
            state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
        if reward > 0:
            wins += 1
    env.close()
    return wins / episodes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=5000, help="Training episodes")
    ap.add_argument("--slippery", action="store_true", help="Use stochastic (slippery) ice")
    ap.add_argument("--show_curve", action="store_true", help="Plot training curve")
    ap.add_argument("--show_policy", action="store_true", help="Print arrow map for greedy policy")
    ap.add_argument("--rollout", action="store_true", help="Live terminal rollout after training")
    ap.add_argument("--delay", type=float, default=0.2, help="Seconds between rollout frames")
    args = ap.parse_args()

    Q, rewards = train_q_learning(
        episodes=args.episodes,
        is_slippery=args.slippery,
    )
    win_rate = evaluate(Q, episodes=200, is_slippery=args.slippery)
    print(f"\nFinal evaluation win-rate: {win_rate:.2f} ({'slippery' if args.slippery else 'deterministic'})")

    if args.show_policy:
        print_policy(Q, is_slippery=args.slippery)

    if args.rollout:
        rollout(Q, is_slippery=args.slippery, delay=args.delay)

    if args.show_curve:
        plot_learning_curve(rewards, title=f"FrozenLake Q-learning ({'slippery' if args.slippery else 'deterministic'})")


if __name__ == "__main__":
    main()
