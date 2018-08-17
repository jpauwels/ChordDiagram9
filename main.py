import os
from flask import Flask, render_template, send_from_directory, g, request
import json
import pymongo
import requests


app = Flask(__name__)

ids = [1235149, 1235736, 1235734, 1235737]

# Generate the list of all possible chords
tones = "ABCDEFG"
qualities = ("maj", "maj7", "min", "min7", "dom7", "7", "aug", "bmaj", "bmaj7", "b7", "bmin", "bmin7")
CHORDS = ["{}{}".format(tone, quality) for tone in tones for quality in qualities]

base_url = 'https://api.jamendo.com/'
client_id = 'f19cc536'

def get_db():
    if not hasattr(g, 'client'):
        g.client = pymongo.MongoClient('mongodb+srv://readonly:1doOzIOAZbbG8I5s@freecluster-78b1r.mongodb.net/test')
    return g.client.jamendo

def chord_id(label):
    return CHORDS.index(label)

def process_track(id):
    '''
    Load track from json file and parse into a matrix
    '''

    # Load chords from DB
    d = get_db()['pieces'].find_one({'_id': id})
    if not d:
        raise Exception("No chords found")
    return d["chordSequence"]

def identity_matrix():
    matrix = [[0]*len(CHORDS) for _ in range(len(CHORDS))]
    for i in range(len(matrix)):
        matrix[i][i] = 1
    return matrix 

def get_audio_path(id):
    #mp3 = name[:-5] + ".mp3"
    #return os.path.join(AUDIO_DIR, mp3)
    # get audio link from Jamendo api
    r = requests.get(base_url+'v3.0/tracks', params={'id': id, 'client_id': client_id})
    return r.json()['results'][0]['audio']

@app.route("/search")
def search():
    query = request.url.split("=")[1].replace('+', ' ')
    p = {'namesearch': query, 'client_id': client_id, 'format': 'json', 'limit': 100}
    r = requests.get("{}{}".format(base_url, "v3.0/tracks"), params=p)
    print("Jamendo search: HTTP {}".format(r.status_code))
    results = r.json()['results']
    data = []
    for result in results:
        if True:
        # Turn on to check DB before inserting link
        #if get_db()['pieces'].find_one({'_id': int(result['id'])}):
            data.append(result)
        if len(data) == 20:
            break
    return render_template('template.html',
                            matrix=identity_matrix(),
                            chord_map=CHORDS,
                            track_list=data)

@app.route("/")
def index():
    '''
    The initial page with empty diagram
    '''
    return render_template('template.html',
                            matrix=identity_matrix(),
                            chord_map=CHORDS,
                            id_list=ids)

@app.route("/<id>")
def get_track(id):
    '''
    Page for each song
    '''
    if id == "favicon.ico":
        return ''
    id = int(id)
    sequence = process_track(id)
    return render_template('template.html',
                            audio_file=get_audio_path(id),
                            id_list=ids,
                            chord_map=CHORDS,
                            matrix=identity_matrix(),
                            sequence=sequence)

#@app.route("/tracks/audio/<name>")
#def get_audio(name):
#    '''
#    Audio for each song
#    '''
#    return send_from_directory("audio", name)

@app.route("/static/<resource>")
def get_static(resource):
    return send_from_directory("static", resource)

if __name__ == '__main__':
    app.run(debug=True)

