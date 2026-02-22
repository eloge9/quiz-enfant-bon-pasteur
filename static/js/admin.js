const socket = io();

// Variables globales
let questions = [];
let currentQuestionIndex = 0;
let timerInterval = null;

// Charger les questions au démarrage
function loadQuestions() {
    fetch('/api/questions')
        .then(response => response.json())
        .then(data => {
            questions = data;
            if (questions.length > 0) {
                displayQuestion(0);
            }
        })
        .catch(error => console.error('Erreur:', error));
}

// Afficher une question
function displayQuestion(index) {
    if (index < 0 || index >= questions.length) return;

    const question = questions[index];
    document.getElementById('question-text').textContent = question.texte;

    // Masquer les deux types de réponses
    document.getElementById('simple-answer').classList.add('hidden');
    document.getElementById('qcm-answer').classList.add('hidden');

    if (question.type === 'simple') {
        // Afficher type simple
        document.getElementById('simple-answer').classList.remove('hidden');
        document.getElementById('simple-answer-text').textContent = question.reponse;
    } else if (question.type === 'qcm') {
        // Afficher type QCM
        document.getElementById('qcm-answer').classList.remove('hidden');
        const container = document.getElementById('propositions-container');
        container.innerHTML = '';

        question.propositions.forEach((prop, i) => {
            const div = document.createElement('div');
            div.className = 'proposition';
            div.textContent = `${i + 1}. ${prop}`;

            // Mettre en évidence la bonne réponse
            if (prop === question.reponse) {
                div.classList.add('correct');
            }

            container.appendChild(div);
        });
    }

    currentQuestionIndex = index;
}

// Navigation
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        displayQuestion(currentQuestionIndex);
        socket.emit('load_question', questions[currentQuestionIndex].id);
    }
}

function nextQuestion() {
    if (currentQuestionIndex < questions.length - 1) {
        currentQuestionIndex++;
        displayQuestion(currentQuestionIndex);
        socket.emit('load_question', questions[currentQuestionIndex].id);
    } else {
        // Revenir à la première
        currentQuestionIndex = 0;
        displayQuestion(0);
        socket.emit('load_question', questions[0].id);
    }
}

// Timer - utilise le système existant
function startTimer() {
    socket.emit('start_timer');
}

function stopTimer() {
    socket.emit('reset'); // Utilise le reset du système existant
}

function resetTimer() {
    socket.emit('reset');
}

// Gestion des points - utilise le système existant
function updatePoints(equipeId, change) {
    const teamName = equipeId === 1 ? 'Bleue' : 'Jaune';
    socket.emit('add_points', {
        'team': teamName,
        'points': change
    });
}

// Socket.IO Events - écoute les événements du système existant
socket.on('connect', () => {
    console.log('Connecté au serveur');
    loadQuestions();
});

socket.on('initial_data', (data) => {
    // Mettre à jour les points des équipes
    if (data.scores) {
        document.getElementById('blue-points').textContent = data.scores.blue_score;
        document.getElementById('yellow-points').textContent = data.scores.yellow_score;
    }

    // Mettre à jour le timer
    if (data.timer_running) {
        document.getElementById('timer-text').textContent = data.timer_seconds;
        document.getElementById('timer-visual').classList.add('warning');
    }

    // Afficher la question actuelle si elle existe
    if (data.current_question) {
        displayQuestionFromData(data.current_question);
    }
});

socket.on('update_scores', (data) => {
    // Mettre à jour l'affichage des points
    document.getElementById('blue-points').textContent = data.blue_score;
    document.getElementById('yellow-points').textContent = data.yellow_score;
});

socket.on('update_timer', (data) => {
    document.getElementById('timer-text').textContent = data.time;

    // Avertissement visuel
    if (data.time <= 10) {
        document.getElementById('timer-visual').classList.add('warning');
    } else {
        document.getElementById('timer-visual').classList.remove('warning');
    }
});

socket.on('times_up', () => {
    document.getElementById('timer-text').textContent = '0';
    document.getElementById('timer-visual').classList.remove('warning');
});

socket.on('display_team', (data) => {
    // Afficher quelle équipe a buzzé
    console.log(`Équipe ${data.team} a buzzé!`);

    // Mettre en évidence visuelle
    const buzzDisplay = document.createElement('div');
    buzzDisplay.className = 'buzz-alert';
    buzzDisplay.innerHTML = `
        <div class="buzz-content">
            <h3>🔔 BUZZ!</h3>
            <p>Équipe ${data.team} a buzzé!</p>
            <small>Buzz #${data.buzz_count}</small>
        </div>
    `;

    // Ajouter à la page
    document.body.appendChild(buzzDisplay);

    // Supprimer après 3 secondes
    setTimeout(() => {
        buzzDisplay.remove();
    }, 3000);
});

socket.on('question_loaded', (data) => {
    if (data) {
        displayQuestionFromData(data);
    }
});

// Fonction pour afficher une question depuis les données
function displayQuestionFromData(question) {
    document.getElementById('question-text').textContent = question.texte;

    // Masquer les deux types de réponses
    document.getElementById('simple-answer').classList.add('hidden');
    document.getElementById('qcm-answer').classList.add('hidden');

    if (question.type === 'simple') {
        // Afficher type simple
        document.getElementById('simple-answer').classList.remove('hidden');
        document.getElementById('simple-answer-text').textContent = question.reponse;
    } else if (question.type === 'qcm') {
        // Afficher type QCM
        document.getElementById('qcm-answer').classList.remove('hidden');
        const container = document.getElementById('propositions-container');
        container.innerHTML = '';

        question.propositions.forEach((prop, i) => {
            const div = document.createElement('div');
            div.className = 'proposition';
            div.textContent = `${i + 1}. ${prop}`;

            // Mettre en évidence la bonne réponse
            if (prop === question.reponse) {
                div.classList.add('correct');
            }

            container.appendChild(div);
        });
    }
}

// Raccourcis clavier
document.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'ArrowLeft':
            previousQuestion();
            break;
        case 'ArrowRight':
            nextQuestion();
            break;
        case ' ':
            e.preventDefault();
            startTimer();
            break;
        case 'Escape':
            stopTimer();
            break;
        case 'r':
        case 'R':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                resetTimer();
            }
            break;
    }
});

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    loadQuestions();
});
