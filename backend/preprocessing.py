import os
import json
import nltk
import numpy as np
import math
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds

total_playlists = 0
total_tracks = 0
inv_idx = {}  # (k, v): (term, (pid, tf=1))
playlists = {}  # (k, v): (pid, playlist JSON)
idf = {}
doc_norms = None
documents = []


def process_mpd(path):
    filenames = os.listdir(path)
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)

            for playlist in mpd_slice["playlists"]:
                playlists[playlist["pid"]] = playlist
                process_playlist(playlist)


def process_playlist(playlist):
    global total_playlists, total_tracks
    total_playlists += 1

    # Create inverted index
    nname = normalize_name(playlist["name"])
    tokens = nltk.word_tokenize(nname)

    lemmatizer = nltk.WordNetLemmatizer()
    for tok in tokens:
        tok = lemmatizer.lemmatize(tok)
        if tok not in inv_idx:
            inv_idx[tok] = []
        inv_idx[tok].append(playlist["pid"])

    # Create documents for SVD
    playlist_tracks = []
    for track in playlist["tracks"]:
        total_tracks += 1
        playlist_tracks.append(track["track_name"])

    documents.append((nname, playlist_tracks))


def compute_idf(n_docs, min_df=2, max_df_ratio=0.2):
    for term, docs in inv_idx.items():
        count_docs = len(docs)
        if count_docs >= min_df and count_docs / n_docs <= max_df_ratio:
            idf[term] = math.log(n_docs / (1 + count_docs), 2)


def compute_doc_norms(n_docs):
    # Precompute the euclidean norm of each document.
    global doc_norms
    print(n_docs)
    norms = np.zeros(n_docs)
    for term, doc in inv_idx.items():
        for d in doc:
            t = idf.get(term, 0)
            norms[d] += t**2
    doc_norms = np.sqrt(norms)


def normalize_name(name):
    """
    Normalizes a string by converting it to lowercase, removing special characters and extra spaces, and returning the result.
    """
    name = name.lower()
    name = re.sub(r"[.,\/#!$%\^\*;:{}=\_`~()@]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def preprocess():
    global inv_idx
    print("Processing...")
    process_mpd("data")
    print("Total playlists:", total_playlists)

    print("Computing idf")
    compute_idf(total_playlists)
    inv_idx = {key: val for key, val in inv_idx.items() if key in idf}  # Prune inv_idx

    print("Computing doc norms")
    compute_doc_norms(total_playlists)

    print("Done")
