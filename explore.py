# ===== 1. 데이터 로드 =====
import nfl_data_py as nfl
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

db_exists = os.path.exists('nfl.db')
conn = sqlite3.connect('nfl.db')

if db_exists:
    pbp = pd.read_sql('SELECT * FROM pbp', conn)
else:
    pbp = nfl.import_pbp_data([2025])
    pbp.to_sql('pbp', conn, if_exists='replace', index=False)



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

# ===== 4. 승패 팀 관점 변환 =====
home = reg[['game_id', 'home_team', 'result']].copy()
home = home.rename(columns={'home_team': 'team'})
home['won'] = home['result'] > 0

away = reg[['game_id', 'away_team', 'result']].copy()
away = away.rename(columns={'away_team': 'team'})
away['won'] = away['result'] < 0

team_results = pd.concat([home, away])

# ===== 5. 턴오버 집계 =====
turnovers = pbp.groupby(['game_id', 'posteam'])[['fumble_lost', 'interception']].sum()
turnovers['total'] = turnovers['fumble_lost'] + turnovers['interception']
turnovers = turnovers.reset_index()

# ===== 6. 턴오버 + 승패 결합 분석 =====
merged_turnover = pd.merge(turnovers, team_results,
         left_on=['game_id', 'posteam'],
         right_on=['game_id', 'team'])

turnovers_effect = merged_turnover.groupby('won')['total'].mean()
turnovers_relation = merged_turnover.groupby('total')['won'].mean()

# ===== 7. 패스 야드 집계 =====
pass_yards = pbp.groupby(['game_id', 'posteam'])[['passing_yards']].sum()
pass_yards = pass_yards.reset_index()

# ===== 8. 패싱 야드 + 승패 결합 분석 =====
merged_passyard = pd.merge(pass_yards, team_results,
                           left_on=['game_id', 'posteam'],
                           right_on=['game_id', 'team'])
passyards_effect = merged_passyard.groupby('won')['passing_yards'].mean()

merged_passyard['yards'] = pd.cut(merged_passyard['passing_yards'],
                                 bins = [0, 176, 221, 272, 500], 
                                 labels = ['~176', '176~221', '221~272', '272+'])
passyards_relation = merged_passyard.groupby('yards')['won'].mean()

# ===== 9. 패널티 집계 =====
penalties = pbp.groupby(['game_id', 'penalty_team'])[['penalty']].sum()
penalties = penalties.reset_index()

# ===== 10. 패널티 + 승패 결합 분석 =====
merged_penalty = pd.merge(penalties, team_results,
                           left_on=['game_id', 'penalty_team'],
                           right_on=['game_id', 'team'])
penalty_effect = merged_penalty.groupby('won')['penalty'].mean()

merged_penalty['penalty_bin'] = pd.cut(merged_penalty['penalty'],
                                       bins=[0, 4, 6, 8, 20],
                                       labels=['~4', '4~6', '6~8', '8+'])
penalty_relation = merged_penalty.groupby('penalty_bin')['won'].mean()

# ===== 11. 3rd down 전환율 집계 =====
third_down = pbp.groupby(['game_id', 'posteam'])[['third_down_converted', 'third_down_failed']].sum()
third_down['attempts'] = third_down['third_down_converted'] + third_down['third_down_failed']
third_down['rate'] = third_down['third_down_converted'] / third_down['attempts']
third_down = third_down.reset_index()

# ===== 12. 3rd down 전환율 + 승패 결합 분석 =====
merged_thirddown = pd.merge(third_down, team_results,
                           left_on=['game_id', 'posteam'],
                           right_on=['game_id', 'team'])
thirddown_effect = merged_thirddown.groupby('won')['rate'].mean()

merged_thirddown['rate_bin'] = pd.cut(merged_thirddown['rate'],
                                 bins = [0, 0.30, 0.385, 0.47, 1.0],
                                 labels = ['~30%', '30~38%', '38~47%', '47%+'])
thirddown_relation = merged_thirddown.groupby('rate_bin')['won'].mean()

# ===== 승패 영향 요약 =====
turnovers_summary = pd.DataFrame({
    'win_rate': merged_turnover.groupby('total')['won'].mean(),
    'matches': merged_turnover.groupby('total').size()
})

passyard_summary = pd.DataFrame({
    'win_rate': merged_passyard.groupby('yards')['won'].mean(),
    'matches': merged_passyard.groupby('yards').size()
})

penalty_summary = pd.DataFrame({
    'win_rate': merged_penalty.groupby('penalty_bin')['won'].mean(),
    'matches': merged_penalty.groupby('penalty_bin').size()
})

thirddown_summary = pd.DataFrame({
    'win_rate': merged_thirddown.groupby('rate_bin')['won'].mean(),
    'matches': merged_thirddown.groupby('rate_bin').size()
})

# ===== 상관관계 분석 =====
factors = team_results.merge(turnovers[['game_id', 'posteam', 'total']],
                             left_on=['game_id', 'team'],
                             right_on=['game_id', 'posteam'])

factors = factors.merge(pass_yards[['game_id', 'posteam', 'passing_yards']],
                        left_on=['game_id', 'team'],
                        right_on=['game_id', 'posteam'])

factors = factors.merge(penalties[['game_id', 'penalty_team', 'penalty']],
                        left_on=['game_id', 'team'],
                        right_on=['game_id', 'penalty_team'])

factors = factors.merge(third_down[['game_id', 'posteam', 'rate']],
                        left_on=['game_id', 'team'],
                        right_on=['game_id', 'posteam'])

factors_clean = factors[['won', 'total', 'passing_yards', 'penalty', 'rate']]
factors_clean = factors_clean.rename(columns={
    'total': 'turnover',
    'rate': 'third_down_rate'
})

correlations = factors_clean.corr()['won'].drop('won')

y = factors_clean['won']
x = factors_clean.drop(columns='won')

model = LogisticRegression()
model.fit(x, y)
accuracy = model.score(x, y)

# print(x.head())
# print(y.head())
# print(accuracy)
# ===== 출력 =====
# print("[턴오버 영향력]")
# print(turnovers_summary)
# print()
# print("[패스야드 영향력]")
# print(passyard_summary)
# print()
# print("[페널티 영향력]")
# print(penalty_summary)
# print()
# print("[3rd down 전환율]")
# print(thirddown_summary)
# print()
# print("[요인별 승패 상관계수]")

# ===== 시각화 =====
plt.bar(turnovers_summary.index, turnovers_summary['win_rate'])
plt.title('Turnover vs Win Rate')
plt.xlabel('Turnovers')
plt.ylabel('Win Rate')
plt.savefig('turnover_winrate.png')

plt.figure()
plt.bar(thirddown_summary.index, thirddown_summary['win_rate'])
plt.title('Third-down conversion rate vs Win Rate')
plt.xlabel('Third-down conversion rates')
plt.ylabel('Win Rate')
plt.savefig('thirddown_winrate.png')

plt.figure()
plt.bar(passyards_relation.index, passyard_summary['win_rate'])
plt.title('Passyard vs Win Rate')
plt.xlabel('Passyards')
plt.ylabel('Win Rate')
plt.savefig('passyard_winrate.png')

plt.figure()
plt.bar(penalty_relation.index, penalty_summary['win_rate'])
plt.title('Penalty vs Win Rate')
plt.xlabel('Penalties')
plt.ylabel('Win Rate')
plt.savefig('penalty_winrate.png')

plt.figure()
plt.bar(correlations.index, correlations.values)
plt.title('Correlation with Win')
plt.ylabel('Correlation')
plt.axhline(0, color='black', linewidth=0.8)   
plt.savefig('correlation_summary.png')

