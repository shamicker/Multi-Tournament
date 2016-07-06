#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import math
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(game=None):
    """Remove all the match records from the database for the given game.
    The default is all games.
    """
    db = connect()
    cursor = db.cursor()
    if game != None:
        delete = "delete from matches where game = %s;"
        cursor.execute(delete, (game,))
    else:
        delete = "delete from matches;"
        cursor.execute(delete)
    db.commit()
    db.close()
    # print cursor.statusmessage


def deletePlayers(person_id=None):
    """Remove the given 'persons' from the database.
    If None, all persons are deleted.
    """
    db = connect()
    cursor = db.cursor()
    if person_id != None:
        delete = "delete from persons where person_id = %s;"
        cursor.execute(delete, (person_id,))
    else:
        delete = "delete from persons;"
        cursor.execute(delete)
    db.commit()
    db.close()
    # print cursor.statusmessage


def countPlayers(game=None):
    """Returns the number of rivals registered into a given game.
    The default is all games.
    """
    db = connect()
    cursor = db.cursor()
    if game != None:
        query = "select count(*) from registered where game = %s;"
        cursor.execute(query, (game,))
    else:
        query = "select count(*) from registered;"
        cursor.execute(query)
    count_rivals = cursor.fetchone()[0]
    db.close()
    # print "Rival count:", count_rivals
    return count_rivals


def registerPlayer(name, person_id=None, game=None):
    """Adds a player to the tournament database.

    The database assigns and returns a person_id number, if none already.
    The database assigns and returns a rival_id if a game is provided.

    Args:
      name: the player's full name (need not be unique).
      person_id: if available, the person's unique id.
            The default is None, in which case they will be registered as an
            available player.
      game: the name of the game to be registered in.
            The default is None, in which case person won't be registered into
            a tournament, but will still be on the person roster.
    """
    db = connect()
    cursor = db.cursor()

    # check if already registered as a person
    if person_id == None:

        # register as a person
        cleaned_name = bleach.clean(name)
        query = "insert into persons (person_name) values (%s) returning person_id;"
        cursor.execute(query, (cleaned_name,))

        # get person's unique id
        p_id = cursor.fetchone()[0]
        db.commit()
    else:
        p_id = person_id

    # if game is given, register as a rival in the tournament
    if game == None:
        r_id = None
    else:
        query = ("insert into registered (game, person_id) values (%s, %s)"
                "returning rival_id")
        cursor.execute(query, (game, p_id))
        
        # get rival_id number
        r_id = cursor.fetchone()[0]
        db.commit()
    db.close()
    # print name, "person_id =", p_id, "rival_id =", r_id
    # if r_id == None:
    #     print "This transaction did not register %s into a tournament."%(name,)
    return p_id, r_id


def playerStandings(game=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list is the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (rival id, name, wins, matches):
        rival_id: the player's unique rival id (per game)
        name: the player's full name (as registered)
        w_l_d_bye: the player's number of wins-losses-draws-byes
        matches: the number of matches the player has played (includes byes)
    """
    db = connect()
    cursor = db.cursor()
    if game == None:
        query = """
            select  rival_id,
                    name,
                    concat_ws('-', wins, losses, draws, byes) as w_l_d_bye,
                    matches
            from view_standings
            order by wins desc, byes desc, draws desc;
        """
        cursor.execute(query)
    else:
        query = """
            select  rival_id,
                    name,
                    concat_ws('-', wins, losses, draws, byes) as w_l_d_bye,
                    matches
            from view_standings
            where game = %s
            order by wins desc, byes desc, draws desc;
        """
        cursor.execute(query, (game,))
    result = cursor.fetchall()
    # print "Game =", game
    # for row in result:
    #     print row
    return result


def reportMatch(game, player, player_status=None, opponent=None):
    """Records the outcome of a single match between two players in a single game.

    If either player_status or opponent are None, it is assumed the player had
    no opponent and therefore the player_status got a 'bye' (a win but no
    pairing). In all cases, the opponent's status is implied.

    Args:
      game: the name of the game played
      player: the id number of one player
      opponent: the id number of the other player.
      player_status: player's outcome of the game.
    """
    db = connect()
    cursor = db.cursor()

    # check if it was a 'bye' game.
    # If yes, assign rival_lo and bye
    if opponent == None or player_status in ['bye', None]:
        rival_lo = player
        rival_hi = None
        lo_status = None
        hi_status = None
        bye = True
    else:
        # assign lo and hi players
        rival_lo = min(player, opponent)
        rival_hi = max(player, opponent)
        bye = None

        # find matching status pairs: won/lost, draw/draw
        statuses = ['won', 'lost', 'draw']
        if player_status not in statuses:
            raise ValueError("Invalid status. Please choose one of %s" % statuses)
        elif player_status == 'won':
            opponent_status = 'lost'
        elif player_status == 'lost':
            opponent_status = 'won'
        elif player_status == 'draw':
            opponent_status = 'draw'

        # translate status pair into lo/hi status
        if rival_hi == player:
            hi_status = player_status
            lo_status = opponent_status
        else:
            lo_status = player_status
            hi_status = opponent_status
    query = """
        insert into matches (match_id, game, rival_lo, rival_hi, lo_status,
        hi_status, bye) values (default, %s, %s, %s, %s, %s, %s);
    """
    try:
        cursor.execute(query, (game, rival_lo, rival_hi, lo_status, hi_status, bye))
    except db.IntegrityError:
        db.rollback()
    else:
        db.commit()
    db.close()
    # print cursor.statusmessage


def swissPairings(game=None):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    cursor = db.cursor()

    # get list of games and standings
    query = "select distinct game from registered;"
    cursor.execute(query)
    games = [row[0] for row in cursor.fetchall()]
    if game not in games or game == None:
        cursor.execute("select * from view_standings;")
    else:
        query = "select * from view_standings where game = %s;"
        cursor.execute(query, (game,))
    standings = cursor.fetchall()

    # which round is being played?
    num_players = len(standings)
    max_matches = int(math.log(num_players)/ math.log(2))
    cursor.execute("select matches from view_standings;")
    matches_played = cursor.fetchone()[0]

    # are there too many rounds?
    if matches_played > max_matches:
        print "No more matches, there's already a winner!"
        return standings

    # round 1 gets random pairing
    elif matches_played == 0:
        random.shuffle(standings)

    # get next set of match-ups
    standings_by_id = [(row[1], row[7]) for row in standings]
    pairings = []
    bye_player = None

    # make pairs
    i = 0
    while i+1 < num_players:
        pairings.append((standings_by_id[i][0], standings_by_id[i][1],
                        standings_by_id[i+1][0], standings_by_id[i+1][1]))
        i += 2
        if i+1 == num_players:
            bye_player = standings_by_id[i]
            pairings.append(bye_player)

    # print "Game =", game
    # for pair in pairings:
    #     print pair
    return pairings
