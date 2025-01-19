import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from fonctions import segmentation, extraction, lancer_aleatoire, decode_ean13_signature  # Import des fonctions


class BarcodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lecteur de Code-Barres")
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.resizable(True, True)

       
        # Degrade de fond
        self.canvas = tk.Canvas(self, width=1200, height=800)
        self.canvas.pack(fill="both", expand=True)
        self.create_gradient()

        # Variables
        self.image = None
        self.image_path = ""
        self.binary_signature = None
        self.decoded_barcode = None

        # Creer l'interface
        self.setup_ui()

    
    def create_gradient(self):
        """Creer un degrade de fond."""
        for i in range(100):
            color = f"#{i:02x}{i:02x}{255-i:02x}"
            self.canvas.create_rectangle(0, i * 9, 1200, (i + 1) * 3, fill=color, outline="")

    def setup_ui(self):
        
        """Creer les widgets de l'interface."""
        self.frame = tk.Frame(self.canvas)
        self.frame.place(relx=0.5, rely=0.05, anchor="n")

        # Bouton pour charger une image
        self.load_button = tk.Button(self.frame, text="Charger une image", command=self.load_image,  fg="black", font=("Arial", 12))
        self.load_button.grid(row=0, column=0, padx=10, pady=5)

        # Boutons pour selectionner le mode
        self.mode_var = tk.StringVar(value="manuel")
        tk.Radiobutton(self.frame, text="Rayon Manuel", variable=self.mode_var, value="manuel", font=("Arial", 12)).grid(row=0, column=1, padx=10)
        tk.Radiobutton(self.frame, text="Rayons Aleatoires", variable=self.mode_var, value="aleatoire", font=("Arial", 12)).grid(row=0, column=2, padx=10)

        # Boutons pour les actions
        self.segment_button = tk.Button(self.frame, text="Segmentation", command=self.segment_image,  fg="black", font=("Arial", 12))
        self.segment_button.grid(row=0, column=3, padx=10, pady=5)

        self.extract_button = tk.Button(self.frame, text="Extraction", command=self.extract_signature,  fg="black", font=("Arial", 12))
        self.extract_button.grid(row=0, column=4, padx=10, pady=5)

        self.decode_button = tk.Button(self.frame, text="Decoder", command=self.decode_barcode,  fg="black", font=("Arial", 12))
        self.decode_button.grid(row=0, column=5, padx=10, pady=5)

        self.verify_button = tk.Button(self.frame, text="Verifier dans la base", command=self.verify_database,  fg="black", font=("Arial", 12))
        self.verify_button.grid(row=0, column=6, padx=10, pady=5)

        # Bouton de reinitialisation
        self.reset_button = tk.Button(self.frame, text="Reinitialiser", command=self.reset_app,  fg="black", font=("Arial", 12))
        self.reset_button.grid(row=0, column=7, padx=10, pady=5)

        # Zone d'affichage d'image
        self.image_label = tk.Label(self.canvas, bg="#ffffff", bd=2, relief="sunken")
        self.image_label.place(relx=0.5, rely=0.6, anchor="center", width=800, height=500)

        # Zone de feedback
        self.feedback = tk.Label(self, text="Pret", font=("Arial", 12), bg="#e9ecef", fg="black")
        self.feedback.place(relx=0.5, rely=0.95, anchor="s")
      
        # Ajouter un label en bas à droite
        footer_label = tk.Label(self, text="Projet Image TS225 2024/2025", font=("Arial", 14), fg="white")
        footer_label.place(relx=1.0, rely=1.0, anchor="se", x=0, y=0)  # Decalage vers l'interieur

        footer_label2 = tk.Label(self, text="Developpe par: Mehdi, Salma, Arif et Louriz", 
                         font=("Arial", 14), fg="white")
        footer_label2.place(relx=0.0, rely=1.0, anchor="sw", x=0, y=0)  # Decalage leger

        # Bouton pour quitter l'application
        self.quit_button = tk.Button(
            self, 
            text="Quitter", 
            command=self.quit_app, 
            fg="red",          # Couleur du texte
            bg="red",            # Couleur de fond
            
            font=("Arial", 12, "bold"), # Police
            relief="raised",     # Effet 3D
            bd=2,                # Bordure
            padx=10,             # Padding horizontal
            pady=5               # Padding vertical
        )
        self.quit_button.place(relx=0.5, rely=0.975, anchor="center")  # Centrage en bas

    def load_image(self):
        """Charger une image depuis le fichier."""
        try:
            file_path = filedialog.askopenfilename(
                title="Selectionner une image",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
            )
            if not file_path:
                self.feedback.config(text="Aucune image selectionnee.")
                return

            self.image_path = file_path
            self.image = Image.open(file_path)
            self.display_image(self.image)
            self.feedback.config(text="Image chargee avec succes.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image : {str(e)}")
            self.feedback.config(text="Erreur lors du chargement.")

    def display_image(self, img):
        """Afficher une image redimensionnee."""
        img = img.resize((800, 500))
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img



    def segment_image(self):
        """Segmentation reelle avec extraction depuis le fichier segmentation."""
        try:
            # Mise à jour du feedback pour informer l'utilisateur
            self.feedback.config(text="Segmentation en cours...")
            self.update_idletasks()
    
            # Verifier si une image est chargee
            if not self.image_path:
                messagebox.showerror("Erreur", "Aucune image chargee !")
                self.feedback.config(text="Erreur : Chargez une image.")
                return
    
            # Appel de la fonction de segmentation
            mask, region = segmentation(self.image_path)
    
            # Affichage du resultat
            plt.figure(figsize=(8, 4))
            plt.subplot(1, 2, 1)
            plt.imshow(region, cmap='gray')
            plt.title("Region detectee")
            plt.axis("off")
    
            plt.subplot(1, 2, 2)
            plt.imshow(mask, cmap='gray')
            plt.title("Masque final")
            plt.axis("off")
    
            plt.tight_layout()
            plt.show()
    
            # Mise à jour du feedback
            self.feedback.config(text="Segmentation terminee.")
        except Exception as e:
            # Gestion des erreurs avec message d'alerte
            messagebox.showerror("Erreur", f"Erreur lors de la segmentation : {str(e)}")
            self.feedback.config(text="Erreur lors de la segmentation.")


    def extract_signature(self):
        """Extraction des signatures avec un rayon manuel ou aleatoire."""
        try:
            # Feedback initial
            self.feedback.config(text="Extraction en cours...")
            self.update_idletasks()
    
            # Verifier si une image est chargee
            if not self.image_path:
                messagebox.showerror("Erreur", "Aucune image chargee !")
                self.feedback.config(text="Erreur : Chargez une image.")
                return
    
            # Verifier si la segmentation a ete realisee (avec des coins detectes)
            if not hasattr(self, 'detected_region') or self.detected_region is None:
                messagebox.showerror("Erreur", "Aucune region detectee. Lancez la segmentation d'abord.")
                self.feedback.config(text="Erreur : Pas de region detectee.")
                return
    
            # Recuperer les coins detectes pour la zone d'interet
            C1, C2, C3, C4 = self.detected_region  # Coins detectes apres segmentation
    
            # Verifier le mode choisi (manuel ou aleatoire)
            if self.mode_var.get() == "manuel":
                messagebox.showinfo("Instruction", "Cliquez sur deux points pour definir un rayon.")
                self.feedback.config(text="Attente de la selection manuelle...")
                self.points = []  # Reinitialiser les points pour la selection manuelle
                self.canvas.bind("<Button-1>", self.on_click_manual)
                return
    
            elif self.mode_var.get() == "aleatoire":
                # Generer un rayon aleatoire avec la fonction lancer_aleatoire
                p1, p2 = lancer_aleatoire(C1, C2, C3, C4)
                points = (p1, p2)
    
            # Appeler la fonction d'extraction pour obtenir la signature binaire
            self.binary_signature = extraction(self.image_path, points[0], points[1])
    
            # Verifier si l'extraction a reussi
            if self.binary_signature is None:
                raise ValueError("Signature non extraite ou invalide.")
    
            # Afficher la signature binaire extraite
            plt.figure()
            plt.step(range(len(self.binary_signature)), self.binary_signature, where='mid')
            plt.title("Signature binaire extraite")
            plt.xlabel("Position")
            plt.ylabel("Valeur (0 ou 1)")
            plt.grid(True)
            plt.show()
    
            # Mise à jour du feedback
            self.feedback.config(text="Extraction terminee avec succes.")
    
        except Exception as e:
            # Gestion des erreurs
            messagebox.showerror("Erreur", f"Erreur lors de l'extraction : {str(e)}")
            self.feedback.config(text="Erreur lors de l'extraction.")
    
    
    def decode_barcode(self):
        """Decodage en utilisant la fonction du fichier fonctions.py."""
        try:
            # Feedback pour l'utilisateur
            self.feedback.config(text="Decodage en cours...")
            self.update_idletasks()
    
            # Verifier si une signature a ete extraite
            if self.binary_signature is None:
                messagebox.showerror("Erreur", "Aucune signature disponible pour le decodage.")
                self.feedback.config(text="Erreur : Aucune signature detectee.")
                return
    
            # Appeler la fonction de decodage
            self.decoded_barcode = decode_ean13_signature(self.binary_signature)
    
            # Mise à jour du feedback avec le code-barres detecte
            self.feedback.config(text=f"Code-barres detecte : {self.decoded_barcode}")
            messagebox.showinfo("Decodage Reussi", f"Code-barres : {self.decoded_barcode}")
    
        except Exception as e:
            # Gestion des erreurs
            messagebox.showerror("Erreur", f"Erreur lors du decodage : {str(e)}")
            self.feedback.config(text="Erreur lors du decodage.")

    def verify_database(self):
        """Verifier dans la base de donnees."""
        try:
            self.feedback.config(text="Verification dans la base...")
            self.update_idletasks()
    
            # Verifier si un code-barres a ete decode
            if not self.decoded_barcode:
                messagebox.showwarning("Attention", "Aucun code-barres decode. Veuillez lancer le decodage d'abord.")
                self.feedback.config(text="Erreur : Pas de code-barres decode.")
                return
    
            # Charger la base de donnees (fichier texte contenant une liste de codes-barres valides)
            database_path = filedialog.askopenfilename(
                title="Charger la base de donnees",
                filetypes=[("Fichiers texte", "*.txt")]
            )
    
            if not database_path:
                self.feedback.config(text="Erreur : Aucune base de donnees selectionnee.")
                return
    
            # Lire la base de donnees
            with open(database_path, 'r') as file:
                database = [line.strip() for line in file.readlines()]
    
            # Verifier si le code-barres est dans la base
            if self.decoded_barcode in database:
                messagebox.showinfo("Resultat", f"Produit trouve : {self.decoded_barcode}")
                self.feedback.config(text="Produit trouve dans la base.")
            else:
                messagebox.showwarning("Resultat", f"Produit non trouve : {self.decoded_barcode}")
                self.feedback.config(text="Produit non trouve dans la base.")
    
        except Exception as e:
            # Gestion des erreurs
            messagebox.showerror("Erreur", f"Erreur lors de la verification : {str(e)}")
            self.feedback.config(text="Erreur lors de la verification.")

    def reset_app(self):
        """Reinitialiser l'application."""
        self.image = None
        self.image_path = ""
        self.binary_signature = None
        self.decoded_barcode = None
        self.image_label.config(image="")
        self.feedback.config(text="Reinitialise.")

    def quit_app(self):
        """Quitter l'application."""
        self.feedback.config(text="Fermeture de l'application...")
        self.update_idletasks()
        self.destroy()  # Ferme la fenetre principale


if __name__ == "__main__":
    app = BarcodeApp()
    app.mainloop()