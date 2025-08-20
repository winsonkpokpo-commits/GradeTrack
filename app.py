""" GradeTrack - Application Streamlit pour le suivi des notes et moyennes Version améliorée : édition en ligne, interface réorganisée, export et sauvegarde. """

import streamlit as st import pandas as pd import matplotlib.pyplot as plt import io import os import uuid from typing import List, Dict, Any, Optional

--- Configuration ---

st.set_page_config(page_title="GradeTrack", layout="wide") CSV_PATH = "notes.csv" EXPECTED_COLS = ["id", "Eleve", "Matiere", "Note", "Coefficient", "Trimestre"]

Petite feuille de style (couleurs légères)

st.markdown( """ <style> .app-header {font-size:28px; font-weight:700;} .small-muted {color: #6c757d; font-size:12px} </style> """, unsafe_allow_html=True, )

--- Fonctions utilitaires ---

def charger_donnees() -> List[Dict[str, Any]]: if os.path.exists(CSV_PATH): try: df = pd.read_csv(CSV_PATH) for col in EXPECTED_COLS: if col not in df.columns: df[col] = None df = df.reindex(columns=EXPECTED_COLS) # Assurer des types simples if not df.empty: df['Note'] = pd.to_numeric(df['Note'], errors='coerce') df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce') return df.to_dict(orient="records") except Exception as e: st.warning(f"Erreur lors du chargement des données : {e}") return [] return []

def sauvegarder_donnees() -> None: try: df = pd.DataFrame(st.session_state.data) for col in EXPECTED_COLS: if col not in df.columns: df[col] = None df = df.reindex(columns=EXPECTED_COLS) tmp_path = CSV_PATH + ".tmp" df.to_csv(tmp_path, index=False) os.replace(tmp_path, CSV_PATH) except Exception as e: st.error(f"Erreur lors de la sauvegarde : {e}")

def ajouter_note(eleve: str, matiere: str, note: float, coef: float, trimestre: str) -> None: if not eleve or eleve.strip() == "": st.error("Nom d'élève invalide") return if not matiere or matiere.strip() == "": st.error("Matière invalide") return try: note_val = float(note) coef_val = float(coef) except Exception: st.error("Note ou coefficient invalide") return

nouvelle = {
    "id": str(uuid.uuid4()),
    "Eleve": eleve.strip(),
    "Matiere": matiere.strip(),
    "Note": note_val,
    "Coefficient": coef_val,
    "Trimestre": str(trimestre),
}
st.session_state.data.append(nouvelle)
sauvegarder_donnees()

def supprimer_note(note_id: str) -> None: original_len = len(st.session_state.data) st.session_state.data = [n for n in st.session_state.data if n.get("id") != note_id] if len(st.session_state.data) < original_len: sauvegarder_donnees() st.success("Note supprimée avec succès") st.experimental_rerun() else: st.warning("ID non trouvé : impossible de supprimer la note")

def calcul_moyenne(df: pd.DataFrame) -> Optional[float]: if df is None or df.empty: return None df = df.copy() df['Note'] = pd.to_numeric(df['Note'], errors='coerce') df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce') df = df.dropna(subset=['Note', 'Coefficient']) total_coef = df['Coefficient'].sum() if total_coef == 0: return None weighted_sum = (df['Note'] * df['Coefficient']).sum() return float(weighted_sum / total_coef)

def couleur_moyenne(moy: Optional[float]) -> str: if moy is None: return "gray" if moy >= 16: return "green" if moy >= 12: return "orange" return "red"

--- Initialisation de l'état ---

if 'data' not in st.session_state: st.session_state.data = charger_donnees()

Construire la liste d'élèves

eleves = sorted({d['Eleve'] for d in st.session_state.data if d.get('Eleve')}) eleves_with_option = ["-- Nouvel élève --"] + eleves

Sidebar: contrôles globaux

st.sidebar.title("Contrôles") selected = st.sidebar.selectbox("🎓 Choisir un élève", options=eleves_with_option)

Création d'un nouvel élève

new_name = "" if selected == "-- Nouvel élève --": new_name = st.sidebar.text_input("Nom du nouvel élève") if st.sidebar.button("➕ Créer l'élève"): if not new_name or new_name.strip() == "": st.sidebar.warning("Entrez un nom valide.") elif new_name.strip() in eleves: st.sidebar.warning("Cet élève existe déjà.") else: eleves.append(new_name.strip()) st.session_state.data.append({ "id": str(uuid.uuid4()), "Eleve": new_name.strip(), "Matiere": "", "Note": 0.0, "Coefficient": 0.0, "Trimestre": "1", }) sauvegarder_donnees() st.sidebar.success(f"Élève '{new_name.strip()}' créé.") st.experimental_rerun()

Réinitialiser

if st.sidebar.button("🔁 Réinitialiser toutes les données"): if st.sidebar.checkbox("Confirmer la suppression de toutes les données"): st.session_state.data = [] sauvegarder_donnees() st.sidebar.success("Toutes les données ont été supprimées.") st.experimental_rerun()

En-tête principal

st.markdown(f"<div class='app-header'>📊 GradeTrack — Suivi des notes</div>", unsafe_allow_html=True) st.markdown("<div class='small-muted'>Interface améliorée · édition en ligne · export CSV</div>", unsafe_allow_html=True)

Tabs réorganisés

tab_ajout, tab_tableau, tab_stats, tab_graph = st.tabs(["➕ Ajouter", "🧾 Tableau (édition)", "📚 Statistiques", "📊 Graphiques"])

--- Onglet Ajouter ---

with tab_ajout: st.subheader("Ajouter une note") if selected == "-- Nouvel élève --" and not (new_name and new_name.strip()): st.info("Créez un nouvel élève depuis la barre latérale avant d'ajouter une note.") else: eleve_input = selected if selected == "-- Nouvel élève --" and new_name and new_name.strip(): eleve_input = new_name.strip()

with st.form("form_ajout_note", clear_on_submit=True):
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

--- Onglet Tableau (édition) ---

with tab_tableau: st.subheader("Tableau complet — édition en ligne") if not st.session_state.data: st.info("Aucune donnée. Ajoutez des notes depuis l'onglet Ajouter.") else: df_all = pd.DataFrame(st.session_state.data) # Afficher le tableau éditable (conserver les ids) edited = st.data_editor(df_all, num_rows="dynamic", use_container_width=True)

col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Enregistrer modifications"):
            # Nettoyage minimal et sauvegarde
            for col in EXPECTED_COLS:
                if col not in edited.columns:
                    edited[col] = None
            # Normaliser types
            edited['Note'] = pd.to_numeric(edited['Note'], errors='coerce')
            edited['Coefficient'] = pd.to_numeric(edited['Coefficient'], errors='coerce')
            st.session_state.data = edited.to_dict(orient='records')
            sauvegarder_donnees()
            st.success("Modifications enregistrées.")
            st.experimental_rerun()
    with col2:
        st.markdown("**Actions rapides :**")
        if st.button("Ajouter une ligne vide"):
            st.session_state.data.append({"id": str(uuid.uuid4()), "Eleve": "", "Matiere": "", "Note": 0.0, "Coefficient": 1.0, "Trimestre": "1"})
            sauvegarder_donnees()
            st.experimental_rerun()

--- Onglet Statistiques ---

with tab_stats: st.subheader("Statistiques par élève / matière") try: df = pd.DataFrame(st.session_state.data) except Exception: df = pd.DataFrame(columns=EXPECTED_COLS)

if df.empty:
    st.info("Pas encore de notes pour calculer des statistiques.")
else:
    # Moyennes globales par élève
    eleve_list = sorted(df['Eleve'].dropna().unique())
    sel_eleve = st.selectbox("Choisir un élève pour détails", options=["Tous"] + eleve_list)
    if sel_eleve == "Tous":
        st.dataframe(df.groupby('Eleve').apply(lambda g: pd.Series({'Moyenne': calcul_moyenne(g), 'Nb Notes': len(g)})).reset_index())
    else:
        df_e = df[df['Eleve'] == sel_eleve]
        if df_e.empty:
            st.info("Pas de notes pour cet élève.")
        else:
            stats = df_e.groupby('Matiere').apply(lambda g: pd.Series({'Moyenne': calcul_moyenne(g), 'Nb Notes': len(g), 'Total Coef': g['Coefficient'].sum()})).reset_index()
            st.dataframe(stats)

--- Onglet Graphiques ---

with tab_graph: st.subheader("Graphiques") try: df = pd.DataFrame(st.session_state.data) except Exception: df = pd.DataFrame(columns=EXPECTED_COLS)

if df.empty:
    st.info("Pas encore de notes pour afficher des graphiques.")
else:
    eleve_list = sorted(df['Eleve'].dropna().unique())
    eleve_choice = st.selectbox("Choisir un élève", options=eleve_list)
    df_e = df[df['Eleve'] == eleve_choice]
    if df_e.empty:
        st.info("Pas de notes pour l'élève choisi.")
    else:
        # Évolution
        moy_trimestres = [calcul_moyenne(df_e[df_e['Trimestre'] == t]) or 0 for t in ['1', '2', '3']]
        fig1, ax1 = plt.subplots()
        ax1.plot(['1', '2', '3'], moy_trimestres, marker='o')
        ax1.set_ylim(0, 20)
        ax1.set_title("Évolution des moyennes trimestrielles")
        st.pyplot(fig1)

        # Moyenne par matière
        moy_matiere = df_e.groupby('Matiere').apply(calcul_moyenne)
        fig2, ax2 = plt.subplots()
        moy_matiere.plot(kind='bar', ax=ax2)
        ax2.set_ylim(0, 20)
        ax2.set_title("Moyenne par matière")
        st.pyplot(fig2)

--- Export CSV pour l'élève ou global ---

st.sidebar.markdown("---") st.sidebar.subheader("Export / Utilitaires") if st.sidebar.button("⬇️ Exporter tout (CSV)"): df_all = pd.DataFrame(st.session_state.data) buf = io.StringIO() df_all.to_csv(buf, index=False) st.sidebar.download_button("Télécharger le CSV complet", buf.getvalue(), file_name="notes_all.csv", mime="text/csv")

st.sidebar.markdown("---") st.sidebar.markdown("Tips: Utilisez l'onglet 'Tableau' pour modifier en masse, puis 'Enregistrer modifications'.")

