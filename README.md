# Quiz Enfant Bon Pasteur

## 🎮 Système de Quiz Interactif avec Buzzers

Un système de quiz complet avec buzzers en temps réel pour enfants, créé avec Flask et SocketIO.

## ✨ Fonctionnalités

### 🏆 Quiz Multi-équipes
- **2 équipes** (Bleue et Jaune) avec buzzers individuels
- **Système de scores** avec animations
- **Compteurs de buzz** pour chaque équipe
- **Timers** automatiques (10s questions, 5s réponses)

### 📱 Interface Multi-écrans
- **Interface principale** : Tableau de contrôle et affichage
- **Interface mobile** : Buzzer pour les téléphones
- **Communication en temps réel** avec Socket.IO

### 🎨 Animations & Effets
- **Animations de buzz** avec effets lumineux
- **Animations de score** quand des points sont ajoutés
- **Effets sonores** (buzz, victoire, etc.)
- **Interface responsive** et moderne

### 🌐 Configuration Réseau Automatique
- **Détection automatique** de l'adresse IP
- **Compatible tous réseaux** sans modification manuelle
- **QR codes** pour connexion facile (futur)

## 🚀 Démarrage Rapide

```bash
# Installer les dépendances
pip install flask flask-socketio flask-cors

# Démarrer le serveur
python server.py
```

## 📱 Accès aux Interfaces

- **Interface principale** : http://localhost:5000
- **Interface mobile** : http://localhost:5000/phone
- **Réseau local** : http://[VOTRE_IP]:5000

## 📁 Structure du Projet

```
quiz-enfant-bon-pasteur/
├── server.py              # Serveur Flask avec SocketIO
├── templates/             # Pages HTML
│   ├── index.html         # Interface principale
│   └── phone.html         # Interface mobile
├── static/
│   ├── css/               # Styles
│   │   ├── style_index.css
│   │   ├── style_phone.css
│   │   └── animations.css # Animations
│   ├── js/                # JavaScript
│   │   ├── config.js      # Configuration auto IP
│   │   ├── script_index.js
│   │   └── script_phone.js
│   └── media/             # Images et sons
│       ├── *.mp3          # Effets sonores
│       └── *.jpg          # Images
└── README.md
```

## 🎯 Utilisation

1. **Démarrer le serveur** : `python server.py`
2. **Ouvrir l'interface principale** sur l'ordinateur
3. **Scanner ou accéder** à l'URL mobile depuis les téléphones
4. **Choisir une équipe** et commencer à buzz !

## 🔧 Configuration Réseau

Le projet détecte **automatiquement** votre adresse IP. Pas besoin de modifier les fichiers quand vous changez de réseau !

## 🎮 Contrôles

### Interface Principale
- **Lancer le Timer** : Démarre le compte à rebours
- **Buzzer équipe** : Test des buzzers locaux
- **Ajouter points** : +5 points par équipe

### Interface Mobile
- **Choisir l'équipe** : Bleue ou Jaune
- **BUZZ!** : Buzzer pour répondre

## 🔄 Prochaines Améliorations

- [ ] Base de données de questions
- [ ] Mode multi-manches
- [ ] Interface admin complète
- [ ] QR codes de connexion
- [ ] Mode compétition avec podium
- [ ] Sauvegarde des parties

---

**Créé avec ❤️ pour les enfants du Bon Pasteur**
