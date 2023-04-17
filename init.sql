CREATE DATABASE IF NOT EXISTS playlistsdb;

USE playlistsdb;
DROP TABLE IF EXISTS playlists;

CREATE TABLE playlists(
    id int,
    playlist_name varchar(128),
    collaborative boolean,
    pid int,
    modified_at int,
    num_tracks int,
    num_albums int,
    num_followers int,
    tracks JSON,
    num_edits int,
    duration_ms int,
    num_artists int,
    playlist_description varchar(1000)
);

-- LOAD DATA LOCAL infile '../data/processed_playlists.csv' INTO TABLE playlists
-- fields terminated by ','
-- lines terminated by '\n'
-- (id, playlist_name, collaborative, pid, modified_at, num_tracks, num_albums, num_followers, tracks, num_edits, duration_ms, num_artists, playlist_description)