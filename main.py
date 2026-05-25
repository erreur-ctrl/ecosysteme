import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Simulation Écosystème Cellulaire", layout="wide")

st.title("🔬 Laboratoire d'Écosystème Cellulaire")
st.write("Une simulation d'automate cellulaire interactive pour observer la dynamique des populations.")

# --- BARRE LATÉRALE : PARAMÈTRES ---
st.sidebar.header("⚙️ Configuration du Monde")
taille_grille = st.sidebar.slider("Taille de la grille (NxN)", 10, 60, 40)
densite_initiale = st.sidebar.slider("Densité initiale de population (%)", 5, 80, 25) / 100

st.sidebar.header("🧬 Règles de Vie & Survie")
taux_repro = st.sidebar.slider("Taux de reproduction (Naissance)", 0.1, 1.0, 0.5)
taux_famine = st.sidebar.slider("Sensibilité à la surpopulation / isolement", 0.1, 1.0, 0.7)

# --- INITIALISATION DE L'ÉTAT ---
if 'grille' not in st.session_state or st.sidebar.button("🔄 Réinitialiser la simulation"):
    st.session_state.grille = np.random.choice(
        [0, 1], 
        size=(taille_grille, taille_grille), 
        p=[1 - densite_initiale, densite_initiale]
    )
    st.session_state.historique = []

# --- CONTRÔLES DE L'ANIMATION ---
col_ctrl1, col_ctrl2 = st.columns(2)
en_cours = col_ctrl1.checkbox("▶️ Lancer la simulation en boucle")

# Zones d'affichage dynamiques
zone_affichage = st.empty()
zone_metriques = st.empty()

# --- BOUCLE DE SIMULATION ---
while en_cours:
    grille_actuelle = st.session_state.grille
    nouvelle_grille = grille_actuelle.copy()
    
    # Algorithme de calcul du voisinage
    for x in range(1, taille_grille - 1):
        for y in range(1, taille_grille - 1):
            voisins = np.sum(grille_actuelle[x-1:x+2, y-1:y+2]) - grille_actuelle[x, y]
            
            if grille_actuelle[x, y] == 1:
                # Règle de mort (Sous-population ou Surpopulation)
                if voisins < 2 or voisins > 3:
                    if np.random.random() < taux_famine:
                        nouvelle_grille[x, y] = 0
            else:
                # Règle de naissance
                if voisins == 3:
                    if np.random.random() < taux_repro:
                        nouvelle_grille[x, y] = 1

    st.session_state.grille = nouvelle_grille
    population_totale = int(np.sum(nouvelle_grille))
    st.session_state.historique.append(population_totale)
    
    # Rendu des graphiques
    with zone_affichage.container():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
        
        # Visuel de l'écosystème
        ax1.imshow(nouvelle_grille, cmap="viridis", origin="lower")
        ax1.axis("off")
        ax1.set_title("Distribution spatiale des cellules")
        
        # Courbe d'évolution temporelle
        ax2.plot(st.session_state.historique, color="#1E88E5", linewidth=2)
        ax2.set_title("Évolution de la population totale")
        ax2.set_xlabel("Générations")
        ax2.set_ylabel("Individus")
        ax2.grid(True, linestyle="--", alpha=0.5)
        
        st.pyplot(fig)
        plt.close(fig)
        
    zone_metriques.metric("Population active", f"{population_totale} cellules")
    time.sleep(0.05)
