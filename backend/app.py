import json
import os
import re
import math
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from dotenv import load_dotenv

load_dotenv()

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = os.getenv('MYSQL_USER_PASSWORD')
MYSQL_PORT = 3306
MYSQL_DATABASE = "playlistsdb"

mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


def sql_search(episode):
    query_sql = f"""SELECT * FROM playlists WHERE LOWER( playlistname ) LIKE '%%{episode.lower()}%%' """
    keys = ["user_id", "artistname", "trackname", "playlistname"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


def sql_search_names(episode):
    query_sql = f"""SELECT DISTINCT playlistname FROM playlists WHERE LOWER( playlistname ) LIKE '%%{episode.lower()}%%' """
    keys = ["playlistname"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


def sql_search_tracks(episode):
    query_sql = f"""SELECT trackname FROM playlists WHERE LOWER( playlistname ) = '{episode.lower()}' """
    keys = ["trackname"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)


@app.route("/search")
def search():
    query = request.args.get("title")
    query_vec = re.findall(r"[a-z]+", query.lower())
    # docs[word] = list of playsist names containing word
    docs = dict()
    IDFs = dict()
    for word in query_vec:
        names = json.loads(sql_search_names(word))
        docs[word] = [i["playlistname"] for i in names]
        # CHANGE LATER: I have no idea how to see the length of a dataset in MYSQL, so I just guessed it was about a million rows
        # ALSO: once we get better tokenizing, add maximium IDF value
        IDFs[word] = math.log(1000000/(1 + len(docs[word])), 2)

    docscore = dict()
    qNorms = 0
    for word in query_vec:
        if IDFs[word] == None:
            continue
        curr_docs = docs[word]
        curr_idf = IDFs[word]
        qNorms += curr_idf ** 2
        for doc in curr_docs:
            docscore[doc] = docscore.get(doc, 0) + curr_idf ** 2

    # since we set all tfs = 1, doc norm is just square root of its score
    qNorms = math.sqrt(qNorms)

    cossim = list()

    for doc in docscore.keys():
        cossim.append((doc, docscore[doc]/(math.sqrt(docscore[doc]) + qNorms)))

    cossim.sort(key=lambda x: x[1], reverse=True)
    topk = cossim[:5]
    print(topk)

    songs = dict()
    for tup in topk:
        print(tup[0])
        tracknames = json.loads(sql_search_tracks(tup[0]))
        pl_songs = [i["trackname"] for i in tracknames]
        for s in pl_songs:
            songs[s] = songs.get(s, 0) + tup[1]

    song_tups = list()
    for s in songs.keys():
        song_tups.append((s, songs[s]))
    song_tups.sort(key=lambda x: x[1], reverse=True)
    print(song_tups[:20])
    return song_tups[:10]

    # for cossim, we need:
    # IDF of every query term = weight
    # because docs are onyl a few words long, tf doesn't carry too much meaning, so we ignore it

    # app.run(debug=True)
