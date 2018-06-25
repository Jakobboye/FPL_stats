import json
import urllib.request, urllib.parse, urllib.error
import datetime
import sqlite3
import csv
import re
#import pandas

def GoalsPerTeam() :
    i = 7


today = datetime.date.today()
url = 'https://fantasy.premierleague.com/drf/bootstrap-static'

# Read data from FPL server.
uh = urllib.request.urlopen(url)
data = uh.read()
print('Retrieved', len(data), 'characters')

# Decode the data
info = json.loads(data.decode())
print('Number of players: ', len(info["elements"]))

# Some random statistics
goals = 0
assists = 0
for count in info["elements"] :
	goals = int(count["goals_scored"]) + goals
	assists = int(count["assists"]) + assists
	
print('Total goals scored: ',goals)
print('Total assists: ',assists)

# Create a SQLite Database with filename containing today's date.
DBfileName = 'FPLstats'+str(today)+'.sqlite'

print('Opening SQLite database', DBfileName)
# Open/create a new SQLite database and create a cursor.
conn = sqlite3.connect(DBfileName)
cur = conn.cursor()

# To start fresh:
cur.executescript('''
                  DROP TABLE IF EXISTS Players;
                  DROP TABLE IF EXISTS Teams;
                  DROP TABLE IF EXISTS Positions;''')

# Creates a table cointaining all players with corresponding stats.
# I've tried to make split the columns in the execute command into reasonable sections.
cur.execute('''CREATE TABLE IF NOT EXISTS Players
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT, position TEXT, team_id INTEGER, selected_by FLOAT,
    points_total INTEGER, cost_now INTEGER,
    goals_scored INTEGER, assists INTEGER, clean_sheets INTEGER,
    goals_conceded INTEGER, own_goals INTEGER,
    saves INTEGER, penalties_saved INTEGER, penalties_missed INTEGER,
    yellow_cards INTEGER, red_cards INTEGER,
    minutes_played INTEGER, bonus INTEGER, bps INTEGER,
    influence FLOAT, creativity FLOAT, threat FLOAT, ict FLOAT,
    trans_in_event INTEGER, trans_out_event INTEGER)''')

for player in info["elements"] :
    name = player["first_name"]+" "+player["second_name"]
    cur.execute('''INSERT OR IGNORE INTO Players (name)
		VALUES ( ? )''', ( name, ) )
    
    cur.execute("SELECT id FROM Players WHERE name = ?",
        (name,))
    player_id = cur.fetchone()[0]
    x = (player["element_type"], player["team_code"], player["selected_by_percent"],
                 player["total_points"], player["now_cost"],
                 player["goals_scored"], player["assists"], player["clean_sheets"],
                 player["goals_conceded"], player["own_goals"],
                 player["saves"], player["penalties_saved"], player["penalties_missed"],
                 player["yellow_cards"], player["red_cards"],
                 player["minutes"], player["bonus"], player["bps"],
                 player["influence"], player["creativity"], player["threat"], player["ict_index"],
                 player["transfers_in_event"], player["transfers_out_event"], player_id)
    cur.execute('''UPDATE Players SET 
                position=?, team_id=?, selected_by=?,
                points_total=?, cost_now=?,
                goals_scored=?, assists=?, clean_sheets=?,
                goals_conceded=?, own_goals=?,
                saves=?, penalties_saved=?, penalties_missed=?,
                yellow_cards=?, red_cards=?,
                minutes_played=?, bonus=?, bps=?,
                influence=?, creativity=?, threat=?, ict=?,
                trans_in_event=?, trans_out_event=? WHERE id=?''',
                x)

cur.execute('''CREATE TABLE IF NOT EXISTS Teams
	(id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    name TEXT, name_short TEXT,
    strength INTEGER, strength_home INTEGER, strength_away INTEGER,
    table_pos INTEGER, played INTEGER, win INTEGER, loss INTEGER, draw INTEGER,
    goals_scored INTEGER, goals_against INTEGER)''')

for team in info["teams"] :
    cur.execute('''INSERT OR REPLACE INTO Teams
	(id, name, name_short, strength, strength_home, strength_away,
	played, win, loss, draw) VALUES (?,?,?,?,?,?,?,?,?,?)''',(team["code"],team["name"],team["short_name"],team["strength"],
    team["strength_overall_home"],team["strength_overall_away"],team["played"],team["win"],team["loss"],team["draw"]))

#cur.execute('''SELECT id FROM Players WHERE goals_scored>0''')

cur.execute('SELECT id FROM Teams')
teams = cur.fetchall()
for team in teams :
    cur.execute('SELECT (SELECT SUM(goals_scored) FROM Players WHERE team_id=?) AS AmountA',team)
    goals_scored = cur.fetchone()
#    print('Goals scored: ',goals_scored)
    cur.execute('UPDATE Teams SET goals_scored = ? WHERE id=?',(goals_scored[0],team[0]))

cur.execute('''CREATE TABLE IF NOT EXISTS Positions
	(id INTEGER UNIQUE, singular_name TEXT, singular_name_short TEXT,
	plural_name TEXT, plural_name_short TEXT)''')

for pos in info["element_types"] :
	cur.execute('''INSERT OR REPLACE INTO Positions (id, singular_name, singular_name_short, plural_name, plural_name_short)
        VALUES ( ?, ?, ?, ?, ?)''', (pos["id"],pos["singular_name"],pos["singular_name_short"],pos["plural_name"],pos["plural_name_short"]))

#cur.execute('SELECT	id, name, goals_scored FROM Teams ORDER BY goals_scored DESC')
#print(cur.fetchall())

conn.commit()
cur.close()













