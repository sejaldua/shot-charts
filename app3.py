import streamlit as st
from nba_api.stats.endpoints import shotchartdetail
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt



st.title('Polygence')
st.caption('April 8th, 2024')


# Load teams file
teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)
# Load players file
players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)

# make a table of players
player_df = pd.DataFrame.from_dict(players)
player_df['playerName'] = player_df['firstName'] + ' ' + player_df['lastName']

# turn the table into a dictionary with keys and values
player_dict = player_df.set_index('playerName').to_dict(orient='index')

# let the user select from the keys of the dictionary to pick a player
player_selection = st.sidebar.selectbox('Select a player', sorted(player_dict.keys()))
player_id = player_dict[player_selection]['playerId']
team_id = player_dict[player_selection]['teamId']

season_options = ['2003-04', '2004-05', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']
seasons = st.sidebar.multiselect('Select season(s)', season_options)

period = st.sidebar.slider('Select a quarter', 1, 4)

# Get team ID based on team name
def get_team_id(team):
  for t in teams:
    if t['teamName'] == team:
      return t['teamId']
  return -1

# Create JSON request
shot_json = shotchartdetail.ShotChartDetail(
            team_id = team_id,
            player_id = player_id,
            season_nullable = seasons,
            context_measure_simple = 'PTS',
            period = period,
            # ahead_behind_nullable='Behind or Tied',
            season_type_all_star = 'Regular Season')
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
# Plot hexbin of shots
ax.hexbin(
    shot_df['LOC_X'],
    shot_df['LOC_Y'] + 60,
    gridsize=(30, 30),
    extent=(-300, 300, 0, 940),
    bins='log',
    cmap='Blues')
ax = create_court(ax, 'black')
# Annotate player name and season
_ = ax.text(0, 1.05, f'{player_selection} Shot Chart Regular Season', transform=ax.transAxes, ha='left', va='baseline')
st.pyplot(fig)