# app.py - Application principale GradeTrack (refactored)
import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from config import Config
from data_manager import DataManager
from views import Views
from admin import Admin

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UI constants
VIEW_DASHBOARD = "📊 Dashboard"
VIEW_STUDENT_DETAIL = "👤 Détail Élève"
VIEW_ADD_DATA = "➕ Ajouter des Données"
VIEW_ADMIN = "⚙️ Administration"

CLASS_ALL = "Toutes"
TRIMESTER_ALL = "Tous"
STUDENT_ALL = "Tous"

@st.cache_data(show_spinner=False)
def load_data_cached(_data_manager: DataManager) -> pd.DataFrame:
    """Load data and cache result to avoid reloading on every interaction.

    The parameter is prefixed with an underscore so Streamlit skips hashing the
    DataManager itself and uses the provided value for cache keying safely.
    """
    return _data_manager.load_data()

@st.cache_data(show_spinner=False)
def unique_classes_from(df: pd.DataFrame) -> list:
    if df is None or df.empty:
        return [CLASS_ALL]
    vals = [
        c for c in df['Classe'].unique()
        if pd.notna(c) and c not in ("", "Non assignée")
    ]
    return [CLASS_ALL] + sorted(vals)

@st.cache_data(show_spinner=False)
def unique_students_from(df: pd.DataFrame) -> list:
    if df is None or df.empty:
        return [STUDENT_ALL]
    vals = [
        e for e in df['Eleve'].unique()
        if pd.notna(e) and e != ""
    ]
    return [STUDENT_ALL] + sorted(vals)

def apply_filters(df: pd.DataFrame, selected_class: str, selected_trimestre: str, selected_student: Optional[str] = None) -> pd.DataFrame:
    """Applique les filtres sur le DataFrame et normalise les entrées."""
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])

    df_filtered = df.copy()

    # Exclure les entrées sans note ni matière
    if 'Note' in df_filtered.columns:
        df_filtered = df_filtered.dropna(subset=['Note'])
    if 'Matiere' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Matiere'] != '']

    # Filtres optionnels
    if selected_class and selected_class != CLASS_ALL and 'Classe' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Classe'] == selected_class]
    if selected_trimestre and selected_trimestre != TRIMESTER_ALL and 'Trimestre' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Trimestre'] == selected_trimestre]
    if selected_student and selected_student != STUDENT_ALL and 'Eleve' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Eleve'] == selected_student]

    return df_filtered

def show_quick_stats(df: pd.DataFrame):
    """Affiche les statistiques rapides dans la sidebar."""
    if df is None or df.empty:
        return

    df_valid = df.copy()
    if 'Note' in df_valid.columns:
        df_valid = df_valid.dropna(subset=['Note'])
    if 'Matiere' in df_valid.columns:
        df_valid = df_valid[df_valid['Matiere'] != '']

    if df_valid.empty:
        return

    st.markdown("### 📈 Stats Rapides")
    total_students = df['Eleve'].nunique() if 'Eleve' in df.columns else 0
    total_grades = len(df_valid)
    avg_grade = df_valid['Note'].mean() if 'Note' in df_valid.columns else np.nan

    st.metric("👥 Élèves", total_students)
    st.metric("📝 Notes", total_grades)
    if not np.isnan(avg_grade):
        st.metric("📊 Moyenne", f"{avg_grade:.2f}/20")

def create_sidebar(df: pd.DataFrame) -> Tuple[str, str, str, Optional[str]]:
    """Crée la sidebar avec les contrôles et retourne l'état sélectionné."""
    with st.sidebar:
        st.markdown("## 🎮 Panneau de Contrôle")

        view_options = [VIEW_DASHBOARD, VIEW_STUDENT_DETAIL, VIEW_ADD_DATA, VIEW_ADMIN]
        view_mode = st.selectbox("Mode d'affichage", view_options, index=0)

        st.markdown("---")

        classes = unique_classes_from(df)
        selected_class = st.selectbox("🏫 Classe", classes)

        selected_trimestre = st.selectbox("📅 Trimestre", [TRIMESTER_ALL, "1", "2", "3"])

        selected_student = None
        if view_mode == VIEW_STUDENT_DETAIL:
            students = unique_students_from(df)
            selected_student = st.selectbox("👤 Élève", students)

        st.markdown("---")
        show_quick_stats(df)
        st.markdown("---")

        if st.button("🔄 Actualiser", use_container_width=True):
            # Clear streamlit cache and reload
            st.cache_data.clear()
            st.rerun()

        return view_mode, selected_class, selected_trimestre, selected_student

def create_header():
    """Crée l'en-tête de l'application."""
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #0f172a, #2563eb); 
                padding: 24px; border-radius: 12px; color: white; margin-bottom: 20px;">
      <h1 style="margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif;">
        {Config.APP_ICON} {Config.APP_NAME}
      </h1>
      <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 1.1rem;">
        {Config.APP_DESCRIPTION}
      </p>
    </div>
    """, unsafe_allow_html=True)

def create_footer():
    """Crée le footer de l'application."""
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; font-size: 13px; color: #666; margin-top: 20px;">
      Développé par {Config.DEVELOPER} — {Config.APP_NAME} © {Config.YEAR}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Point d'entrée principal de l'application."""
    try:
        st.set_page_config(**Config.PAGE_CONFIG)

        data_manager = DataManager()
        df = load_data_cached(data_manager)

        if df is None or df.empty:
            st.warning("Aucune donnée de notes disponible. Utilisez '➕ Ajouter des Données' pour importer des notes.")
            # still allow admin/add-data views
        view_mode, selected_class, selected_trimestre, selected_student = create_sidebar(df)

        create_header()
        df_filtered = apply_filters(df, selected_class, selected_trimestre, selected_student)

        if view_mode == VIEW_DASHBOARD:
            Views.show_dashboard(df_filtered)
        elif view_mode == VIEW_STUDENT_DETAIL:
            if selected_student and selected_student != STUDENT_ALL:
                Views.show_student_detail(df_filtered, selected_student)
            else:
                st.info("👆 Veuillez sélectionner un élève dans la sidebar pour voir ses détails")
        elif view_mode == VIEW_ADD_DATA:
            Views.show_add_data()
        elif view_mode == VIEW_ADMIN:
            Admin.show_admin_panel(df)

        create_footer()

    except Exception as exc:  # Top-level catch to display friendly message & log
        # Log the string form of the exception explicitly for easier local debugging,
        # then log the exception with traceback.
        logger.error("Erreur: %s", str(exc))
        logger.exception("Erreur inattendue dans l'application GradeTrack")
        st.error("Une erreur inattendue est survenue. Consultez les logs pour plus de détails.")

if __name__ == "__main__":
    main()
