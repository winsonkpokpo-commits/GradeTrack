# app.py - Application principale GradeTrack
import streamlit as st
import numpy as np
from config import Config
from data_manager import DataManager
from views import Views
from admin import Admin

def apply_filters(df, selected_class, selected_trimestre, selected_student=None):
    """Applique les filtres sur le DataFrame"""
    if df.empty:
        return df
        
    df_filtered = df.copy()
    
    # Exclure les élèves sans notes par défaut
    df_filtered = df_filtered.dropna(subset=['Note'])
    df_filtered = df_filtered[df_filtered['Matiere'] != '']
    
    if selected_class and selected_class != "Toutes":
        df_filtered = df_filtered[df_filtered['Classe'] == selected_class]
    if selected_trimestre and selected_trimestre != "Tous":
        df_filtered = df_filtered[df_filtered['Trimestre'] == selected_trimestre]
    if selected_student and selected_student != "Tous":
        df_filtered = df_filtered[df_filtered['Eleve'] == selected_student]
    
    return df_filtered

def create_sidebar(df):
    """Crée la sidebar avec les contrôles"""
    with st.sidebar:
        st.markdown("## 🎮 Panneau de Contrôle")
        
        # Sélecteur de vue
        view_options = [
            "📊 Dashboard",
            "👤 Détail Élève", 
            "➕ Ajouter des Données",
            "⚙️ Administration"
        ]
        
        view_mode = st.selectbox("Mode d'affichage", view_options, index=0)
        
        st.markdown("---")
        
        # Filtres communs
        classes = ["Toutes"] + sorted([
            c for c in df['Classe'].unique() 
            if pd.notna(c) and c not in ["", "Non assignée"]
        ]) if not df.empty else ["Toutes"]
        
        selected_class = st.selectbox("🏫 Classe", classes)
        selected_trimestre = st.selectbox("📅 Trimestre", ["Tous", "1", "2", "3"])
        
        # Filtre élève spécifique pour la vue détail
        selected_student = None
        if view_mode == "👤 Détail Élève":
            students = ["Tous"] + sorted([
                e for e in df['Eleve'].unique() 
                if pd.notna(e) and e != ""
            ]) if not df.empty else ["Tous"]
            selected_student = st.selectbox("👤 Élève", students)
        
        st.markdown("---")
        
        # Statistiques rapides
        show_quick_stats(df)
        
        st.markdown("---")
        
        # Bouton d'actualisation
        if st.button("🔄 Actualiser", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        return view_mode, selected_class, selected_trimestre, selected_student

def show_quick_stats(df):
    """Affiche les statistiques rapides dans la sidebar"""
    if df.empty:
        return
    
    df_valid = df.dropna(subset=['Note'])
    df_valid = df_valid[df_valid['Matiere'] != '']
    
    if df_valid.empty:
        return
    
    st.markdown("### 📈 Stats Rapides")
    
    total_students = df['Eleve'].nunique()
    total_grades = len(df_valid)
    avg_grade = df_valid['Note'].mean()
    
    st.metric("👥 Élèves", total_students)
    st.metric("📝 Notes", total_grades)
    
    if not np.isnan(avg_grade):
        st.metric("📊 Moyenne", f"{avg_grade:.2f}/20")

def create_header():
    """Crée l'en-tête de l'application"""
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
    """Crée le footer de l'application"""
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; font-size: 13px; color: #666; margin-top: 20px;">
      Développé par {Config.DEVELOPER} — {Config.APP_NAME} © {Config.YEAR}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Point d'entrée principal de l'application"""
    # Configuration de la page
    st.set_page_config(**Config.PAGE_CONFIG)
    
    # Initialiser le gestionnaire de données
    data_manager = DataManager()
    
    # Charger les données
    df = DataManager.load_data()
    
    # Interface sidebar
    view_mode, selected_class, selected_trimestre, selected_student = create_sidebar(df)
    
    # Header principal
    create_header()
    
    # Appliquer les filtres
    df_filtered = apply_filters(df, selected_class, selected_trimestre, selected_student)
    
    # Afficher le contenu selon la vue sélectionnée
    if view_mode == "📊 Dashboard":
        Views.show_dashboard(df_filtered)
        
    elif view_mode == "👤 Détail Élève":
        if selected_student and selected_student != "Tous":
            Views.show_student_detail(df_filtered, selected_student)
        else:
            st.info("👆 Veuillez sélectionner un élève dans la sidebar pour voir ses détails")
            
    elif view_mode == "➕ Ajouter des Données":
        Views.show_add_data()
        
    elif view_mode == "⚙️ Administration":
        Admin.show_admin_panel(df)
    
    # Footer
    create_footer()

if __name__ == "__main__":
    # Ajouter l'import pandas qui manquait
    import pandas as pd
    main()