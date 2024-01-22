import streamlit as st
import sqlite3
import pandas as pd
import re  # Module pour les expressions régulières

# Fonction pour créer la base de données
def create_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.commit()
    conn.close()

# Fonction pour valider le mot de passe
def is_valid_password(password):
    # Au moins 8 caractères, une majuscule, un chiffre, un caractère spécial
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password) is not None

# Fonction pour ajouter un utilisateur à la base de données avec vérification du nom d'utilisateur
def add_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Vérifier si le nom d'utilisateur existe déjà
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    existing_user = c.fetchone()

    if existing_user:
        st.error("Ce nom d'utilisateur est déjà utilisé. Veuillez choisir un autre.")
    else:
        # Vérifier si le mot de passe est valide
        if not is_valid_password(password):
            st.error("Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre et un caractère spécial.")
        else:
            # Ajouter l'utilisateur s'il n'existe pas déjà et que le mot de passe est valide
            c.execute('INSERT INTO users VALUES (?, ?)', (username, password))
            conn.commit()
            st.success("Inscription réussie!")

    conn.close()


# Fonction pour vérifier les informations de connexion
def check_login(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

# Fonction pour supprimer un utilisateur de la base de données
def delete_user(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE username=?', (username,))
    conn.commit()
    conn.close()

# Créer la base de données au démarrage de l'application
create_db()

# Stocker le nom de l'utilisateur actuellement connecté dans la session Streamlit
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Liste des utilisateurs connectés
if 'connected_users' not in st.session_state:
    st.session_state.connected_users = []

# Sélection de l'onglet
selected_tab = st.sidebar.radio("Navigation", ["Connexion", "Liste des utilisateurs"])

# Afficher le formulaire de connexion
st.subheader("Connexion")
login_username = st.text_input("Nom d'utilisateur", key="login_username_input")
login_password = st.text_input("Mot de passe", type="password", key="login_password_input")
if st.button("Se connecter"):
    if check_login(login_username, login_password):
        st.session_state.current_user = login_username  # Stocker le nom de l'utilisateur connecté
        st.session_state.connected_users.append(st.session_state.current_user)  # Ajouter l'utilisateur à la liste des connectés
        st.success("Connexion réussie!")
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect.")

# Afficher le formulaire d'inscription dans un expander
with st.expander("Créez-vous un compte si ce n'est pas déjà fait 😉"):
    st.subheader("Inscription")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        add_user(username, password)  # Appeler la fonction add_user

# Onglet Liste des utilisateurs
if selected_tab == "Liste des utilisateurs":
    st.subheader("Liste des utilisateurs inscrits")
    # Récupérer la liste des utilisateurs depuis la base de données
    conn = sqlite3.connect('user_data.db')
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    # Afficher le DataFrame des utilisateurs inscrits
    st.dataframe(users_df)

    # Possibilité de supprimer un utilisateur
    delete_username = st.text_input("Nom d'utilisateur à supprimer")
    if st.button("Supprimer utilisateur"):
        delete_user(delete_username)
        st.success("Utilisateur supprimé!")

    # Liste des utilisateurs connectés
    st.subheader("Liste des utilisateurs connectés")

    # Créer un DataFrame pour les utilisateurs connectés
    connected_users_df = pd.DataFrame({"Utilisateur connecté": st.session_state.connected_users})

    # Afficher le DataFrame des utilisateurs connectés
    st.dataframe(connected_users_df)


# Bouton de déconnexion
if st.sidebar.button("Se déconnecter"):
    if st.session_state.current_user is not None and st.session_state.current_user in st.session_state.connected_users:
        st.session_state.connected_users.remove(st.session_state.current_user)  # Retirer l'utilisateur de la liste des connectés
        st.sidebar.success(f"Au revoir {st.session_state.current_user}, Déconnexion réussie!")
        st.session_state.current_user = None  # Réinitialiser le nom de l'utilisateur actuellement connecté
    else:
        st.sidebar.warning("Vous n'êtes pas connecté.")



