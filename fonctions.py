#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 18:11:26 2025

@author: Mehdi

Diverses Fonctions 

""" 


###############################################################################
#                            IMPORTATIONS                                    #
###############################################################################

# Modules standards
import os
import random

# Modules scientifiques
import numpy as np
from scipy.signal import convolve2d
from skimage import color, io
from skimage.morphology import closing, opening, square
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu

# Modules pour l'interface graphique
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.ndimage import map_coordinates

###############################################################################
#                              SEGMENTATION                                   #
###############################################################################

def segmentation(image_path):
    # Chargement de l'image
    img = io.imread(image_path)
    if img.shape[-1] == 4:
        img = img[..., :3]
    I = color.rgb2gray(img)

    # Parametres
    sigma_noise = 0.02
    sigma_G = 1.8
    sigma_T = 18
    seuil_coherence = 0.3

    # Ajout de bruit
    bruit = np.random.normal(0, sigma_noise, I.shape)
    I_bruite = np.clip(I + bruit, 0, 1)

    # Calcul des gradients
    size = int(3 * sigma_G)
    x, y = np.meshgrid(np.arange(-size, size+1), np.arange(-size, size+1))

    G_x = -(x / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2*sigma_G**2))
    G_y = -(y / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2*sigma_G**2))

    I_x = convolve2d(I_bruite, G_x, mode='same', boundary='symm')
    I_y = convolve2d(I_bruite, G_y, mode='same', boundary='symm')

    norme = np.sqrt(I_x**2 + I_y**2) + 1e-8
    I_x /= norme
    I_y /= norme

    # Tenseur de structure
    size_T = int(2 * sigma_T)
    G = (1 / (2 * np.pi * sigma_T**2)) * np.exp(-(x**2 + y**2) / (2 * sigma_T**2))

    T_xx = convolve2d(I_x**2, G, mode='same', boundary='symm')
    T_xy = convolve2d(I_x * I_y, G, mode='same', boundary='symm')
    T_yy = convolve2d(I_y**2, G, mode='same', boundary='symm')

    D1 = 1 - np.sqrt((T_xx - T_yy)**2 + 4 * (T_xy**2)) / (T_xx + T_yy + 1e-15)

    # Segmentation
    M = (D1 > seuil_coherence).astype(int)
    M_clean = closing(M, square(3))
    M_clean = opening(M_clean, square(2))

    labels = label(M_clean)
    if labels.max() > 0:
        regions = regionprops(labels)
        largest_region = max(regions, key=lambda r: r.area)
        return largest_region.bbox 
    else:
        raise ValueError("Aucune region coherente detectee.")


###############################################################################
#                          RAYON ALeATOIRE                                    #
###############################################################################
def lancer_aleatoire(C1, C2, C3, C4):

    """
    Genere un rayon aleatoire ou oriente dans une zone delimitee par 4 coins.

    Parametres:
        C1, C2, C3, C4 (tuple): Coordonnees des coins de la region (x, y).

    Retourne:
        point1, point2 (tuple): Coordonnees des points de depart et d'arrivee du rayon.

    Remarque:
        - Les rayons peuvent etre orientes selon un angle aleatoire autour du centre de la zone.
        - Cela permet d'explorer differentes directions pour couvrir plus de possibilites de detection.
    """
    
    # Verification des coordonnees
    if not all(len(point) == 2 for point in [C1, C2, C3, C4]):
        raise ValueError("Tous les points doivent avoir deux coordonnees (x, y).")

    # Generer un angle aleatoire
    angle = np.random.uniform(0, 360)
    angle_rad = np.radians(angle)

    # Calculer le centre de la region
    center_x = (C1[0] + C2[0] + C3[0] + C4[0]) / 4
    center_y = (C1[1] + C2[1] + C3[1] + C4[1]) / 4

    # Rayon depuis le centre dans la direction donnee
    radius = min(np.linalg.norm(np.array(C1) - np.array([center_x, center_y])),
                 np.linalg.norm(np.array(C3) - np.array([center_x, center_y])))

    # Calcul des points
    x_start = center_x + radius * np.cos(angle_rad)
    y_start = center_y + radius * np.sin(angle_rad)
    x_end = center_x - radius * np.cos(angle_rad)
    y_end = center_y - radius * np.sin(angle_rad)

    return (x_start, y_start), (x_end, y_end)


        
###############################################################################
#                               EXTRACTION                                    #
###############################################################################


def extraction(image, p1, p2):
    """
    Extrait une signature binaire de 95 bits le long d'un rayon defini par deux points.

    Parametres:
        - image (numpy.ndarray): Image en niveaux de gris.
        - p1 (tuple): Point de depart du rayon (x, y).
        - p2 (tuple): Point d'arrivee du rayon (x, y).

    Retourne:
        - signature_95bits (list): Liste de 95 bits representant la signature extraite.
    """

    # etape 1 : Calcul de la longueur du rayon
    longueur_rayon = int(np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2))
    print(f"Longueur du rayon: {longueur_rayon} pixels")

    # etape 2 : Extraction initiale de la signature
    nb_points = max(longueur_rayon, 95)  # Nombre de points a echantillonner
    t = np.linspace(0, 1, nb_points)    # Parametre d'interpolation

    # Calcul des coordonnees du rayon
    x = p1[0] + (p2[0] - p1[0]) * t
    y = p1[1] + (p2[1] - p1[1]) * t

    # Extraction des intensites sur le rayon avec interpolation bilineaire
    intensities = map_coordinates(image, [y, x], order=1, mode='reflect')

    # etape 3 : Application du seuil d'Otsu
    threshold = threshold_otsu(intensities)  # Calcul du seuil d'Otsu
    binary_signature = (intensities > threshold).astype(int)  # Binarisation

    # etape 4 : Trouver les limites utiles
    non_zero = np.nonzero(binary_signature)[0]
    if len(non_zero) == 0:
        print("Aucune region utile trouvee dans la signature.")
        return None  # Retourne None si aucune donnee utile

    # etape 5 : Reduction aux indices utiles
    start_idx = non_zero[0]
    end_idx = non_zero[-1]

    # Coordonnees des points utiles
    t_start = start_idx / nb_points
    t_end = end_idx / nb_points

    useful_p1 = (
        p1[0] + (p2[0] - p1[0]) * t_start,
        p1[1] + (p2[1] - p1[1]) * t_start
    )
    useful_p2 = (
        p1[0] + (p2[0] - p1[0]) * t_end,
        p1[1] + (p2[1] - p1[1]) * t_end
    )

    # etape 6 : Ajustement et extraction finale
    useful_length = np.sqrt((useful_p2[0] - useful_p1[0])**2 + (useful_p2[1] - useful_p1[1])**2)
    u = max(1, int(useful_length / 95))  # Calcul de l'unite de base
    print(f"Unite de base u calculee : {u}")

    # etape 7 : Extraction finale sur 95 * u points
    nb_points_final = 95 * u
    t = np.linspace(0, 1, nb_points_final)
    x = useful_p1[0] + (useful_p2[0] - useful_p1[0]) * t
    y = useful_p1[1] + (useful_p2[1] - useful_p1[1]) * t

    # Extraction finale avec interpolation
    final_signature = map_coordinates(image, [y, x], order=1, mode='reflect')

    # Binarisation finale avec Otsu
    final_threshold = threshold_otsu(final_signature)
    final_binary_signature = (final_signature > final_threshold).astype(int)

    # etape 8 : Selection des 95 premiers bits
    if len(final_binary_signature) >= 95:
        signature_95bits = final_binary_signature[:95]
        return signature_95bits  # Retourne la signature binaire
    else:
        print("La signature extraite est trop courte.")
        return None


###############################################################################
#                               DeCODAGE                                      #
###############################################################################

def decode_ean13_signature(binary_signature):
    """
    Decoder un code-barres EAN-13 a partir de sa signature binaire.

    Parametres:
    - binary_signature: liste d'entiers (0 ou 1), representant la signature binaire du code-barres (95 bits)

    Retourne:
    - code_barres: chaîne de caracteres representant le code EAN-13 decode
    """
    # Verifier la longueur de la signature
    if len(binary_signature) != 95:
        raise ValueError("La signature binaire doit contenir exactement 95 bits.")

    # Motifs de garde
    guard_left = [1, 0, 1]
    guard_center = [0, 1, 0, 1, 0]
    guard_right = [1, 0, 1]

    # Verifier les motifs de garde
    if binary_signature[0:3] != guard_left:
        raise ValueError("Motif de garde gauche incorrect.")
    if binary_signature[45:50] != guard_center:
        raise ValueError("Motif de garde central incorrect.")
    if binary_signature[92:95] != guard_right:
        raise ValueError("Motif de garde droit incorrect.")

    # Tables de codage pour les chiffres
    code_L = {
        '0001101': '0',
        '0011001': '1',
        '0010011': '2',
        '0111101': '3',
        '0100011': '4',
        '0110001': '5',
        '0101111': '6',
        '0111011': '7',
        '0110111': '8',
        '0001011': '9',
    }

    code_G = {
        '0100111': '0',
        '0110011': '1',
        '0011011': '2',
        '0100001': '3',
        '0011101': '4',
        '0111001': '5',
        '0000101': '6',
        '0010001': '7',
        '0001001': '8',
        '0010111': '9',
    }

    code_R = {
        '1110010': '0',
        '1100110': '1',
        '1101100': '2',
        '1000010': '3',
        '1011100': '4',
        '1001110': '5',
        '1010000': '6',
        '1000100': '7',
        '1001000': '8',
        '1110100': '9',
    }

    # Table de parite pour determiner le premier chiffre
    parity_table = {
        'LLLLLL': '0',
        'LLGLGG': '1',
        'LLGGLG': '2',
        'LLGGGL': '3',
        'LGLLGG': '4',
        'LGGLLG': '5',
        'LGGGLL': '6',
        'LGLGLG': '7',
        'LGLGGL': '8',
        'LGGLGL': '9',
    }

    # Decodage des 6 chiffres de gauche
    left_digits = []
    parity_pattern = ''
    for i in range(6):
        start = 3 + i * 7
        end = start + 7
        pattern_bits = binary_signature[start:end]
        pattern = ''.join(map(str, pattern_bits))

        if pattern in code_L:
            digit = code_L[pattern]
            parity_pattern += 'L'
        elif pattern in code_G:
            digit = code_G[pattern]
            parity_pattern += 'G'
        else:
            raise ValueError(f"Motif inconnu dans la partie gauche : {pattern}")
        left_digits.append(digit)

    # Determiner le premier chiffre a partir du motif de parite
    if parity_pattern in parity_table:
        first_digit = parity_table[parity_pattern]
    else:
        raise ValueError(f"Motif de parite inconnu : {parity_pattern}")

    # Decodage des 6 chiffres de droite
    right_digits = []
    for i in range(6):
        start = 50 + i * 7
        end = start + 7
        pattern_bits = binary_signature[start:end]
        pattern = ''.join(map(str, pattern_bits))

        if pattern in code_R:
            digit = code_R[pattern]
        else:
            raise ValueError(f"Motif inconnu dans la partie droite : {pattern}")
        right_digits.append(digit)

    # Construire le code-barres complet
    code_barres = first_digit + ''.join(left_digits) + ''.join(right_digits)

    # Verifier la cle de contrôle
    digits = list(map(int, code_barres))
    if len(digits) != 13:
        raise ValueError("Le code-barres doit contenir 13 chiffres.")

    # Calcul de la cle de contrôle selon la norme EAN-13
    # etape 1 : Somme des chiffres en positions paires (2e, 4e, ..., 12e)
    sum_even = sum(digits[i] for i in range(1, 12, 2))

    # etape 2 : Multiplier la somme par 3
    sum_even *= 3

    # etape 3 : Somme des chiffres en positions impaires (1ere, 3e, ..., 11e)
    sum_odd = sum(digits[i] for i in range(0, 12, 2))

    # etape 4 : Calculer le total
    total = sum_even + sum_odd

    # etape 5 : Calculer la cle de contrôle
    check_digit = (10 - (total % 10)) % 10

    # Verifier si la cle de contrôle est correcte
    if check_digit != digits[-1]:
        raise ValueError(f"Cle de contrôle invalide : attendu {check_digit}, obtenu {digits[-1]}")

    return code_barres


