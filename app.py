"""
GradeTrack - Application Streamlit pour le suivi des notes et moyennes
Version sans matplotlib, avec Altair pour les graphiques.
"""

import streamlit as st
import pandas as pd
import altair as alt
import io
import os
import uuid
from typing import List, Dict, Any, Optional

# --- Configuration ---
st.set_page_config(page_title="GradeTrack", layout="wide")
CSV_PATH = "notes.csv"
EXPECTED_COLS = ["id", "Eleve", "Matiere", "Note", "Coefficient", "Trimestre"]

# --- Fonctions utilitaires ---
def charger_donnees() -> List[Dict[str, Any]]:
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            for col in EXPECTED_COLS:
                if col not in df.columns:
                    df[col] = None
            df = df.reindex(columns=EXPECTED_COLS)
            # s'assurer que chaque ligne a un id
            df['id'] = df['id'].fillna('').astype(str)
            df.loc[df['id'] == '', 'id'] = [str(uuid.uuid4()) for _ in range((df['id'] == '').sum())]
            return df.to_dict(orient="records")
        except Exception as e:
            st.warning(f"Erreur lors du chargement des données : {e}")
            return []
    return []

def sauvegarder_donnees() -> None:
    try:
        df = pd.DataFrame(st.session_state.data)
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = None
        df = df.reindex(columns=EXPECTED_COLS)
        tmp_path = CSV_PATH + ".tmp"
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, CSV_PATH)
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

def ajouter_note(eleve: str, matiere: str, note: float, coef: float, trimestre: str) -> None:
    if not eleve or eleve.strip() == "":
        st.error("Nom d'élève invalide")
        return
    if not matiere or matiere.strip() == "":
        st.error("Matière invalide")
        return
    try:
        note_val = float(note)
        coef_val = float(coef)
    except Exception:
        st.error("Note ou coefficient invalide")
        return
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

def supprimer_note(note_id: str) -> None:
    original_len = len(st.session_state.data)
    st.session_state.data = [n for n in st.session_state.data if n.get("id") != note_id]
    if len(st.session_state.data) < original_len:
        sauvegarder_donnees()
        st.success("Note supprimée avec succès")
        st.experimental_rerun()
    else:
        st.warning("ID non trouvé : impossible de supprimer la note")

def calcul_moyenne(df: pd.DataFrame) -> Optional[float]:
    if df is None or df.empty:
        return None
    df = df.copy()
    df['Note'] = pd.to_numeric(df['Note'], errors='coerce')
    df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce')
    df = df.dropna(subset=['Note', 'Coefficient'])
    total_coef = df['Coefficient'].sum()
    if total_coef == 0:
        return None
    weighted_sum = (df['Note'] * df['Coefficient']).sum()
    return float(weighted_sum / total_coef)

def couleur_moyenne(moy: Optional[float]) -> str:
    if moy is None:
        return "gray"
    if moy >= 16:
        return "green"
    if moy >= 12:
        return "orange"
    return "red"

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')

# --- Initialisation de l'état ---
if 'data' not in st.session_state:
    st.session_state.data = charger_donnees()

# --- Sidebar ---
st.sidebar.title("Contrôles")

# Importer CSV (ajouter ou remplacer)
uploaded = st.sidebar.file_uploader("Importer un CSV (colonnes attendues: Eleve,Matiere,Note,Coefficient,Trimestre)", type=['csv'])
if uploaded is not None:
    try:
        df_up = pd.read_csv(uploaded)
        # normaliser colonnes
        for col in EXPECTED_COLS:
            if col not in df_up.columns:
                df_up[col] = None
        df_up = df_up.reindex(columns=EXPECTED_COLS)
        # créer id si manquant
        df_up['id'] = df_up['id'].fillna('')
        missing_ids = (df_up['id'] == '')
        df_up.loc[missing_ids, 'id'] = [str(uuid.uuid4()) for _ in range(missing_ids.sum())]
        # option: ajouter ou remplacer
        mode = st.sidebar.radio("Mode d'import", options=["Ajouter aux données", "Remplacer toutes les données"])
        if st.sidebar.button("📥 Valider l'import"):
            if mode == "Remplacer toutes les données":
                st.session_state.data = df_up.to_dict(orient="records")
            else:
                # concat en évitant les duplications d'id
                existing_ids = {d['id'] for d in st.session_state.data}
                new_records = [r for r in df_up.to_dict(orient="records") if r['id'] not in existing_ids]
                st.session_state.data.extend(new_records)
            sauvegarder_donnees()
            st.sidebar.success("Import effectué.")
            st.experimental_rerun()
    except Exception as e:
        st.sidebar.error(f"Erreur à l'import : {e}")

eleves = sorted({(d.get('Eleve') or '').strip() for d in st.session_state.data if (d.get('Eleve') or '').strip()})
eleves_with_option = ["-- Nouvel élève --"] + eleves

selected = st.sidebar.selectbox("🎓 Choisir un élève", options=eleves_with_option)
new_name = ""
if selected == "-- Nouvel élève --":
    new_name = st.sidebar.text_input("Nom du nouvel élève")
    if st.sidebar.button("➕ Créer l'élève"):
        if not new_name or new_name.strip() == "":
            st.sidebar.warning("Entrez un nom valide.")
        elif new_name.strip() in eleves:
            st.sidebar.warning("Cet élève existe déjà.")
        else:
            eleves.append(new_name.strip())
            st.session_state.data.append({
                "id": str(uuid.uuid4()),
                "Eleve": new_name.strip(),
                "Matiere": "",
                "Note": 0.0,
                "Coefficient": 0.0,
                "Trimestre": "1",
            })
            sauvegarder_donnees()
            st.sidebar.success(f"Élève '{new_name.strip()}' créé.")
            st.experimental_rerun()

if st.sidebar.button("🔁 Réinitialiser toutes les données"):
    if st.sidebar.checkbox("Confirmer la suppression de toutes les données"):
        st.session_state.data = []
        sauvegarder_donnees()
        st.sidebar.success("Toutes les données ont été supprimées.")
        st.experimental_rerun()

# bouton de téléchargement (export)
try:
    df_full = pd.DataFrame(st.session_state.data)
    if not df_full.empty:
        csv_bytes = dataframe_to_csv_bytes(df_full)
        st.sidebar.download_button("📤 Exporter toutes les données (CSV)", data=csv_bytes, file_name="notes_export.csv", mime="text/csv")
except Exception:
    pass

st.title("📊 GradeTrack - Suivi des notes et moyennes")
if selected == "-- Nouvel élève --" and not (new_name and new_name.strip()):
    st.info("Créez un nouvel élève depuis la barre latérale puis revenez ici pour ajouter des notes.")

# --- Formulaire ---
with st.form("form_ajout_note", clear_on_submit=True):
    st.subheader("Ajouter une note")
    eleve_input = selected
    if selected == "-- Nouvel élève --" and new_name and new_name.strip():
        eleve_input = new_name.strip()
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

# --- DataFrame ---
try:
    df = pd.DataFrame(st.session_state.data)
except Exception:
    df = pd.DataFrame(columns=EXPECTED_COLS)

for col in EXPECTED_COLS:
    if col not in df.columns:
        df[col] = None

if not df.empty:
    df['Note'] = pd.to_numeric(df['Note'], errors='coerce')
    df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce')

eleve_choisi: Optional[str] = None
if selected == "-- Nouvel élève --":
    if new_name and new_name.strip():
        eleve_choisi = new_name.strip()
else:
    eleve_choisi = selected

if (not eleve_choisi or eleve_choisi == "-- Nouvel élève --") and eleves:
    eleve_choisi = eleves[0]

if eleve_choisi and eleve_choisi in df['Eleve'].values:
    df_eleve = df[df['Eleve'] == eleve_choisi].copy()
else:
    df_eleve = pd.DataFrame(columns=df.columns)

if not df_eleve.empty:
    matieres = sorted(df_eleve['Matiere'].dropna().unique())
    filtre_matiere = st.sidebar.selectbox("Filtrer par matière", options=["Toutes"] + matieres)
    if filtre_matiere != "Toutes":
        df_eleve = df_eleve[df_eleve['Matiere'] == filtre_matiere]
    filtre_trimestre = st.sidebar.selectbox("Filtrer par trimestre", options=["Tous", "1", "2", "3"])
    if filtre_trimestre != "Tous":
        df_eleve = df_eleve[df_eleve['Trimestre'] == filtre_trimestre]

# --- Onglets ---
tab1, tab2, tab3 = st.tabs(["📄 Notes & Moyennes", "📚 Statistiques", "📊 Graphiques"])

with tab1:
    st.subheader(f"Notes enregistrées — {eleve_choisi if eleve_choisi else '—'}")
    if not df_eleve.empty:
        for idx, row in df_eleve.reset_index(drop=True).iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            c1.write(row.get('Matiere', ''))
            c2.write(row.get('Note', ''))
            c3.write(row.get('Coefficient', ''))
            c4.write(f"T{row.get('Trimestre', '')}")
            key_del = f"del_{row.get('id')}_{idx}"
            if c5.button("🗑️", key=key_del):
                supprimer_note(row.get('id'))
        moyennes = {t: calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) for t in ['1', '2', '3']}
        moy_globale = calcul_moyenne(df_eleve)
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"**T1 :** <span style='color:{couleur_moyenne(moyennes['1'])}'>{(moyennes['1'] or 0):.2f}</span>", unsafe_allow_html=True)
        col2.markdown(f"**T2 :** <span style='color:{couleur_moyenne(moyennes['2'])}'>{(moyennes['2'] or 0):.2f}</span>", unsafe_allow_html=True)
        col3.markdown(f"**T3 :** <span style='color:{couleur_moyenne(moyennes['3'])}'>{(moyennes['3'] or 0):.2f}</span>", unsafe_allow_html=True)
        col4.markdown(f"**Générale :** <span style='color:{couleur_moyenne(moy_globale)}'>{(moy_globale or 0):.2f}</span>", unsafe_allow_html=True)
        # Bouton export spécifique à l'élève affiché
        try:
            csv_eleve = dataframe_to_csv_bytes(df_eleve)
            st.download_button(f"📤 Exporter les notes de {eleve_choisi} (CSV)", data=csv_eleve, file_name=f"notes_{eleve_choisi}.csv", mime="text/csv")
        except Exception:
            pass
    else:
        st.info("Aucune note trouvée pour cet élève.")

with tab2:
    st.subheader(f"Statistiques par matière — {eleve_choisi if eleve_choisi else '—'}")
    if not df_eleve.empty:
        stats = df_eleve.groupby('Matiere').apply(
            lambda g: pd.Series({
                'Moyenne': calcul_moyenne(g),
                'Nb Notes': len(g),
                'Total Coef': g['Coefficient'].sum()
            })
        ).reset_index()
        # Formater moyennes (2 décimales) et afficher
        stats['Moyenne'] = stats['Moyenne'].apply(lambda x: float(f"{(x or 0):.2f}") if pd.notna(x) else None)
        st.dataframe(stats)
    else:
        st.info("Pas encore de notes pour cet élève.")

with tab3:
    st.subheader(f"Graphiques — {eleve_choisi if eleve_choisi else '—'}")
    if not df_eleve.empty:
        # Graphique ligne (moyenne par trimestre)
        moy_trimestres_df = pd.DataFrame({
            "Trimestre": ['1', '2', '3'],
            "Moyenne": [calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) or 0 for t in ['1', '2', '3']]
        })
        line_chart = alt.Chart(moy_trimestres_df).mark_line(point=True).encode(
            x=alt.X("Trimestre:N", title="Trimestre"),
            y=alt.Y("Moyenne:Q", scale=alt.Scale(domain=[0, 20]), title="Moyenne")
        ).properties(title="Évolution des moyennes trimestrielles")
        st.altair_chart(line_chart, use_container_width=True)

        # Moyenne par matière (bar chart)
        # calculer moyennes par matière en utilisant la fonction existante
        moys = []
        for m in df_eleve['Matiere'].dropna().unique():
            m_df = df_eleve[df_eleve['Matiere'] == m]
            moys.append({"Matiere": m, "Moyenne": calcul_moyenne(m_df) or 0})
        moy_matiere = pd.DataFrame(moys)
        if not moy_matiere.empty:
            bar_chart = alt.Chart(moy_matiere).mark_bar().encode(
                x=alt.X("Matiere:N", sort=None, title="Matière"),
                y=alt.Y("Moyenne:Q", scale=alt.Scale(domain=[0, 20]), title="Moyenne"),
                tooltip=["Matiere", alt.Tooltip("Moyenne", format=".2f")]
            ).properties(title="Moyenne par matière")
            st.altair_chart(bar_chart, use_container_width=True)

        # Répartition des coefficients par matière (pie chart)
        coef_matiere = df_eleve.groupby('Matiere')['Coefficient'].sum().reset_index()
        coef_matiere = coef_matiere[coef_matiere['Coefficient'] > 0]  # ignorer coef nuls ou négatifs s'il y en a
        if len(coef_matiere) > 0:
            pie = alt.Chart(coef_matiere).mark_arc().encode(
                theta=alt.Theta(field="Coefficient", type="quantitative"),
                color=alt.Color("Matiere:N", legend=alt.Legend(title="Matière")),
                tooltip=[alt.Tooltip("Matiere:N"), alt.Tooltip("Coefficient:Q", format=".2f")]
            ).properties(title="Répartition des coefficients par matière")
            st.altair_chart(pie, use_container_width=True)
        else:
            st.info("Pas de coefficients valides pour construire un camembert.")
    else:
        st.info("Pas encore de notes pour cet élève.")