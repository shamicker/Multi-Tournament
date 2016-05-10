-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


-- delete and drop anything that might previously exist
drop database if exists tournament;

-- create database named tournament
create database tournament;

-- connect to tournament database
\c tournament

create table players (
	player_id serial primary key,
	player_name varchar not null,
	datecreated timestamp default current_timestamp,
	unique (player_id, player_name)
	);

create table matches (
	match_id serial primary key,
	player_1 serial references players,
	player_2 serial references players (player_id),
	winner serial references players (player_id),
	loser serial references players (player_id),
	check (player_1 < player_2),
	check (winner != loser),
	unique (player_1, player_2)
	);

insert into players (player_name) values ('mickey'), ('minnie');

insert into matches (player_1, player_2, winner, loser) values ('1', '2', '2', '1');

select * from players;
select * from matches;