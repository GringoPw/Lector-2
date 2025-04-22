import customtkinter as ctk
from tkinter import ttk
import re

class TableFrame(ctk.CTkFrame):
    def __init__(self, parent, update_callback):
        super().__init__(parent)
        self.update_callback = update_callback
        self.current_editor = None  # Track the current active editor
        self.setup_ui()
    
    def parse_qr_data(self, qr_string):
        """
        Parsea una cadena QR y maneja correctamente los valores negativos marcados con apóstrofe.
        Ejemplo: ]00000862]19'04'2025]5935]'119.00]5762.00]28.33]27]56908]
        """
        print(f"Parseando QR: {qr_string}")
        
        # Dividir por "]" y eliminar elementos vacíos
        parts = [p for p in qr_string.split("]") if p]
        
        if not parts:
            print("QR inválido: no se encontraron partes")
            return None
        
        # Extraer número de ticket (primer elemento)
        ticket_number = parts[0].strip()
        print(f"Número de ticket extraído: {ticket_number}")
        
        # Procesar los demás campos
        data = {}
        
        # Mapeo de índices a nombres de campos (ajustar según la estructura real del QR)
        field_mapping = {
            0: "ticket_number",
            1: "fecha",
            2: "otro_campo",
            3: "resto_agregado",  # Este es el campo que puede tener apóstrofe para negativos
            4: "nro_fdo_inicial",
            5: "nro_fdo_final",
            6: "cant_fardos",
            7: "fibra_bruta"
        }
        
        for i, part in enumerate(parts):
            if i in field_mapping:
                field_name = field_mapping[i]
                
                # Manejar valores con apóstrofe (negativos)
                if "'" in part and field_name in ["resto_agregado", "fibra_bruta"]:
                    # Reemplazar el apóstrofe por un signo menos
                    value = part.replace("'", "-")
                    print(f"Valor negativo detectado: {part} -> {value}")
                else:
                    value = part
                
                # Convertir a número si es posible
                try:
                    if "." in value:
                        data[field_name] = float(value)
                    elif value.replace("-", "").isdigit():
                        data[field_name] = int(value)
                    else:
                        data[field_name] = value
                except ValueError:
                    data[field_name] = value
        
        print(f"Datos parseados: {data}")
        return ticket_number, data
    
    def calculate_derived_values(self, values):
        """
        Calcula los valores derivados: FIBRA NETA y RINDE
        """
        try:
            # Índices de las columnas (ajustar si es necesario)
            fibra_bruta_idx = self.columns.index("FIBRA-BRUTA")
            resto_idx = self.columns.index("RESTO")
            agregado_idx = self.columns.index("AGREGADO")
            tara_fardo_idx = self.columns.index("TARA FARDO")
            fibra_neta_idx = self.columns.index("FIBRA NETA")
            rinde_idx = self.columns.index("RINDE")
            kg_netos_idx = self.columns.index("Kg Netos")
            rinde_semilla_idx = self.columns.index("RINDE SEMILLA")
            
            # Calcular FIBRA NETA = FIBRA BRUTA + RESTO - AGREGADO - TARA FARDO
            fibra_bruta = float(values[fibra_bruta_idx] or 0)
            resto = float(values[resto_idx] or 0)
            agregado = float(values[agregado_idx] or 0)
            tara_fardo = float(values[tara_fardo_idx] or 0)
            
            fibra_neta = fibra_bruta + resto - agregado - tara_fardo
            values[fibra_neta_idx] = round(fibra_neta, 2) if fibra_neta != 0 else ""
            
            # Calcular RINDE = (FIBRA NETA / KG NETOS) * 100
            kg_netos = float(values[kg_netos_idx] or 0)
            if kg_netos > 0:
                
                rinde = round((float(fibra_neta) / float(kg_netos)) / 1000 * 100 , 10)
                values[rinde_idx] = round(rinde, 2) if rinde != 0 else ""
                
                # Calcular RINDE SEMILLA = 100 - RINDE
                rinde_semilla = round(float(kg_netos) * 0.45, 2)
                values[rinde_semilla_idx] = round(rinde_semilla, 2) if rinde_semilla != 0 else ""
            else:
                values[rinde_idx] = ""
                values[rinde_semilla_idx] = ""
                
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error al calcular valores derivados: {e}")
        
        return values
    
    def find_and_update_row(self, ticket_number, qr_data):
        """
        Busca una fila por número de ticket y la actualiza con los datos del QR secundario.
        Retorna True si se encontró y actualizó, False en caso contrario.
        """
        print(f"Buscando ticket: {ticket_number}")
        print(f"Datos QR recibidos: {qr_data}")
        
        # Limpiar el número de ticket (eliminar ceros a la izquierda)
        clean_ticket = ticket_number.lstrip('0')
        print(f"Ticket limpio para búsqueda: {clean_ticket}")
        
        ticket_encontrado = False
        for item in self.tree.get_children():
            values = list(self.tree.item(item)["values"])
            if not values or len(values) == 0:
                continue
                
            # Obtener y limpiar el ticket de la fila (eliminar ceros a la izquierda)
            row_ticket = str(values[0]).strip().lstrip('0')
            print(f"Comparando con valores de fila: {row_ticket} (original: {values[0]})")
            
            # Comparar los tickets normalizados
            if row_ticket == clean_ticket:
                print("¡Ticket encontrado!")
                ticket_encontrado = True
                
                # Asegurarse de que todos los campos necesarios existen
                try:
                    # Actualizar los valores en la tabla
                    values[3] = qr_data.get("nro_fdo_inicial", values[3])  # Nº FDO INICIAL
                    values[4] = qr_data.get("nro_fdo_final", values[4])    # Nº FDO FINAL
                    values[5] = qr_data.get("cant_fardos", values[5])      # CANT.FDS.
                    
                    # Conversión segura de valores numéricos
                    values[6] = float(qr_data.get("fibra_bruta", values[6]) or 0)  # FIBRA-BRUTA
                    
                    # Manejo de resto y agregado
                    resto_agregado = float(qr_data.get("resto_agregado", 0))
                    if resto_agregado > 0:
                        values[7] = resto_agregado  # RESTO
                        values[8] = 0               # AGREGADO
                    else:
                        values[7] = 0               # RESTO
                        values[8] = abs(resto_agregado)  # AGREGADO
                    
                    # Calcular TARA FARDO (2 kg por fardo)
                    cant_fardos = int(qr_data.get("cant_fardos", values[5]) or 0)
                    values[9] = cant_fardos * 2
                    
                    # Calcular valores derivados (FIBRA NETA y RINDE)
                    values = self.calculate_derived_values(values)
                    
                    # Actualizar la fila con nuevos valores
                    self.tree.item(item, values=values)
                    
                    # Llamar al callback de actualización
                    self.update_callback(item, values)
                    
                    print("Fila actualizada exitosamente")
                    break
                
                except Exception as e:
                    print(f"Error al actualizar fila: {e}")
                    return False
        
        if not ticket_encontrado:
            print(f"No se encontró el ticket {ticket_number} en la tabla")
        
        return ticket_encontrado
    
    def process_qr_code(self, qr_string):
        """
        Procesa un código QR completo, extrae el número de ticket y los datos,
        y actualiza la fila correspondiente.
        """
        result = self.parse_qr_data(qr_string)
        if result:
            ticket_number, qr_data = result
            return self.find_and_update_row(ticket_number, qr_data)
        return False
    
    def setup_ui(self):
        self.columns = ("Nº Ticket", "Cliente", "Kg Netos", "Nº FDO INICIAL", "Nº FDO FINAL", "CANT.FDS.", 
                   "FIBRA-BRUTA", "RESTO", "AGREGADO", "TARA FARDO", "FIBRA NETA", "RINDE", "RINDE SEMILLA")
        
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=10)
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center", stretch=True)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)
        
        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.setup_style()
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=20, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#1a73e8')])  # Cambiado a azul como solicitado
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])
    
    def save_current_edit(self):
        """Guarda la edición actual si hay un editor activo"""
        if self.current_editor:
            entry, item, col_idx = self.current_editor
            value = entry.get()
            values = list(self.tree.item(item)["values"])
            
            column_name = self.columns[col_idx]
            if column_name in ["Nº FDO INICIAL", "Nº FDO FINAL"]:
                if value.isdigit():
                    values[col_idx] = int(value)
                    
                    inicial_idx = self.columns.index("Nº FDO INICIAL")
                    final_idx = self.columns.index("Nº FDO FINAL")
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
                    pass
            
            # Calcular valores derivados después de cualquier cambio
            values = self.calculate_derived_values(values)
            
            self.update_callback(item, values)
            self.tree.item(item, values=values)
            entry.destroy()
            self.current_editor = None
            return True
        return False
    
    def on_cell_click(self, event):
        # Primero guardar cualquier edición en curso
        self.save_current_edit()
        
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            column_name = self.tree.heading(column)["text"]
            
            editable_columns = ["Nº FDO INICIAL", "Nº FDO FINAL", "FIBRA-BRUTA", "RESTO", "AGREGADO"]
            if column_name in editable_columns:
                item = self.tree.selection()[0]
                col_idx = self.columns.index(column_name)
                
                x, y, w, h = self.tree.bbox(item, column)
                entry = ttk.Entry(self.tree, width=15)
                entry.place(x=x, y=y, width=w, height=h)
                
                # Obtener el valor actual y establecerlo en el entry
                current_value = self.tree.item(item)["values"][col_idx]
                entry.insert(0, current_value if current_value is not None else "")
                
                # Guardar referencia al editor actual
                self.current_editor = (entry, item, col_idx)
                
                def save_edit(event=None):
                    if self.current_editor and self.current_editor[0] == entry:
                        self.save_current_edit()
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
                            col = self.columns.index(editable_columns[0]) + 1
                            bbox = self.tree.bbox(next_item, f"#{col}")
                            if bbox:
                                new_event = type('Event', (), {'x': bbox[0] + 5, 'y': bbox[1] + 5})
                                self.on_cell_click(new_event)
                    else:
                        # Simular un clic en la siguiente columna editable
                        col = self.columns.index(next_col_name) + 1
                        bbox = self.tree.bbox(item, f"#{col}")
                        if bbox:
                            new_event = type('Event', (), {'x': bbox[0] + 5, 'y': bbox[1] + 5})
                            self.on_cell_click(new_event)
                    
                    return "break"
                
                entry.bind('<Return>', save_edit)
                entry.bind('<FocusOut>', save_edit)
                entry.bind('<Tab>', focus_next)
                entry.focus_set()
    
    def add_row(self, data):
        datos = data.split("\t")
        kg_netos = float(datos[15]) if len(datos) > 15 and datos[15] else 0
        
        valores = [datos[0], datos[4], kg_netos] + [""] * 10
        item = self.tree.insert("", "end", values=valores)
        return item
    
    def highlight_empty_fields(self, item):
        values = self.tree.item(item)["values"]
        editable_columns = ["Nº FDO INICIAL", "Nº FDO FINAL", "FIBRA-BRUTA", "RESTO", "AGREGADO"]
        for col in editable_columns:
            col_idx = self.columns.index(col)
            if not values[col_idx]:
                self.tree.item(item, tags=(f"empty_{col_idx}",))
                self.tree.tag_configure(f"empty_{col_idx}", background="red")
    
    def clear(self):
        # Asegurarse de destruir cualquier editor activo
        if self.current_editor:
            self.current_editor[0].destroy()
            self.current_editor = None
            
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def get_selection(self):
        return self.tree.selection()
    
    def get_item_values(self, item):
        return self.tree.item(item)["values"]
    
    def get_item_index(self, item):
        return self.tree.index(item)
