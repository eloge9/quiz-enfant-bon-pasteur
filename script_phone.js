const socket = io("http://192.168.137.1:5000");
let team = "";
let canBuzz = true;
let buzzCount = 0;

document.getElementById("select-blue").onclick = function () {
  team = "Bleue";
  setupTeam("blue");
};

document.getElementById("select-yellow").onclick = function () {
  team = "Jaune";
  setupTeam("yellow");
};

function setupTeam(color) {
  document.getElementById("team-selection").classList.remove("hidden");
  document.getElementById("team-info").classList.remove("hidden");
  document.getElementById("team-name").innerText = "Équipe " + team;
  document.body.style.backgroundColor =
    color === "blue" ? "#cce5ff" : "#fff3cd";

  document.querySelector(".team-selection").classList.add("hidden");

  // Personnaliser le buzzer selon l'équipe
  const buzzer = document.getElementById("buzzer");
  if (color === "blue") {
    buzzer.style.backgroundColor = "#007bff";
    buzzer.style.color = "white";
  } else {
    buzzer.style.backgroundColor = "#ffc107";
    buzzer.style.color = "black";
  }
}

document.getElementById("buzzer").onclick = function () {
  if (canBuzz) {
    socket.emit("buzz", { team: team });
    buzzCount++;
    document.getElementById("buzz-count").innerText =
      "Nombre de buzz: " + buzzCount;

    // Effet visuel temporaire
    this.style.transform = "scale(0.95)";
    this.style.opacity = "0.8";

    // Désactiver temporairement le buzzer
    canBuzz = false;
    setTimeout(() => {
      canBuzz = true;
      this.style.transform = "";
      this.style.opacity = "";
    }, 1000); // Délai de 1 seconde entre les buzz
  }
};

socket.on("display_team", function (data) {
  document.getElementById("buzzed-team").innerText =
    "L'équipe " + data.team + " a buzzé!";
  document.getElementById("team-display").classList.remove("hidden");
});

socket.on("update_timer", function (data) {
  document.getElementById("timer").innerText =
    "Temps restant: " + data.time + "s";
});

socket.on("update_answer_timer", function (data) {
  document.getElementById("answer-timer").innerText =
    "Temps pour répondre: " + data.time + "s";
});

socket.on("reset_buzzers", function () {
  canBuzz = true;
  document.getElementById("team-display").classList.add("hidden");
  document.getElementById("buzzer").style.transform = "";
  document.getElementById("buzzer").style.opacity = "";
});

socket.on("times_up", function () {
  alert("Temps écoulé !");
});

socket.on("times_up_answer", function () {
  alert("Temps de réponse écoulé !");
});

// Gestion des erreurs de connexion
socket.on("connect_error", function (error) {
  console.log("Erreur de connexion:", error);
  alert("Erreur de connexion au serveur");
});

// Gestion de la reconnexion
socket.on("reconnect", function (attemptNumber) {
  console.log("Reconnecté après", attemptNumber, "tentatives");
});
