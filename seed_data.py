"""
Script pour ajouter des questions d'exemple dans la base de données
"""
import sqlite3
from database import get_connection

def add_sample_questions():
    """Ajouter des questions d'exemple"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Questions simples
    questions_simples = [
        ("Quel est le premier livre de la Bible ?", "simple", "Genèse"),
        ("Combien de disciples Jésus avait-il ?", "simple", "12"),
        ("Qui a construit l'arche ?", "simple", "Noé"),
        ("Quel est le fruit défendu dans le jardin d'Éden ?", "simple", "L'arbre de la connaissance du bien et du mal"),
        ("Qui a été jeté dans la fosse aux lions ?", "simple", "Daniel"),
    ]
    
    # Questions QCM
    questions_qcm = [
        ("Qui a mené les Hébreux hors d'Égypte ?", "qcm", "Moïse", ["Moïse", "Abraham", "David", "Salomon"]),
        ("Quel est le plus grand commandement ?", "qcm", "Aimer Dieu et son prochain", ["Aimer Dieu et son prochain", "Ne pas tuer", "Honorer ses parents", "Ne pas voler"]),
        ("Qui a renié Jésus trois fois ?", "qcm", "Pierre", ["Pierre", "Jean", "Judas", "Thomas"]),
        ("Dans quel ville Jésus est-il né ?", "qcm", "Bethléem", ["Bethléem", "Jérusalem", "Nazareth", "Capharnaüm"]),
        ("Qui a écrit la plupart des épîtres du Nouveau Testament ?", "qcm", "Paul", ["Paul", "Pierre", "Jean", "Jacques"]),
    ]
    
    # Insérer les questions simples
    for texte, type_q, reponse in questions_simples:
        cursor.execute('''
            INSERT INTO questions (texte, type, reponse) VALUES (?, ?, ?)
        ''', (texte, type_q, reponse))
    
    # Insérer les questions QCM
    for texte, type_q, reponse, propositions in questions_qcm:
        cursor.execute('''
            INSERT INTO questions (texte, type, reponse) VALUES (?, ?, ?)
        ''', (texte, type_q, reponse))
        
        question_id = cursor.lastrowid
        
        # Insérer les propositions
        for prop in propositions:
            cursor.execute('''
                INSERT INTO propositions (question_id, texte) VALUES (?, ?)
            ''', (question_id, prop))
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(questions_simples) + len(questions_qcm)} questions ajoutées avec succès!")

if __name__ == '__main__':
    add_sample_questions()
