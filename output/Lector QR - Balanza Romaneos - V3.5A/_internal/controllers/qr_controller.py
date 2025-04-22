      
import pyperclip
from qr_processor import process_qr, format_data
from utils import cargar_configuracion

class QRController:
    def __init__(self, qr_data_model):
        self.qr_data = qr_data_model
    
    def process_qr(self, qr_text):
        # Esta función llama a process_qr del módulo qr_processor
        # La función process_qr detecta automáticamente el tipo de QR y
        # llama a process_second_qr si es necesario
        result = process_qr(qr_text)
        
        # Si no hay error, guardamos los datos
        if not result.startswith("⚠️"):
            datos = result.split("\t")
            self.qr_data.add_data(datos)
        return result
    
    def process_secondary_qr(self, qr_text, table_frame):
        """
        Procesa un QR secundario y actualiza la fila correspondiente en la tabla.
        Retorna un mensaje de éxito o error.
        """
        from qr_processor import process_qr_type2
        
        # Dividir el texto por ']' para obtener los campos
        qr_fields = qr_text.split(']')
        
        # Procesar el QR secundario
        result = process_qr_type2(qr_text, qr_fields)
        
        if "error" not in result:
            # Buscar y actualizar la fila correspondiente
            ticket_encontrado = table_frame.find_and_update_row(result["nro_ticket"], result)
            
            if ticket_encontrado:
                return f"✅ Datos del ticket {result['nro_ticket']} actualizados correctamente."
            else:
                return f"⚠️ No se encontró el ticket {result['nro_ticket']} en la tabla."
        else:
            return result["error"]
    
    def update_calculations(self, item, values):
        values[10] = self.calculate_fibra_neta(values)
        kg_netos = values[2]
        values[11] = self.calculate_rinde(values[10], kg_netos)
        values[12] = self.calculate_rinde_semilla(kg_netos)
        return values
    
    def calculate_fibra_neta(self, values):
        try:
            fibra_bruta = float(str(values[6]) or 0)
            resto = float(str(values[7]) or 0)
            agregado = float(str(values[8]) or 0)
            tara_fardo = float(str(values[9]) or 0)
            fibra_neta = fibra_bruta + resto - agregado - tara_fardo
            return round(fibra_neta, 2)
        except (ValueError, TypeError):
            return ""
    
    def calculate_rinde(self, fibra_neta, kg_netos):
        try:
            if fibra_neta and kg_netos:
                return round((float(fibra_neta) / float(kg_netos)) / 1000 * 100, 10)
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
    
    def copy_row_to_clipboard(self, selection, get_values_func, get_index_func):
        item = selection[0]
        index = get_index_func(item)
        selected_data = self.qr_data.get_data(index)
        current_values = get_values_func(item)
        
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
        return True
    
    def clear_data(self):
        self.qr_data.clear()