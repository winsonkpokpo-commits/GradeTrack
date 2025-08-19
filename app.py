GradeTrack - Application Streamlit pour le suivi des notes et moyennes

Fichier réécrit 

import streamlit as st import pandas as pd import matplotlib.pyplot as plt import io import os import uuid from typing import List, Dict, Any, Optional

--- Configuration ---

st.set_page_config(page_title="GradeTrack", layout="wide") CSV_PATH = "notes.csv"

--- Fonctions utilitaires ---

def charger_donnees() -> List[Dict[str, Any]]: """Charge les données depuis le CSV et renvoie une liste de dictionnaires. Si le fichier est absent ou illisible, renvoie une liste vide. """ if os.path.exists(CSV_PATH): try: df = pd.read_csv(CSV_PATH) # S'assurer que les colonnes essentielles existent expected_cols = {"id", "Eleve", "Matiere", "Note", "Coefficient", "Trimestre"} if not expected_cols.issubset(set(df.columns)): # Tentative de réparation : ignorer colonnes supplémentaires / manquantes df = df.reindex(columns=list(expected_cols & set(df.columns))) return df.to_dict(orient="records") except Exception as e: st.warning(f"Erreur lors du chargement des données : {e}") return []

def sauvegarder_donnees(): """Sauvegarde le contenu de st.session_state.data dans le CSV. Utilise un écrasement atomique simple (écriture directe).""" try: pd.DataFrame(st.session_state.data).to_csv(CSV_PATH, index=False) except Exception as e: st.error(f"Erreur lors de la sauvegarde : {e}")

def ajouter_note(eleve: str, matiere: str, note: float, coef: float, trimestre: str) -> None: """Ajoute une note (sous forme de dict) dans st.session_state.data puis sauvegarde.""" # Validation minimale if not eleve or eleve.strip() == "": st.error("Nom d'élève invalide") return if not matiere or matiere.strip() == "": st.error("Matière invalide") return try: note_val = float(note) coef_val = float(coef) except Exception: st.error("Note ou coefficient invalide") return

nouvelle = {
    "id": str(uuid.uuid4()),
    "Eleve": eleve.strip(),
    "Matiere": matiere.strip(),
    "Note": note_val,
    "Coefficient": coef_val,
    "Trimestre": str(trimestre)
}
st.session_state.data.append(nouvelle)
sauvegarder_donnees()

def supprimer_note(note_id: str) -> None: """Supprime une note par son id, sauvegarde et relance l'app.""" original_len = len(st.session_state.data) st.session_state.data = [n for n in st.session_state.data if n.get("id") != note_id] if len(st.session_state.data) < original_len: sauvegarder_donnees() st.toast("Note supprimée avec succès", icon="🗑️") st.experimental_rerun() else: st.warning("ID non trouvé : impossible de supprimer la note")

def calcul_moyenne(df: pd.DataFrame) -> Optional[float]: """Calcule la moyenne pondérée (Note * Coef) / somme(coef). Retourne None si impossible (pas de notes ou somme des coefficients = 0). """ if df is None or df.empty: return None # Assurer des conversions numériques df = df.copy() df['Note'] = pd.to_numeric(df['Note'], errors='coerce') df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce') df = df.dropna(subset=['Note', 'Coefficient']) total_coef = df['Coefficient'].sum() if total_coef == 0: return None weighted_sum = (df['Note'] * df['Coefficient']).sum() return float(weighted_sum / total_coef)

def couleur_moyenne(moy: Optional[float]) -> str: if moy is None: return "gray" if moy >= 16: return "green" if moy >= 12: return "orange" return "red"

--- Initialisation de l'état ---

if 'data' not in st.session_state: st.session_state.data = charger_donnees()

Construire la liste d'élèves

eleves = sorted({d['Eleve'] for d in st.session_state.data if d.get('Eleve')})

Toujours proposer l'option de créer un nouvel élève

eleves_with_option = ["-- Nouvel élève --"] + eleves

--- Sidebar: sélection élève et options globales ---

st.sidebar.title("Contrôles") selected = st.sidebar.selectbox("🎓 Choisir un élève", options=eleves_with_option)

Si l'utilisateur veut créer un nouvel élève, on affiche un champ

if selected == "-- Nouvel élève --": new_name = st.sidebar.text_input("Nom du nouvel élève") if st.sidebar.button("➕ Créer l'élève"): if not new_name or new_name.strip() == "": st.sidebar.warning("Entrez un nom valide.") elif new_name.strip() in eleves: st.sidebar.warning("Cet élève existe déjà.") else: # On l'ajoute comme une entrée sans notes pour qu'il apparaisse dans la liste eleves.append(new_name.strip()) st.session_state.data.append({ "id": str(uuid.uuid4()), "Eleve": new_name.strip(), "Matiere": "", "Note": 0.0, "Coefficient": 0.0, "Trimestre": "1", }) sauvegarder_donnees() st.sidebar.success(f"Élève '{new_name.strip()}' créé.") st.experimental_rerun()

Bouton réinitialiser (avec confirmation)

if st.sidebar.button("🔁 Réinitialiser toutes les données"): if st.sidebar.checkbox("Confirmer la suppression de toutes les données"): st.session_state.data = [] sauvegarder_donnees() st.sidebar.success("Toutes les données ont été supprimées.") st.experimental_rerun()

st.title("📊 GradeTrack - Suivi des notes et moyennes")

Si l'utilisateur a choisi "-- Nouvel élève --" et n'a pas encore créé un nom, on affiche un message

if selected == "-- Nouvel élève --" and not ("new_name" in locals() and new_name.strip()): st.info("Créez un nouvel élève depuis la barre latérale puis revenez ici pour ajouter des notes.")

--- Formulaire d'ajout de note ---

with st.form("form_ajout_note"): st.subheader("Ajouter une note") eleve_input = selected # Si l'utilisateur a choisi de créer un nouvel élève et vient de saisir un nom, on le prend if selected == "-- Nouvel élève --" and 'new_name' in locals() and new_name.strip(): eleve_input = new_name.strip()

matiere = st.text_input("Matière")
note = st.number_input("Note (0-20)", min_value=0.0, max_value=20.0, value=10.0, step=0.1)
coef = st.number_input("Coefficient", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
trimestre = st.selectbox("Trimestre", ["1", "2", "3"])
submit = st.form_submit_button("➕ Ajouter la note")

if submit:
    if eleve_input in [None, "", "-- Nouvel élève --"]:
        st.warning("Veuillez sélectionner ou créer un élève avant d'ajouter une note.")
    else:
        if not matiere or matiere.strip() == "":
            st.warning("Veuillez entrer une matière valide.")
        else:
            ajouter_note(eleve_input, matiere.strip(), note, coef, trimestre)
            st.success(f"Note ajoutée pour {eleve_input} — {matiere.strip()} : {note} (coef {coef})")
            st.experimental_rerun()

--- Conversion des données en DataFrame propre ---

try: df = pd.DataFrame(st.session_state.data) except Exception: df = pd.DataFrame(columns=["id", "Eleve", "Matiere", "Note", "Coefficient", "Trimestre"])

S'assurer des colonnes

for col in ["id", "Eleve", "Matiere", "Note", "Coefficient", "Trimestre"]: if col not in df.columns: df[col] = None

Nettoyage type

if not df.empty: df['Note'] = pd.to_numeric(df['Note'], errors='coerce') df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce')

Déterminer l'élève sélectionné (après création possible)

eleve_choisi = None if selected == "-- Nouvel élève --": if 'new_name' in locals() and new_name.strip(): eleve_choisi = new_name.strip() else: eleve_choisi = selected

Si aucun élève sélectionné et qu'il existe des élèves, choisir le premier

if (not eleve_choisi or eleve_choisi == "-- Nouvel élève --") and eleves: eleve_choisi = eleves[0]

Filtrer les données pour l'élève choisi

if eleve_choisi and eleve_choisi in df['Eleve'].values: df_eleve = df[df['Eleve'] == eleve_choisi].copy() else: df_eleve = pd.DataFrame(columns=df.columns)

--- Filtres additionnels sur la barre latérale (uniquement si l'élève a des notes) ---

if not df_eleve.empty: matieres = sorted(df_eleve['Matiere'].dropna().unique()) filtre_matiere = st.sidebar.selectbox("Filtrer par matière", options=["Toutes"] + matieres) if filtre_matiere != "Toutes": df_eleve = df_eleve[df_eleve['Matiere'] == filtre_matiere]

filtre_trimestre = st.sidebar.selectbox("Filtrer par trimestre", options=["Tous", "1", "2", "3"])
if filtre_trimestre != "Tous":
    df_eleve = df_eleve[df_eleve['Trimestre'] == filtre_trimestre]

--- Onglets principaux ---

tab1, tab2, tab3 = st.tabs(["📄 Notes & Moyennes", "📚 Statistiques", "📊 Graphiques"])

with tab1: st.subheader(f"Notes enregistrées — {eleve_choisi if eleve_choisi else '—'}") if not df_eleve.empty: # Affichage par ligne avec bouton supprimer for idx, row in df_eleve.reset_index(drop=True).iterrows(): c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1]) c1.write(row.get('Matiere', '')) c2.write(row.get('Note', '')) c3.write(row.get('Coefficient', '')) c4.write(f"T{row.get('Trimestre', '')}") key_del = f"del_{row.get('id')}_{idx}" if c5.button("🗑️", key=key_del): supprimer_note(row.get('id'))

# Moyennes par trimestre + générale
    moyennes = {t: calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) for t in ['1', '2', '3']}
    moy_globale = calcul_moyenne(df_eleve)

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"**T1 :** <span style='color:{couleur_moyenne(moyennes['1'])}'>{(moyennes['1'] or 0):.2f}</span>", unsafe_allow_html=True)
    col2.markdown(f"**T2 :** <span style='color:{couleur_moyenne(moyennes['2'])}'>{(moyennes['2'] or 0):.2f}</span>", unsafe_allow_html=True)
    col3.markdown(f"**T3 :** <span style='color:{couleur_moyenne(moyennes['3'])}'>{(moyennes['3'] or 0):.2f}</span>", unsafe_allow_html=True)
    col4.markdown(f"**Générale :** <span style='color:{couleur_moyenne(moy_globale)}'>{(moy_globale or 0):.2f}</span>", unsafe_allow_html=True)

else:
    st.info("Aucune note trouvée pour cet élève.")

with tab2: st.subheader(f"Statistiques par matière — {eleve_choisi if eleve_choisi else '—'}") if not df_eleve.empty: stats = df_eleve.groupby('Matiere').apply( lambda g: pd.Series({ 'Moyenne': calcul_moyenne(g), 'Nb Notes': len(g), 'Total Coef': g['Coefficient'].sum() }) ).reset_index() st.dataframe(stats) else: st.info("Pas encore de notes pour cet élève.")

with tab3: st.subheader(f"Graphiques — {eleve_choisi if eleve_choisi else '—'}") if not df_eleve.empty: # Évolution trimestrielle moy_trimestres = [calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) or 0 for t in ['1', '2', '3']] fig1, ax1 = plt.subplots() ax1.plot(['1', '2', '3'], moy_trimestres, marker='o') ax1.set_ylim(0, 20) ax1.set_title("Évolution des moyennes trimestrielles") ax1.set_xlabel("Trimestre") ax1.set_ylabel("Moyenne") ax1.grid(True) st.pyplot(fig1)

# Moyenne par matière
    moy_matiere = df_eleve.groupby('Matiere').apply(calcul_moyenne)
    fig2, ax2 = plt.subplots()
    moy_matiere.plot(kind='bar', ax=ax2)
    counts = df_eleve['Matiere'].value_counts()
    for i, (label, val) in enumerate(moy_matiere.items()):
        ax2.text(i, val + 0.3, f"{int(counts[label])} note(s)", ha='center', fontsize=8)
    ax2.set_ylim(0, 20)
    ax2.set_title("Moyenne par matière")
    ax2.set_ylabel("Moyenne")
    st.pyplot(fig2)

    # Répartition des coefficients par matière (camembert)
    coef_matiere = df_eleve.groupby('Matiere')['Coefficient'].sum()
    if len(coef_matiere) > 1:
        fig3, ax3 = plt.subplots()
        ax3.pie(coef_matiere, labels=coef_matiere.index, autopct='%1.1f%%', startangle=90)
        ax3.set_title("Répartition des coefficients par matière")
        st.pyplot(fig3)
    else:
        st.info("Pas assez de matières pour générer un camembert.")
else:
    st.info("Pas encore de notes pour cet élève.")

--- Export CSV pour l'élève ---

if not df_eleve.empty: export_df = df_eleve.drop(columns=['id']) if 'id' in df_eleve.columns else df_eleve csv_buffer = io.StringIO() export_df.to_csv(csv_buffer, index=False) st.download_button("⬇️ Exporter les notes CSV", csv_buffer.getvalue(), file_name=f"notes_{eleve_choisi}.csv", mime="text/csv")

--- Message de fin / aide ---

st.sidebar.markdown("---") st.sidebar.markdown("Tips: Vous pouvez ajouter des élèves puis leurs notes.\n- Supprimez les notes avec l'icône 🗑️.\n- Utilisez l'export CSV pour partager les notes.")

