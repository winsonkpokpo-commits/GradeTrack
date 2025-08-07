import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime

# ========== Configuration et constantes ==========

st.set_page_config(
    page_title="GradeTrack Complet", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Fonctions utilitaires ==========

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Base utilisateurs simple
USERS = {
    "alice": hash_password("alice123"),
    "bob": hash_password("bob456"),
    "demo": hash_password("demo123"),
}

def check_credentials(username, password):
    """Vérifie les identifiants utilisateur"""
    return username in USERS and hash_password(password) == USERS[username]

def get_data_path(username):
    """Retourne le chemin du fichier de données pour un utilisateur"""
    return f"{username}_notes.csv"

def load_user_data(username):
    """Charge les données d'un utilisateur"""
    path = get_data_path(username)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            required_columns = ["Matière", "Note", "Coefficient", "Trimestre"]
            if not all(col in df.columns for col in required_columns):
                return create_empty_dataframe()
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {e}")
            return create_empty_dataframe()
    else:
        return create_empty_dataframe()

def create_empty_dataframe():
    """Crée un DataFrame vide avec les bonnes colonnes"""
    return pd.DataFrame(columns=["Matière", "Note", "Coefficient", "Trimestre", "Date"])

def save_user_data(username, df):
    """Sauvegarde les données d'un utilisateur"""
    try:
        df.to_csv(get_data_path(username), index=False)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

def calculer_moyenne(df):
    """Calcule la moyenne pondérée"""
    if df.empty or df["Coefficient"].sum() == 0:
        return None
    return round((df["Note"] * df["Coefficient"]).sum() / df["Coefficient"].sum(), 2)

def calculer_statistiques_detaillees(df):
    """Calcule des statistiques détaillées"""
    if df.empty:
        return None
    
    stats = {
        "moyenne": calculer_moyenne(df),
        "note_min": df["Note"].min(),
        "note_max": df["Note"].max(),
        "nombre_notes": len(df),
        "nombre_matieres": df["Matière"].nunique()
    }
    return stats

def valider_note(note, coef, matiere, trimestre):
    """Valide les données d'une note"""
    errors = []
    if not matiere or matiere.strip() == "":
        errors.append("La matière ne peut pas être vide")
    if note < 0 or note > 20:
        errors.append("La note doit être entre 0 et 20")
    if coef <= 0 or coef > 6:
        errors.append("Le coefficient doit être entre 0.1 et 6")
    if trimestre not in ["1", "2", "3"]:
        errors.append("Le trimestre doit être 1, 2 ou 3")
    return errors

# ========== Styles CSS ==========

def load_custom_css():
    """Charge des styles CSS personnalisés"""
    st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .grade-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== Interface principale ==========

def main():
    load_custom_css()
    
    # --- Authentification ---
    if "user" not in st.session_state:
        show_login_page()
        return
    
    user = st.session_state["user"]
    
    # --- Chargement des données de l'utilisateur ---
    if "data" not in st.session_state or st.session_state.get("last_user") != user:
        st.session_state["data"] = load_user_data(user)
        st.session_state["last_user"] = user
    
    df = st.session_state["data"]
    
    # --- Sidebar navigation ---
    with st.sidebar:
        st.title("🎓 GradeTrack")
        st.write(f"Connecté en tant que: **{user}**")
        st.markdown("---")
        
        menu = st.selectbox(
            "Navigation", 
            ["🏠 Accueil", "➕ Ajouter note", "📋 Voir notes", "📈 Statistiques", "📤 Exporter", "🔓 Déconnexion"]
        )
        
        # Statistiques rapides dans la sidebar
        if not df.empty:
            st.markdown("### 📊 Aperçu rapide")
            stats = calculer_statistiques_detaillees(df)
            if stats:
                st.metric("Moyenne générale", f"{stats['moyenne']}/20")
                st.metric("Nombre de notes", stats['nombre_notes'])
                st.metric("Matières", stats['nombre_matieres'])
    
    # --- Contenu principal basé sur le menu ---
    if menu == "🏠 Accueil":
        show_home_page(user, df)
    elif menu == "➕ Ajouter note":
        show_add_note_page(user, df)
    elif menu == "📋 Voir notes":
        show_view_notes_page(user, df)
    elif menu == "📈 Statistiques":
        show_statistics_page(df)
    elif menu == "📤 Exporter":
        show_export_page(user, df)
    elif menu == "🔓 Déconnexion":
        show_logout_page()

def show_login_page():
    """Page de connexion"""
    st.title("🔐 Connexion à GradeTrack")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Authentification")
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")
            login_button = st.form_submit_button("Se connecter", use_container_width=True)
            
            if login_button:
                if check_credentials(username, password):
                    st.session_state["user"] = username
                    st.success(f"Bienvenue {username} !")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect")
        
        # Aide pour les utilisateurs demo
        with st.expander("ℹ️ Comptes de démonstration"):
            st.write("**Utilisateurs disponibles:**")
            st.write("- alice / alice123")
            st.write("- bob / bob456") 
            st.write("- demo / demo123")

def show_home_page(user, df):
    """Page d'accueil"""
    st.title(f"👋 Bonjour {user} !")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎓 Bienvenue dans ton espace GradeTrack personnalisé
        
        Cette application te permet de :
        - ➕ **Ajouter tes notes** avec leurs coefficients
        - 📋 **Consulter et modifier** tes notes existantes
        - 📈 **Visualiser tes statistiques** par trimestre
        - 📤 **Exporter tes données** en CSV
        
        Utilise le menu à gauche pour naviguer entre les différentes fonctionnalités.
        """)
        
        if not df.empty:
            st.markdown("### 📊 Résumé de tes notes")
            stats = calculer_statistiques_detaillees(df)
            if stats:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Moyenne générale", f"{stats['moyenne']}/20")
                with col_b:
                    st.metric("Notes enregistrées", stats['nombre_notes'])
                with col_c:
                    st.metric("Matières suivies", stats['nombre_matieres'])
    
    with col2:
        if df.empty:
            st.info("🎯 Commence par ajouter ta première note !")
        else:
            st.markdown("### 🏆 Dernières notes ajoutées")
            recent_notes = df.tail(5)
            for _, row in recent_notes.iterrows():
                color = "🟢" if row['Note'] >= 15 else "🟡" if row['Note'] >= 10 else "🔴"
                st.markdown(f"{color} **{row['Matière']}** : {row['Note']}/20 (T{row['Trimestre']})")

def show_add_note_page(user, df):
    """Page d'ajout de note"""
    st.title("➕ Ajouter une nouvelle note")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("form_ajout", clear_on_submit=True):
            st.markdown("### 📝 Informations de la note")
            
            col_a, col_b = st.columns(2)
            with col_a:
                matiere = st.text_input("Matière *", placeholder="Ex: Mathématiques")
                note = st.number_input("Note (/20) *", min_value=0.0, max_value=20.0, step=0.1, value=10.0)
            
            with col_b:
                coef = st.number_input("Coefficient *", min_value=0.1, max_value=6.0, step=0.1, value=1.0)
                trimestre = st.selectbox("Trimestre *", ["1", "2", "3"])
            
            valider = st.form_submit_button("✅ Ajouter la note", use_container_width=True)
            
            if valider:
                errors = valider_note(note, coef, matiere, trimestre)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Ajouter la date
                    nouvelle = {
                        "Matière": matiere.strip(),
                        "Note": note,
                        "Coefficient": coef,
                        "Trimestre": trimestre,
                        "Date": datetime.now().strftime("%Y-%m-%d")
                    }
                    df = pd.concat([df, pd.DataFrame([nouvelle])], ignore_index=True)
                    st.session_state["data"] = df
                    
                    if save_user_data(user, df):
                        st.success(f"✅ Note ajoutée avec succès : {matiere} - {note}/20 (coef {coef}) au trimestre {trimestre}")
                    else:
                        st.error("❌ Erreur lors de la sauvegarde")
    
    with col2:
        if not df.empty:
            st.markdown("### 📊 Aperçu actuel")
            for t in sorted(df["Trimestre"].unique()):
                dft = df[df["Trimestre"] == t]
                moyenne_t = calculer_moyenne(dft)
                if moyenne_t:
                    st.metric(f"Trimestre {t}", f"{moyenne_t}/20")

def show_view_notes_page(user, df):
    """Page de consultation des notes"""
    st.title("📋 Notes enregistrées")
    
    if df.empty:
        st.info("📝 Aucune note enregistrée. Commence par ajouter ta première note !")
        return
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        trimestre_filter = st.selectbox("Filtrer par trimestre", ["Tous"] + sorted(df["Trimestre"].unique()))
    with col2:
        matiere_filter = st.selectbox("Filtrer par matière", ["Toutes"] + sorted(df["Matière"].unique()))
    
    # Application des filtres
    df_filtered = df.copy()
    if trimestre_filter != "Tous":
        df_filtered = df_filtered[df_filtered["Trimestre"] == trimestre_filter]
    if matiere_filter != "Toutes":
        df_filtered = df_filtered[df_filtered["Matière"] == matiere_filter]
    
    if df_filtered.empty:
        st.warning("Aucune note ne correspond aux filtres sélectionnés.")
        return
    
    st.markdown(f"### 📊 {len(df_filtered)} note(s) affichée(s)")
    
    # Éditeur de données
    edited_df = st.data_editor(
        df_filtered,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Note": st.column_config.NumberColumn(
                "Note (/20)",
                min_value=0,
                max_value=20,
                step=0.1
            ),
            "Coefficient": st.column_config.NumberColumn(
                "Coefficient",
                min_value=0.1,
                max_value=6.0,
                step=0.1
            )
        }
    )
    
    # Note: La sauvegarde automatique est simplifiée pour éviter les erreurs
    if st.button("💾 Sauvegarder les modifications"):
        st.session_state["data"] = edited_df
        if save_user_data(user, edited_df):
            st.success("✅ Modifications sauvegardées!")
        else:
            st.error("❌ Erreur lors de la sauvegarde")

def show_statistics_page(df):
    """Page des statistiques"""
    st.title("📈 Statistiques détaillées")
    
    if df.empty:
        st.info("📊 Ajoute des notes pour voir les statistiques.")
        return
    
    # Statistiques générales
    stats = calculer_statistiques_detaillees(df)
    if stats:
        st.markdown("### 🎯 Vue d'ensemble")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Moyenne générale", f"{stats['moyenne']}/20")
        with col2:
            st.metric("Note minimale", f"{stats['note_min']}/20")
        with col3:
            st.metric("Note maximale", f"{stats['note_max']}/20")
        with col4:
            st.metric("Total des notes", stats['nombre_notes'])
    
    # Statistiques par trimestre
    st.markdown("### 📅 Analyse par trimestre")
    
    for t in sorted(df["Trimestre"].unique()):
        st.subheader(f"Trimestre {t}")
        dft = df[df["Trimestre"] == t]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            moyenne_t = calculer_moyenne(dft)
            if moyenne_t is not None:
                st.metric(f"Moyenne T{t}", f"{moyenne_t}/20")
                st.write(f"📊 {len(dft)} note(s)")
                st.write(f"🎯 {dft['Matière'].nunique()} matière(s)")
        
        with col2:
            # Graphique simple avec st.bar_chart
            if not dft.empty:
                chart_data = dft.set_index('Matière')['Note']
                st.bar_chart(chart_data, height=300)
                st.caption(f"Notes du Trimestre {t}")
    
    # Vue d'ensemble avec graphiques Streamlit natifs
    st.markdown("### 📊 Vue d'ensemble des notes")
    
    # Graphique des moyennes par matière
    if not df.empty:
        moyennes_matieres = df.groupby("Matière").apply(lambda x: calculer_moyenne(x))
        moyennes_matieres = moyennes_matieres.dropna()
        
        if not moyennes_matieres.empty:
            st.markdown("#### Moyennes par matière")
            st.bar_chart(moyennes_matieres, height=400)
        
        # Distribution des notes avec histogramme
        st.markdown("#### Distribution des notes")
        st.histogram(df, x="Note", bins=10)

def show_export_page(user, df):
    """Page d'export"""
    st.title("📤 Exporter les données")
    
    if df.empty:
        st.info("📄 Aucune donnée à exporter.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Export CSV")
        st.write(f"📊 {len(df)} note(s) à exporter")
        
        # Options d'export
        include_stats = st.checkbox("Inclure les statistiques", value=True)
        
        # Génération du CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        
        if include_stats:
            stats = calculer_statistiques_detaillees(df)
            stats_text = f"\n\n# Statistiques générales\n"
            stats_text += f"# Moyenne générale: {stats['moyenne']}/20\n"
            stats_text += f"# Nombre total de notes: {stats['nombre_notes']}\n"
            stats_text += f"# Nombre de matières: {stats['nombre_matieres']}\n"
            csv_data += stats_text.encode("utf-8")
        
        st.download_button(
            label="📥 Télécharger le fichier CSV",
            data=csv_data,
            file_name=f"{user}_notes_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.markdown("### 👀 Aperçu des données")
        st.dataframe(df, use_container_width=True)

def show_logout_page():
    """Page de déconnexion"""
    st.title("🔓 Déconnexion")
    st.write("Êtes-vous sûr de vouloir vous déconnecter ?")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Confirmer la déconnexion", use_container_width=True):
            st.session_state.clear()
            st.success("Déconnexion réussie !")
            st.rerun()

# ========== Lancement de l'application ==========

if __name__ == "__main__":
    main()