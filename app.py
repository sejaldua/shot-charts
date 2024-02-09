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
player_df['playerName'] = player_df['firstName'] + ([' '] * player_df.shape[0]) + player_df['lastName']

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
        if (player['firstName'] + ' ' + player['lastName']) == name:
            print('found player')
            return player['playerId']
    return -1



TEAM = st.sidebar.selectbox('Select a team', team_list)
tid = get_team_id(TEAM)

print(player_df[player_df['teamId'] == tid]['playerName'].to_list())
PLAYER = st.sidebar.selectbox('Select a player', player_df[player_df['teamId'] == tid]['playerName'].to_list())
print(PLAYER)
pid = get_player_id(PLAYER)
print(pid)

SEASONS = [f'{i}-{str(i+1)[2:]}' for i in range(2010, 2024)]
SEASON = st.sidebar.selectbox('Select a season', SEASONS, index=len(SEASONS)-1)


shot_json = shotchartdetail.ShotChartDetail(
            team_id = tid, # team parameter
            player_id = pid, # player parameter
            context_measure_simple = 'PTS',
            season_nullable = SEASON, # season parameter
            season_type_all_star = 'Regular Season')

# Load data into a Python dictionary
shot_data = json.loads(shot_json.get_json())
# Get the relevant data from our dictionary
relevant_data = shot_data['resultSets'][0]
# Get the headers and row data
headers = relevant_data['headers']
rows = relevant_data['rowSet']
# Create pandas DataFrame
shot_data = pd.DataFrame(rows)
shot_data.columns = headers

# Function to draw basketball court
def create_court(ax, color):

  # Short corner 3PT lines
  ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
  ax.plot([220, 220], [0, 140], linewidth=2, color=color)

  # 3PT Arc
  ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

  # Lane and Key
  ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
  ax.plot([80, 80], [0, 190], linewidth=2, color=color)
  ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
  ax.plot([60, 60], [0, 190], linewidth=2, color=color)
  ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
  ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

  # Rim
  ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

  # Backboard
  ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

  # Remove ticks
  ax.set_xticks([])
  ax.set_yticks([])

  # Set axis limits
  ax.set_xlim(-250, 250)
  ax.set_ylim(0, 470)



st.title('Shot Chart Visualization')

st.write('Hello Polygence Pod!')

