from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins=["http://192.168.137.1:5501", "http://localhost:63342",
                                               "http://localhost:5000"])

buzzed_team = None
time_limit = 10
current_time = time_limit
answer_time_limit = 5
current_answer_time = answer_time_limit

# Variables globales pour les scores et le compteur de buzz
blue_score = 0
yellow_score = 0
buzz_count = {'Bleue': 0, 'Jaune': 0}
last_buzz_time = 0

timer_thread = None
answer_timer_thread = None
timer_running = False


def reset_timers():
    global current_time, current_answer_time, buzzed_team, timer_running
    current_time = time_limit
    current_answer_time = answer_time_limit
    buzzed_team = None
    timer_running = False
    emit('reset_buzzers', broadcast=True)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connecté')


@socketio.on('buzz')
def handle_buzz(data):
    global buzzed_team, current_time, buzz_count, last_buzz_time
    current_time_now = time.time()

    # Vérifions si le bon temp s'est écoulé depuis le dernier buzz
    if buzzed_team and buzzed_team != data['team'] and (current_time_now - last_buzz_time) < 5:
        return  # zapper le buzz si le délai n'est pas écoulé

    team = data['team']
    buzz_count[team] = buzz_count.get(team, 0) + 1
    buzzed_team = team
    last_buzz_time = current_time_now

    emit('display_team', {
        'team': buzzed_team,
        'buzz_count': buzz_count[team]
    }, broadcast=True)

    # Démarrer le timer de déblocage
    socketio.start_background_task(unlock_other_team)


def unlock_other_team():
    global buzzed_team
    socketio.sleep(5)  # Attendre 5 secondes
    if buzzed_team:
        buzzed_team = None
        emit('unlock_teams', broadcast=True)


@socketio.on('start_timer')
def handle_start_timer():
    global timer_running
    timer_running = True
    socketio.start_background_task(timer_countdown)


def timer_countdown():
    global current_time, timer_running
    while current_time > 0 and timer_running:
        emit('update_timer', {'time': current_time}, broadcast=True)
        socketio.sleep(1)
        current_time -= 1
    if current_time <= 0:
        emit('times_up', broadcast=True)
        reset_timers()


@socketio.on('add_points')
def handle_add_points(data):
    global blue_score, yellow_score
    if data['team'] == 'Bleue':
        blue_score += data['points']
    elif data['team'] == 'Jaune':
        yellow_score += data['points']
    emit('update_scores', {'blue_score': blue_score, 'yellow_score': yellow_score}, broadcast=True)


@socketio.on('reset')
def handle_reset():
    global buzz_count, last_buzz_time
    buzz_count = {'Bleue': 0, 'Jaune': 0}
    last_buzz_time = 0
    reset_timers()


if __name__ == '__main__':
    print("Demarage server")
    socketio.run(app, host='0.0.0.0', port=5000)