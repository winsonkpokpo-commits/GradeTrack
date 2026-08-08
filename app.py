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
VIEW_ANALYTICS = "📈 Analytics"
VIEW_STUDENT_DETAIL = "👤 Détail Élève"
VIEW_ADD_DATA = "➕ Ajouter des Données"
VIEW_ADMIN = "⚙️ Administration"

CLASS_ALL = "Toutes"
TRIMESTER_ALL = "Tous"
STUDENT_ALL = "Tous"

def load_data_cached(data_manager: DataManager) -> pd.DataFrame:
    """Wrapper around a module-level cached loader so Streamlit can key the cache.

    The leading-underscore parameter on the cached function ensures Streamlit
    skips hashing the DataManager object itself.
    """
    return _cached_loader(data_manager)


@st.cache_data(show_spinner=False)
def _cached_loader(_data_manager: DataManager) -> pd.DataFrame:
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

def show_subject_averages(df: pd.DataFrame):
    """Group by Matiere and show bar chart + table of average Note per subject."""
    if df is None or df.empty or 'Matiere' not in df.columns or 'Note' not in df.columns:
        st.info("Données insuffisantes pour afficher les moyennes par matière.")
        return

    df_valid = df.dropna(subset=['Note'])
    df_valid = df_valid[df_valid['Matiere'] != '']
    if df_valid.empty:
        st.info("Données insuffisantes pour afficher les moyennes par matière.")
        return

    subj = df_valid.groupby('Matiere', dropna=True)['Note'].mean().round(2).sort_values(ascending=False)
    subj_df = subj.reset_index().rename(columns={'Matiere': 'Matière', 'Note': 'Moyenne /20'})

    left, right = st.columns([1, 1])
    with left:
        st.bar_chart(subj)
    with right:
        st.dataframe(subj_df, hide_index=True)

def show_class_ranking(df: pd.DataFrame, selected_class: str):
    """Show ranking of students within a class or ranking of classes overall."""
    if df is None or df.empty or 'Note' not in df.columns:
        st.info("Données insuffisantes pour établir le classement.")
        return

    df_valid = df.dropna(subset=['Note'])
    df_valid = df_valid[df_valid['Note'].astype(str) != '']
    if df_valid.empty:
        st.info("Données insuffisantes pour établir le classement.")
        return

    if selected_class and selected_class != CLASS_ALL and 'Classe' in df_valid.columns:
        # Rank students within the selected class
        df_sel = df_valid[df_valid['Classe'] == selected_class]
        if df_sel.empty or 'Eleve' not in df_sel.columns:
            st.info("Pas assez de données pour ce classement de classe sélectionnée.")
            return
        ranked = df_sel.groupby('Eleve', dropna=True)['Note'].mean().round(2).sort_values(ascending=False).reset_index()
        ranked.insert(0, 'Rang', range(1, len(ranked) + 1))
        ranked = ranked.rename(columns={'Eleve': 'Élève', 'Note': 'Moyenne /20'})
        st.dataframe(ranked, hide_index=True)
    else:
        # Rank classes overall
        if 'Classe' not in df_valid.columns:
            st.info("Pas assez de données pour établir le classement des classes.")
            return
        ranked = df_valid.groupby('Classe', dropna=True)['Note'].mean().round(2).sort_values(ascending=False).reset_index()
        ranked.insert(0, 'Rang', range(1, len(ranked) + 1))
        ranked = ranked.rename(columns={'Classe': 'Classe', 'Note': 'Moyenne /20'})
        st.dataframe(ranked, hide_index=True)

def show_trimester_trend(df: pd.DataFrame):
    """Show trend of mean Note per Trimestre (optionally per Classe)."""
    if df is None or df.empty or 'Trimestre' not in df.columns or 'Note' not in df.columns:
        st.info("Données insuffisantes pour afficher la tendance par trimestre.")
        return

    df_valid = df.dropna(subset=['Note'])
    if df_valid.empty:
        st.info("Données insuffisantes pour afficher la tendance par trimestre.")
        return

    # Compute mean note by Trimestre and Classe
    group = df_valid.groupby(['Trimestre', 'Classe'], dropna=True)['Note'].mean()
    # If multiple classes present, unstack to get columns per class
    try:
        trend = group.unstack('Classe')
    except Exception:
        trend = group.unstack('Classe')

    # Ensure Trimestre sorted by natural order if numeric-like
    try:
        trend = trend.reindex(sorted(trend.index, key=lambda x: int(x)))
    except Exception:
        trend = trend.sort_index()

    st.line_chart(trend)
    st.caption("Ce graphique ignore intentionnellement le filtre 'Trimestre' de la sidebar; "
               "il montre la tendance complète par trimestre (passez TRIMESTER_ALL pour voir la série complète).")

def show_export_options(df: pd.DataFrame):
    """Provide CSV download and attempt a simple PDF summary using fpdf2."""
    left, right = st.columns([1, 1])
    csv_bytes = (df.to_csv(index=False).encode('utf-8-sig') if df is not None else b'')
    with left:
        st.download_button("Télécharger CSV", data=csv_bytes, file_name="gradetrack_export.csv", mime="text/csv")

    with right:
        try:
            from fpdf import FPDF

            # Build a simple ASCII-only PDF summary (Helvetica)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            total_students = int(df['Eleve'].nunique()) if df is not None and 'Eleve' in df.columns else 0
            total_grades = int(len(df.dropna(subset=['Note']))) if df is not None and 'Note' in df.columns else 0
            overall_avg = float(df['Note'].mean()) if df is not None and 'Note' in df.columns and not df['Note'].dropna().empty else 0.0

            pdf.cell(0, 8, txt=f"GradeTrack Summary", ln=1)
            pdf.cell(0, 8, txt=f"Total unique students: {total_students}", ln=1)
            pdf.cell(0, 8, txt=f"Total grades: {total_grades}", ln=1)
            pdf.cell(0, 8, txt=f"Overall average: {overall_avg:.2f}/20", ln=1)
            pdf.ln(4)

            # Averages per subject (ASCII only)
            if df is not None and 'Matiere' in df.columns and 'Note' in df.columns:
                subj = df.dropna(subset=['Note'])
                subj = subj[subj['Matiere'] != '']
                if not subj.empty:
                    subj_avg = subj.groupby('Matiere', dropna=True)['Note'].mean().round(2)
                    pdf.cell(0, 8, txt="Average per subject:", ln=1)
                    for mat, val in subj_avg.items():
                        # Ensure plain ASCII: replace accented chars with plain approximations
                        mat_ascii = (str(mat)
                                     .replace('é', 'e')
                                     .replace('è', 'e')
                                     .replace('ê', 'e')
                                     .replace('à', 'a')
                                     .replace('ù', 'u')
                                     .replace('ô', 'o')
                                     .replace('î', 'i'))
                        pdf.cell(0, 7, txt=f"- {mat_ascii}: {val:.2f}/20", ln=1)

            pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
            st.download_button("Télécharger PDF", data=pdf_bytes, file_name="gradetrack_summary.pdf", mime="application/pdf")
        except ImportError:
            st.caption("Export PDF indisponible : installez `fpdf2` (`pip install fpdf2`).")

def show_analytics(df_filtered: pd.DataFrame, df_trend: pd.DataFrame, selected_class: str):
    """Wrapper that displays all analytics sections in order."""
    st.header("📈 Analytics")
    show_subject_averages(df_filtered)
    st.markdown("---")
    show_class_ranking(df_filtered, selected_class)
    st.markdown("---")
    show_trimester_trend(df_trend)
    st.markdown("---")
    show_export_options(df_filtered)

def create_sidebar(df: pd.DataFrame) -> Tuple[str, str, str, Optional[str]]:
    """Crée la sidebar avec les contrôles et retourne l'état sélectionné."""
    with st.sidebar:
        st.markdown("## 🎮 Panneau de Contrôle")

        view_options = [VIEW_DASHBOARD, VIEW_ANALYTICS, VIEW_STUDENT_DETAIL, VIEW_ADD_DATA, VIEW_ADMIN]
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
        elif view_mode == VIEW_ANALYTICS:
            # For trends we want the full trimester series, so pass TRIMESTER_ALL to the trend DF.
            df_trend = apply_filters(df, selected_class, TRIMESTER_ALL, None)
            show_analytics(df_filtered, df_trend, selected_class)
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
