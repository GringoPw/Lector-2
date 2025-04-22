import customtkinter as ctk
from tkinter import ttk, messagebox
import pyperclip
from qr_processor import process_qr, format_data, process_second_qr
from utils import cargar_configuracion

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector de QR - Ticket B - JP 2025")
        self.root.geometry("1400x800")
        self.setup_ui()
        self.datos_escaneados = []

    def setup_ui(self):
        self.create_input_frame()
        self.create_table()
        self.create_button_frame()

    def create_input_frame(self):
        frame_input = ctk.CTkFrame(self.root)
        frame_input.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(frame_input, text="📷 Escanea el código QR:", font=("Roboto", 16)).pack(side="left", padx=(0, 10))
        self.entry = ctk.CTkEntry(frame_input, width=400, height=40, font=("Roboto", 14))
        self.entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entry.bind('<Return>', self.scan_qr)

        ctk.CTkButton(frame_input, text="Escanear", command=self.scan_qr, width=100, height=40, font=("Roboto", 14)).pack(side="right")

    def create_table(self):
        self.table_frame = ctk.CTkFrame(self.root)
        self.table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Nº Ticket", "Cliente", "Kg Netos", "Nº FDO INICIAL", "Nº FDO FINAL", "CANT.FDS.", 
                   "FIBRA-BRUTA", "RESTO", "AGREGADO", "TARA FARDO", "FIBRA NETA", "RINDE", "RINDE SEMILLA")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center", stretch=True)

        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)

        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=20, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

    def cargar_configuracion(archivo="config.txt"):
        configuracion = {}
        try:
            with open(archivo, "r", encoding="utf-8") as file:
                for linea in file:
                    linea = linea.strip()
                    if "=" in linea:
                        columna, formula = linea.split("=", 1)
                        configuracion[columna.strip()] = formula.strip()
        except FileNotFoundError:
            print("⚠️ Archivo de configuración no encontrado. Se usarán valores por defecto.")
        return configuracion

    def create_button_frame(self):
        frame_buttons = ctk.CTkFrame(self.root)
        frame_buttons.pack(pady=10, padx=20, fill="x")

        self.btn_clear = ctk.CTkButton(frame_buttons, text="🗑 Limpiar Tabla", command=self.clear_table, width=150, height=40, font=("Roboto", 14), fg_color="red")
        self.btn_clear.pack(side="left", padx=10, pady=5, expand=True, fill="x")

        self.btn_copy = ctk.CTkButton(frame_buttons, text="📋 Copiar Fila", command=self.copy_selected_row, width=150, height=40, font=("Roboto", 14), fg_color="green")
        self.btn_copy.pack(side="right", padx=10, pady=5, expand=True, fill="x")

    def on_cell_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            column_name = self.tree.heading(column)["text"]
            
            editable_columns = ["Nº FDO INICIAL", "Nº FDO FINAL", "FIBRA-BRUTA", "RESTO", "AGREGADO"]
            if column_name in editable_columns:
                item = self.tree.selection()[0]
                col_idx = self.tree["columns"].index(column_name)
                
                x, y, w, h = self.tree.bbox(item, column)
                entry = ttk.Entry(self.tree, width=15)
                entry.place(x=x, y=y, width=w, height=h)
                entry.insert(0, self.tree.item(item)["values"][col_idx])

                def save_edit(event=None):
                    value = entry.get()
                    values = list(self.tree.item(item)["values"])
                    
                    if column_name in ["Nº FDO INICIAL", "Nº FDO FINAL"]:
                        if value.isdigit():
                            values[col_idx] = int(value)
                            
                            inicial_idx = self.tree["columns"].index("Nº FDO INICIAL")
                            final_idx = self.tree["columns"].index("Nº FDO FINAL")
                            if values[inicial_idx] and values[final_idx]:
                                try:
                                    cant_fds = int(values[final_idx]) - int(values[inicial_idx]) + 1
                                    values[5] = cant_fds  # CANT.FDS.
                                    values[9] = cant_fds * 2  # TARA FARDO
                                except (ValueError, TypeError):
                                    pass
                    else:  # Columnas de fibra
                        try:
                            values[col_idx] = float(value) if value else ""
                        except ValueError:
                            entry.destroy()
                            return
                    
                    self.update_calculations(item, values)
                    entry.destroy()
                    return "break"

                def focus_next(event):
                    save_edit()
                    
                    # Encontrar el siguiente campo editable
                    current_col_index = editable_columns.index(column_name)
                    next_col_index = (current_col_index + 1) % len(editable_columns)
                    next_col_name = editable_columns[next_col_index]
                    
                    # Si estamos en el último campo editable, mover a la siguiente fila
                    if next_col_index == 0:
                        next_item = self.tree.next(item)
                        if next_item:
                            self.tree.selection_set(next_item)
                            self.tree.focus(next_item)
                            # Simular un clic en la primera columna editable de la nueva fila
                            col = self.tree["columns"][self.tree["columns"].index(editable_columns[0])]
                            bbox = self.tree.bbox(next_item, col)
                            if bbox:
                                event.x = bbox[0] + 5
                                event.y = bbox[1] + 5
                                self.on_cell_click(event)
                    else:
                        # Simular un clic en la siguiente columna editable
                        col = self.tree["columns"][self.tree["columns"].index(next_col_name)]
                        bbox = self.tree.bbox(item, col)
                        if bbox:
                            event.x = bbox[0] + 5
                            event.y = bbox[1] + 5
                            self.on_cell_click(event)
                    
                    return "break"

                entry.bind('<Return>', save_edit)
                entry.bind('<FocusOut>', save_edit)
                entry.bind('<Tab>', focus_next)
                entry.focus()
    
    def scan_qr(self, event=None):
        qr_text = self.entry.get()
        if not qr_text:
            messagebox.showwarning("Advertencia", "⚠️ Ingresa un código QR válido.")
            return

        # Determinar el tipo de QR basado en su formato
        if qr_text.count(']') >= 20:  # QR original (largo)
            self.process_primary_qr(qr_text)
        elif qr_text.count(']') >= 8:  # QR secundario (corto)
            self.process_secondary_qr(qr_text)
        else:
            messagebox.showerror("Error", "⚠️ Formato de QR no reconocido.")
        
        self.entry.delete(0, ctk.END)

    def process_primary_qr(self, qr_text):
        """Procesa el QR primario (original)."""
        result = process_qr(qr_text)
        if not result.startswith("⚠️"):
            datos = result.split("\t")
            kg_netos = float(datos[15]) if datos[15] else 0
            
            valores = [datos[0], datos[4], kg_netos] + [""] * 10
            item = self.tree.insert("", "end", values=valores)
            self.datos_escaneados.append(datos)
            
            self.highlight_empty_fields(item)
        else:
            messagebox.showerror("Error", result)

    def process_secondary_qr(self, qr_text):
        """Procesa el QR secundario y actualiza la fila correspondiente."""
        result = process_second_qr(qr_text)
        if "error" not in result:
            # Buscar el ticket en la tabla
            ticket_encontrado = False
            for item in self.tree.get_children():
                values = list(self.tree.item(item)["values"])
                if str(values[0]) == str(result["nro_ticket"]):
                    ticket_encontrado = True
                    
                    # Actualizar los valores en la tabla
                    values[3] = result["nro_fdo_inicial"]  # Nº FDO INICIAL
                    values[4] = result["nro_fdo_final"]    # Nº FDO FINAL
                    values[5] = result["cant_fardos"]      # CANT.FDS.
                    values[6] = float(result["fibra_bruta"])  # FIBRA-BRUTA
                    
                    # Determinar si resto_agregado es resto o agregado
                    resto_agregado = float(result["resto_agregado"])
                    if resto_agregado > 0:
                        values[7] = resto_agregado  # RESTO
                        values[8] = 0               # AGREGADO
                    else:
                        values[7] = 0               # RESTO
                        values[8] = abs(resto_agregado)  # AGREGADO
                    
                    # Calcular TARA FARDO (2 kg por fardo)
                    values[9] = int(result["cant_fardos"]) * 2
                    
                    # Actualizar cálculos
                    self.update_calculations(item, values)
                    
                    messagebox.showinfo("Éxito", f"✅ Datos del ticket {result['nro_ticket']} actualizados correctamente.")
                    break
            
            if not ticket_encontrado:
                messagebox.showwarning("Advertencia", f"⚠️ No se encontró el ticket {result['nro_ticket']} en la tabla.")
        else:
            messagebox.showerror("Error", result["error"])

    def highlight_empty_fields(self, item):
        values = self.tree.item(item)["values"]
        editable_columns = ["Nº FDO INICIAL", "Nº FDO FINAL", "FIBRA-BRUTA", "RESTO", "AGREGADO"]
        for col in editable_columns:
            col_idx = self.tree["columns"].index(col)
            if not values[col_idx]:
                self.tree.item(item, tags=(f"empty_{col_idx}",))
                self.tree.tag_configure(f"empty_{col_idx}", background="red")

    def update_calculations(self, item, values):
        values[10] = self.calculate_fibra_neta(values)
        kg_netos = values[2]
        values[11] = self.calculate_rinde(values[10], kg_netos)
        values[12] = self.calculate_rinde_semilla(kg_netos)
        
        self.tree.item(item, values=values)
        self.highlight_empty_fields(item)

    def calculate_fibra_neta(self, values):
        try:
            fibra_bruta = float(str(values[6]) or 0)
            resto = float(str(values[7]) or 0)
            agregado = float(str(values[8]) or 0)
            tara_fardo = float(str(values[9]) or 0)
            fibra_neta = fibra_bruta + resto - agregado - tara_fardo
            print(fibra_neta)
            return round(fibra_neta, 2)
        except (ValueError, TypeError):
            return ""

    def calculate_rinde(self, fibra_neta, kg_netos):
        try:
            if fibra_neta and kg_netos:
                return round((float(fibra_neta) / float(kg_netos)) / 1000 * 100 , 10)
            return ""
        except (ValueError, TypeError, ZeroDivisionError):
            return ""

    def calculate_rinde_semilla(self, kg_netos):
        try:
            if kg_netos:
                return round(float(kg_netos) * 0.45, 2)
            return ""
        except (ValueError, TypeError):
            return ""

    def copy_selected_row(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "⚠️ Por favor, selecciona una fila para copiar.")
            return
        
        item = selection[0]
        index = self.tree.index(item)
        selected_data = self.datos_escaneados[index]
        current_values = self.tree.item(item)["values"]
        
        # Crear una copia de los datos base y asegurarse de que sea una lista
        modified_data = list(selected_data)
        
        # Formatear los datos según la estructura esperada por format_data
        formatted_data = []
        for i, value in enumerate(modified_data):
            if isinstance(value, (float, int)):
                formatted_data.append(f"{value:.2f}")
            else:
                formatted_data.append(str(value))
        
        # Obtener columnas y filas base
        columnas, filas = format_data([formatted_data])
        fila = filas[0]
        
        # Mapear los valores adicionales a las columnas correspondientes
        config_formulas = cargar_configuracion()

        columnas_adicionales = {
            "Nº FDO INIC": current_values[3],
            "Nº FDO FINAL": current_values[4],
            "CANT.FDS.": current_values[5],
            "FIBRA-BRUTA": current_values[6],
            "RESTO": current_values[7],
            "AGREGADO": current_values[8],
            "TARA FARDO": current_values[9],
        } 
        """  "RINDE": current_values[11], """
        """  "RINDE SEMILLA(KGRS)": current_values[12] """
        """ "FIBRA NETA": current_values[10], """

        for columna, formula in config_formulas.items():
            if columna not in columnas_adicionales or columnas_adicionales[columna] in [None, ""]:
                if formula.startswith("="):  # Si es una fórmula de Excel
                    columnas_adicionales[columna] = formula  
                else:  
                    try:
                        columnas_adicionales[columna] = float(formula) if formula.replace(".", "", 1).isdigit() else formula
                    except ValueError:
                        columnas_adicionales[columna] = formula  # Si no es número, dejar el string original


        
        # Actualizar la fila con los valores adicionales
        for i, columna in enumerate(columnas):
            if columna in columnas_adicionales:
                valor = columnas_adicionales[columna]
                if valor != "":
                    if isinstance(valor, (float, int)):
                        fila[i] = f"{valor:.2f}"
                    else:
                        fila[i] = str(valor)
        
        # Convertir a texto para Excel
        text_for_excel = "\t".join(map(str, fila))
        
        # Copiar al portapapeles
        pyperclip.copy(text_for_excel)
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", "✅ Datos copiados al portapapeles correctamente.")

    def show_copy_tooltip(self, text):
        tooltip = ctk.CTkToplevel(self.root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{self.root.winfo_pointerx()}+{self.root.winfo_pointery()}")
        
        label = ctk.CTkLabel(tooltip, text="¡Datos copiados al portapapeles!", wraplength=300)
        label.pack(padx=10, pady=10)
        
        self.root.after(3000, tooltip.destroy)  # Cerrar después de 3 segundos

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.datos_escaneados.clear()
        messagebox.showinfo("Éxito", "✅ Tabla limpiada exitosamente.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = QRApp(root)
    root.mainloop()