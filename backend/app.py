import json
import os
import re
import math
import numpy as np
import nltk
from nltk.corpus import stopwords
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from dotenv import load_dotenv
import preprocessing
import text_mining
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


load_dotenv()
nltk.download("punkt")

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
# os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# # These are the DB credentials for your OWN MySQL
# # Don't worry about the deployment credentials, those are fixed
# # You can use a different DB name if you want to
# MYSQL_USER = "root"
# MYSQL_USER_PASSWORD = os.getenv("MYSQL_USER_PASSWORD")
# MYSQL_PORT = 3306
# MYSQL_DATABASE = "playlistsdb"

# mysql_engine = MySQLDatabaseHandler(
#     MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE
# )

# # Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
# # albert xiao is so hot
# mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

preprocessing.preprocess()
text_mining.init()


def accumulate_dot_scores(query_word_counts, inv_idx, idf):
    doc_scores = {}
    for i, qi in query_word_counts.items():
        if i in idf:
            for j, dij in inv_idx[i]:
                doc_scores[j] = doc_scores.get(
                    j, 0) + idf[i] * qi * idf[i] * dij

    return doc_scores


def index_search(query, inv_idx, idf, doc_norms):
    """
    Search the collection of documents for the given query.

    Returns
    =======
    results: sorted tuple list (score, pid)
    """
    results = []

    query_tokens = preprocessing.tokenize(query)

    query_word_counts = nltk.FreqDist(query_tokens)

    query_norm = 0
    for i, tf in query_word_counts.items():
        if i in idf:
            query_norm += (tf * idf[i]) ** 2
    query_norm = np.sqrt(query_norm)

    dot_scores = accumulate_dot_scores(query_word_counts, inv_idx, idf)
    for doc, score in dot_scores.items():
        cossim = score / (query_norm * doc_norms[doc])
        results.append((cossim, doc))

    results.sort(reverse=True, key=lambda x: x[0])
    return results


def rocchio(query, relevant, irrelevant, playlists, a, b, c):

    q0_dict = dict()
    for w in query.split(" "):
        q0_dict.update({w: q0_dict.get(w, 0) + a})

    sum_r = dict()
    sum_nr = dict()

    for pl in relevant:
        for w in pl.split(" "):
            sum_r.update({w: sum_r.get(w, 0) + b})
    if len(relevant) != 0:
        for pl in relevant:
            for w in pl.split(" "):
                sum_r.update({w: sum_r.get(w, 0)/len(relevant)})

    for pl in irrelevant:
        for w in pl.split(" "):
            sum_r.update({w: sum_nr.get(w, 0) - c})
    if len(irrelevant) != 0:
        for pl in irrelevant:
            for w in pl.split(" "):
                sum_nr.update({w: sum_nr.get(w, 0)/len(irrelevant)})

    all_keys = set(q0_dict.keys())
    all_keys.update(set(sum_r.keys()))
    all_keys.update(set(sum_nr.keys()))

    q1_dict = dict()
    q1 = ""
    for w in all_keys:
        q1_dict[w] = round(q0_dict.get(w, 0) +
                           sum_r.get(w, 0) - sum_nr.get(w, 0))
        if q1_dict[w] < 0:
            q1_dict[w] = 0
        for i in range(q1_dict[w]):
            q1 += w

    return q1


@app.route("/search")
def search():
    query = request.args.get("title")
    query = preprocessing.normalize_name(query)
    query = rocchio(query, {"nothing", "Nothing"}, {"Views", "views"},
                    preprocessing.playlists, 1, .5, -.5)
    k = 100  # Number of playlists to examine
    queries = query.split()
    songs = []
    song_total_scores = {}
# made with each word
    for q in queries:
        top_playlists = index_search(
            q, preprocessing.inv_idx, preprocessing.idf, preprocessing.doc_norms
        )[:k]
        song_scores = {}
        for score, pid in top_playlists:
            for track in preprocessing.playlists[pid]["tracks"]:
                song = track["track_name"]
                if song not in song_scores:
                    song_scores[song] = 0

                song_scores[song] += score

        ranked_songs = list(song_scores.items())
        ranked_songs.sort(key=lambda x: x[1], reverse=True)
        ranked_songs = ranked_songs[:1000]
        songs1 = {i: sco for i, sco in ranked_songs}
        for song, sco in songs1.items():
            song_total_scores[song] = song_total_scores.get(song, 0) + sco
        songs.append(songs1)
# made with full query
    top_playlists = index_search(
        query, preprocessing.inv_idx, preprocessing.idf, preprocessing.doc_norms)[:k]
    song_scores = {}
    for score, pid in top_playlists:
        for track in preprocessing.playlists[pid]["tracks"]:
            song = track["track_name"]
            if song not in song_scores:
                song_scores[song] = 0

            song_scores[song] += score

    ranked_songs = list(song_scores.items())
    ranked_songs.sort(key=lambda x: x[1], reverse=True)
    ranked_songs = ranked_songs[:1000]
    songs1 = {i: sco for i, sco in ranked_songs}

    outs = set()
    for i in list(songs1.items()):
        cur = i[0]
        exists = True
        for lists in songs:
            if cur not in lists:
                exists = False
        if exists:
            outs.add(i[0])
    print(outs)
    song_total_scores = song_scores
    for s in song_total_scores.keys():
        if s in outs:
            song_total_scores[s] += 100
    song_total_scores_tup = list(song_total_scores.items())
    song_total_scores_tup.sort(key=lambda x: x[1], reverse=True)

   # r_songs = sorted(list(songs.items()), key= lambda x:x[1],reverse=True)
    print(song_total_scores_tup[:15])
    return song_total_scores_tup[:15]
    # app.run(debug=True)
