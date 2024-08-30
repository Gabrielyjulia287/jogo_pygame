# app.py (Flask)
from flask import Flask, render_template, redirect, url_for
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game')
def start_game():
    # Aqui você pode usar subprocess para iniciar o jogo Pygame
    subprocess.Popen(['python', 'game.py'])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
