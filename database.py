import sqlite3
import os

# Nom de la base de données
DB_NAME = 'quiz.db'

def init_database():
    """Initialiser la base de données SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Créer la table questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texte TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('simple', 'qcm')),
            reponse TEXT NOT NULL
        )
    ''')
    
    # Créer la table propositions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS propositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            texte TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Créer la table equipes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            points INTEGER DEFAULT 0
        )
    ''')
    
    # Insérer les équipes par défaut si elles n'existent pas
    cursor.execute('INSERT OR IGNORE INTO equipes (nom, points) VALUES (?, ?)', ('Bleue', 0))
    cursor.execute('INSERT OR IGNORE INTO equipes (nom, points) VALUES (?, ?)', ('Jaune', 0))
    
    conn.commit()
    conn.close()

def get_connection():
    """Obtenir une connexion à la base de données"""
    return sqlite3.connect(DB_NAME)

# Initialiser la base de données au démarrage
if not os.path.exists(DB_NAME):
    init_database()
