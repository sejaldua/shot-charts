import streamlit as st
from nba_api.stats.endpoints import shotchartdetail
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

st.title('Hi Polygence Pod!')
st.write('Shot Chart Visualization App')

# Load teams file
teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)
# Load players file
players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)

player_df = pd.DataFrame.from_dict(players)
print(player_df.columns)
player_df['name'] = player_df.apply(lambda x: x['firstName'] + ' ' + x['lastName'], axis=1)
player_list = player_df['name'].tolist()
selected_player = st.sidebar.selectbox('Pick a player', player_list)
player_dict = player_df.set_index('name').to_dict(orient='index')
player_id = player_dict[selected_player]["playerId"]
team_id = player_dict[selected_player]["teamId"]
seasons = ['2020-21', '2021-22', '2022-23', '2023-24']
season_id = st.sidebar.multiselect('Select a season', seasons)
st.write(f'You selected {selected_player} {player_dict[selected_player]["playerId"]}')
# st.dataframe(player_df)

# Get team ID based on team name
def get_team_id(t):
  for team in teams:
    if team['teamName'] == t:
      return team['teamId']
  return -1

# Get player ID based on player name
def get_player_id(first, last):
  for player in players:
    if player['firstName'] == first and player['lastName'] == last:
      return player['playerId']
  return -1

shot_json = shotchartdetail.ShotChartDetail(
    team_id = team_id,
    player_id = player_id,
    context_measure_simple = 'PTS',
    season_nullable = season_id,
    season_type_all_star = 'Regular Season'
    # season_segment_nullable='Post All-Star'
)

# Load data into a Python dictionary
shot_data = json.loads(shot_json.get_json())

# Get the relevant data from our dictionary
relevant_data = shot_data['resultSets'][0]

# Get the headers and row data
headers = relevant_data['headers']
rows = relevant_data['rowSet']

# Create pandas DataFrame
shot_df = pd.DataFrame(rows)
shot_df.columns = headers

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

  return ax

# Draw basketball court
fig = plt.figure(figsize=(4, 3.76))
ax = fig.add_axes([0, 0, 1, 1])
ax.hexbin(shot_df['LOC_X'], shot_df['LOC_Y'] + 60,
          gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='Blues')
ax = create_court(ax, 'black')

st.pyplot(fig)
