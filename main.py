import os
from flask import Flask, render_template, send_from_directory, g
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

get_db()
exit()

def chord_id(label):
    return CHORDS.index(label)

def process_track(id):
    '''
    Load track from json file and parse into a matrix
    '''

    # Load chords from DB
    d = get_db()['pieces'].find_one({'_id': id})
    labels = [chord_id(c['label']) for c in d["chordSequence"]]
    print(labels)
    changes = [(labels[i], labels[i+1]) for i in range(len(labels) - 1)]
    matrix = [[0]*len(CHORDS) for _ in range(len(CHORDS))]
    
    # Adds chords
    for start, end in changes:
        matrix[start][end] = 0.5 
        matrix[end][start] = 0.25

    # Gives each arc the same width
    for i in range(len(matrix)):
        matrix[i][i] = 1 - sum(matrix[i])

    return matrix, d["chordSequence"]

def default_matrix():
    '''
    Generates the matrix that is shown on page load
    '''
    matrix = [[0]*len(CHORDS) for _ in range(len(CHORDS))]
    for i in range(len(matrix)):
        matrix[i][i] = 1 - sum(matrix[i])
    return matrix 

def get_audio_path(id):
    #mp3 = name[:-5] + ".mp3"
    #return os.path.join(AUDIO_DIR, mp3)
    # get audio link from Jamendo api
    r = requests.get(base_url+'v3.0/tracks', params={'id': id, 'client_id': client_id})
    return r.json()['results'][0]['audio']

@app.route("/")
def template_test():
    '''
    The initial page with empty diagram
    '''
    return render_template('template.html',
                            matrix=default_matrix(),
                            chord_map=CHORDS,
                            id_list=ids)

@app.route("/<id>")
def get_track(id):
    '''
    Page for each song
    '''
    id = int(id)
    matrix, sequence = process_track(id)
    return render_template('template.html',
                            audio_file=get_audio_path(id),
                            id_list=ids,
                            chord_map=CHORDS,
                            matrix=matrix,
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

