import streamlit as st

# Import packages
from nba_api.stats.endpoints import shotchartdetail
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# Load teams file
teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)
# Load players file
players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)

team_df = pd.DataFrame(teams)
player_df = pd.DataFrame(players)
player_df['playerName'] = player_df['firstName'] + (' ' * player_df.shape[0]) + player_df['lastName']

team_list = team_df['teamName'].to_list()

# Get team ID based on team name
def get_team_id(t):
    print(t)
    for team in teams:
        if team['teamName'] == t:
            return team['teamId']
    return -1

# Get player ID based on player name
def get_player_id(name):
    for player in players:
        if player['firstName'] + ' ' + player['lastName'] == name:
            return player['playerId']
    return -1



TEAM = st.sidebar.selectbox('Select a team', team_list)
tid = get_team_id(TEAM)

PLAYER = st.sidebar.selectbox('Select a player', player_df[player_df['teamId'] == tid]['playerName'].to_list())
pid = get_player_id(PLAYER)

SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(2010, 2024)]
print(SEASONS)

# Create JSON request
# shot_json = shotchartdetail.ShotChartDetail(
#             team_id = tid,
#             player_id = pid,
#             context_measure_simple = 'PTS',
#             season_nullable = '2011-12',
#             season_type_all_star = 'Regular Season')

st.title('Shot Chart Visualization')

st.write('Hello Polygence Pod!')

