
# My testing grounds.
# To be run right after importing tournament.sql

from tournament import *
import random

# add 19 persons, but only 18 rivals (to have diff rival and person numbers)
print "\nPopulate the tables."
registerPlayer("Pluto")
registerPlayer("Bruno Walton", None, 'bingo')
registerPlayer("Boots O''Neal", None, 'bingo')
registerPlayer("Cathy Burton", None, 'canasta')
registerPlayer("Diane Grant", None, 'canasta')
registerPlayer("Twilight Sparkle", None, 'poker')
registerPlayer("Rainbow Dash", None, 'poker')
registerPlayer("Princess Celestia", None, 'poker')
registerPlayer("Princess Luna", None, 'canasta')
registerPlayer("Pinkie Pie", None, 'bingo')
registerPlayer("Fluttershy", None, 'bingo')
registerPlayer("Applejack", None, 'bingo')
registerPlayer("Rarity", None, 'bingo')
registerPlayer("Mickey Mouse", None, 'canasta')
registerPlayer("Minnie Mouse", None, 'canasta')
registerPlayer("Donald Duck", None, 'canasta')
registerPlayer("Daisy Duck", None, 'poker')
registerPlayer("Porky Pig", None, 'poker')
registerPlayer("Goofy", None, 'poker')

# add matches
print "\nPopulate with a few matches."
reportMatch('bingo', 1, 'won', 2)
reportMatch('bingo', 9, 'lost', 10)
reportMatch('bingo', 11, 'draw', 12)
reportMatch('canasta', 3, 'won', 4)
reportMatch('canasta', 8, 'lost', 13)
reportMatch('canasta', 14, 'draw', 15)

# TEST 1
print "\nTEST: delete matches"
deleteMatches('canasta')
deleteMatches()

# replace 3 matches
print "\nreplace 3 matches"
reportMatch('bingo', 1, 'won', 2)
reportMatch('bingo', 9, 'lost', 10)
reportMatch('bingo', 11, 'draw', 12)

# TEST 2
print "\nTEST: delete rivals"
deletePlayers(5)
deletePlayers()

# replace players
print "\nreplace some players"
registerPlayer("Pluto")
registerPlayer("Mickey Mouse", None, 'bingo')
registerPlayer("Minnie Mouse", None, 'bingo')
registerPlayer("Donald Duck", None, 'bingo')
registerPlayer("Daisy Duck", None, 'bingo')
registerPlayer("Porky Pig", None, 'bingo')
registerPlayer("Goofy", None, 'bingo')
registerPlayer("Twilight Sparkle", None, 'poker')
registerPlayer("Rainbow Dash", None, 'poker')
registerPlayer("Princess Celestia", None, 'poker')

# TEST 3
print "\nTEST: count rivals"
countPlayers()
countPlayers('poker')

# TEST 4
print "\nTEST: register a few players"
registerPlayer('Arthur Dent', None, 'bingo')
registerPlayer('Hello Kitty')
registerPlayer('Sally Magoo', '13', None)

# TEST 5
print "\nTEST: player standings"
playerStandings("bingo")
playerStandings()

# TEST 6 & 7
print "\nTEST: reportMatch, swissPairings, and swissPairings' loop!"
i = 3
while i > 0:
	print "\nTEST LOOPING"
	game = 'bingo'
	pairings = swissPairings(game)
	statuses = ['won', 'lost', 'draw']
	count = countPlayers(game)
	if count%2 != 0:
		bye_player = pairings.pop()[0]
		reportMatch(game, bye_player)
		print "bye_player:", bye_player
	for row in pairings:
		id1 = row[0]
		id2 = row[2]
		status = random.choice(statuses)
		print id1, status, "against", id2
		reportMatch(game, id1, status, id2)
	for row in playerStandings(game):
		print row
	i -= 1
