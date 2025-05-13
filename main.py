import os
import logging
import argparse
from typing import List

from config import GameConfig
from agent import (
    Agent, TitForTatAgent, AlwaysBeatAgent, AlwaysStillAgent,
    RandomAgent, ForgivingTitForTatAgent, GradualAgent, PatternDetectorAgent, AdaptiveAgent,
    WinStayLoseShiftAgent, TwoCoopOneDefectAgent, RewardPunishmentAgent, EscapeTigerAgent,
    InchingAgent, TrustBuildingAgent, GrudgeAgent, PunishmentEscalationAgent, ConsensusAgent,
    ProbeAgent, CappedAgent, ShortMemoryAgent, MediumMemoryAgent, LongMemoryAgent,
    TitForTatStartMediumMemoryAgent, AdaptivePunishmentAgent, GradualForgivingAgent,
    PatternMatchingTitForTatAgent, FrequencyAnalysisAgent, RhythmDetectorAgent, HybridAgent, PavlovAgent
)
from match import Match
from tournament import Tournament

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_agents() -> List[Agent]:
    """创建所有可用的智能体实例"""
    return [
        TitForTatAgent("以牙还牙"),
        AlwaysBeatAgent("总是背叛"),
        AlwaysStillAgent("总是合作"),
        RandomAgent("随机策略"),
        ForgivingTitForTatAgent("宽容的以牙还牙"),
        GradualAgent("渐进报复"),
        PatternDetectorAgent("模式识别"),
        AdaptiveAgent("自适应"),
        WinStayLoseShiftAgent("赢则保持输则改变"),
        TwoCoopOneDefectAgent("两合作一背叛"),
        RewardPunishmentAgent("助长惩罚"),
        EscapeTigerAgent("虎口脱险"),
        InchingAgent("得寸进尺"),
        TrustBuildingAgent("信任建立"),
        GrudgeAgent("记仇"),
        PunishmentEscalationAgent("惩罚升级"),
        ConsensusAgent("共识策略"),
        ProbeAgent("试探策略"),
        CappedAgent("封顶策略"),
        ShortMemoryAgent("短期记忆"),
        MediumMemoryAgent("中期记忆"),
        LongMemoryAgent("长期记忆"),
        TitForTatStartMediumMemoryAgent("以牙还牙开始的中期记忆"),
        AdaptivePunishmentAgent("适应性惩罚"),
        GradualForgivingAgent("渐进宽恕"),
        PatternMatchingTitForTatAgent("模式匹配以牙还牙"),
        FrequencyAnalysisAgent("频率分析"),
        RhythmDetectorAgent("节奏检测"),
        HybridAgent("混合策略"),
        PavlovAgent("巴甫洛夫策略")
    ]

def run_individual_match(config: GameConfig, agent_a: Agent, agent_b: Agent, log_file: str = None):
    """
    运行个人赛（两个智能体对抗）
    
    参数:
        config: 游戏配置
        agent_a: 第一个智能体
        agent_b: 第二个智能体
        log_file: 日志文件路径（可选）
    """
    # 配置日志
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
    logger.info(f"===== 个人赛: {agent_a.name} vs {agent_b.name} =====")
    logger.info(f"配置: {config}")
    
    match = Match(config)
    result = match.run(agent_a, agent_b)
    
    logger.info(f"对抗结果:")
    logger.info(f"{result}")
    logger.info("个人赛结束")
    
    return result

def run_tournament(config: GameConfig, agents: List[Agent] = None, log_file: str = None):
    """
    运行大比赛
    
    参数:
        config: 游戏配置
        agents: 参与比赛的智能体列表（默认使用所有可用智能体）
        log_file: 日志文件路径（可选）
    """
    if agents is None:
        agents = get_all_agents()
    
    # 创建日志目录
    if log_file is None:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        log_file = os.path.join("logs", "tournament.log")
    
    logger.info(f"===== 大比赛开始 =====")
    logger.info(f"参赛智能体: {[agent.name for agent in agents]}")
    
    # 运行大比赛
    tournament = Tournament(config, agents, log_file)
    ranked = tournament.run()
    
    # 保存结果
    results_file = os.path.join("logs", "tournament_results.txt")
    tournament.save_results(ranked, results_file)
    
    # 显示最终排名
    logger.info("最终排名:")
    for i, (agent, score) in enumerate(ranked):
        logger.info(f"{i+1}. {agent.name}: {score:.2f}")
    
    return ranked

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='博弈论智能体比赛')
    parser.add_argument('--version', action='version', version='v0.1', 
                        help='显示版本信息')
    parser.add_argument('--mode', type=str, default='tournament', 
                        choices=['individual', 'tournament'],
                        help='比赛模式：个人赛或大比赛')
    parser.add_argument('--beat', type=int, default=5,
                        help='选择beat且对方选择still时的得分')
    parser.add_argument('--wwin', type=int, default=3,
                        help='双方都选择still时的得分')
    parser.add_argument('--llost', type=int, default=1,
                        help='双方都选择beat时的得分')
    parser.add_argument('--beaten', type=int, default=0,
                        help='选择still且对方选择beat时的得分')
    parser.add_argument('--rounds', type=int, default=500,
                        help='每场对抗的回合数')
    parser.add_argument('--matches', type=int, default=30,
                        help='每对智能体之间的对抗次数')
    parser.add_argument('--agent1', type=str, default='TitForTatAgent',
                        help='个人赛智能体1名称（仅在个人赛模式下使用）')
    parser.add_argument('--agent2', type=str, default='RandomAgent',
                        help='个人赛智能体2名称（仅在个人赛模式下使用）')
    parser.add_argument('--log', type=str, default=None,
                        help='日志文件路径')
    return parser.parse_args()

def get_agent_by_name(name: str) -> Agent:
    """根据名称获取智能体实例"""
    agents = {
        'TitForTatAgent': TitForTatAgent("以牙还牙"),
        'AlwaysBeatAgent': AlwaysBeatAgent("总是背叛"),
        'AlwaysStillAgent': AlwaysStillAgent("总是合作"),
        'RandomAgent': RandomAgent("随机策略"),
        'ForgivingTitForTatAgent': ForgivingTitForTatAgent("宽容的以牙还牙"),
        'GradualAgent': GradualAgent("渐进报复"),
        'PatternDetectorAgent': PatternDetectorAgent("模式识别"),
        'AdaptiveAgent': AdaptiveAgent("自适应"),
        'WinStayLoseShiftAgent': WinStayLoseShiftAgent("赢则保持输则改变"),
        'TwoCoopOneDefectAgent': TwoCoopOneDefectAgent("两合作一背叛"),
        'RewardPunishmentAgent': RewardPunishmentAgent("助长惩罚"),
        'EscapeTigerAgent': EscapeTigerAgent("虎口脱险"),
        'InchingAgent': InchingAgent("得寸进尺"),
        'TrustBuildingAgent': TrustBuildingAgent("信任建立"),
        'GrudgeAgent': GrudgeAgent("记仇"),
        'PunishmentEscalationAgent': PunishmentEscalationAgent("惩罚升级"),
        'ConsensusAgent': ConsensusAgent("共识策略"),
        'ProbeAgent': ProbeAgent("试探策略"),
        'CappedAgent': CappedAgent("封顶策略"),
        'ShortMemoryAgent': ShortMemoryAgent("短期记忆"),
        'MediumMemoryAgent': MediumMemoryAgent("中期记忆"),
        'LongMemoryAgent': LongMemoryAgent("长期记忆"),
        'TitForTatStartMediumMemoryAgent': TitForTatStartMediumMemoryAgent("以牙还牙开始的中期记忆"),
        'AdaptivePunishmentAgent': AdaptivePunishmentAgent("适应性惩罚"),
        'GradualForgivingAgent': GradualForgivingAgent("渐进宽恕"),
        'PatternMatchingTitForTatAgent': PatternMatchingTitForTatAgent("模式匹配以牙还牙"),
        'FrequencyAnalysisAgent': FrequencyAnalysisAgent("频率分析"),
        'RhythmDetectorAgent': RhythmDetectorAgent("节奏检测"),
        'HybridAgent': HybridAgent("混合策略"),
        'PavlovAgent': PavlovAgent("巴甫洛夫策略")
    }
    
    if name not in agents:
        raise ValueError(f"未知智能体名称: {name}，可用智能体: {list(agents.keys())}")
    
    return agents[name]

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()
    
    # 创建游戏配置
    try:
        config = GameConfig(
            beat=args.beat, wwin=args.wwin, llost=args.llost, beaten=args.beaten,
            rounds_per_match=args.rounds, num_matches=args.matches
        )
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        exit(1)
    
    # 根据模式运行比赛
    if args.mode == 'individual':
        try:
            agent1 = get_agent_by_name(args.agent1)
            agent2 = get_agent_by_name(args.agent2)
            run_individual_match(config, agent1, agent2, args.log)
        except Exception as e:
            logger.error(f"个人赛运行错误: {e}")
            exit(1)
    else:  # tournament
        try:
            run_tournament(config, get_all_agents(), args.log)
        except Exception as e:
            logger.error(f"大比赛运行错误: {e}")
            exit(1)