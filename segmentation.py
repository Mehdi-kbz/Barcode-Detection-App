import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from skimage import color

# Charger l'image
img = plt.imread('Code-barre-FR.jpg')

# Vérifier et gérer les 4 canaux (R, G, B, A)
if img.shape[-1] == 4:  # Si l'image contient un canal alpha
    img = img[..., :3]  # Garder uniquement les canaux R, G, B

# Convertir en niveaux de gris
I = color.rgb2gray(img)

# Ajouter du bruit gaussien blanc
sigma_noise = 0.022  # écart-type du bruit, à ajuster en fonction de l'effet souhaité
bruit = np.random.normal(0, sigma_noise, I.shape)
I_bruite = I + bruit
I_bruite = np.clip(I_bruite, 0, 1)  # Pour s'assurer que les valeurs restent dans [0,1]

# Paramètre sigma pour les gradients
sigma_G = 1.8
size = int(3 * sigma_G)  # plus large pour un meilleur calcul du gradient
x, y = np.meshgrid(np.arange(-size, size + 1), np.arange(-size, size + 1))

# Définir les dérivées du filtre gaussien pour G_x et G_y
G_x = -(x / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2 * sigma_G**2))
G_y = -(y / (2 * np.pi * sigma_G**4)) * np.exp(-(x**2 + y**2) / (2 * sigma_G**2))

# Calcul des composantes du gradient I_x et I_y
I_x = convolve2d(I_bruite, G_x, mode='same', boundary='symm')  # Gradient horizontal
I_y = convolve2d(I_bruite, G_y, mode='same', boundary='symm')  # Gradient vertical

# Normalisation des gradients
norme = np.sqrt(I_x**2 + I_y**2) +1e-8
I_x = I_x/norme
I_y = I_y/norme


## Tenseur de structure T ##

# Filtre gaussien pour le lissage local des composants du tenseur
sigma_T = 18
size_T = int(2 * sigma_T)
x_T, y_T = np.meshgrid(np.arange(-size_T, size_T + 1), np.arange(-size_T, size_T + 1))

# Définition du filtre gaussien pour le lissage
G = (1 / (2 * np.pi * sigma_T**2)) * np.exp(-(x_T**2 + y_T**2) / (2 * sigma_T**2))

# Calcul des composantes du tenseur de structure
T_xx = convolve2d(I_x**2, G, mode='same', boundary='symm')
T_xy = convolve2d(I_x * I_y, G, mode='same', boundary='symm')
T_yy = convolve2d(I_y**2, G, mode='same', boundary='symm')

# Mesure de cohérence
D1 = 1 - np.sqrt((T_xx-T_yy)**2 + 4*(T_xy**2)) / (T_xx + T_yy)

# Binarisation
seuil = 0.3
N = (D1 > seuil)
M=N.astype(int)



# Use the cleaned binary image
rows, cols = np.where(M > 0)  # Coordinates of active pixels
coords = np.column_stack((cols, rows))  # (x, y) as (col, row)

# Verify active pixels exist
if len(coords) == 0:
    raise ValueError("Aucune région active détectée dans l'image binaire.")

# Calculate the barycentre
barycentre = coords.mean(axis=0)
print(f"Barycentre : {barycentre}")

# Compute covariance matrix
covariance_matrix = np.cov(coords, rowvar=False)

# Compute eigenvectors and eigenvalues
valeurs_propres, vecteurs_propres = np.linalg.eigh(covariance_matrix)

# Select the principal eigenvector
vecteur_directeur = vecteurs_propres[:, np.argmax(valeurs_propres)]
print(f"Vecteur directeur principal : {vecteur_directeur}")

# Projections onto the principal eigenvector
projections = np.dot(coords - barycentre, vecteur_directeur)

# Determine the extremities
idx_gauche = np.argmin(projections)
idx_droite = np.argmax(projections)

extremite_gauche = coords[idx_gauche]
extremite_droite = coords[idx_droite]










########## Affichage des résultats ##########
plt.figure(figsize=(15, 5))

# Image originale
plt.subplot(1, 4, 1)
plt.imshow(img, cmap='gray')
plt.title('Image à traiter')
plt.axis('off')


# Carte binaire des régions d'intérêt
plt.subplot(1, 4, 2)
plt.imshow(I_bruite, cmap='gray')
plt.title(f'Image bruitée avec sigma_bruit = {sigma_noise}')
plt.axis('off')

# Mesure de cohérence D
plt.subplot(1, 4, 3)
plt.imshow(D1, cmap='gray')
plt.title('Mesure de cohérence D' )
plt.axis('off')

# Carte binaire des régions d'intérêt
plt.subplot(1, 4, 4)
plt.imshow(M, cmap='gray')
plt.title('Régions probables de code-barres')
plt.axis('off')


# Stratégie multiechelle, pour que ça marche tout le temps (petit ou grand code barre) il fait diviser la taille de l'image par  2 aprés avoir appliqué un filtre passe bas 2D de paramètre 0.7
#O = barycentre ( moyenne )
#M est un point du nuage des points binarisés
#produit scalaire : OM.u1

#u1 vecteur propre principal
#projection sur le vect proore principal
#vecteur propre = vecteur direceteur de la matrice de covariance des positions x, y

