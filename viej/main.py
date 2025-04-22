# main.py
import customtkinter as ctk
from gui import QRApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    root = ctk.CTk()
    app = QRApp(root)
    root.mainloop()