📘 GradeTrack

GradeTrack est une petite application que j’ai créée pour suivre mes notes et mes moyennes.
L’idée est d’avoir un outil simple, visuel et pratique pour ne plus se perdre dans les calculs et voir son évolution au fil du temps.

* Ce que l’app permet de faire

Ajouter des notes avec matière, type d’évaluation et coefficient

Voir un tableau récapitulatif avec possibilité de corriger ou supprimer des notes

Calculer automatiquement la moyenne générale et par matière

Afficher des graphiques (histogrammes, évolution des notes, comparaison entre matières)

Exporter les notes en CSV pour les sauvegarder


Installation

1. Télécharger le projet (ou cloner depuis GitHub si disponible)


2. Installer les dépendances :

pip install streamlit pandas matplotlib


3. Lancer l’application :

streamlit run GradeTrack_app.py


Organisation

GradeTrack/
│── GradeTrack_app.py   # Code principal
│── notes.csv           # Fichier généré automatiquement avec les notes
│── README.md           # Ce fichier

💡 Idées pour la suite

Pouvoir se connecter avec un compte

Exporter directement en Excel

Ajouter des filtres (par trimestre, par matière, etc.)

Pourquoi pas un jour une IA qui prédit la moyenne à la fin du semestre
