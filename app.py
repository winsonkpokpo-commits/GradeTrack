# app.py
# Application Streamlit pour le suivi des notes et moyennes des élèves ("GradeTrack")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import uuid

st.set_page_config(page_title="GradeTrack", layout="wide")

CSV_PATH = "notes.csv"

def charger_donnees():
    if os.path.exists(CSV_PATH):
        try:
            return pd.read_csv(CSV_PATH).to_dict(orient="records")
        except Exception:
            st.warning("Erreur lors du chargement des données. Le fichier CSV est peut-être corrompu.")
    return []

def sauvegarder_donnees():
    pd.DataFrame(st.session_state.data).to_csv(CSV_PATH, index=False)

if 'data' not in st.session_state:
    st.session_state.data = charger_donnees()

def ajouter_note(eleve, matiere, note, coef, trimestre):
    st.session_state.data.append({
        'id': str(uuid.uuid4()),
        'Eleve': eleve,
        'Matiere': matiere,
        'Note': note,
        'Coefficient': coef,
        'Trimestre': trimestre
    })
    sauvegarder_donnees()

def supprimer_note(note_id):
    st.session_state.data = [n for n in st.session_state.data if n.get('id') != note_id]
    sauvegarder_donnees()
    st.toast("Note supprimée avec succès", icon="🗑️")
    st.experimental_rerun()

def calcul_moyenne(df):
    if df.empty:
        return None
    weighted_sum = (df['Note'] * df['Coefficient']).sum()
    total_coef = df['Coefficient'].sum()
    return weighted_sum / total_coef if total_coef != 0 else None

def couleur_moyenne(moy):
    if moy is None:
        return "gray"
    return "green" if moy >= 16 else "orange" if moy >= 12 else "red"

st.title("📊 GradeTrack - Suivi des notes et moyennes")

# Sidebar : choix élève
eleves = sorted(set(d['Eleve'] for d in st.session_state.data))
eleve_choisi = st.sidebar.selectbox("🎓 Choisir un élève", options=eleves + ["-- Nouvel élève --"])

if eleve_choisi == "-- Nouvel élève --":
    nouveau_eleve = st.sidebar.text_input("Nom du nouvel élève")
    if nouveau_eleve:
        if nouveau_eleve not in eleves:
            eleves.append(nouveau_eleve)
            eleves.sort()
            eleve_choisi = nouveau_eleve
            st.experimental_rerun()
        else:
            st.sidebar.warning("Cet élève existe déjà.")

# Réinitialisation (admin)
if st.sidebar.button("🔁 Réinitialiser toutes les données"):
    st.session_state.data = []
    sauvegarder_donnees()
    st.sidebar.success("Toutes les données ont été supprimées.")
    st.experimental_rerun()

# Formulaire ajout de note
with st.form(f"form_{eleve_choisi}"):
    st.markdown(f"### Ajouter une note pour {eleve_choisi}")
    matiere = st.text_input("Matière")
    note = st.number_input("Note (0-20)", 0.0, 20.0, step=0.1)
    coef = st.number_input("Coefficient", 0.1, 10.0, step=0.1)
    trimestre = st.selectbox("Trimestre", ["1", "2", "3"])
    submit = st.form_submit_button("➕ Ajouter la note")

    if submit:
        if eleve_choisi in [None, "", "-- Nouvel élève --"]:
)
if not df.empty:
    df['Note'] = pd.to_numeric(df['Note'], errors='coerce')
    df['Coefficient'] = pd.to_numeric(df['Coefficient'], errors='coerce')
df_eleve = df[df['Eleve'] == eleve_choisi] if eleve_choisi in df['Eleve'].values else pd.DataFrame()

# Filtres
if not df_eleve.empty:
    matieres = sorted(df_eleve['Matiere'].unique())
    filtre_matiere = st.sidebar.selectbox("Filtrer par matière", ["Toutes"] + matieres)
    if filtre_matiere != "Toutes":
        df_eleve = df_eleve[df_eleve['Matiere'] == filtre_matiere]

    filtre_trimestre = st.sidebar.selectbox("Filtrer par trimestre", ["Tous", "1", "2", "3"])
    if filtre_trimestre != "Tous":
        df_eleve = df_eleve[df_eleve['Trimestre'] == filtre_trimestre]

# Onglets
tab1, tab2, tab3 = st.tabs(["📄 Notes & Moyennes", "📚 Statistiques", "📊 Graphiques"])

with tab1:
    st.subheader(f"Notes enregistrées - {eleve_choisi}")
    if not df_eleve.empty:
        for idx, row in df_eleve.reset_index(drop=True).iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            c1.write(row['Matiere'])
            c2.write(row['Note'])
            c3.write(row['Coefficient'])
            c4.write(f"T{row['Trimestre']}")
            if c5.button("🗑️", key=f"del_{row['id']}"):
                supprimer_note(row['id'])

        moyennes = {t: calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) for t in ['1', '2', '3']}
        moy_globale = calcul_moyenne(df_eleve)

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"**T1 :** <span style='color:{couleur_moyenne(moyennes['1'])}'>{(moyennes['1'] or 0):.2f}</span>", unsafe_allow_html=True)
        col2.markdown(f"**T2 :** <span style='color:{couleur_moyenne(moyennes['2'])}'>{(moyennes['2'] or 0):.2f}</span>", unsafe_allow_html=True)
        col3.markdown(f"**T3 :** <span style='color:{couleur_moyenne(moyennes['3'])}'>{(moyennes['3'] or 0):.2f}</span>", unsafe_allow_html=True)
        col4.markdown(f"**Générale :** <span style='color:{couleur_moyenne(moy_globale)}'>{(moy_globale or 0):.2f}</span>", unsafe_allow_html=True)
    else:
        st.info("Aucune note trouvée pour cet élève.")

with tab2:
    st.subheader(f"Statistiques par matière - {eleve_choisi}")
    if not df_eleve.empty:
        stats = df_eleve.groupby('Matiere').apply(
            lambda g: pd.Series({
                'Moyenne': calcul_moyenne(g),
                'Nb Notes': len(g),
                'Total Coef': g['Coefficient'].sum()
            })
        ).reset_index()
        st.dataframe(stats)
    else:
        st.info("Pas encore de notes pour cet élève.")

with tab3:
    st.subheader(f"Graphiques - {eleve_choisi}")
    if not df_eleve.empty:
        # Évolution trimestrielle
        moy_trimestres = [calcul_moyenne(df_eleve[df_eleve['Trimestre'] == t]) or 0 for t in ['1', '2', '3']]
        fig1, ax1 = plt.subplots()
        ax1.plot(['1', '2', '3'], moy_trimestres, marker='o', color='blue')
        ax1.set_ylim(0, 20)
        ax1.set_title("Évolution des moyennes trimestrielles")
        ax1.set_xlabel("Trimestre")
        ax1.set_ylabel("Moyenne")
        ax1.grid(True)
        st.pyplot(fig1)

        # Moyenne par matière
        moy_matiere = df_eleve.groupby('Matiere').apply(calcul_moyenne)
        fig2, ax2 = plt.subplots()
        moy_matiere.plot(kind='bar', ax=ax2, color='skyblue')
        counts = df_eleve['Matiere'].value_counts()
        for i, (label, val) in enumerate(moy_matiere.items()):
            ax2.text(i, val + 0.3, f"{counts[label]} note(s)", ha='center', fontsize=8)
        ax2.set_ylim(0, 20)
        ax2.set_title("Moyenne par matière")
        ax2.set_ylabel("Moyenne")
        st.pyplot(fig2)

        # Camembert
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

# Export CSV
if not df_eleve.empty:
    export_df = df_eleve.drop(columns=['id']) if 'id' in df_eleve else df_eleve
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    st.download_button("⬇️ Exporter les notes CSV", csv_buffer.getvalue(), file_name=f"notes_{eleve_choisi}.csv", mime="text/csv")