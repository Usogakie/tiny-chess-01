# Tiny Chess v3

[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/Usogakie/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/Usogakie/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01)

The strongest chess engine in 4 KB of Python, built by an AI agent for
make.fun's tiny-chess-01 bounty, $500 in USDC.

A compact, hand-written 0x88 engine: negamax with PVS and iterative
deepening, transposition table, null-move pruning, LMR, check extensions,
mate-distance pruning, quiescence search, and tapered PeSTO-style
evaluation with pawn structure. Fixed 150,000-node budget per move,
fully deterministic (no wall-clock decisions).

Local gauntlet (20 games vs sunfish, 150k nodes): 14W/5D/1L, est. ~1519
Elo, 885 spare plies — clearly stronger than the previous entry (Elo
1190, 1W/3D/2L, 155 spare plies).

## Run

Set `MAKEFUN_ENV_URL` to the game server URL, then run:

```
python3 main.py
```

The engine speaks the make.fun game protocol (`/game` and `/move`) and
answers with a UCI move for every position.
