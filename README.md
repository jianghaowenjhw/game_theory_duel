# Game_Theory_Duel

# 博弈论智能体比赛

这个项目实现了一个博弈论框架，用于模拟和比较不同策略智能体在特定博弈规则下的表现。

## 博弈规则

这个框架基于一个类似囚徒困境的博弈规则：

- 每轮博弈中，两个参与者各自做出一个选择：`beat`（背叛）或`still`（合作）
- 根据双方的选择，分别获得不同的得分：
  - 双方都选择`beat`：双方各得`llost`分
  - 双方都选择`still`：双方各得`wwin`分
  - 一方选择`beat`，另一方选择`still`：选择`beat`的一方得`beat`分，选择`still`的一方得`beaten`分
- 这些参数满足关系：`beat > wwin > llost > beaten`

## 项目结构

- `config.py`: 游戏配置类，管理所有博弈参数
- `agent.py`: 智能体基类和各种策略实现
- `match.py`: 对抗逻辑模块，负责执行单场或多场对抗
- `tournament.py`: 大比赛组织模块，负责执行所有智能体的两两对抗和排名
- `main.py`: 主程序入口，提供命令行接口

## 可用智能体

项目实现了以下几种不同策略的智能体：

### 基础策略
1. **以牙还牙 (TitForTatAgent)**: 初始选择合作，后续模仿对手的上一轮选择
2. **总是背叛 (AlwaysBeatAgent)**: 永远选择背叛
3. **总是合作 (AlwaysStillAgent)**: 永远选择合作
4. **随机策略 (RandomAgent)**: 随机选择背叛或合作
5. **赢则保持输则改变 (WinStayLoseShiftAgent)**: 如果上一轮获益就保持策略，否则改变策略

### 记忆与惩罚策略
6. **宽容的以牙还牙 (ForgivingTitForTatAgent)**: 只有当对手在最近3轮中有至少2次背叛才会选择背叛
7. **渐进报复 (GradualAgent)**: 随着对手背叛次数增加，报复强度也会增加
8. **记仇策略 (GrudgeAgent)**: 以合作开始，一旦对手有过背叛就永远背叛
9. **惩罚升级 (PunishmentEscalationAgent)**: 以合作开始，以牙还牙为模板，但随着对手背叛次数增加，连续惩罚次数也增加
10. **助长惩罚策略 (RewardPunishmentAgent)**: 对合作行为给予奖励，增加合作频率；对背叛行为施以严厉惩罚
11. **适应性惩罚 (AdaptivePunishmentAgent)**: 根据对手背叛倾向动态调整惩罚强度
12. **渐进宽恕 (GradualForgivingAgent)**: 会逐步惩罚对手，但也会随时间宽恕对手的背叛

### 模式识别与分析策略
13. **模式识别 (PatternDetectorAgent)**: 尝试识别对手的行为模式并提前应对
14. **自适应 (AdaptiveAgent)**: 根据对手的合作倾向调整自己的策略
15. **频率分析 (FrequencyAnalysisAgent)**: 分析对手在不同情境下的背叛频率，据此调整策略
16. **节奏检测 (RhythmDetectorAgent)**: 尝试识别对手是否有固定的合作/背叛节奏并提前应对
17. **模式匹配以牙还牙 (PatternMatchingTitForTatAgent)**: 在以牙还牙基础上增加模式预测能力

### 记忆策略
18. **短期记忆 (ShortMemoryAgent)**: 根据前三次对手行为调整合作概率(0.3-0.7)
19. **中期记忆 (MediumMemoryAgent)**: 根据前15次对手行为调整合作概率(0.2-0.8)
20. **长期记忆 (LongMemoryAgent)**: 根据所有历史行为调整合作概率(0.2-0.8)

### 试探策略
21. **虎口脱险 (EscapeTigerAgent)**: 在连续合作后突然背叛试探对手，若对手不惩罚则利用，否则回到合作
22. **得寸进尺 (InchingAgent)**: 在对手合作时逐渐增加背叛，在对手背叛时减少背叛
23. **试探策略 (ProbeAgent)**: 以以牙还牙开始，合作概率逐渐降低至0.5
24. **两合作一背叛 (TwoCoopOneDefectAgent)**: 智能体首先合作两次，然后背叛一次，循环往复

### 高级策略
25. **信任建立 (TrustBuildingAgent)**: 初始保持合作建立信任，根据信任度决定后续行为
26. **共识策略 (ConsensusAgent)**: 上一步选择相同时合作，选择不同时2/7概率合作
27. **封顶策略 (CappedAgent)**: 对手合作时90%概率合作，对手背叛时总是背叛
28. **以牙还牙开始的中期记忆 (TitForTatStartMediumMemoryAgent)**: 前5轮采用以牙还牙策略，之后使用中期记忆调整策略
29. **混合策略 (HybridAgent)**: 根据对手表现动态切换不同策略，选择最优者
30. **巴甫洛夫策略 (PavlovAgent)**: 双方合作或我方背叛对方合作时保持策略，否则改变策略

## 使用方法

### 命令行参数

```
python main.py [options]

选项:
  --mode {individual,tournament}  比赛模式：个人赛或大比赛 (默认: tournament)
  --beat BEAT                     选择beat且对方选择still时的得分 (默认: 5)
  --wwin WWIN                     双方都选择still时的得分 (默认: 3)
  --llost LLOST                   双方都选择beat时的得分 (默认: 1)  
  --beaten BEATEN                 选择still且对方选择beat时的得分 (默认: 0)
  --rounds ROUNDS                 每场对抗的回合数 (默认: 300)
  --matches MATCHES               每对智能体之间的对抗次数 (默认: 3)
  --agent1 AGENT1                 个人赛智能体1名称 (默认: TitForTatAgent)
  --agent2 AGENT2                 个人赛智能体2名称 (默认: RandomAgent)
  --log LOG                       日志文件路径
```

### 个人赛示例

运行两个指定智能体的对抗：

```bash
python main.py --mode individual --agent1 TitForTatAgent --agent2 PavlovAgent --rounds 200 --matches 5
```

### 大比赛示例

运行所有智能体参与的大比赛：

```bash
python main.py --beat 10 --wwin 5 --llost 2 --beaten -5 --rounds 150 --matches 20
```

## 扩展智能体

要创建新的智能体策略，只需继承`Agent`基类并实现`decide`方法：

```python
from agent import Agent

class MyNewAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name if name else "我的新策略")
        # 初始化其他所需变量
    
    def decide(self, history_self, history_opponent):
        # 根据历史做出决策
        # 返回 "beat" 或 "still"
        return decision
        
    def reset(self):
        # 清空内部状态（如果需要）
        pass
```

## 大比赛评分规则

- 每对智能体进行多场对抗
- 对于每对对抗，取每个智能体的最低得分作为该对抗的得分
- 每个智能体的总得分为其与所有其他智能体对抗得分的平均值
- 根据总得分对所有智能体进行排名