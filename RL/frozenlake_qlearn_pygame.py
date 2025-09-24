#!/usr/bin/env python3
# frozenlake_qlearn_pygame.py
import sys, time, argparse, numpy as np, gymnasium as gym, pygame as pg

# ---------- RL bits ----------
def make_env(is_slippery: bool):
    return gym.make("FrozenLake-v1", map_name="4x4", is_slippery=is_slippery)

def epsilon_greedy(Q, s, nA, eps):
    return np.random.randint(nA) if np.random.rand() < eps else int(np.argmax(Q[s]))

def train_q_learning(episodes=5000, alpha=0.8, gamma=0.95,
                     eps_start=1.0, eps_end=0.05, eps_decay=0.9995,
                     is_slippery=False, seed=0):
    rng = np.random.default_rng(seed)
    env = make_env(is_slippery)
    nS, nA = env.observation_space.n, env.action_space.n
    Q = np.zeros((nS, nA), dtype=np.float32)
    eps = eps_start
    wins = 0
    for ep in range(episodes):
        s, _ = env.reset(seed=int(rng.integers(0, 1_000_000)))
        done = False
        while not done:
            a = epsilon_greedy(Q, s, nA, eps)
            ns, r, term, trunc, _ = env.step(a)
            done = term or trunc
            best_next = np.max(Q[ns])
            td_target = r + (0.0 if done else gamma * best_next)
            Q[s, a] += alpha * (td_target - Q[s, a])
            s = ns
        wins += 1 if r > 0 else 0
        eps = max(eps_end, eps * eps_decay)
        if (ep + 1) % max(1, episodes // 10) == 0:
            print(f"[{ep+1}/{episodes}] ε={eps:.3f} recent win-rate≈{wins/max(1,ep+1):.2f}")
    env.close()
    return Q

# ---------- Pygame viz ----------
COL_BG = (18, 18, 22)
COL_GRID = (60, 60, 70)
COL_START = (120, 200, 255)
COL_FREE = (230, 230, 240)
COL_HOLE = (40, 40, 50)
COL_GOAL = (130, 230, 160)
COL_AGENT = (240, 120, 80)
FONT_COL = (230, 230, 240)

def draw_board(screen, desc, cell, agent_rc, stats, tile=96, pad=10):
    H, W = desc.shape
    screen.fill(COL_BG)
    # tiles
    for r in range(H):
        for c in range(W):
            ch = desc[r, c]
            if ch == b'S': color = COL_START
            elif ch == b'F': color = COL_FREE
            elif ch == b'H': color = COL_HOLE
            elif ch == b'G': color = COL_GOAL
            else: color = COL_FREE
            rect = pg.Rect(pad + c*tile, pad + r*tile, tile-2, tile-2)
            pg.draw.rect(screen, color, rect, border_radius=12)
            pg.draw.rect(screen, COL_GRID, rect, width=2, border_radius=12)

    # agent
    ar, ac = agent_rc
    cx = pad + ac*tile + tile//2
    cy = pad + ar*tile + tile//2
    pg.draw.circle(screen, COL_AGENT, (cx, cy), int(tile*0.28))

    # HUD
    font = pg.font.SysFont("Menlo,Consolas,monospace", 18)
    lines = [
        f"Episodes: {stats['episodes']}   Wins: {stats['wins']}   Win rate: {stats['win_rate']:.2f}",
        f"Step: {stats['step']}   Slippery: {stats['slippery']}   Speed: {stats['speed']}x  ( +/- to change )",
        "SPACE: toggle autoplay   R: reset episode   ESC/Q: quit",
    ]
    y = pad + H*tile + 12
    for L in lines:
        surf = font.render(L, True, FONT_COL)
        screen.blit(surf, (pad, y))
        y += 22

def idx_to_rc(idx, width=4):
    return divmod(idx, width)

def eval_episode(Q, is_slippery=False, autoplay=True, speed=1.0):
    env = make_env(is_slippery)
    desc = env.unwrapped.desc  # bytes array of S/F/H/G
    s, _ = env.reset()
    step = 0
    wins = 0
    H, W = desc.shape
    pg.init()
    tile = 96
    pad = 10
    screen = pg.display.set_mode((pad*2 + W*tile, pad*2 + H*tile + 90))
    pg.display.set_caption("FrozenLake — Q-learning visualizer")
    clock = pg.time.Clock()
    stats = {"episodes": 1, "wins": 0, "win_rate": 0.0, "step": 0,
             "slippery": is_slippery, "speed": speed}
    done = False
    t_accum = 0.0
    delay = max(0.03, 0.2 / max(0.25, min(4.0, speed)))  # frame pacing

    while True:
        # events
        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); env.close(); sys.exit(0)
            if e.type == pg.KEYDOWN:
                if e.key in (pg.K_ESCAPE, pg.K_q): pg.quit(); env.close(); sys.exit(0)
                if e.key == pg.K_SPACE: autoplay = not autoplay
                if e.key == pg.K_r:
                    s, _ = env.reset(); step = 0; done = False
                if e.key in (pg.K_PLUS, pg.K_EQUALS): speed = min(4.0, speed + 0.25)
                if e.key == pg.K_MINUS: speed = max(0.25, speed - 0.25)
        stats["speed"] = speed
        delay = max(0.03, 0.2 / speed)

        # act
        if autoplay and not done:
            a = int(np.argmax(Q[s]))
            ns, r, term, trunc, _ = env.step(a)
            done = term or trunc
            s = ns
            step += 1
            stats["step"] = step
            if done:
                if r > 0: wins += 1
                stats["episodes"] += 1
                stats["wins"] = wins
                stats["win_rate"] = wins / max(1, stats["episodes"]-1)
                # brief pause then reset
                pg.time.wait(400)
                s, _ = env.reset(); step = 0; done = False

        # draw
        agent_rc = idx_to_rc(s, 4)
        draw_board(screen, desc, None, agent_rc, stats, tile=tile, pad=pad)
        pg.display.flip()
        clock.tick(60)
        time.sleep(delay)

# ---------- main ----------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=5000, help="Q-learning training episodes")
    ap.add_argument("--slippery", action="store_true", help="Use stochastic FrozenLake")
    ap.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    args = ap.parse_args()

    print("Training Q-learning…")
    Q = train_q_learning(episodes=args.episodes, is_slippery=args.slippery)
    print("Launching visualizer… (SPACE to pause, +/- to change speed)")
    eval_episode(Q, is_slippery=args.slippery, autoplay=True, speed=args.speed)
