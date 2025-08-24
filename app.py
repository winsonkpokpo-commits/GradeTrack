# Grade_track_V6_with_html.py
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import uuid
import time
import io
import numpy as np

# --- Configuration / constantes ---
CSV_PATH = "gradetrack_data.csv"
EXPECTED_COLS = ['id','Eleve','Classe','Matiere','Note','Coefficient','Trimestre','Date','Commentaire']

st.set_page_config(
    page_title="GradeTrack Modern",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DataManager ----------------
class DataManager:
    """Gestionnaire de données avec cache Streamlit"""
    @staticmethod
    @st.cache_data(ttl=60)
    def load_data():
        if os.path.exists(CSV_PATH):
            try:
                df = pd.read_csv(CSV_PATH)
                # ajouter colonnes manquantes
                for col in EXPECTED_COLS:
                    if col not in df.columns:
                        if col == "Date":
                            df[col] = datetime.now().strftime("%Y-%m-%d")
                        elif col == "Classe":
                            df[col] = "Non assignée"
                        else:
                            df[col] = "" if col == "Commentaire" else None
                # réordonner
                df = df.reindex(columns=EXPECTED_COLS)
                # ids
                if 'id' in df.columns:
                    df['id'] = df['id'].fillna('').astype(str)
                    missing = (df['id'] == '') | df['id'].isna()
                    if missing.any():
                        df.loc[missing, 'id'] = [str(uuid.uuid4()) for _ in range(missing.sum())]
                else:
                    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                return df
            except Exception as e:
                st.error(f"Erreur lors du chargement: {e}")
                return pd.DataFrame(columns=EXPECTED_COLS)
        # fichier absent -> vide
        return pd.DataFrame(columns=EXPECTED_COLS)

    @staticmethod
    def save_data(df):
        try:
            df.to_csv(CSV_PATH, index=False)
            # vider le cache
            try:
                st.cache_data.clear()
            except Exception:
                pass
            return True
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde: {e}")
            return False

    @staticmethod
    def calculate_statistics(df):
        if df is None or df.empty:
            return {}
        df_clean = df.copy()
        df_clean['Note'] = pd.to_numeric(df_clean['Note'], errors='coerce')
        df_clean = df_clean.dropna(subset=['Note'])
        if df_clean.empty:
            return {}
        notes = df_clean['Note']
        moy_par_matiere = df_clean.groupby('Matiere')['Note'].mean().round(2).to_dict()
        return {
            'nb_eleves': int(df['Eleve'].nunique()) if 'Eleve' in df else 0,
            'nb_notes': int(len(df_clean)),
            'moyenne_generale': float(notes.mean()),
            'mediane': float(notes.median()),
            'note_min': float(notes.min()),
            'note_max': float(notes.max()),
            'ecart_type': float(notes.std()),
            'taux_reussite': float((notes >= 10).mean() * 100),
            'taux_excellence': float((notes >= 16).mean() * 100),
            'notes_par_trimestre': df_clean.groupby('Trimestre')['Note'].count().to_dict(),
            'moyenne_par_classe': df_clean.groupby('Classe')['Note'].mean().round(2).to_dict(),
            'moyenne_par_matiere': moy_par_matiere
        }

# ---------------- ChartGenerator ----------------
class ChartGenerator:
    @staticmethod
    def create_overview_metrics(stats):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Élèves", value=stats.get('nb_eleves', 0))
        with col2:
            st.metric("📝 Notes", value=stats.get('nb_notes', 0))
        with col3:
            moyenne = stats.get('moyenne_generale', 0) or 0
            st.metric("📊 Moyenne", value=f"{moyenne:.2f}/20")
        with col4:
            taux = stats.get('taux_reussite', 0) or 0
            st.metric("✅ Réussite", value=f"{taux:.1f}%")

    @staticmethod
    def create_evolution_chart(df):
        if df.empty:
            return None
        df_copy = df.copy()
        df_copy['Note'] = pd.to_numeric(df_copy['Note'], errors='coerce')
        df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
        df_copy = df_copy.dropna(subset=['Note','Date'])
        if df_copy.empty:
            return None
        df_copy['Mois'] = df_copy['Date'].dt.to_period('M')
        monthly_avg = df_copy.groupby('Mois')['Note'].mean().reset_index()
        monthly_avg['Mois'] = monthly_avg['Mois'].astype(str)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_avg['Mois'], y=monthly_avg['Note'],
                                 mode='lines+markers', name='Moyenne mensuelle'))
        fig.update_layout(title='📈 Évolution des Moyennes Mensuelles', xaxis_title='Mois', yaxis=dict(range=[0,20]))
        return fig

    @staticmethod
    def create_grade_distribution(df):
        if df.empty:
            return None
        df_copy = df.copy()
        df_copy['Note'] = pd.to_numeric(df_copy['Note'], errors='coerce').dropna()
        if df_copy.empty:
            return None
        fig = px.histogram(df_copy, x='Note', nbins=20, title='📊 Distribution des Notes')
        fig.update_layout(yaxis_title='Nombre')
        return fig

# ---------------- Helpers ----------------
def apply_filters(df, selected_class, selected_trimestre):
    df_filtered = df.copy()
    if selected_class and selected_class != "Toutes":
        df_filtered = df_filtered[df_filtered['Classe'] == selected_class]
    if selected_trimestre and selected_trimestre != "Tous":
        df_filtered = df_filtered[df_filtered['Trimestre'] == selected_trimestre]
    return df_filtered

def create_sample_data():
    sample_data = []
    students = ["Alice Martin", "Bob Dupont", "Claire Bernard", "David Moreau", "Emma Leroy"]
    subjects = ["Mathématiques", "Français", "Histoire", "Sciences", "Anglais"]
    classes = ["6A", "6B", "5A"]
    for student in students:
        classe = np.random.choice(classes)
        for subject in subjects:
            for trimestre in ["1","2","3"]:
                for _ in range(np.random.randint(2,5)):
                    note = np.random.normal(12, 3)
                    note = max(0, min(20, note))
                    sample_data.append({
                        "id": str(uuid.uuid4()),
                        "Eleve": student,
                        "Classe": classe,
                        "Matiere": subject,
                        "Note": round(note,2),
                        "Coefficient": int(np.random.choice([1,1,1,2,2,3])),
                        "Trimestre": trimestre,
                        "Date": (datetime.now() - timedelta(days=np.random.randint(0,365))).strftime("%Y-%m-%d"),
                        "Commentaire": ""
                    })
    return pd.DataFrame(sample_data)

# ---------------- Vues principales ----------------
def show_dashboard(df):
    st.markdown("### 📊 Vue d'Ensemble")
    stats = DataManager.calculate_statistics(df)
    ChartGenerator.create_overview_metrics(stats)

    # --- Cards HTML (meilleure / plus faible matière) ---
    best = "—"
    worst = "—"
    if stats.get('moyenne_par_matiere'):
        mpm = stats['moyenne_par_matiere']
        if len(mpm) > 0:
            sorted_items = sorted(mpm.items(), key=lambda x: x[1], reverse=True)
            best = f"{sorted_items[0][0]} ({sorted_items[0][1]:.2f})"
            worst = f"{sorted_items[-1][0]} ({sorted_items[-1][1]:.2f})"
    extra_html = f"""
    <div style="display:flex; gap:16px; margin-top:20px;">
      <div style="flex:1; background:white; padding:16px; border-radius:8px; 
                  box-shadow:0 2px 6px rgba(0,0,0,0.06);">
        <h3 style="margin:0;">🔥 Meilleure matière</h3>
        <p style="font-size:18px; color:#16a34a; margin-top:8px;">{best}</p>
      </div>
      <div style="flex:1; background:white; padding:16px; border-radius:8px; 
                  box-shadow:0 2px 6px rgba(0,0,0,0.06);">
        <h3 style="margin:0;">⚠️ Matière la plus faible</h3>
        <p style="font-size:18px; color:#dc2626; margin-top:8px;">{worst}</p>
      </div>
    </div>
    """
    st.markdown(extra_html, unsafe_allow_html=True)

    # --- Graphiques ---
    col1, col2 = st.columns(2)
    with col1:
        fig_evol = ChartGenerator.create_evolution_chart(df)
        if fig_evol:
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Données insuffisantes pour l'évolution")
    with col2:
        fig_dist = ChartGenerator.create_grade_distribution(df)
        if fig_dist:
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("Aucune distribution disponible")

    st.markdown("### 📝 Dernières Notes")
    if not df.empty:
        df_recent = df.copy()
        df_recent['Date'] = pd.to_datetime(df_recent['Date'], errors='coerce')
        df_recent = df_recent.dropna(subset=['Date']).sort_values('Date', ascending=False).head(10)
        df_display = df_recent[['Eleve','Matiere','Note','Coefficient','Trimestre','Classe','Date']].copy()
        df_display['Date'] = df_display['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune note enregistrée")

# ---------------- Admin view ----------------
def show_admin(df):
    admin_html = """
    <div style="background:#f1f5f9; padding:16px; border-radius:8px; margin-bottom:16px;">
      <h2 style="margin:0; color:#0f172a;">⚙️ Administration</h2>
      <p style="margin:0; font-size:14px; opacity:0.8;">Exporter, importer ou réinitialiser les données</p>
    </div>
    """
    st.markdown(admin_html, unsafe_allow_html=True)

    export_format = st.selectbox("Format d'export", ["CSV","Excel","JSON"])
    if st.button("📤 Exporter"):
        export_data(df, export_format)
    st.markdown("---")
    st.markdown("### Import / Test")
    uploaded = st.file_uploader("Charger un CSV (colonnes attendues : Eleve,Classe,Matiere,Note,Coefficient,Trimestre,Date,Commentaire)", type=["csv"])
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            # essayer d'ajouter IDs et colonnes manquantes
            for col in EXPECTED_COLS:
                if col not in new_df.columns:
                    new_df[col] = "" if col == "Commentaire" else None
            new_df = new_df.reindex(columns=EXPECTED_COLS)
            if DataManager.save_data(new_df):
                st.success("Nouveau dataset sauvegardé")
                time.sleep(1)
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Erreur import : {e}")

    if st.button("Charger des données d'exemple"):
        sample_df = create_sample_data()
        if DataManager.save_data(sample_df):
            st.success("Données d'exemple ajoutées")
            time.sleep(1)
            st.experimental_rerun()

# ---------------- Administration export simple ----------------
def export_data(df, format_type="CSV"):
    if df.empty:
        st.warning("Aucune donnée à exporter")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        if format_type == "CSV":
            csv_data = df.to_csv(index=False)
            st.download_button("💾 Télécharger CSV", csv_data, file_name=f"gradetrack_export_{timestamp}.csv", mime="text/csv")
        elif format_type == "Excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Notes')
            st.download_button("💾 Télécharger Excel", buffer.getvalue(), file_name=f"gradetrack_export_{timestamp}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        elif format_type == "JSON":
            json_data = df.to_json(orient='records', indent=2)
            st.download_button("💾 Télécharger JSON", json_data, file_name=f"gradetrack_export_{timestamp}.json", mime="application/json")
        st.success(f"✅ Export {format_type} prêt")
    except Exception as e:
        st.error(f"Erreur export: {e}")

# ---------------- Main ----------------
def main():
    df = DataManager.load_data()
    with st.sidebar:
        st.markdown("## 🎮 Panneau de Contrôle")
        view_mode = st.selectbox("Mode d'affichage", ["📊 Dashboard", "⚙️ Administration"], index=0)
        st.markdown("---")
        classes = ["Toutes"] + sorted([c for c in df['Classe'].unique() if pd.notna(c) and c != ""]) if not df.empty else ["Toutes"]
        selected_class = st.selectbox("Classe", classes)
        selected_trimestre = st.selectbox("Trimestre", ["Tous","1","2","3"])
        if st.button("🔄 Actualiser"):
            try:
                st.cache_data.clear()
            except Exception:
                pass
            st.experimental_rerun()

    # >>> HEADER HTML <<<
    header_html = """
    <div style="background: linear-gradient(90deg,#0f172a,#2563eb); 
                padding:24px; border-radius:12px; color:white; margin-bottom:20px;">
      <h1 style="margin:0; font-family: 'Segoe UI', Tahoma, sans-serif;">📊 GradeTrack</h1>
      <p style="margin:4px 0 0 0; opacity:0.9;">Suivi visuel des notes et performances scolaires</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    df_filtered = apply_filters(df, selected_class, selected_trimestre)
    if view_mode == "📊 Dashboard":
        show_dashboard(df_filtered)
    elif view_mode == "⚙️ Administration":
        show_admin(df)

    # >>> FOOTER HTML <<<
    st.markdown("""
    <hr>
    <div style="text-align:center; font-size:13px; color:gray; margin-top:20px;">
      Développé par Winson — GradeTrack © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()