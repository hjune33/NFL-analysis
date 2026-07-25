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
turnovers = turnovers.reset_index()

# ===== 5. 승패 팀 관점 변환 =====
home = reg[['game_id', 'home_team', 'result']].copy()
home = home.rename(columns={'home_team': 'team'})
home['won'] = home['result'] > 0

away = reg[['game_id', 'away_team', 'result']].copy()
away = away.rename(columns={'away_team': 'team'})
away['won'] = away['result'] < 0

team_results = pd.concat([home, away])

# ===== 6. 턴오버 + 승패 결합 분석 =====
merged = pd.merge(turnovers, team_results,
         left_on=['game_id', 'posteam'],
         right_on=['game_id', 'team'])

turnovers_effect = merged.groupby('won')['total'].mean()
turnovers_relation = merged.groupby('total')['won'].mean()

# ===== 출력 =====
print("[턴오버와 승패]")
print(turnovers_effect)
print()
print("[턴오버 수별 승률]")
print(turnovers_relation)