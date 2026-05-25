import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import time

st.set_page_config(page_title="Simulation Écosystème Complet 🐺🐑🌿", layout="wide")

st.title("🔬 Écosystème : Loups 🐺, Moutons 🐑 et Herbe 🌿")
st.write("Modélisation d'une chaîne trophique complète à trois niveaux.")

# --- BARRE LATÉRALE : PARAMÈTRES ---
st.sidebar.header("⚙️ Configuration du Monde")
taille_grille = st.sidebar.slider("Taille de la grille (NxN)", 10, 60, 40)
densite_moutons = st.sidebar.slider("Densité initiale Moutons (%)", 5, 50, 20) / 100
densite_loups = st.sidebar.slider("Densité initiale Loups (%)", 1, 20, 5) / 100
densite_herbe = st.sidebar.slider("Densité initiale Herbe (%)", 10, 90, 50) / 100

st.sidebar.header("🌿 Végétation")
vitesse_herbe = st.sidebar.slider("Fréquence de repousse de l'herbe", 0.01, 0.50, 0.08, step=0.01)

st.sidebar.header("🐑 Comportement des Moutons")
repro_mouton = st.sidebar.slider("Taux de reproduction Mouton", 0.05, 0.5, 0.20)
famine_mouton = st.sidebar.slider("Mortalité Mouton (Manque d'herbe)", 0.05, 0.5, 0.15)

st.sidebar.header("🐺 Comportement des Loups")
efficacite_chasse = st.sidebar.slider("Probabilité de manger un mouton", 0.1, 1.0, 0.60)
famine_loup = st.sidebar.slider("Mortalité Loup (Famine)", 0.05, 0.5, 0.20)

# --- INITIALISATION ---
if 'grille' not in st.session_state or st.sidebar.button("🔄 Réinitialiser l'écosystème"):
    grille = np.zeros((taille_grille, taille_grille), dtype=int)
    
    for x in range(taille_grille):
        for y in range(taille_grille):
            r = np.random.random()
            if r < densite_moutons:
                grille[x, y] = 2  # Mouton
            elif r < (densite_moutons + densite_loups):
                grille[x, y] = 3  # Loup
            elif r < (densite_moutons + densite_loups + densite_herbe):
                grille[x, y] = 1  # Herbe
                
    st.session_state.grille = grille
    st.session_state.hist_herbe = []
    st.session_state.hist_moutons = []
    st.session_state.hist_loups = []

# --- CONTRÔLES ---
en_cours = st.checkbox("▶️ Lancer la simulation de l'écosystème")

zone_affichage = st.empty()
zone_metriques = st.empty()

# Palette : 0=Terre nue (Marron/Gris), 1=Herbe (Vert), 2=Mouton (Bleu ciel), 3=Loup (Rouge)
cmap_ecosysteme = ListedColormap(['#3E2723', '#4CAF50', '#E0F7FA', '#D32F2F'])

# --- BOUCLE BIOLOGIQUE ---
while en_cours:
    grille_actuelle = st.session_state.grille
    nouvelle_grille = grille_actuelle.copy()
    
    nb_herbe = 0
    nb_moutons = 0
    nb_loups = 0
    
    for x in range(1, taille_grille - 1):
        for y in range(1, taille_grille - 1):
            entite = grille_actuelle[x, y]
            
            # Analyse du voisinage proche
            voisins = grille_actuelle[x-1:x+2, y-1:y+2]
            herbe_autour = np.sum(voisins == 1)
            moutons_autour = np.sum(voisins == 2)
            loups_autour = np.sum(voisins == 3)
            
            if entite == 0:  # --- CASE VIDE / TERRE NUE ---
                # L'herbe repousse selon la fréquence réglée
                if np.random.random() < vitesse_herbe:
                    nouvelle_grille[x, y] = 1
                    
            elif entite == 1:  # --- HERBE ---
                nb_herbe += 1
                
            elif entite == 2:  # --- MOUTON ---
                nb_moutons += 1
                # 1. Risque numéro 1 : Se faire manger par un loup
                if loups_autour > 0 and np.random.random() < efficacite_chasse:
                    nouvelle_grille[x, y] = 0
                # 2. Nutrition : Le mouton mange l'herbe sous lui ou autour s'il y en a
                elif herbe_autour > 0:
                    # Le mouton mange, la case d'herbe voisine devient vide
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if grille_actuelle[x+dx, y+dy] == 1:
                                nouvelle_grille[x+dx, y+dy] = 0
                                break
                    # Si bien nourri, possibilité de se reproduire
                    if np.random.random() < repro_mouton:
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if nouvelle_grille[x+dx, y+dy] in [0, 1]: # Naissance sur terre ou herbe
                                    nouvelle_grille[x+dx, y+dy] = 2
                                    break
                # 3. Famine : Si pas d'herbe autour, le mouton risque de mourir
                elif herbe_autour == 0 and np.random.random() < famine_mouton:
                    nouvelle_grille[x, y] = 0
                                
            elif entite == 3:  # --- LOUP ---
                nb_loups += 1
                # Le loup a besoin de proies
                if moutons_autour == 0 and np.random.random() < famine_loup:
                    nouvelle_grille[x, y] = 0
                elif moutons_autour > 0:
                    # Chasse : le loup mange un mouton aux alentours
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if grille_actuelle[x+dx, y+dy] == 2:
                                nouvelle_grille[x+dx, y+dy] = 0
                                break
                    # Reproduction si nourriture abondante
                    if np.random.random() < 0.20:
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if nouvelle_grille[x+dx, y+dy] in [0, 1]:
                                    nouvelle_grille[x+dx, y+dy] = 3
                                    break

    st.session_state.grille = nouvelle_grille
    st.session_state.hist_herbe.append(nb_herbe)
    st.session_state.hist_moutons.append(nb_moutons)
    st.session_state.hist_loups.append(nb_loups)
    
    # --- RENDU VISUEL ---
    with zone_affichage.container():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
        
        # Carte
        ax1.imshow(nouvelle_grille, cmap=cmap_ecosysteme, vmin=0, vmax=3, origin="lower")
        ax1.axis("off")
        ax1.set_title("Carte : Terre (Marron) | Herbe (Vert) | Moutons (Blanc) | Loups (Rouge)")
        
        # Graphique à 3 courbes
        ax2.plot(st.session_state.hist_herbe, color="#4CAF50", linewidth=1.5, label="Herbe 🌿")
        ax2.plot(st.session_state.hist_moutons, color="#81D4FA", linewidth=2, label="Moutons 🐑")
        ax2.plot(st.session_state.hist_loups, color="#E53935", linewidth=2, label="Loups 🐺")
        ax2.set_title("Dynamique globale de l'écosystème")
        ax2.set_xlabel("Générations")
        ax2.set_ylabel("Quantité / Population")
        ax2.legend(loc="upper right")
        ax2.grid(True, linestyle="--", alpha=0.3)
        
        st.pyplot(fig)
        plt.close(fig)
        
    # Métriques
    col_m1, col_m2, col_m3 = zone_metriques.columns(3)
    col_m1.metric("Quantité d'herbe 🌿", nb_herbe)
    col_m2.metric("Moutons vivants 🐑", nb_moutons)
    col_m3.metric("Loups vivants 🐺", nb_loups)
    
    time.sleep(0.05)
