import streamlit as st
import sqlite3


def creer_base_de_donnees():
    conn = sqlite3.connect("gestion_stock.db")
    cur = conn.cursor()

    # Table des catégories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL
        )
    """)

    # Table des produits
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            description TEXT,
            prix_unitaire REAL NOT NULL,
            quantite_stock INTEGER NOT NULL DEFAULT 0,
            categorie_id INTEGER,
            FOREIGN KEY (categorie_id) REFERENCES categories (id) ON DELETE SET NULL
        )
    """)

    # Table des commandes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER,
            quantite INTEGER NOT NULL,
            date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE CASCADE
        )
    """)

    # Table des fournisseurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            contact TEXT
        )
    """)

    conn.commit()
    conn.close()


# Connexion à la base SQLite
def init_connection():
    return sqlite3.connect("gestion_stock.db")


# Fonctions pour interagir avec la base de données
def ajouter_produit(conn, nom, description, prix, quantite, categorie_id):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produits (nom, description, prix_unitaire, quantite_stock, categorie_id)
        VALUES (?, ?, ?, ?, ?)
    """, (nom, description, prix, quantite, categorie_id))
    conn.commit()


def obtenir_produits(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.nom, p.description, p.prix_unitaire, p.quantite_stock, c.nom AS categorie
        FROM produits p
        LEFT JOIN categories c ON p.categorie_id = c.id
    """)
    return cur.fetchall()


def ajouter_categorie(conn, nom):
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (nom) VALUES (?)", (nom,))
    conn.commit()


def obtenir_categories(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM categories")
    return cur.fetchall()


# Interface Streamlit
def main():
    # Créer la base de données si elle n'existe pas encore
    creer_base_de_donnees()

    conn = init_connection()
    st.set_page_config(page_title="Gestion de Stock", page_icon="📦", layout="wide")

    # Header personnalisé avec une image (facultatif)
    st.markdown("""
    <style>
    .title {
        font-size: 35px;
        font-weight: bold;
        color: #4CAF50;
    }
    .footer {
        font-size: 14px;
        color: #888;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #ccc;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Application de Gestion de Stock (SQLite)</div>", unsafe_allow_html=True)

    menu = ["Produits", "Catégories", "Commandes", "Fournisseurs"]
    choix = st.sidebar.selectbox("Menu", menu)

    if choix == "Produits":
        st.subheader("Gestion des Produits")
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom du produit")
            description = st.text_area("Description")

        with col2:
            prix = st.number_input("Prix unitaire", min_value=0.0, step=0.01)
            quantite = st.number_input("Quantité en stock", min_value=0, step=1)

        categories = obtenir_categories(conn)
        categorie_id = st.selectbox("Catégorie", [c[0] for c in categories],
                                    format_func=lambda x: [c[1] for c in categories if c[0] == x][0])

        if st.button("Ajouter produit"):
            ajouter_produit(conn, nom, description, prix, quantite, categorie_id)
            st.success("Produit ajouté avec succès !")

        st.subheader("Liste des produits")
        produits = obtenir_produits(conn)
        for produit in produits:
            st.write(
                f"**ID**: {produit[0]} | **Nom**: {produit[1]} | **Catégorie**: {produit[5]} | **Prix**: {produit[3]} | **Stock**: {produit[4]}")

    elif choix == "Catégories":
        st.subheader("Gestion des Catégories")
        nom = st.text_input("Nom de la catégorie")
        if st.button("Ajouter catégorie"):
            ajouter_categorie(conn, nom)
            st.success("Catégorie ajoutée avec succès !")

        st.subheader("Liste des catégories")
        categories = obtenir_categories(conn)
        for categorie in categories:
            st.write(f"**ID**: {categorie[0]} | **Nom**: {categorie[1]}")

    # Footer avec votre signature
    st.markdown("<div class='footer'>Développé par Kate | 2025</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
