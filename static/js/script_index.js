const socket = io.connect(window.SOCKET_IO_URL);
let isBuzzed = false;
let currentTeam = "";
let questionTimerInterval, answerTimerInterval;
let isTimerRunning = false;
// fonction pour permetre d'afvoir un son comme effet sonor
// Précharger les sons
const ringSound = new Audio(window.mediaPaths.enter);
const winSound = new Audio(window.mediaPaths.win);
ringSound.volume = 0.5;
winSound.volume = 0.5;

const ring = () => {
  ringSound.currentTime = 0;
  ringSound.play().catch(e => console.log('Son ring bloqué:', e));
};
const win = () => {
  winSound.currentTime = 0;
  winSound.play().catch(e => console.log('Son win bloqué:', e));
};

// Gesttion des scores de chaque equipe et des buzz
socket.on("update_scores", function (data) {
  document.getElementById("blue-score").textContent =
    "Score : " + data.blue_score;
  document.getElementById("yellow-score").textContent =
    "Score : " + data.yellow_score;
});

socket.on("display_team", function (data) {
  document.querySelectorAll(".buzzed-team").forEach(function (element) {
    element.textContent =
      data.team + " a buzzé! (Buzz #" + data.buzz_count + ")";
    element.classList.add("buzzed");
    ring();
  });

  const counterId =
    data.team === "Bleue" ? "blue-buzz-counter" : "yellow-buzz-counter";
  const counter = document.getElementById(counterId);
  counter.textContent = "Nombre de buzz: " + data.buzz_count;

  counter.classList.add("buzz-animation");
  setTimeout(() => {
    counter.classList.remove("buzz-animation");
  }, 500);

  if (data.team === "Bleue") {
    document.getElementById("yellow-buzzer").disabled = true;
    stopQuestionTimer();
    startAnswerTimer("blue");
    currentTeam = "blue";
  } else if (data.team === "Jaune") {
    document.getElementById("blue-buzzer").disabled = true;
    stopQuestionTimer();
    startAnswerTimer("yellow");
    currentTeam = "yellow";
  }
});

// Gestion du temps des timers
socket.on("update_timer", function (data) {
  const progress = ((10 - data.time) / 10) * 100;
  document.getElementById("question-timer-bar").style.width = progress + "%";
  document.getElementById("question-timer-bar-yellow").style.width =
    progress + "%";
  document.getElementById("timer-display").textContent =
    "Temps restant: " + data.time + "s";
});

socket.on("update_answer_timer", function (data) {
  const progress = ((5 - data.time) / 5) * 100;
  const timerBar =
    currentTeam === "blue"
      ? document.getElementById("answer-timer-bar")
      : document.getElementById("answer-timer-bar-yellow");
  timerBar.style.width = progress + "%";
});

function startQuestionTimer() {
  if (!isBuzzed && !isTimerRunning) {
    isTimerRunning = true;
    let duration = 10;
    let progress = 0;

    // Réinitialisation des barres et de l'affichage
    document.getElementById("question-timer-bar").style.width = "0%";
    document.getElementById("question-timer-bar-yellow").style.width = "0%";
    document.getElementById("timer-display").textContent = "Temps restant: 10s";

    questionTimerInterval = setInterval(function () {
      progress += 99 / (duration * 10);
      if (progress >= 100) {
        clearInterval(questionTimerInterval);
        isTimerRunning = false;
        socket.emit("times_up");
        resetBuzzers();
        win();
      } else {
        document.getElementById("question-timer-bar").style.width =
          progress + "%";
        document.getElementById("question-timer-bar-yellow").style.width =
          progress + "%";
        const timeLeft = Math.ceil(duration * (1 - progress / 100));
        document.getElementById("timer-display").textContent =
          "Temps restant: " + timeLeft + "s";
      }
    }, 100);
  }
}

function stopQuestionTimer() {
  clearInterval(questionTimerInterval);
  isTimerRunning = false;
}

function startAnswerTimer(team) {
  let duration = 5;
  let progress = 0;
  clearInterval(answerTimerInterval);

  const blueTimer = document.getElementById("answer-timer-bar");
  const yellowTimer = document.getElementById("answer-timer-bar-yellow");

  // Réinitialiser les barres
  blueTimer.style.width = "0%";
  yellowTimer.style.width = "0%";

  answerTimerInterval = setInterval(function () {
    progress += 100 / (duration * 10);
    if (progress >= 100) {
      clearInterval(answerTimerInterval);
      resetBuzzers();
      win();
    } else {
      if (team === "blue") {
        blueTimer.style.width = progress + "%";
      } else {
        yellowTimer.style.width = progress + "%";
      }
    }
  }, 100);
}

function resetBuzzers() {
  document.getElementById("blue-buzzer").disabled = false;
  document.getElementById("yellow-buzzer").disabled = false;
  document.querySelectorAll(".buzzed-team").forEach(function (element) {
    element.textContent = "Aucune équipe n'a buzzé";
    element.classList.remove("buzzed");
  });
  document.getElementById("blue-buzz-counter").textContent =
    "Nombre de buzz: 0";
  document.getElementById("yellow-buzz-counter").textContent =
    "Nombre de buzz: 0";

  // Réinitialiser toutes les barres de progression
  document.getElementById("question-timer-bar").style.width = "0%";
  document.getElementById("question-timer-bar-yellow").style.width = "0%";
  document.getElementById("answer-timer-bar").style.width = "0%";
  document.getElementById("answer-timer-bar-yellow").style.width = "0%";
  document.getElementById("timer-display").textContent = "";

  isBuzzed = false;
  currentTeam = "";
  isTimerRunning = false;
  clearInterval(questionTimerInterval);
  clearInterval(answerTimerInterval);
}

// Event Listeners
document.getElementById("start-timer-button").addEventListener("click", () => {
  resetBuzzers();
  startQuestionTimer();
});

document.getElementById("blue-buzzer").addEventListener("click", () => {
  if (!isBuzzed) {
    socket.emit("buzz", { team: "Bleue" });
    isBuzzed = true;
  }
});

document.getElementById("yellow-buzzer").addEventListener("click", () => {
  if (!isBuzzed) {
    socket.emit("buzz", { team: "Jaune" });
    isBuzzed = true;
  }
});

// ajout des point a chaque equipe
document.getElementById("blue-add-points").addEventListener("click", () => {
  socket.emit("add_points", { team: "Bleue", points: 5 });
  const scoreElement = document.getElementById("blue-score");
  scoreElement.classList.add("updated");
  setTimeout(() => scoreElement.classList.remove("updated"), 500);
});

document.getElementById("yellow-add-points").addEventListener("click", () => {
  socket.emit("add_points", { team: "Jaune", points: 5 });
  const scoreElement = document.getElementById("yellow-score");
  scoreElement.classList.add("updated");
  setTimeout(() => scoreElement.classList.remove("updated"), 500);
});

// Socket Events
socket.on("times_up", () => {
  alert("Temps écoulé !");
  resetBuzzers();
});

socket.on("times_up_answer", () => {
  alert("Temps de réponse écoulé !");
  resetBuzzers();
});

socket.on("reset_buzzers", resetBuzzers);

// Gestion des erreurs de connexion
socket.on("connect_error", (error) => {
  console.error("Erreur de connexion:", error);
});

socket.on("connect", () => {
  console.log("Connecté au serveur");
});

socket.on("disconnect", () => {
  console.log("Déconnecté du serveur");
});
