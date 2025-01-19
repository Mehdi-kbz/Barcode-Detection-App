#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 11:25:26 2024

code segmentation

@author: Mehdi
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from skimage import color, io
from skimage.morphology import closing, opening, square
from skimage.measure import label, regionprops

###############################################################################
#                              PARAMeTRES                                     #
###############################################################################

# Fichier image
image_path = 'images/thon.png'

# Parametres bruit
sigma_noise = 0.02  # ecart-type du bruit gaussien

# Parametres du filtre gaussien
sigma_G = 1.8  # ecart-type pour le calcul du gradient gaussien

# Parametres du tenseur de structure
sigma_T = 18   # ecart-type pour le lissage dans le tenseur

# Parametres de segmentation
seuil_coherence = 0.3  # Seuil pour la coherence

###############################################################################
#                            CHARGEMENT IMAGE                                 #
###############################################################################

img = io.imread(image_path)

# Supprimer le canal alpha si present
if img.shape[-1] == 4:
    img = img[..., :3]

# Conversion en niveaux de gris
I = color.rgb2gray(img)

###############################################################################
#                         AJOUT DE BRUIT (OPTIONNEL)                          #
###############################################################################

bruit = np.random.normal(0, sigma_noise, I.shape)
I_bruite = np.clip(I + bruit, 0, 1)

###############################################################################
#                    CALCUL DES GRADIENTS GAUSSIENS                           #
###############################################################################

# Generer les filtres derives de la gaussienne
size = int(3 * sigma_G)
x, y = np.meshgrid(np.arange(-size, size+1), np.arange(-size, size+1))

G_x = -(x / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2*sigma_G**2))
G_y = -(y / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2*sigma_G**2))

# Appliquer les filtres pour calculer les gradients
I_x = convolve2d(I_bruite, G_x, mode='same', boundary='symm')
I_y = convolve2d(I_bruite, G_y, mode='same', boundary='symm')

# Normaliser les gradients
norme = np.sqrt(I_x**2 + I_y**2) + 1e-8
I_x /= norme
I_y /= norme

###############################################################################
#                           TENSEUR DE STRUCTURE                              #
###############################################################################

# Calcul du filtre gaussien pour le lissage
size_T = int(2 * sigma_T)
x_T, y_T = np.meshgrid(np.arange(-size_T, size_T+1), np.arange(-size_T, size_T+1))
G = (1 / (2 * np.pi * sigma_T**2)) * np.exp(-(x_T**2 + y_T**2)/(2*sigma_T**2))

# Calcul des composantes du tenseur
T_xx = convolve2d(I_x**2, G, mode='same', boundary='symm')
T_xy = convolve2d(I_x * I_y, G, mode='same', boundary='symm')
T_yy = convolve2d(I_y**2, G, mode='same', boundary='symm')

###############################################################################
#                       MESURE DE COHeRENCE ET SEGMENTATION                   #
###############################################################################

# Calcul de la coherence D
D1 = 1 - np.sqrt((T_xx - T_yy)**2 + 4*(T_xy**2)) / (T_xx + T_yy + 1e-15)

# Segmentation par seuil
M = (D1 > seuil_coherence).astype(int)

###############################################################################
#                       NETTOYAGE MORPHOLOGIQUE                               #
###############################################################################

# Nettoyage avec ouverture et fermeture morphologiques
M_clean = closing(M, square(3))  # Connexion des barres
M_clean = opening(M_clean, square(2))  # Suppression du bruit

###############################################################################
#           EXTRACTION DE LA PLUS GRANDE ReGION CONNEXE (CODE-BARRE)          #
###############################################################################

labels = label(M_clean)

if labels.max() > 0:
    # Identifier la plus grande region
    regions = regionprops(labels)
    largest_region = max(regions, key=lambda r: r.area)

    # Creer le masque final base sur cette region
    M_final = np.zeros_like(M_clean)
    M_final[labels == largest_region.label] = 1
else:
    M_final = np.zeros_like(M_clean)

###############################################################################
#          ANALYSE GEOMeTRIQUE DE LA ReGION IDENTIFIeE (PCA)                  #
###############################################################################

Y, X = np.mgrid[0:M.shape[0], 0:M.shape[1]]

if np.sum(M) > 0:
    # Calcul du barycentre
    O_x = np.sum(X * M) / np.sum(M)
    O_y = np.sum(Y * M) / np.sum(M)

    # Centrage des points
    X_c = X - O_x
    Y_c = Y - O_y

    # Matrice de covariance
    C_xx = np.sum(X_c * X_c * M) / np.sum(M)
    C_xy = np.sum(X_c * Y_c * M) / np.sum(M)
    C_yy = np.sum(Y_c * Y_c * M) / np.sum(M)

    C = np.array([[C_xx, C_xy], [C_xy, C_yy]])

    # Calcul des vecteurs propres
    vals, vecs = np.linalg.eig(C)
    idx = np.argsort(vals)[::-1]
    vecs = vecs[:, idx]

    # Calcul des coins du rectangle oriente
    u1, u2 = vecs[:, 0], vecs[:, 1]
    alpha = X_c * u1[0] + Y_c * u1[1]
    beta = X_c * u2[0] + Y_c * u2[1]

    alpha_min, alpha_max = np.min(alpha[M==0]), np.max(alpha[M==0])
    beta_min, beta_max = np.min(beta[M==0]), np.max(beta[M==0])

    def corner(a, b):
        return (O_x + a * u1[0] + b * u2[0], O_y + a * u1[1] + b * u2[1])

    C1 = corner(alpha_min, beta_min)
    C2 = corner(alpha_max, beta_min)
    C3 = corner(alpha_max, beta_max)
    C4 = corner(alpha_min, beta_max)
else:
    C1 = C2 = C3 = C4 = (0, 0)

###############################################################################
#                               AFFICHAGE                                     #
###############################################################################

plt.figure(figsize=(15, 5))

# Image originale
plt.subplot(1, 2, 1)
plt.imshow(img, cmap='gray')
plt.title('Image originale')
plt.axis('off')

# Masque final
plt.subplot(1, 2, 2)
plt.imshow(M_final, cmap='gray')
plt.title('Code-barres detecte')
plt.axis('off')

# Rectangle oriente
#plt.subplot(1, 3, 3)
#plt.imshow(M_final, cmap='gray')

# Tracer le rectangle rouge
rect_x = [C1[0], C2[0], C3[0], C4[0], C1[0]]
rect_y = [C1[1], C2[1], C3[1], C4[1], C1[1]]
#plt.plot(rect_x, rect_y, 'r-', linewidth=2)

# Ajout des droites horizontales (2 lignes)
for _ in range(2):
    # Generer une position verticale (y) aleatoire entre les bords verticaux
    t = np.random.uniform(0, 1)  # Coefficient pour interpoler sur l'horizontale

    # Calculer les points de depart et d'arrivee sur l'horizontale
    x_start = C1[0] * (1 - t) + C4[0] * t  # Interpolation sur la gauche (C1 -> C4)
    y_start = C1[1] * (1 - t) + C4[1] * t

    x_end = C2[0] * (1 - t) + C3[0] * t    # Interpolation sur la droite (C2 -> C3)
    y_end = C2[1] * (1 - t) + C3[1] * t

    # Tracer la ligne horizontale bleue
   # plt.plot([x_start, x_end], [y_start, y_end], 'b--', linewidth=1.5)

# Ajout des droites selon les diagonales (2 lignes)
# Diagonale 1 (C1 -> C3)
#plt.plot([C1[0], C3[0]], [C1[1], C3[1]], 'g--', linewidth=1.5)

# Diagonale 2 (C2 -> C4)
#plt.plot([C2[0], C4[0]], [C2[1], C4[1]], 'g--', linewidth=1.5)

# Parametres de l'affichage
#plt.title('Lancers aleatoirs des rayons')
#plt.axis('off')
