import nfl_data_py as nfl

games = nfl.import_schedules([2024, 2025])

# 정규시즌만 (플레이오프 제외)
reg = games[games['game_type'] == 'REG']

print("총 경기 수:", len(reg))
print(reg[['home_team', 'away_team', 'home_score', 'away_score', 'result']].head())

home_wins = len(reg[reg['result'] > 0])
away_wins = len(reg[reg['result'] < 0])
ties = len(reg[reg['result'] == 0])

print("홈 승:", home_wins)
print("원정 승:", away_wins)
print("무승부:", ties)
print("홈 승률:", round(home_wins / len(reg) * 100, 1), "%")
print("홈 팀 승리 평균 득점:", round(reg[reg['result'] > 0]['result'].mean(), 1))
print("홈 팀 패배 평균 실점:", round(reg[reg['result'] < 0]['result'].mean(), 1))
