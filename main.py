import customtkinter as ctk
from tkinter import messagebox
from ui.input_frame import InputFrame
from ui.table_frame import TableFrame
from ui.button_frame import ButtonFrame
from models.qr_data import QRData
from controllers.qr_controller import QRController

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector de QR - Ticket B - JP 2025 - 3.5B")
        self.root.geometry("1400x800")
        
        # Model
        self.qr_data = QRData()
        
        # Controller
        self.controller = QRController(self.qr_data)
        
        # UI Components
        self.setup_ui()
        
    def setup_ui(self):
        # Input frame
        self.input_frame = InputFrame(self.root, self.scan_qr)
        self.input_frame.pack(pady=20, padx=20, fill="x")
        
        # Table frame
        self.table_frame = TableFrame(self.root, self.controller.update_calculations)
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Button frame
        self.button_frame = ButtonFrame(
            self.root, 
            self.clear_table, 
            self.copy_selected_row
        )
        self.button_frame.pack(pady=10, padx=20, fill="x")
    
    def scan_qr(self, qr_text):
        if not qr_text:
            messagebox.showwarning("Advertencia", "⚠️ Ingresa un código QR válido.")
            return
        
        # Detectar el tipo de QR basado en la cantidad de campos
        qr_fields = qr_text.split(']')
        num_fields = len(qr_fields)
        
        if num_fields >= 9 and num_fields < 21:
            # Es un QR secundario, debe actualizar una fila existente
            result = self.controller.process_secondary_qr(qr_text, self.table_frame)
            if result.startswith("✅"):
                messagebox.showinfo("Éxito", result)
                self.input_frame.clear_entry()
            elif result.startswith("⚠️"):
                messagebox.showwarning("Advertencia", result)
            else:
                messagebox.showerror("Error", result)
        else:
            # Es un QR primario o de otro tipo, procesar normalmente
            result = self.controller.process_qr(qr_text)
            if not result.startswith("⚠️"):
                item = self.table_frame.add_row(result)
                self.input_frame.clear_entry()
                self.table_frame.highlight_empty_fields(item)
            else:
                messagebox.showerror("Error", result)
    
    def clear_table(self):
        self.table_frame.clear()
        self.controller.clear_data()
        messagebox.showinfo("Éxito", "✅ Tabla limpiada exitosamente.")
    
    def copy_selected_row(self):
        selection = self.table_frame.get_selection()
        if not selection:
            messagebox.showwarning("Advertencia", "⚠️ Por favor, selecciona una fila para copiar.")
            return
        
        success = self.controller.copy_row_to_clipboard(
            selection, 
            self.table_frame.get_item_values,
            self.table_frame.get_item_index
        )
        
        if success:
            messagebox.showinfo("Éxito", "✅ Datos copiados al portapapeles correctamente.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = QRApp(root)
    root.mainloop()