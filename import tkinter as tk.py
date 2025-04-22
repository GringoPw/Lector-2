import tkinter as tk

class SizeTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Seguimiento de Tamaño")

        # Label para mostrar el tamaño
        self.label = tk.Label(self.root, text="", font=("Arial", 20))
        self.label.pack(expand=True)

        # Vincular el evento de cambio de tamaño
        self.root.bind("<Configure>", self.update_size)

        self.root.mainloop()

    def update_size(self, event):
        # Solo actualiza si el evento viene del redimensionamiento de la ventana principal
        if event.widget == self.root:
            ancho = self.root.winfo_width()
            alto = self.root.winfo_height()
            self.label.config(text=f"Ancho: {ancho} px\nAlto: {alto} px")

SizeTrackerApp()
