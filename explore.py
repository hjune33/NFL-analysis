# ===== 1. 데이터 로드 =====
import nfl_data_py as nfl
import pandas as pd

games = nfl.import_schedules([2024, 2025])
# 정규시즌만 (플레이오프 제외)
reg = games[games['game_type'] == 'REG']

# ===== 2. 홈 어드밴티지 =====
home_wins = len(reg[reg['result'] > 0])
away_wins = len(reg[reg['result'] < 0])
ties = len(reg[reg['result'] == 0])
team_avg_score = reg.groupby('home_team')['home_score'].mean().sort_values(ascending=False)
team_avg_con_score = reg.groupby('home_team')['away_score'].mean().sort_values(ascending=True)
team_margin = (team_avg_score - team_avg_con_score).sort_values(ascending=False)
team_avg_win = reg[reg['result'] > 0].groupby('home_team').size().sort_values(ascending=False)

# ===== 3. 팀별 성적표 =====
team_stats = pd.DataFrame({
    'score': round(team_avg_score, 1),
    'allow': round(team_avg_con_score, 1),
    'margin': round(team_margin, 1),
    'wins': team_avg_win
})
team_stats = team_stats.sort_values('wins', ascending=False)

# ===== 4. 턴오버 집계 =====
pbp = nfl.import_pbp_data([2025])
turnovers = pbp.groupby(['game_id', 'posteam'])[['fumble_lost', 'interception']].sum()
turnovers['total'] = turnovers['fumble_lost'] + turnovers['interception']

# ===== 출력 =====
# print("홈 승:", home_wins)
# print("원정 승:", away_wins)
# print("무승부:", ties)
# print("홈 승률:", round(home_wins / len(reg) * 100, 1), "%")
# print("홈 팀 승리 평균 득점:", round(reg[reg['result'] > 0]['result'].mean(), 1))
# print("홈 팀 패배 평균 실점:", round(reg[reg['result'] < 0]['result'].mean(), 1))
# print("홈 팀 평균 득점:", round(team_avg_score, 1))
# print("홈 팀 평균 실점:", round(team_avg_con_score, 1))
# print("팀 별 득실 차 ", round(team_margin, 1))
# print("홈 팀 평균 승:", team_avg_win)
# print(team_stats)
print(turnovers)
print(turnovers.sort_values('total', ascending=False).head(10))