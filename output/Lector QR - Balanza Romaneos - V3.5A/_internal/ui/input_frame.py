import customtkinter as ctk

class InputFrame(ctk.CTkFrame):
    def __init__(self, parent, scan_callback):
        super().__init__(parent)
        self.scan_callback = scan_callback
        self.setup_ui()
    
    def setup_ui(self):
        ctk.CTkLabel(self, text="📷 Escanea el código QR:", font=("Roboto", 16)).pack(side="left", padx=(0, 10))
        
        self.entry = ctk.CTkEntry(self, width=400, height=40, font=("Roboto", 14))
        self.entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry.bind('<Return>', self.on_scan)
        
        ctk.CTkButton(
            self, 
            text="Escanear", 
            command=self.on_scan, 
            width=100, 
            height=40, 
            font=("Roboto", 14)
        ).pack(side="right")
    
    def on_scan(self, event=None):
        qr_text = self.entry.get()
        self.scan_callback(qr_text)
    
    def clear_entry(self):
        self.entry.delete(0, ctk.END)