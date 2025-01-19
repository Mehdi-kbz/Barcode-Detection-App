#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 11:25:26 2024

code extraction

@author: Mehdi & Arif
"""





import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def cv2_to_imageTk(cv2_image):
    if len(cv2_image.shape) == 2:  # grayscale
        cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_GRAY2RGB)
    else:
        cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv2_image_rgb)
    image_tk = ImageTk.PhotoImage(image=pil_image)
    return image_tk

class ImageApp(tk.Tk):
    def __init__(self, image_path):
        super().__init__()
        self.title("Application de Traitement d'Image")
        self.points = []
        self.image_path = image_path
        self.load_image()
        self.setup_gui()

    def load_image(self):
        if not os.path.exists(self.image_path):
            messagebox.showerror("Erreur", f"L'image {self.image_path} n'existe pas!")
            self.destroy()
        else:
            self.cv_image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            if self.cv_image is None:
                messagebox.showerror("Erreur", "Impossible de charger l'image!")
                self.destroy()
            else:
                self.cv_image_color = cv2.cvtColor(self.cv_image, cv2.COLOR_GRAY2BGR)
                self.photo_image = cv2_to_imageTk(self.cv_image_color)

    def setup_gui(self):
        self.canvas = tk.Canvas(self, width=self.cv_image_color.shape[1], height=self.cv_image_color.shape[0])
        self.canvas.pack()
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.bind("<Button-1>", self.on_click)
        self.status_label = tk.Label(self, text="Selectionnez deux points sur l'image pour definir le rayon")
        self.status_label.pack()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_click(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        cv2.circle(self.cv_image_color, (x, y), 3, (0, 0, 255), -1)
        self.photo_image = cv2_to_imageTk(self.cv_image_color)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        if len(self.points) == 1:
            self.status_label.config(text="Premier point selectionne. Selectionnez le second point.")
        elif len(self.points) == 2:
            self.status_label.config(text="Deux points selectionnes. Traitement en cours...")
            self.canvas.unbind("<Button-1>")
            self.after(100, self.process_image)

    def process_image(self):
        p1, p2 = self.points
        # 1. Calculer la longueur du rayon
        longueur_rayon = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        print(f"Longueur du rayon: {longueur_rayon:.2f} pixels")

        # 2. Extraire la première signature
        nb_points = max(int(longueur_rayon), 95)
        t = np.linspace(0, 1, nb_points)
        x = np.array([p1[0] + (p2[0] - p1[0])*t_i for t_i in t], dtype=np.float32)
        y = np.array([p1[1] + (p2[1] - p1[1])*t_i for t_i in t], dtype=np.float32)
        signature = cv2.remap(self.cv_image, x.reshape(-1,1), y.reshape(-1,1), cv2.INTER_LINEAR)[:, 0]

        # 3. Calculer et appliquer le seuil d'Otsu
        hist, bins = np.histogram(signature, bins=256, range=(0, 256))
        total_pixels = signature.size
        sum_total = sum(i * h for i, h in enumerate(hist))

        max_criteria = -1
        threshold = 0
        criteria_values = []  # Pour stocker les valeurs du critère

        for k in range(256):
            w_b = sum(hist[:k])
            w_f = total_pixels - w_b

            if w_b == 0 or w_f == 0:
                criteria_values.append(0)
                continue

            sum_b = sum(i * hist[i] for i in range(k))
            m_b = sum_b / w_b if w_b != 0 else 0
            m_f = (sum_total - sum_b) / w_f if w_f != 0 else 0

            criteria = w_b * w_f * (m_b - m_f) ** 2
            criteria_values.append(criteria)

            if criteria > max_criteria:
                max_criteria = criteria
                threshold = k

        print(f"Seuil d'Otsu calcule : {threshold}")

        # 4. Binariser la première signature
        binary_signature = (signature > threshold).astype(np.uint8)

        # 5. Trouver les limites utiles
        non_zero = np.nonzero(binary_signature)[0]
        if len(non_zero) > 0:
            start_idx = non_zero[0]
            end_idx = non_zero[-1]
            print(f"Limites utiles : {start_idx} à {end_idx}")

            # 6. Calculer les coordonnees des points du rayon utile
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

            # 7. Calculer l'unite de base u
            useful_length = np.sqrt((useful_p2[0] - useful_p1[0])**2 +
                                    (useful_p2[1] - useful_p1[1])**2)
            u = max(1, int(useful_length / 95))
            print(f"Unite de base u calculee : {u}")

            # 8. Extraire la nouvelle signature le long du rayon utile
            nb_points_final = 95 * u
            t = np.linspace(0, 1, nb_points_final)
            x = np.array([useful_p1[0] + (useful_p2[0] - useful_p1[0])*t_i for t_i in t], dtype=np.float32)
            y = np.array([useful_p1[1] + (useful_p2[1] - useful_p1[1])*t_i for t_i in t], dtype=np.float32)
            final_signature = cv2.remap(self.cv_image, x.reshape(-1,1), y.reshape(-1,1), cv2.INTER_LINEAR)[:, 0]

            # 9. Binariser la signature finale
            final_binary_signature = (final_signature > threshold).astype(np.uint8)

            # Affichage des resultats
            self.display_plots(signature, binary_signature, final_signature, final_binary_signature, nb_points_final, criteria_values)
            len_sin=len(final_binary_signature)
            print(f"Taille signature : {len_sin}")
            print(final_binary_signature)

            # Afficher l'image avec les rayons
            cv2.line(self.cv_image_color, p1, p2, (0, 255, 0), 1)  # Rayon initial en vert
            cv2.line(self.cv_image_color,
                    (int(useful_p1[0]), int(useful_p1[1])),
                    (int(useful_p2[0]), int(useful_p2[1])),
                    (255, 0, 0), 2)  # Rayon utile en bleu

            self.photo_image = cv2_to_imageTk(self.cv_image_color)
            self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
            self.status_label.config(text="Traitement termine.")
        else:
            print("Aucune region utile trouvee dans la signature")
            messagebox.showinfo("Information", "Aucune region utile trouvee dans la signature")
            self.status_label.config(text="Aucune region utile trouvee dans la signature.")

    def display_plots(self, signature, binary_signature, final_signature, final_binary_signature, nb_points_final, criteria_values):
        plot_window = tk.Toplevel(self)
        plot_window.title("Resultats")
        fig = plt.Figure(figsize=(8, 12))  # Ajuster la taille pour 5 subplots
        ax1 = fig.add_subplot(511)
        ax1.plot(signature)
        ax1.set_title('Première signature')
        ax1.grid(True)

        ax2 = fig.add_subplot(512)
        ax2.step(range(len(binary_signature)), binary_signature, where='mid')
        ax2.set_title('Première signature binarisee')
        ax2.grid(True)

        ax3 = fig.add_subplot(513)
        ax3.plot(final_signature)
        ax3.set_title(f'Signature finale ({nb_points_final} points)')
        ax3.grid(True)

        ax4 = fig.add_subplot(514)
        ax4.step(range(len(final_binary_signature)), final_binary_signature, where='mid')
        ax4.set_title('Signature finale binarisee')
        ax4.grid(True)

        ax5 = fig.add_subplot(515)
        ax5.plot(range(256), criteria_values)
        ax5.set_title('Critère d\'Otsu en fonction du seuil')
        ax5.set_xlabel('Seuil')
        ax5.set_ylabel('Critère')
        ax5.grid(True)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def on_closing(self):
        plt.close('all')
        self.destroy()

if __name__ == "__main__":
    chemin_image = 'images/barpreview.png'
    app = ImageApp(chemin_image)
    app.mainloop()
