# Mastermind 密码破解

经典逻辑推理游戏：电脑随机生成 4 颗珠子的密码（6 种颜色，可重复），你有 10 次机会猜出它。

## 玩法

- 颜色：`R` 红 / `B` 蓝 / `G` 绿 / `Y` 黄 / `O` 橙 / `P` 紫
- 每次输入 4 个字母猜测（如 `RBGY`）
- 反馈两类：
  - **黑 peg（●）**：颜色和位置都对
  - **白 peg（○）**：颜色对但位置不对（按去重规则结算：先配对黑 peg，剩下的按颜色取交集，一颗密码珠只算一次）

## 运行

```bash
python3 -m mastermind            # 交互游玩
python3 -m mastermind --auto    # Knuth 极小极大自动求解演示
python3 -m mastermind --code RBGY  # 固定密码（调试/测试用）
```

Python 3.10+，仅标准库。

## 求解器说明

`--auto` 采用 Knuth（1977）的极小极大策略：候选集初始为全部 1296 种密码；
每一步在所有猜法中挑选"最坏情况下剩余候选最少"的那一个，理论上 ≤ 5 步必解。

## 许可证

MIT License — Copyright (c) 2026 ljiang9
