-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


create table players (
	player_id serial primary key,
	player_name varchar not null,
	datecreated timestamp default current_timestamp,
	unique (player_id, player_name)
	);

create table matches (
	match_id serial primary key,
	player_id serial not null references players,
	opp_id serial not null references players (player_id),
	winner serial not null,
	loser serial not null,
	check (player_id != opp_id),
	check (winner != loser),
	check (winner in (player_id, opp_id)),
	check (loser in (player_id, opp_id)),
	unique (match_id, player_id, opp_id)
	);
