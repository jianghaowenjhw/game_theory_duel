class GameConfig:
    """
    游戏配置类，存储并验证博弈相关参数
    """
    def __init__(self, beat: int, wwin: int, llost: int, beaten: int, 
                 rounds_per_match: int, num_matches: int):
        """
        初始化游戏配置
        
        参数:
            beat: 选择beat且对方选择still时的得分
            wwin: 双方都选择still时的得分
            llost: 双方都选择beat时的得分
            beaten: 选择still且对方选择beat时的得分
            rounds_per_match: 每场对抗的回合数
            num_matches: 每对智能体之间的对抗次数
        """
        # 验证参数满足 beat > wwin > llost > beaten
        if not (beat > wwin > llost >= beaten):
            raise ValueError(f"参数必须满足 beat({beat}) > wwin({wwin}) > llost({llost}) >= beaten({beaten})")
        # 验证回合数和匹配次数为正整数
        if rounds_per_match <= 0 or num_matches <= 0:
            raise ValueError("回合数和匹配次数必须为正整数")
        
        self.beat = beat
        self.wwin = wwin
        self.llost = llost
        self.beaten = beaten
        self.rounds_per_match = rounds_per_match
        self.num_matches = num_matches
    
    def __str__(self):
        return (f"GameConfig(beat={self.beat}, wwin={self.wwin}, "
                f"llost={self.llost}, beaten={self.beaten}, "
                f"rounds={self.rounds_per_match}, matches={self.num_matches})")