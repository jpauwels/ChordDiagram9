import os
from flask import Flask, render_template
import json

app = Flask(__name__)

TRACK_DIR = "tracks"
tracks = os.listdir(TRACK_DIR)

# Generate the list of all possible chords
tones = "ABCDEFG"
qualities = ("maj", "maj7", "min", "min7", "dom7", "7", "aug", "bmaj", "bmaj7", "b7", "bmin", "bmin7")
CHORDS = ["{}{}".format(tone, quality) for tone in tones for quality in qualities]

def chord_id(label):
    return CHORDS.index(label)

def process_track(path):
    with open(path) as f:
        d = json.load(f)
    labels = [chord_id(c['label']) for c in d["chordSequence"]]
    changes = [(labels[i], labels[i+1]) for i in range(len(labels) - 1)]
    matrix = [[0]*len(CHORDS) for _ in range(len(CHORDS))]
    for start, end in changes:
        matrix[start][end] = 1
        matrix[end][start] = max(0.3, matrix[end][start])
    return matrix

@app.route("/")
def template_test():
    return render_template('template.html', track_list=tracks)

@app.route("/tracks/<name>")
def get_track(name):
    return render_template('vis.html',
                            chord_map=CHORDS,
                            matrix=process_track(os.path.join(TRACK_DIR, name)))

if __name__ == '__main__':
    app.run(debug=True)

