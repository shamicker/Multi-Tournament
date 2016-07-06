-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


drop database if exists tournament;
create database tournament;

-- connect to tournament database
\c tournament


-- table 1
-- list of all persons in the 'arena' and are available for playing.
-- Note: there is a separate roster for people 'registered' in a tournament.
create table persons (
    person_id serial not null,
    person_name varchar not null,
    primary key (person_id),
    unique (person_id, person_name)
    );


-- table 2
-- list of persons registered into a game (rivals are nameless persons)
create table registered (
    rival_id serial not null,
    person_id integer not null,
    game varchar not null,
    primary key (rival_id),
    foreign key (person_id) references persons (person_id) on delete cascade,
    unique (game, person_id),
    unique (game, rival_id),
    unique (rival_id, person_id)
    );


-- create enum type for win/lose/draw options
create type wld as enum ('won', 'draw', 'lost', 'bye');


-- table 3
-- list of all matches and outcomes
create table matches (
    game varchar not null,
    match_id serial not null,
    rival_lo integer not null,
    rival_hi integer,
    lo_status wld,
    hi_status wld,
    bye boolean,
    primary key (match_id),
    foreign key (game, rival_lo) references registered (game, rival_id) on delete cascade,
    foreign key (game, rival_hi) references registered (game, rival_id) on delete cascade,
    check (rival_lo < rival_hi),
    check ((bye is true and
                lo_status is null and hi_status is null
           )
        or (bye is not true and (
                (lo_status = 'won' and hi_status = 'lost') or
                (lo_status = 'lost' and hi_status = 'won') or
                (lo_status = 'draw' and hi_status = 'draw')
                                 )
            )),
    unique (game, rival_lo, rival_hi),
    unique (rival_lo, bye)
    );


-- view 1
-- a re-arrangement of table matches - this is by rival instead of match.
create view rival_status as
        select  game,
                match_id,
                rival_lo as rival_id,
                lo_status as status,
                bye
        from matches
    union all
        select  game,
                match_id,
                rival_hi as rival_id,
                hi_status as status,
                bye
        from matches
    where rival_hi is not null;


-- view 3
-- view of list of standings with name, sorted by game and status (desc)
create view view_standings as
    select  registered.game as game,
            registered.rival_id as rival_id,
            sum(case when status = 'won' then 1 else 0 end) as wins,
            sum(case when status = 'draw' then 1 else 0 end) as draws,
            sum(case when status = 'lost' then 1 else 0 end) as losses,
            sum(case when bye = true then 1 else 0 end) as byes,
            sum(case 
                    when status in ('won', 'draw', 'lost') then 1
                    when bye = true then 1 else 0 end
                ) as matches,
            person_name as name
    from registered
        left join rival_status
            on registered.rival_id = rival_status.rival_id
        left join persons
            on registered.person_id = persons.person_id
    group by registered.rival_id, persons.person_name
    order by game, wins desc, byes desc, draws desc;
