import customtkinter as ctk

class ButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, clear_callback, copy_callback):
        super().__init__(parent)
        self.clear_callback = clear_callback
        self.copy_callback = copy_callback
        self.setup_ui()
    
    def setup_ui(self):
        self.btn_clear = ctk.CTkButton(
            self, 
            text="🗑 Limpiar Tabla", 
            command=self.clear_callback, 
            width=150, 
            height=40, 
            font=("Roboto", 14), 
            fg_color="red"
        )
        self.btn_clear.pack(side="left", padx=10, pady=5, expand=True, fill="x")
        
        self.btn_copy = ctk.CTkButton(
            self, 
            text="📋 Copiar Fila", 
            command=self.copy_callback, 
            width=150, 
            height=40, 
            font=("Roboto", 14), 
            fg_color="green"
        )
        self.btn_copy.pack(side="right", padx=10, pady=5, expand=True, fill="x")