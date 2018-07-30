import os
from flask import Flask, render_template, send_from_directory
import json

app = Flask(__name__)

AUDIO_DIR = "audio"
TRACK_DIR = "tracks"
tracks = os.listdir(TRACK_DIR)

# Generate the list of all possible chords
tones = "ABCDEFG"
qualities = ("maj", "maj7", "min", "min7", "dom7", "7", "aug", "bmaj", "bmaj7", "b7", "bmin", "bmin7")
CHORDS = ["{}{}".format(tone, quality) for tone in tones for quality in qualities]

def chord_id(label):
    return CHORDS.index(label)

def process_track(path):
    '''
    Load track from json file and parse into a matrix
    '''

    # Load file
    with open(path) as f:
        d = json.load(f)
    labels = [chord_id(c['label']) for c in d["chordSequence"]]
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

def get_audio_path(name):
    wav = name[:-5] + ".wav"
    return os.path.join(AUDIO_DIR, wav)

@app.route("/")
def template_test():
    '''
    The initial page with empty diagram
    '''
    return render_template('template.html',
                            matrix=default_matrix(),
                            chord_map=CHORDS,
                            track_list=tracks)

@app.route("/tracks/<name>")
def get_track(name):
    '''
    Page for each song
    '''
    matrix, sequence = process_track(os.path.join(TRACK_DIR, name)) 
    return render_template('template.html',
                            audio_file=get_audio_path(name),
                            track_list=tracks,
                            chord_map=CHORDS,
                            matrix=matrix,
                            sequence=sequence)

@app.route("/tracks/audio/<name>")
def get_audio(name):
    '''
    Audio for each song
    '''
    return send_from_directory("audio", name)

@app.route("/static/<resource>")
def get_static(resource):
    return send_from_directory("static", resource)

if __name__ == '__main__':
    app.run(debug=True)

