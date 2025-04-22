import customtkinter as ctk
from tkinter import ttk

class TableFrame(ctk.CTkFrame):
    def __init__(self, parent, update_callback):
        super().__init__(parent)
        self.update_callback = update_callback
        self.setup_ui()
    
    def find_and_update_row(self, ticket_number, qr_data):
        """
        Busca una fila por número de ticket y la actualiza con los datos del QR secundario.
        Retorna True si se encontró y actualizó, False en caso contrario.
        """
        print(f"Buscando ticket: {ticket_number}")
        print(f"Datos QR recibidos: {qr_data}")
        
        ticket_encontrado = False
        for item in self.tree.get_children():
            values = list(self.tree.item(item)["values"])
            print(f"Comparando con valores de fila: {values[0]}")
            
            # Convertir ambos a string para comparación segura
            if str(values[0]).strip() == str(ticket_number).strip():
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
                    values = self.update_callback(item, values)
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
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])
    
    def on_cell_click(self, event):
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
                entry.insert(0, self.tree.item(item)["values"][col_idx])
                
                def save_edit(event=None):
                    value = entry.get()
                    values = list(self.tree.item(item)["values"])
                    
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
                            entry.destroy()
                            return
                    
                    self.update_callback(item, values)
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
                            col = self.columns[self.columns.index(editable_columns[0])]
                            bbox = self.tree.bbox(next_item, col)
                            if bbox:
                                event.x = bbox[0] + 5
                                event.y = bbox[1] + 5
                                self.on_cell_click(event)
                    else:
                        # Simular un clic en la siguiente columna editable
                        col = self.columns[self.columns.index(next_col_name)]
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
    
    def add_row(self, data):
        datos = data.split("\t")
        kg_netos = float(datos[15]) if datos[15] else 0
        
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
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def get_selection(self):
        return self.tree.selection()
    
    def get_item_values(self, item):
        return self.tree.item(item)["values"]
    
    def get_item_index(self, item):
        return self.tree.index(item)
    
    