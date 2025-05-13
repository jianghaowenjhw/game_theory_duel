import logging
from typing import Tuple, List

from config import GameConfig
from agent import Agent

class MatchResult:
    """单次对抗的结果记录"""
    def __init__(self):
        self.scores_a: List[int] = []  # 每场对抗中智能体A的得分列表
        self.scores_b: List[int] = []  # 每场对抗中智能体B的得分列表
        self.histories_a: List[List[str]] = []  # 每场对抗中智能体A的决策历史
        self.histories_b: List[List[str]] = []  # 每场对抗中智能体B的决策历史
    
    def add_match(self, score_a: int, score_b: int, history_a: List[str], history_b: List[str]):
        """添加一场对抗的结果"""
        self.scores_a.append(score_a)
        self.scores_b.append(score_b)
        self.histories_a.append(history_a.copy())
        self.histories_b.append(history_b.copy())
    
    def get_avg_scores(self) -> Tuple[float, float]:
        """获取平均得分"""
        avg_a = sum(self.scores_a) / len(self.scores_a) if self.scores_a else 0
        avg_b = sum(self.scores_b) / len(self.scores_b) if self.scores_b else 0
        return avg_a, avg_b
    
    def get_min_scores(self) -> Tuple[int, int]:
        """获取最低得分"""
        min_a = min(self.scores_a) if self.scores_a else 0
        min_b = min(self.scores_b) if self.scores_b else 0
        return min_a, min_b
    
    def get_middle_scores(self) -> Tuple[float, float]:
        """获取中位数得分"""
        sorted_a = sorted(self.scores_a)
        sorted_b = sorted(self.scores_b)
        mid_a = sorted_a[len(sorted_a) // 2] if sorted_a else 0
        mid_b = sorted_b[len(sorted_b) // 2] if sorted_b else 0
        return mid_a, mid_b
    
    def get_win_count_info(self) -> str:
        """获取胜负情况统计"""
        win_a = 0
        win_b = 0
        draws = 0
        
        for score_a, score_b in zip(self.scores_a, self.scores_b):
            if score_a > score_b:
                win_a += 1
            elif score_b > score_a:
                win_b += 1
            else:
                draws += 1
        
        return f"A胜:{win_a} B胜:{win_b} 平局:{draws}"
    
    def __str__(self):
        """生成可读的结果字符串"""
        min_a, min_b = self.get_min_scores()
        avg_a, avg_b = self.get_avg_scores()
        win_info = self.get_win_count_info()
        return (f"对抗次数: {len(self.scores_a)}\n"
                f"A得分: {self.scores_a}，平均: {avg_a:.2f}，最低: {min_a}\n" 
                f"B得分: {self.scores_b}，平均: {avg_b:.2f}，最低: {min_b}\n"
                f"胜负情况: {win_info}")


class Match:
    """对抗逻辑处理类"""
    
    def __init__(self, config: GameConfig):
        """
        初始化对抗
        
        参数:
            config: 游戏配置
        """
        self.config = config
        self.logger = logging.getLogger('Match')
    
    def run(self, agent_a: Agent, agent_b: Agent) -> MatchResult:
        """
        运行多次对抗
        
        参数:
            agent_a: 第一个智能体
            agent_b: 第二个智能体
            
        返回:
            包含所有对抗结果的MatchResult对象
        """
        self.logger.info(f"开始对抗: {agent_a} vs {agent_b}")
        result = MatchResult()
        
        for match_idx in range(self.config.num_matches):
            # 每场对抗前重置智能体
            agent_a.reset()
            agent_b.reset()
            
            # 运行单场对抗
            score_a, score_b, history_a, history_b = self._run_single_match(agent_a, agent_b)
            result.add_match(score_a, score_b, history_a, history_b)
            
            self.logger.debug(f"第{match_idx+1}场对抗结束，得分: A={score_a}, B={score_b}")
        
        self.logger.info(f"对抗结束: {agent_a} vs {agent_b}, 结果: {result}")
        return result
    
    def _run_single_match(self, agent_a: Agent, agent_b: Agent) -> Tuple[int, int, List[str], List[str]]:
        """
        执行单场对抗
        
        参数:
            agent_a: 第一个智能体
            agent_b: 第二个智能体
            
        返回:
            (a_score, b_score, a_history, b_history): 智能体得分和决策历史
        """
        history_a, history_b = [], []
        total_a, total_b = 0, 0
        
        for round_idx in range(self.config.rounds_per_match):
            # 获取两个智能体的决策
            action_a = agent_a.decide(history_a, history_b)
            action_b = agent_b.decide(history_b, history_a)
            
            # 验证决策的合法性
            if action_a not in ["beat", "still"] or action_b not in ["beat", "still"]:
                self.logger.error(f"非法动作: A={action_a}, B={action_b}")
                raise ValueError(f"智能体只能返回 'beat' 或 'still'，而不是 A={action_a}, B={action_b}")
            
            # 计算得分
            reward_a, reward_b = self._calculate_reward(action_a, action_b)
              # 更新历史和总分
            history_a.append(action_a)
            history_b.append(action_b)
            total_a += reward_a
            total_b += reward_b
            self.logger.debug(f"回合 {round_idx+1}: A={action_a}, B={action_b}, 得分: A={reward_a}, B={reward_b}")
        
        return total_a, total_b, history_a, history_b
    
    def _calculate_reward(self, action_a: str, action_b: str) -> Tuple[int, int]:
        """
        计算两个智能体的得分
        
        参数:
            action_a: 智能体A的动作
            action_b: 智能体B的动作
            
        返回:
            (reward_a, reward_b): 两个智能体的得分
        """
        if action_a == "beat" and action_b == "beat":
            # 双方都选择beat
            return self.config.llost, self.config.llost
        elif action_a == "still" and action_b == "still":
            # 双方都选择still
            return self.config.wwin, self.config.wwin
        elif action_a == "beat" and action_b == "still":
            # A选择beat，B选择still
            return self.config.beat, self.config.beaten
        else:  # action_a == "still" and action_b == "beat"
            # A选择still，B选择beat
            return self.config.beaten, self.config.beat