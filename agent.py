import random
from typing import List, Union, Optional

class Agent:
    """
    智能体基类，所有策略必须继承此类并实现decide方法
    """
    def __init__(self, name: Optional[str] = None):
        """初始化智能体"""
        self.name = name if name else self.__class__.__name__
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        """
        根据历史决策下一步行动
        
        参数:
            history_self: 自己的历史动作列表
            history_opponent: 对手的历史动作列表
            
        返回:
            'beat' 或 'still'
        """
        raise NotImplementedError("必须在子类中实现decide方法")
    
    def reset(self):
        """重置智能体状态，每场对抗前调用"""
        pass
    
    def __str__(self):
        return self.name


class TitForTatAgent(Agent):
    """以牙还牙策略: 第一回合选择still, 之后模仿对手上一回合的选择"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:  # 第一回合
            return "still"
        return history_opponent[-1]  # 复制对手上一回合的选择


class AlwaysBeatAgent(Agent):
    """始终选择beat的策略"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        return "beat"


class AlwaysStillAgent(Agent):
    """始终选择still的策略"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        return "still"


class RandomAgent(Agent):
    """随机策略"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        return random.choice(["beat", "still"])


class ForgivingTitForTatAgent(Agent):
    """宽容的以牙还牙: 只有当对手在最近3轮中有至少2次beat才会选择beat"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if len(history_opponent) < 3:
            return "still"
        
        # 检查最近三轮
        if history_opponent[-3:].count("beat") >= 2:
            return "beat"
        else:
            return "still"


class GradualAgent(Agent):
    """渐进式报复: 探测对手背叛倾向并做出相应的报复"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.revenge_counter = 0  # 报复计数器
        self.defect_count = 0    # 对手背叛次数
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"
            
        # 检查对手是否在上一轮背叛
        if history_opponent[-1] == "beat" and history_self[-1] == "still":
            self.defect_count += 1
            self.revenge_counter = self.defect_count  # 设置报复次数与背叛总次数相等
        
        # 如果在报复模式中，继续背叛
        if self.revenge_counter > 0:
            self.revenge_counter -= 1
            return "beat"
        
        return "still"
    
    def reset(self):
        """重置报复状态"""
        self.revenge_counter = 0
        self.defect_count = 0


class PatternDetectorAgent(Agent):
    """模式检测智能体: 尝试检测对手的行为模式"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.pattern_length = 3  # 尝试识别的模式长度
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if len(history_opponent) < self.pattern_length + 1:
            return "still"  # 开始时合作
        
        # 尝试检测对手最近行为是否有可识别模式
        recent_pattern = history_opponent[-self.pattern_length:]
        
        # 查找历史中类似的模式
        for i in range(len(history_opponent) - self.pattern_length * 2):
            if history_opponent[i:i+self.pattern_length] == recent_pattern:
                # 如果找到相同模式，预测下一步
                prediction = history_opponent[i+self.pattern_length]
                # 如果预测对手会背叛，提前背叛
                if prediction == "beat":
                    return "beat"
        
        # 默认为合作
        return "still"


class AdaptiveAgent(Agent):
    """自适应智能体: 根据对手过去行为调整策略"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.cooperation_rate = 0.0  # 对手合作率
        self.total_rounds = 0
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"
        
        # 统计对手合作率
        still_count = history_opponent.count("still")
        self.total_rounds = len(history_opponent)
        self.cooperation_rate = still_count / self.total_rounds if self.total_rounds > 0 else 0
        
        # 根据对手的合作倾向决定策略
        if self.cooperation_rate >= 0.7:  # 对手很合作
            return "still"  # 我们也合作
        elif self.cooperation_rate <= 0.3:  # 对手不太合作
            return "beat"   # 我们也背叛
        else:  # 对手行为不确定
            # 使用TitForTat策略
            return history_opponent[-1]
    
    def reset(self):
        """重置统计数据"""
        self.cooperation_rate = 0.0
        self.total_rounds = 0


class TwoCoopOneDefectAgent(Agent):
    """两报一背叛策略: 智能体首先合作两次，然后背叛一次，循环往复"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.counter = 0  # 用于追踪循环位置
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        # 更新计数器
        self.counter = (self.counter + 1) % 3
        
        # 前两步合作，第三步背叛
        if self.counter < 2:
            return "still"
        else:
            return "beat"
    
    def reset(self):
        """重置计数器"""
        self.counter = 0


class RewardPunishmentAgent(Agent):
    """助长惩罚策略: 对合作行为奖励，对背叛行为惩罚"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.punishment_counter = 0  # 惩罚计数器
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
        
        # 根据对方上一次行为决定
        if history_opponent[-1] == "still":
            # 对方合作，我们也合作，奖励合作行为
            self.punishment_counter = max(0, self.punishment_counter - 1)  # 减少惩罚计数
            return "still"
        else:
            # 对方背叛，我们进行连续惩罚
            self.punishment_counter = min(5, self.punishment_counter + 2)  # 增加惩罚计数，但有上限
            
            # 如果惩罚计数器大于0，执行惩罚
            if self.punishment_counter > 0:
                return "beat"
            return "still"
    
    def reset(self):
        """重置惩罚计数器"""
        self.punishment_counter = 0


class EscapeTigerAgent(Agent):
    """虎口脱险策略: 在连续合作后突然背叛一次，观察对方反应"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.coop_streak = 0  # 连续合作计数
        self.test_mode = False  # 是否处于试探模式
        self.exploit_mode = False  # 是否处于利用模式
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
        
        # 如果上一轮双方都合作，增加合作计数
        if history_self and history_self[-1] == "still" and history_opponent[-1] == "still":
            self.coop_streak += 1
        else:
            self.coop_streak = 0
            
        # 如果在试探模式中
        if self.test_mode:
            self.test_mode = False
            # 检查对方对我们的试探背叛的反应
            if history_opponent[-1] == "still":
                # 对方没有惩罚我们的背叛，进入利用模式
                self.exploit_mode = True
                return "beat"
            else:
                # 对方惩罚了我们，恢复合作
                self.exploit_mode = False
                return "still"
        
        # 如果在利用模式中，继续背叛
        if self.exploit_mode:
            # 检查对方是否开始惩罚我们
            if history_opponent[-1] == "beat":
                # 对方开始惩罚，退出利用模式
                self.exploit_mode = False
                return "still"
            else:
                # 继续利用
                return "beat"
        
        # 如果连续合作达到阈值，进入试探模式
        if self.coop_streak >= 5:
            self.test_mode = True
            self.coop_streak = 0
            return "beat"  # 进行试探性背叛
        
        # 正常情况下保持合作
        return "still"
    
    def reset(self):
        """重置状态"""
        self.coop_streak = 0
        self.test_mode = False
        self.exploit_mode = False


class InchingAgent(Agent):
    """得寸进尺策略: 在对方合作时逐渐增加背叛，在对方背叛时减少背叛"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.defect_rate = 0.0  # 背叛概率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        # 根据对方上一轮行为调整背叛概率
        if history_opponent[-1] == "still":
            # 对方合作，我们增加一点背叛概率
            self.defect_rate = min(0.7, self.defect_rate + 0.05)
        else:
            # 对方背叛，我们迅速降低背叛概率
            self.defect_rate = max(0.0, self.defect_rate - 0.2)
        
        # 按背叛概率决定行动
        if random.random() < self.defect_rate:
            return "beat"
        return "still"
    
    def reset(self):
        """重置背叛概率"""
        self.defect_rate = 0.0


class TrustBuildingAgent(Agent):
    """信任建立策略: 初始保持合作建立信任，识别并惩罚背叛"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.trust_level = 1.0  # 信任级别，初始为完全信任
        self.forgiveness = 0.1  # 宽恕速率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        # 前3轮强制合作，建立信任关系
        if len(history_opponent) < 3:
            return "still"
            
        # 根据对方行为更新信任度
        if history_opponent and history_opponent[-1] == "beat":
            # 对方背叛，大幅降低信任度
            self.trust_level = max(0.0, self.trust_level - 0.3)
        else:
            # 对方合作，缓慢恢复信任度
            self.trust_level = min(1.0, self.trust_level + self.forgiveness)
        
        # 根据信任度决定是否合作
        if random.random() < self.trust_level:
            return "still"  # 信任时合作
        else:
            return "beat"   # 不信任时背叛
    
    def reset(self):
        """重置信任度"""
        self.trust_level = 1.0


class GrudgeAgent(Agent):
    """记仇策略: 以合作开始, 如果对手有过beat则一直beat"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.grudge = False  # 是否记仇
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        # 检查对手是否有过背叛
        if "beat" in history_opponent:
            self.grudge = True
            
        # 如果记仇，则一直背叛
        if self.grudge:
            return "beat"
            
        return "still"
    
    def reset(self):
        """重置记仇状态"""
        self.grudge = False


class PunishmentEscalationAgent(Agent):
    """惩罚策略: 以still开始, 以以牙还牙为模版, 但会随着对手beat次数增加惩罚力度"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.opponent_defect_count = 0  # 对手背叛计数
        self.punishment_streak = 0  # 当前连续惩罚次数
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        # 如果处于惩罚模式，继续惩罚
        if self.punishment_streak > 0:
            self.punishment_streak -= 1
            return "beat"
            
        # 如果对手上轮背叛，开始惩罚
        if history_opponent[-1] == "beat":
            self.opponent_defect_count += 1
            # 惩罚次数与对手总背叛次数有关
            self.punishment_streak = min(5, self.opponent_defect_count // 2)
            return "beat"
            
        return "still"
    
    def reset(self):
        """重置惩罚状态"""
        self.opponent_defect_count = 0
        self.punishment_streak = 0


class ConsensusAgent(Agent):
    """共识策略: 上一步选择相同时合作, 上一步选择不同时2/7概率合作"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_self or not history_opponent:
            return "still"  # 首轮默认合作
            
        # 检查上一轮双方是否选择相同
        if history_self[-1] == history_opponent[-1]:
            # 选择相同，合作
            return "still"
        else:
            # 选择不同，2/7概率合作
            return "still" if random.random() < 2/7 else "beat"


class ProbeAgent(Agent):
    """试探策略: 以以牙还牙开始, 但合作概率逐渐降低至0.5"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.cooperation_prob = 1.0  # 初始合作概率为100%
        self.rounds = 0
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        self.rounds += 1
        
        # 逐渐降低合作概率，最低至0.5
        if self.cooperation_prob > 0.5:
            self.cooperation_prob = max(0.5, 1.0 - 0.01 * self.rounds)
            
        # 以牙还牙基础上加入降低的合作概率
        tit_for_tat_action = history_opponent[-1]
        
        # 如果基础策略是合作，但按概率变为背叛
        if tit_for_tat_action == "still" and random.random() > self.cooperation_prob:
            return "beat"
        
        return tit_for_tat_action
    
    def reset(self):
        """重置状态"""
        self.cooperation_prob = 1.0
        self.rounds = 0


class CappedAgent(Agent):
    """封顶策略: 对手合作时0.9概率合作, 对手beat时总是beat"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        # 根据对手上一轮行为决定
        if history_opponent[-1] == "still":
            # 对手合作，90%概率合作
            return "still" if random.random() < 0.9 else "beat"
        else:
            # 对手背叛，必定背叛
            return "beat"


class ShortMemoryAgent(Agent):
    """短期记忆: 根据前三次的合作次数决定合作概率(0.3-0.7)"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.coop_prob = 0.7  # 初始合作概率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if len(history_opponent) < 3:
            return "still" if random.random() < self.coop_prob else "beat"
            
        # 统计前三次对手合作次数
        recent_actions = history_opponent[-3:]
        coop_count = recent_actions.count("still")
        
        # 根据合作次数调整概率，范围在0.3-0.7之间
        self.coop_prob = 0.3 + (coop_count / 3) * 0.4
        
        # 按概率决定是否合作
        return "still" if random.random() < self.coop_prob else "beat"
    
    def reset(self):
        """重置合作概率"""
        self.coop_prob = 0.7


class MediumMemoryAgent(Agent):
    """近期记忆: 根据前15次的合作次数决定合作概率(0.2-0.8)"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.coop_prob = 0.7  # 初始合作概率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still" if random.random() < self.coop_prob else "beat"
            
        # 统计近期对手合作次数（最多15轮）
        lookback = min(15, len(history_opponent))
        recent_actions = history_opponent[-lookback:]
        coop_count = recent_actions.count("still")
        
        # 根据合作次数调整概率，范围在0.2-0.8之间
        self.coop_prob = 0.2 + (coop_count / lookback) * 0.6
        
        # 按概率决定是否合作
        return "still" if random.random() < self.coop_prob else "beat"
    
    def reset(self):
        """重置合作概率"""
        self.coop_prob = 0.7


class LongMemoryAgent(Agent):
    """长期记忆: 根据所有的合作次数决定合作概率(0.2-0.8)"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.coop_prob = 0.7  # 初始合作概率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still" if random.random() < self.coop_prob else "beat"
            
        # 统计所有对手合作次数
        coop_count = history_opponent.count("still")
        
        # 根据历史合作比例调整概率，范围在0.2-0.8之间
        self.coop_prob = 0.2 + (coop_count / len(history_opponent)) * 0.6
        
        # 按概率决定是否合作
        return "still" if random.random() < self.coop_prob else "beat"
    
    def reset(self):
        """重置合作概率"""
        self.coop_prob = 0.7


class WinStayLoseShiftAgent(Agent):
    """赢则保持，输则改变策略"""
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_self or not history_opponent:
            return "still"  # 第一轮默认合作
        
        last_action = history_self[-1]
        
        # 简单判断上一轮是否"赢"
        # 这里简化处理，如果对方选择still则认为自己"赢"了
        if history_opponent[-1] == "still":
            return last_action  # 赢则保持
        else:
            # 输则改变
            return "beat" if last_action == "still" else "still"


class TitForTatStartMediumMemoryAgent(Agent):
    """以牙还牙开始的近期记忆: 前5轮采用以牙还牙，之后根据近期记忆调整策略"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.coop_prob = 0.7  # 初始合作概率
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        # 前5轮使用以牙还牙
        if len(history_opponent) < 5:
            if not history_opponent:
                return "still"
            return history_opponent[-1]
        
        # 之后使用中期记忆策略
        # 统计近期对手合作次数（最多15轮）
        lookback = min(15, len(history_opponent))
        recent_actions = history_opponent[-lookback:]
        coop_count = recent_actions.count("still")
        
        # 根据合作次数调整概率，范围在0.2-0.8之间
        self.coop_prob = 0.2 + (coop_count / lookback) * 0.6
        
        # 按概率决定是否合作
        return "still" if random.random() < self.coop_prob else "beat"
    
    def reset(self):
        """重置合作概率"""
        self.coop_prob = 0.7


class AdaptivePunishmentAgent(Agent):
    """适应性惩罚: 根据对手背叛倾向动态调整惩罚强度"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.punishment_level = 1  # 初始惩罚级别
        self.defect_count = 0     # 对手背叛总次数
        self.rounds = 0           # 总回合数
        self.punishment_streak = 0  # 当前连续惩罚次数
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        self.rounds += 1
        
        # 如果处于惩罚模式，继续惩罚
        if self.punishment_streak > 0:
            self.punishment_streak -= 1
            return "beat"
            
        # 如果对手上轮背叛，更新统计并考虑惩罚
        if history_opponent[-1] == "beat":
            self.defect_count += 1
            
            # 计算背叛比例
            defect_rate = self.defect_count / self.rounds
            
            # 根据背叛比例动态调整惩罚级别
            if defect_rate > 0.5:
                self.punishment_level = 3  # 严厉惩罚
            elif defect_rate > 0.3:
                self.punishment_level = 2  # 中等惩罚
            else:
                self.punishment_level = 1  # 轻微惩罚
                
            # 设置惩罚持续时间
            self.punishment_streak = self.punishment_level
            return "beat"
            
        return "still"
    
    def reset(self):
        """重置状态"""
        self.punishment_level = 1
        self.defect_count = 0
        self.rounds = 0
        self.punishment_streak = 0


class GradualForgivingAgent(Agent):
    """渐进宽恕: 会渐进式惩罚对手，但也会逐渐宽恕"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.revenge_counter = 0  # 报复计数器
        self.forgiveness = 0      # 宽恕计数器（在固定回合后宽恕）
        self.rounds_since_defect = 0  # 距离上次被背叛的回合数
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"
        
        # 更新距离上次被背叛的回合数
        if history_opponent[-1] == "beat":
            self.rounds_since_defect = 0
        else:
            self.rounds_since_defect += 1
            
        # 如果对手背叛，设置报复和宽恕计时
        if history_opponent[-1] == "beat" and history_self[-1] == "still":
            # 背叛次数增加，报复也增加
            self.revenge_counter = 2  # 背叛后连续惩罚2次
            self.forgiveness = 5      # 5回合后宽恕
        
        # 如果在报复模式，继续惩罚
        if self.revenge_counter > 0:
            self.revenge_counter -= 1
            return "beat"
        
        # 如果宽恕计时结束，完全宽恕
        if self.rounds_since_defect >= self.forgiveness:
            self.forgiveness = 0  # 重置宽恕计时
            return "still"
        
        # 根据距离上次背叛的时间，增加合作概率
        coop_prob = min(0.9, 0.5 + self.rounds_since_defect * 0.1)
        
        # 按概率决定是否合作
        return "still" if random.random() < coop_prob else "beat"
    
    def reset(self):
        """重置状态"""
        self.revenge_counter = 0
        self.forgiveness = 0
        self.rounds_since_defect = 0


class PatternMatchingTitForTatAgent(Agent):
    """模式匹配以牙还牙: 尝试识别对手模式并进行反制"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.pattern_length = 4  # 尝试识别的模式长度
        self.min_occurrences = 2  # 模式至少出现次数才会考虑
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_opponent:
            return "still"  # 首轮默认合作
            
        # 如果历史足够长，尝试识别模式
        if len(history_opponent) >= self.pattern_length * 3:
            # 检查对手最近的行为模式
            pattern = self._find_best_pattern(history_opponent)
            if pattern:
                # 预测下一步，如果预计对方会背叛，我们也背叛
                next_action = self._predict_next_action(history_opponent, pattern)
                if next_action == "beat":
                    return "beat"
        
        # 默认使用以牙还牙策略
        return history_opponent[-1]
    
    def _find_best_pattern(self, history: List[str]) -> str:
        """查找历史中最常出现的模式"""
        if len(history) < self.pattern_length * 2:
            return None
            
        # 最近行为
        recent = ''.join(['1' if a == "beat" else '0' for a in history[-self.pattern_length:]])
        
        # 在之前的历史中查找相同模式
        full_history = ''.join(['1' if a == "beat" else '0' for a in history])
        occurrences = 0
        
        # 从头开始搜索，跳过最后一个模式（我们当前正在判断的）
        for i in range(len(full_history) - self.pattern_length * 2 + 1):
            if full_history[i:i+self.pattern_length] == recent:
                occurrences += 1
                
        # 如果模式出现次数达到阈值，认为模式有效
        if occurrences >= self.min_occurrences:
            return recent
        return None
    
    def _predict_next_action(self, history: List[str], pattern: str) -> str:
        """根据找到的模式预测对手下一步动作"""
        full_history = ''.join(['1' if a == "beat" else '0' for a in history])
        
        # 查找所有模式出现的位置
        positions = []
        for i in range(len(full_history) - len(pattern)):
            if full_history[i:i+len(pattern)] == pattern:
                positions.append(i)
        
        # 统计模式后的动作
        next_actions = []
        for pos in positions:
            if pos + len(pattern) < len(full_history):
                next_actions.append(full_history[pos + len(pattern)])
        
        # 如果有足够数据，预测最可能的下一步
        if next_actions:
            # 计算背叛概率
            defect_prob = next_actions.count('1') / len(next_actions)
            # 如果背叛概率大于50%，预测对方会背叛
            if defect_prob > 0.5:
                return "beat"
        
        return "still"


class FrequencyAnalysisAgent(Agent):
    """频率分析智能体: 分析对手背叛频率，根据不同情境调整策略"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        # 追踪在我选择still后对方的背叛频率
        self.after_still_defect = 0
        self.after_still_total = 0
        # 追踪在我选择beat后对方的背叛频率
        self.after_beat_defect = 0
        self.after_beat_total = 0
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        # 更新统计数据
        if len(history_self) > 1 and len(history_opponent) > 1:
            if history_self[-2] == "still":
                self.after_still_total += 1
                if history_opponent[-1] == "beat":
                    self.after_still_defect += 1
            else:  # history_self[-2] == "beat"
                self.after_beat_total += 1
                if history_opponent[-1] == "beat":
                    self.after_beat_defect += 1
        
        # 前几轮默认合作
        if len(history_opponent) < 5:
            return "still"
            
        # 计算不同情境下的背叛概率
        after_still_defect_rate = self.after_still_defect / max(1, self.after_still_total)
        after_beat_defect_rate = self.after_beat_defect / max(1, self.after_beat_total)
        
        # 策略选择
        # 如果对手在我们合作后经常背叛，我们选择背叛
        if after_still_defect_rate > 0.6:
            return "beat"
        # 如果对手在我们背叛后经常背叛（报复），但在我们合作后不背叛，选择合作
        elif after_beat_defect_rate > after_still_defect_rate + 0.3:
            return "still"
        # 如果对手不管我们做什么都倾向于背叛，我们也背叛
        elif after_still_defect_rate > 0.4 and after_beat_defect_rate > 0.4:
            return "beat"
        # 如果我们判断不出明显的模式，使用以牙还牙策略
        else:
            if not history_opponent:
                return "still"
            return history_opponent[-1]
    
    def reset(self):
        """重置统计数据"""
        self.after_still_defect = 0
        self.after_still_total = 0
        self.after_beat_defect = 0
        self.after_beat_total = 0


class RhythmDetectorAgent(Agent):
    """节奏检测智能体: 尝试识别对手是否有固定的合作/背叛节奏"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.detected_rhythm = None  # 检测到的节奏
        self.rhythm_confidence = 0   # 节奏的置信度
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if len(history_opponent) < 6:
            return "still"  # 前几轮默认合作
            
        # 尝试检测对手是否有固定节奏
        if not self.detected_rhythm:
            # 检查常见的固定周期模式
            rhythms = [
                ["beat"],  # 总是背叛
                ["still"],  # 总是合作
                ["beat", "still"],  # 交替背叛和合作
                ["still", "still", "beat"],  # 两合作一背叛
                ["still", "beat", "beat"]   # 一合作两背叛
            ]
            
            for rhythm in rhythms:
                confidence = self._check_rhythm(history_opponent, rhythm)
                if confidence > 0.7 and confidence > self.rhythm_confidence:
                    self.detected_rhythm = rhythm
                    self.rhythm_confidence = confidence
        
        # 如果检测到节奏，根据预测采取最优应对
        if self.detected_rhythm:
            # 预测对手下一步
            next_idx = len(history_opponent) % len(self.detected_rhythm)
            predicted_next = self.detected_rhythm[next_idx]
            
            # 如果预测对手会背叛，我们也背叛
            if predicted_next == "beat":
                return "beat"
            else:
                # 如果检测到对手总是合作，偶尔背叛一下
                if len(self.detected_rhythm) == 1 and self.detected_rhythm[0] == "still":
                    if random.random() < 0.1:  # 10%概率背叛
                        return "beat"
                return "still"
        
        # 如果没有检测到明确节奏，使用以牙还牙策略
        if not history_opponent:
            return "still"
        return history_opponent[-1]
    
    def _check_rhythm(self, history: List[str], pattern: List[str]) -> float:
        """检查历史中是否符合给定节奏模式，返回置信度"""
        if not history or not pattern:
            return 0.0
            
        matches = 0
        total = 0
        
        # 根据模式的周期检查历史
        for i in range(len(history)):
            expected = pattern[i % len(pattern)]
            if history[i] == expected:
                matches += 1
            total += 1
            
        return matches / total if total > 0 else 0.0
    
    def reset(self):
        """重置检测状态"""
        self.detected_rhythm = None
        self.rhythm_confidence = 0


class HybridAgent(Agent):
    """混合策略: 根据对手表现动态切换不同策略"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.strategies = {
            "tit_for_tat": lambda h_self, h_opp: h_opp[-1] if h_opp else "still",
            "always_beat": lambda h_self, h_opp: "beat",
            "always_still": lambda h_self, h_opp: "still"
        }
        self.current_strategy = "tit_for_tat"  # 默认策略
        self.strategy_performance = {s: 0 for s in self.strategies}  # 策略表现评分
        self.rounds = 0
        self.last_switch = 0  # 上次切换策略的回合
        
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        self.rounds += 1
        
        # 每10轮考虑切换一次策略
        if self.rounds - self.last_switch >= 10:
            self._evaluate_strategies(history_self, history_opponent)
            self.last_switch = self.rounds
            
        # 使用当前最佳策略
        return self.strategies[self.current_strategy](history_self, history_opponent)
    
    def _evaluate_strategies(self, history_self: List[str], history_opponent: List[str]):
        """评估不同策略的表现，选择最佳策略"""
        if len(history_opponent) < 10:
            return  # 历史不足，保持当前策略
            
        # 获取最近10轮历史
        recent_opponent = history_opponent[-10:]
        recent_self = history_self[-10:]
        
        # 重置评分
        self.strategy_performance = {s: 0 for s in self.strategies}
        
        # 模拟每种策略在最近10轮的表现
        for strategy_name, strategy_func in self.strategies.items():
            score = 0
            
            # 假设我们一直使用该策略，评估得分
            for i in range(10):
                if i == 0 and len(history_opponent) <= 10:
                    # 第一轮没有前置历史
                    action = "still"
                else:
                    # 使用策略决定动作
                    prev_self = recent_self[:i] if i > 0 else history_self[-(10+i):-10]
                    prev_opp = recent_opponent[:i] if i > 0 else history_opponent[-(10+i):-10]
                    action = strategy_func(prev_self, prev_opp)
                    
                # 根据我方动作和对方实际动作计算得分
                opp_action = recent_opponent[i]
                if action == "still" and opp_action == "still":
                    # 双方合作
                    score += 3  # 假设wwin=3
                elif action == "beat" and opp_action == "still":
                    # 我背叛对方合作
                    score += 5  # 假设beat=5
                elif action == "still" and opp_action == "beat":
                    # 我合作对方背叛
                    score += -2  # 假设beaten=-2
                else:  # action == "beat" and opp_action == "beat"
                    # 双方都背叛
                    score += 1  # 假设llost=1
                    
            # 更新策略评分
            self.strategy_performance[strategy_name] = score
            
        # 选择得分最高的策略
        self.current_strategy = max(
            self.strategy_performance.items(),
            key=lambda x: x[1]
        )[0]
    
    def reset(self):
        """重置状态"""
        self.current_strategy = "tit_for_tat"
        self.strategy_performance = {s: 0 for s in self.strategies}
        self.rounds = 0
        self.last_switch = 0


class PavlovAgent(Agent):
    """巴甫洛夫策略: 上回合获益则保持策略，否则改变策略"""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.last_payoff = None  # 上一轮的收益
        self.default_action = "still"  # 第一轮默认行动
    
    def decide(self, history_self: List[str], history_opponent: List[str]) -> str:
        if not history_self or not history_opponent:
            return self.default_action
            
        # 计算上一轮的收益
        last_action_self = history_self[-1]
        last_action_opp = history_opponent[-1]
        
        if last_action_self == "still" and last_action_opp == "still":
            # 双方合作，保持合作
            return "still"
        elif last_action_self == "beat" and last_action_opp == "still":
            # 我背叛对方合作，继续背叛
            return "beat"
        elif last_action_self == "still" and last_action_opp == "beat":
            # 我合作对方背叛，改变策略
            return "beat"
        else:  # last_action_self == "beat" and last_action_opp == "beat"
            # 双方都背叛，改变策略
            return "still"
            
    def reset(self):
        """重置状态"""
        self.last_payoff = None