#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 10:21:31 2024

@author: Mehdi

main program 
"""

###############################################################################
#                            IMPORTATIONS                                    #
###############################################################################

import os
from fonctions import segmentation, lancer_aleatoire, extract_signature, decode_ean13_signature

###############################################################################
#                               MAIN                                          #
###############################################################################

def main():
    """
    Programme principal :
    1. Charge une image fournie par l'utilisateur.
    2. Effectue la segmentation pour detecter la region d'interet.
    3. Lance des rayons aleatoires pour extraire des signatures.
    4. Tente de decoder le code-barres EAN-13 jusqu'a reussir ou atteindre la limite.
    """
    # Demande a l'utilisateur de fournir un chemin d'image valide
    image_path = input("Veuillez entrer le chemin du fichier image : ")
    while not os.path.exists(image_path):
        print("Fichier introuvable. Veuillez reessayer.")
        image_path = input("Veuillez entrer un chemin valide : ")

    # etape 1 : Segmentation pour detecter la region d'interet
    try:
        min_row, min_col, max_row, max_col = segmentation(image_path)
        print("Segmentation reussie. Region detectee.")
    except Exception as e:
        print(f"Erreur lors de la segmentation : {e}")
        return

    # Definir les coins de la region detectee
    p1 = (min_col, min_row)
    p2 = (max_col, min_row)
    p3 = (max_col, max_row)
    p4 = (min_col, max_row)

    # etape 2 : Recherche d'un code-barres en lancant des rayons aleatoires
    max_attempts = 20  # Limite d'essais
    attempt = 0
    code_barres = None

    while attempt < max_attempts:
        print(f"Tentative {attempt + 1}/{max_attempts}...")

        # Generer un rayon aleatoire
        point1, point2 = lancer_aleatoire(p1, p2, p3, p4)

        # Extraire la signature le long du rayon genere
        signature_95bits = extract_signature(image_path, point1, point2)

        if signature_95bits is not None:
            try:
                # Tenter de decoder la signature
                code_barres = decode_ean13_signature(signature_95bits)
                print(f"Code-barres detecte : {code_barres}")
                break  # Arreter la boucle si un code valide est trouve
            except ValueError as e:
                print(f"Erreur de decodage : {e}")
        else:
            print("Signature non valide ou non extraite correctement.")

        attempt += 1

    # etape 3 : Resultat final
    if code_barres:
        print(f"Code-barres final detecte : {code_barres}")
    else:
        print("echec de la detection apres plusieurs tentatives.")


###############################################################################
#                            EXECUTION DU PROGRAMME                           #
###############################################################################

if __name__ == "__main__":
    main()
