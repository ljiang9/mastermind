#!/usr/bin/env python3
"""Mastermind 密码破解游戏：4 孔 6 色，10 次机会。

规则：电脑随机生成 4 颗珠子的密码（颜色可重复）。
每猜一次，得到两类反馈：
  黑 peg（●）：颜色和位置都对；
  白 peg（○）：颜色对但位置不对（按去重规则结算，先配对黑 peg，再配对白 peg）。

颜色：R 红 / B 蓝 / G 绿 / Y 黄 / O 橙 / P 紫。
"""

import argparse
import random
import secrets
import sys
from collections import Counter

COLORS = "RBGYOP"
COLOR_NAMES = {"R": "红", "B": "蓝", "G": "绿", "Y": "黄", "O": "橙", "P": "紫"}
PEGS = 4
MAX_TRIES = 10


def score(code: str, guess: str) -> tuple[int, int]:
    """计算反馈 (black, white)。

    先结算黑 peg：同位置同颜色；再结算白 peg：在剩余珠子中按颜色
    取交集（处理重复色，保证一颗密码珠只对应一次反馈）。
    """
    black = sum(c == g for c, g in zip(code, guess))
    leftover = Counter()
    leftover_guess = Counter()
    for c, g in zip(code, guess):
        if c != g:
            leftover[c] += 1
            leftover_guess[g] += 1
    white = sum(min(leftover[color], leftover_guess[color]) for color in COLORS)
    return black, white


def random_code() -> str:
    return "".join(secrets.choice(COLORS) for _ in range(PEGS))


def parse_guess(raw: str) -> str | None:
    """规范化一次输入；返回 4 字母大写猜测，无效返回 None。"""
    guess = raw.strip().upper()
    if len(guess) != PEGS or any(ch not in COLORS for ch in guess):
        return None
    return guess


def solve(code: str, first_guess: str = "RRBB", verbose: bool = True) -> list[tuple[str, tuple[int, int]]]:
    """Knuth 极小极大求解演示（返回 [(猜测, 反馈), ...]）。

    候选集 S = 所有可能的密码；每次在全部 1296 种猜法中挑出让
    “最坏剩余候选数”最小的那一个（Knuth 1977），理论上 ≤ 5 步。
    候选数 < 500 时才做完整极小极大加速；演示用。
    """
    from itertools import product

    all_guesses = ["".join(p) for p in product(COLORS, repeat=PEGS)]
    candidates = list(all_guesses)
    history = []
    guess = first_guess
    while True:
        black, white = score(code, guess)
        history.append((guess, (black, white)))
        if verbose:
            print(f"第 {len(history)} 步：猜 {guess} → {black} 黑 {white} 白")
        if black == PEGS:
            break
        candidates = [c for c in candidates if score(c, guess) == (black, white)]
        guess = _knuth_next(all_guesses, candidates)
    return history


def _knuth_next(all_guesses: list[str], candidates: list[str]) -> str:
    """极小极大：在全部猜法中选最坏情况下剩余候选最少的。"""
    best, best_score = candidates[0], None
    for g in all_guesses:
        buckets: dict[tuple[int, int], int] = {}
        for c in candidates:
            key = score(c, g)
            buckets[key] = buckets.get(key, 0) + 1
        worst = max(buckets.values())
        # 平局优先选仍是候选的猜法（可能就是答案）
        prefer = 0 if g in candidates else 1
        key = (worst, prefer)
        if best_score is None or key < best_score:
            best, best_score = g, key
    return best


def play_interactive(code: str | None = None) -> int:
    code = code or random_code()
    print("=== Mastermind 密码破解 ===")
    print(f"颜色：{', '.join(f'{c}={COLOR_NAMES[c]}' for c in COLORS)}")
    print(f"猜出 4 颗珠子的顺序，共 {MAX_TRIES} 次机会。")
    print("反馈：●黑 = 颜色位置都对；○白 = 颜色对位置错（去重结算）\n")

    for turn in range(1, MAX_TRIES + 1):
        while True:
            raw = input(f"第 {turn}/{MAX_TRIES} 次猜（4 个字母，如 RBGY）：")
            guess = parse_guess(raw)
            if guess is None:
                print(f"  无效输入：请用 {PEGS} 个字母，只允许 {COLORS}")
                continue
            break
        black, white = score(code, guess)
        marks = "●" * black + "○" * white
        print(f"  {guess} → {black} 黑 {white} 白 {marks or '(无)'}")
        if black == PEGS:
            print(f"\n🎉 破解成功！用了 {turn} 次。密码就是 {code}。")
            return 0
    print(f"\n😢 机会用完。密码是 {code}。")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mastermind 密码破解游戏")
    parser.add_argument("--code", metavar="CODE", help="固定密码用于测试，如 RGBY")
    parser.add_argument("--auto", action="store_true", help="自动求解演示（Knuth 极小极大）")
    parser.add_argument("--seed", type=int, help="随机种子（测试用）")
    args = parser.parse_args(argv)

    if args.code:
        code = parse_guess(args.code)
        if code is None:
            print(f"错误：--code 必须是 {PEGS} 个字母，只允许 {COLORS}", file=sys.stderr)
            return 2
    else:
        if args.seed is not None:
            random.seed(args.seed)
        code = "".join(random.choice(COLORS) for _ in range(PEGS))

    if args.auto:
        history = solve(code)
        print(f"\n✅ 共用 {len(history)} 步破解密码 {code}（上限 {MAX_TRIES} 步）")
        return 0 if len(history) <= MAX_TRIES else 1
    return play_interactive(code)


if __name__ == "__main__":
    sys.exit(main())
