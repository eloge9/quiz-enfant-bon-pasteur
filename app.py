from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import time
import json
from database import init_database, get_connection

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins=["*"])

# Variables globales du système existant
buzzed_team = None
time_limit = 30
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

# Variables admin
current_question_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/phone')
def phone():
    return render_template('phone.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# === API POUR LES QUESTIONS ===

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Récupérer toutes les questions"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.id, q.texte, q.type, q.reponse,
               GROUP_CONCAT(p.texte, '|||') as propositions
        FROM questions q
        LEFT JOIN propositions p ON q.id = p.question_id
        GROUP BY q.id
        ORDER BY q.id
    ''')
    questions = []
    for row in cursor.fetchall():
        question = {
            'id': row[0],
            'texte': row[1],
            'type': row[2],
            'reponse': row[3],
            'propositions': row[4].split('|||') if row[4] else []
        }
        questions.append(question)
    conn.close()
    return jsonify(questions)

@app.route('/api/questions', methods=['POST'])
def add_question():
    """Ajouter une nouvelle question"""
    data = request.get_json()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insérer la question
    cursor.execute('''
        INSERT INTO questions (texte, type, reponse) VALUES (?, ?, ?)
    ''', (data['texte'], data['type'], data['reponse']))
    
    question_id = cursor.lastrowid
    
    # Insérer les propositions si c'est un QCM
    if data['type'] == 'qcm' and data.get('propositions'):
        for prop in data['propositions']:
            cursor.execute('''
                INSERT INTO propositions (question_id, texte) VALUES (?, ?)
            ''', (question_id, prop))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'question_id': question_id})

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Supprimer une question"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Supprimer d'abord les propositions
    cursor.execute('DELETE FROM propositions WHERE question_id = ?', (question_id,))
    
    # Supprimer la question
    cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# === API POUR LES ÉQUIPES ===

@app.route('/api/equipes', methods=['GET'])
def get_equipes():
    """Récupérer les équipes et leurs points"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nom, points FROM equipes ORDER BY id')
    equipes = []
    for row in cursor.fetchall():
        equipes.append({
            'id': row[0],
            'nom': row[1],
            'points': row[2]
        })
    conn.close()
    return jsonify(equipes)

@app.route('/api/equipes/<int:equipe_id>/points', methods=['POST'])
def update_points(equipe_id):
    """Mettre à jour les points d'une équipe"""
    data = request.get_json()
    points = data.get('points', 0)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Récupérer les points actuels
    cursor.execute('SELECT points FROM equipes WHERE id = ?', (equipe_id,))
    result = cursor.fetchone()
    
    if result:
        new_points = max(0, result[0] + points)  # Ne pas aller en dessous de 0
        cursor.execute('UPDATE equipes SET points = ? WHERE id = ?', (new_points, equipe_id))
        conn.commit()
        
        # Émettre l'événement Socket.IO
        socketio.emit('points_updated', {
            'equipe_id': equipe_id,
            'new_points': new_points,
            'change': points
        }, broadcast=True)
    
    conn.close()
    return jsonify({'success': True, 'new_points': new_points})

# === API POUR LE TIMER (INTÉGRATION SYSTÈME EXISTANT) ===

@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    """Démarrer le timer de 30 secondes (système existant)"""
    global timer_running, current_time
    timer_running = True
    current_time = time_limit
    
    socketio.emit('update_timer', {'time': current_time}, broadcast=True)
    socketio.start_background_task(timer_countdown)
    
    return jsonify({'success': True})

@app.route('/api/timer/stop', methods=['POST'])
def stop_timer():
    """Arrêter le timer (système existant)"""
    global timer_running
    timer_running = False
    
    socketio.emit('timer_stopped', broadcast=True)
    return jsonify({'success': True})

# === ÉVÉNEMENTS SOCKET.IO ===

def reset_timers():
    """Réinitialiser les timers (système existant)"""
    global current_time, current_answer_time, buzzed_team, timer_running
    current_time = time_limit
    current_answer_time = answer_time_limit
    buzzed_team = None
    timer_running = False
    emit('reset_buzzers', broadcast=True)

# === ÉVÉNEMENTS SOCKET.IO SYSTÈME EXISTANT ===

@socketio.on('connect')
def handle_connect():
    """Quand un client se connecte"""
    print('Client connecté - SID:', request.sid)
    print('Origin:', request.environ.get('HTTP_ORIGIN', 'Unknown'))
    
    # Envoyer les données initiales
    emit('initial_data', {
        'equipes': get_equipes().get_json().get_json(),
        'current_question': get_current_question(),
        'timer_running': timer_running,
        'timer_seconds': current_time if timer_running else time_limit,
        'buzzed_team': buzzed_team,
        'scores': {'blue_score': blue_score, 'yellow_score': yellow_score}
    })

@socketio.on('buzz')
def handle_buzz(data):
    """Gérer le buzz (système existant)"""
    global buzzed_team, current_time, buzz_count, last_buzz_time
    current_time_now = time.time()

    # Vérifier si le bon temps s'est écoulé depuis le dernier buzz
    if buzzed_team and buzzed_team != data['team'] and (current_time_now - last_buzz_time) < 5:
        return  # Zapper le buzz si le délai n'est pas écoulé

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
    """Débloquer l'autre équipe après 5 secondes"""
    global buzzed_team
    socketio.sleep(5)  # Attendre 5 secondes
    if buzzed_team:
        buzzed_team = None
        emit('unlock_teams', broadcast=True)

@socketio.on('start_timer')
def handle_start_timer():
    """Démarrer le timer (système existant)"""
    global timer_running
    timer_running = True
    socketio.start_background_task(timer_countdown)

def timer_countdown():
    """Compte à rebours du timer (système existant)"""
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
    """Ajouter des points (système existant)"""
    global blue_score, yellow_score
    if data['team'] == 'Bleue':
        blue_score += data['points']
    elif data['team'] == 'Jaune':
        yellow_score += data['points']
    
    # Mettre à jour dans la base de données
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE equipes SET points = ? WHERE nom = ?', (blue_score, 'Bleue'))
    cursor.execute('UPDATE equipes SET points = ? WHERE nom = ?', (yellow_score, 'Jaune'))
    conn.commit()
    conn.close()
    
    emit('update_scores', {'blue_score': blue_score, 'yellow_score': yellow_score}, broadcast=True)

@socketio.on('reset')
def handle_reset():
    """Réinitialiser le jeu (système existant)"""
    global buzz_count, last_buzz_time
    buzz_count = {'Bleue': 0, 'Jaune': 0}
    last_buzz_time = 0
    reset_timers()

@socketio.on('load_question')
def handle_load_question(question_id):
    """Charger une question spécifique"""
    global current_question_id
    current_question_id = question_id
    
    question_data = get_current_question()
    socketio.emit('question_loaded', question_data, broadcast=True)

def get_current_question():
    """Récupérer la question actuelle"""
    if current_question_id is None:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.id, q.texte, q.type, q.reponse,
               GROUP_CONCAT(p.texte, '|||') as propositions
        FROM questions q
        LEFT JOIN propositions p ON q.id = p.question_id
        WHERE q.id = ?
        GROUP BY q.id
    ''', (current_question_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'texte': row[1],
            'type': row[2],
            'reponse': row[3],
            'propositions': row[4].split('|||') if row[4] else []
        }
    return None

if __name__ == '__main__':
    # Initialiser la base de données
    init_database()
    
    print("Démarrage du serveur de quiz...")
    print("Accès à l'interface admin : http://localhost:5000/admin")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
