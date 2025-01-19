#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:55:00 2024

@author: starbook
"""

import cv2
import numpy as np

def otsu_threshold(signal):
    """
    Calcule le seuil d'Otsu à partir d'un tableau 1D (signal).
    Retourne le seuil calculé.
    """
    hist, bins = np.histogram(signal, bins=256, range=(0, 256))
    total_pixels = signal.size
    sum_total = sum(i * h for i, h in enumerate(hist))

    max_criteria = -1
    threshold = 0

    w_b = 0
    sum_b = 0

    for k in range(256):
        w_b += hist[k]
        if w_b == 0:
            continue
        w_f = total_pixels - w_b
        if w_f == 0:
            break

        sum_b += k * hist[k]
        m_b = sum_b / w_b if w_b != 0 else 0
        m_f = (sum_total - sum_b) / w_f if w_f != 0 else 0

        criteria = w_b * w_f * (m_b - m_f) ** 2
        if criteria > max_criteria:
            max_criteria = criteria
            threshold = k

    return threshold

def extract(cv_image, p1, p2):
    """
    Extrait la signature binarisée finale de 95 bits du code-barres.
    Entrées:
        image_path: chemin vers l'image (str)
        p1, p2: tuples (x, y) des deux points définissant le rayon
    Sortie:
        final_binary_signature: array (longueur 95) binaire (0/1)
    """


    # 1. Calcul de la longueur du rayon
    longueur_rayon = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    # 2. Extraire la première signature
    nb_points = max(int(longueur_rayon), 95)
    t = np.linspace(0, 1, nb_points)
    x = np.array([p1[0] + (p2[0] - p1[0])*t_i for t_i in t], dtype=np.float32)
    y = np.array([p1[1] + (p2[1] - p1[1])*t_i for t_i in t], dtype=np.float32)
    signature = cv2.remap(cv_image, x.reshape(-1,1), y.reshape(-1,1), cv2.INTER_LINEAR)[:, 0]

    # 3. Calcul du seuil d'Otsu
    threshold = otsu_threshold(signature)

    # 4. Binarisation de la première signature
    binary_signature = (signature > threshold).astype(np.uint8)

    # 5. Trouver les limites utiles
    non_zero = np.nonzero(binary_signature)[0]
    if len(non_zero) == 0:
        # Aucune région utile trouvée
        return None

    start_idx = non_zero[0]
    end_idx = non_zero[-1]

    # 6. Calculer les coordonnées du rayon utile
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

    # 7. Calculer l'unité de base u
    useful_length = np.sqrt((useful_p2[0] - useful_p1[0])**2 +
                            (useful_p2[1] - useful_p1[1])**2)
    u = max(1, int(useful_length / 95))

    # 8. Extraire la nouvelle signature le long du rayon utile
    nb_points_final = 95 * u
    t = np.linspace(0, 1, nb_points_final)
    x = np.array([useful_p1[0] + (useful_p2[0] - useful_p1[0])*t_i for t_i in t], dtype=np.float32)
    y = np.array([useful_p1[1] + (useful_p2[1] - useful_p1[1])*t_i for t_i in t], dtype=np.float32)
    final_signature = cv2.remap(cv_image, x.reshape(-1,1), y.reshape(-1,1), cv2.INTER_LINEAR)[:, 0]

    # 9. Binariser la signature finale
    final_binary_signature = (final_signature > threshold).astype(np.uint8)

    # Rééchantillonnage si la longueur n'est pas exactement 95
    if len(final_binary_signature) != 95:
        indices = np.round(np.linspace(0, len(final_binary_signature)-1, 95)).astype(int)
        final_binary_signature = final_binary_signature[indices]

    return final_binary_signature
