import nfl_data_py as nfl

# 24, 25 시즌 경기 데이터 불러오기
games = nfl.import_schedules([2024, 2025])

# 데이터가 확인
print(games.shape)      # (행 개수, 열 개수)
print(games.columns)    # 어떤 컬럼들이 있는지
print(games.head())     # 맨 위 5줄 미리보기