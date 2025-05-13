import os
import logging
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime

from config import GameConfig
from agent import Agent
from match import Match

class Tournament:
    """大比赛组织类，负责组织全部对抗并计算最终排名"""
    
    def __init__(self, config: GameConfig, agents: List[Agent], log_path: str):
        """
        初始化大比赛
        
        参数:
            config: 游戏配置
            agents: 参与比赛的智能体列表
            log_path: 日志文件路径
        """
        self.config = config
        self.agents = agents
        self.log_path = log_path
        self.logger = self._init_logger(log_path)
        
        # 验证智能体
        self._validate_agents()
    
    def _init_logger(self, log_path: str) -> logging.Logger:
        """初始化日志记录器"""
        # 确保日志目录存在
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 配置日志
        logger = logging.getLogger('Tournament')
        logger.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        return logger
    
    def _validate_agents(self):
        """验证智能体有效性和唯一性"""
        if len(self.agents) < 2:
            raise ValueError("至少需要两个智能体才能进行比赛")
        
        # 检查智能体名称是否唯一
        names = [agent.name for agent in self.agents]
        if len(names) != len(set(names)):
            # 发现重名智能体，为其添加后缀
            name_counts = {}
            for i, agent in enumerate(self.agents):
                if agent.name in name_counts:
                    name_counts[agent.name] += 1
                    self.agents[i].name = f"{agent.name}_{name_counts[agent.name]}"
                else:
                    name_counts[agent.name] = 0
    
    def run(self) -> List[Tuple[Agent, float]]:
        """
        运行大比赛
        
        返回:
            list[(agent, score)]: 按得分排序的智能体列表
        """
        self.logger.info(f"===== 开始大比赛 =====")
        self.logger.info(f"配置: {self.config}")
        self.logger.info(f"参赛智能体: {[agent.name for agent in self.agents]}")
        
        start_time = time.time()
        scores = {agent.name: {} for agent in self.agents}
        agent_lookup = {agent.name: agent for agent in self.agents}
        
        # 两两对抗
        total_matches = len(self.agents) * (len(self.agents) - 1) // 2
        completed = 0
        
        for i, agent_a in enumerate(self.agents):
            for j, agent_b in enumerate(self.agents):
                if i >= j:  # 避免重复和自对抗
                    continue
                    
                self.logger.info(f"对抗 {agent_a.name} vs {agent_b.name} 开始")
                match = Match(self.config)
                result = match.run(agent_a, agent_b)
                
                # 记录最低得分（根据规则5）
                score_a, score_b = result.get_025_scores()
                scores[agent_a.name][agent_b.name] = score_a
                scores[agent_b.name][agent_a.name] = score_b
                  # 写入日志
                self.logger.info(f"{agent_a.name} vs {agent_b.name}:")
                self.logger.info(f"  25分位数: {agent_a.name}={score_a}, {agent_b.name}={score_b}")
                self.logger.info(f"  所有得分: {agent_a.name}={result.scores_a}, {agent_b.name}={result.scores_b}")
                self.logger.info(f"  胜负情况: {result.get_win_count_info()}")
                
                completed += 1
                self.logger.info(f"已完成: {completed}/{total_matches} ({completed/total_matches*100:.1f}%)")
        
        # 计算每个智能体的平均得分
        final_scores = {}
        for agent_name in scores:
            # 计算与所有其他对手的平均得分
            opponent_scores = list(scores[agent_name].values())
            if opponent_scores:
                final_scores[agent_name] = sum(opponent_scores) / len(opponent_scores)
            else:
                final_scores[agent_name] = 0
        
        # 生成排名
        ranked = [(agent_lookup[name], score) for name, score in final_scores.items()]
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        # 记录最终排名
        self.logger.info(f"===== 比赛结束 =====")
        self.logger.info(f"耗时: {time.time() - start_time:.2f} 秒")
        self.logger.info(f"最终排名:")
        for i, (agent, score) in enumerate(ranked):
            self.logger.info(f"  第 {i+1} 名: {agent.name} - 得分: {score:.2f}")
        
        return ranked
    
    def save_results(self, ranked: List[Tuple[Agent, float]], filename: str = None):
        """
        保存比赛结果到文件
        
        参数:
            ranked: 排名后的智能体列表
            filename: 输出文件名（默认使用时间戳）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tournament_results_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"博弈论大比赛结果\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"参数: beat={self.config.beat}, wwin={self.config.wwin}, "
                   f"llost={self.config.llost}, beaten={self.config.beaten}\n")
            f.write(f"回合数: {self.config.rounds_per_match}, 对抗次数: {self.config.num_matches}\n\n")
            
            f.write("最终排名:\n")
            for i, (agent, score) in enumerate(ranked):
                f.write(f"{i+1}. {agent.name}: {score:.2f}\n")
                
        self.logger.info(f"结果已保存至 {filename}")
        return filename