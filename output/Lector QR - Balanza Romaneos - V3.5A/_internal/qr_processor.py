def process_qr(qr_text):
    """
    Procesa el texto del código QR y devuelve los datos formateados.
    Detecta el tipo de QR basado en la cantidad de campos:
    - Tipo 1: >= 21 campos
    - Tipo 2: >= 9 y < 21 campos
    """
    print(f"Procesando QR: {qr_text[:30]}...")  # Imprimir para depuración
    
    # Dividir el texto por ']' para contar campos
    qr_fields = qr_text.split(']')
    num_fields = len(qr_fields)
    
    print(f"Número de campos detectados: {num_fields}")
    
    # Determinar el tipo de QR basado en la cantidad de campos
    if num_fields >= 21:
        print("Detectado QR de tipo 1 (>= 21 campos)")
        """Procesa el QR de tipo 1 (formato completo)."""
    try:
        # Aquí va el código original de procesamiento
        nro_ticket_balanza = qr_fields[1].strip()  # Ticket de balanza
        fecha = qr_fields[2].strip()  # Fecha (dd-mm-yy)
        sucursal = qr_fields[3].strip()
        sucursales = {"0000": "VILLA ANGELA", "0004": "MARFRA", "0002": "FIBRAL", "PRESIDENCIA ROQUE SAENZ PEæA": "FIBRAL"}
        sucursal = sucursales.get(sucursal, sucursal)
        desmote = qr_fields[4].strip()  # Desmote
        cliente = qr_fields[5].strip()  # Cliente
        productor = qr_fields[6].strip()  # Productor
        cliente_cuit = qr_fields[7].strip()  # CUIT Cliente
        transportista_nro_remito = qr_fields[8].strip()  # Remito (puede contener "DTV")
        transporte = qr_fields[9].strip()  # Transporte
        nombre_chofer = qr_fields[10].strip()  # Chofer
        dni_chofer = qr_fields[11].strip()  # DNI Chofer
        patente_chasis = qr_fields[12].strip()  # Patente Chasis
        patente_acoplado = qr_fields[13].strip()  # Patente Acoplado
        
        try:
            fibra_bruta = float(qr_fields[14].strip()) / 1000  # Convertir kg a toneladas
            tara = float(qr_fields[15].strip()) / 1000  # Convertir kg a toneladas
            fibra_neta = round(fibra_bruta - tara, 2)  # Calcular Fibra Neta correctamente

            # Formatear los valores con coma como separador decimal
            fibra_bruta = f"{fibra_bruta:.2f}"
            tara = f"{tara:.2f}"
            fibra_neta = f"{fibra_neta:.2f}"

        except ValueError:
            fibra_bruta, tara, fibra_neta = "error", "error", "error"

        tipo_semilla = qr_fields[16].strip()
        tipo_de_cosecha = qr_fields[17].strip()  # Tipo de Cosecha
        provincia_procedencia = qr_fields[18].strip()  # Provincia
        localidad_procedencia = qr_fields[19].strip()  # Procedencia
        presentacion = qr_fields[20].strip()  # Presentación

        return "\t".join([
            nro_ticket_balanza, fecha, sucursal, desmote, cliente, productor,
            cliente_cuit, transportista_nro_remito, transporte, nombre_chofer,
            dni_chofer, patente_chasis, patente_acoplado, fibra_bruta,
            tara, fibra_neta, tipo_semilla,
            tipo_de_cosecha, provincia_procedencia, localidad_procedencia, presentacion
        ])
    except (IndexError, ValueError) as e:
        return f"⚠️ Error al procesar QR tipo 1: {e}"
    except Exception as e:
        return f"⚠️ Error al procesar el código QR tipo 1: {str(e)}"
        

def process_qr_type2(qr_text, qr_fields):
    """Procesa el QR de tipo 2 (formato corto)."""
    try:
        # Limpiamos los campos (eliminamos espacios y caracteres no deseados)
        qr_fields = [field.strip() for field in qr_fields]
        
        # Imprimir campos para depuración
        for i, field in enumerate(qr_fields):
            print(f"Campo {i}: '{field}'")
        
        # Eliminar ceros iniciales del número de ticket
        nro_ticket = qr_fields[1].lstrip('0')
        
        # Formatear la fecha (cambiar ' por /)
        fecha_desmote = qr_fields[2].replace("'", "/")
        
        # Extraer los demás campos
        fibra_bruta = qr_fields[3]
        resto_agregado = qr_fields[4].replace("'", "-")
        fibra_neta = qr_fields[5]
        rinde = qr_fields[6]
        cant_fardos = qr_fields[7]
        nro_fdo_inicial = qr_fields[8]
        
        # Calcular número de fardo final
        try:
            nro_fdo_final = int(nro_fdo_inicial) + int(cant_fardos) - 1
        except (ValueError, TypeError):
            nro_fdo_final = ""
        
        return {
            "nro_ticket": nro_ticket,
            "fecha_desmote": fecha_desmote,
            "fibra_bruta": fibra_bruta,
            "resto_agregado": resto_agregado,
            "fibra_neta": fibra_neta,
            "rinde": rinde,
            "cant_fardos": cant_fardos,
            "nro_fdo_inicial": nro_fdo_inicial,
            "nro_fdo_final": str(nro_fdo_final)
        }
    except (IndexError, ValueError) as e:
        return {"error": f"⚠️ Error al procesar QR tipo 2: {e}"}
    except Exception as e:
        return {"error": f"⚠️ Error al procesar el código QR tipo 2: {str(e)}"}



def extract_date(fecha_str):
    try:
        if '-' in fecha_str:
            dia, mes, anio = fecha_str.split('-')
            if len(anio) == 2:
                anio = '20' + anio
        elif '/' in fecha_str:
            dia, mes, anio = fecha_str.split('/')
        else:
            return "", "", ""
        
        return str(int(dia)), str(int(mes)), str(anio)
    except (ValueError, IndexError):
        return "", "", ""

def has_dtv(numero_remito):
    return "SI" if isinstance(numero_remito, str) and "DTV" in numero_remito.upper() else "NO"

def format_data(datos_escaneados):
    columnas = [
        "DESMOTADORA", "DIA", "MES", "AÑO", "DESMOTE", "MES2", "CLIENTE", "PRODUCTOR", "CUIT",
        "FECHA DE REMITO", "Nº RTO", "Nº TICKET", "Nº TICKET FIBRAL", "TPTE", "CHOFER", "DNI CHOFER",
        "P/CH", "P/ACOP", "ALGODÓN EN BRUTO TN", "TARA", "ALGODÓN NETO EN TN", "RINDE", "GRADO",
        "PRECIOS", "BASE", "TOTAL A PAGAR", "AJUSTES", "DESCUENTO (Fl+C)", "ANTICIPO", "SALDO",
        "TC BILL VEND", "CARGA USD", "IMPORTE A PAGAR CARGADOR", "ANTICIPOS", "SALDO A PAGAR CARGADORES",
        "CARGADOR", "FECHA DE PAGO DE CARGADORES", "TARIFA FLETES", "NETO FLETES", "IVA", "FLETE A PAGAR",
        "FACTURADO A:", "FACTURA FLETE", "ANTICIPO3", "SALDO A PAGAR FLETES", "PAGO DE FLETES",
        "VARIEDAD SEMILLA", "RINDE SEMILLA(KGRS)", "MES DE LIQUIDACION", "NºLIQUIDACION", "DTV", "GUIA",
        "NN", "IMPORTE S/IVA", "IVA4", "RETENCIONES", "IMPORTE LIQUIDACION", "Nº FACT. FIBRA",
        "PRECIO/Un.*TN FIBRA", "FIBRA-BRUTA", "RESTO", "AGREGADO", "TARA FARDO", "FIBRA NETA",
        "Nº FDO INIC", "Nº FDO FINAL", "CANT.FDS.", "MES CIERRE DESMOTE", "FACT. DESMOTE", "MONTO",
        "G.NUM", "P.LONG", "P.RESIST.", "P. MIKE", "ELIM.MTRAS.", "CONTAMINADO", "OBSERVACIONES/Variedad",
        "TIPO COSECHA", "PROVINCIA", "PROCEDENCIA", "PRESENTACION"
    ]

    mapeo_columnas = {
        "DESMOTADORA": 2,
        "DIA": lambda fila: extract_date(fila[1])[0],
        "MES": lambda fila: extract_date(fila[1])[1],
        "AÑO": lambda fila: extract_date(fila[1])[2],
        "DESMOTE": 3,
        "MES2": lambda fila: extract_date(fila[1])[1],
        "CLIENTE": 4,
        "PRODUCTOR": 5,
        "CUIT": 6,
        "FECHA DE REMITO": 1,
        "Nº RTO": 7,
        "Nº TICKET": 0,
        "Nº TICKET FIBRAL": lambda fila: "",
        "TPTE": 8,
        "CHOFER": 9,
        "DNI CHOFER": 10,
        "P/CH": 11,
        "P/ACOP": 12,
        "ALGODÓN EN BRUTO TN": 13,
        "TARA": 14,
        "ALGODÓN NETO EN TN": 15,
        "DTV": lambda fila: has_dtv(fila[7]),
        "VARIEDAD SEMILLA": 16,
        "TIPO COSECHA": 17,
        "PROVINCIA": 18,
        "PROCEDENCIA": 19,
        "PRESENTACION": 20
    }

    filas_formateadas = []
    for fila in datos_escaneados:
        fila_ordenada = []
        for col in columnas:
            if col in mapeo_columnas:
                valor = mapeo_columnas[col]
                if callable(valor):
                    fila_ordenada.append(valor(fila))
                elif isinstance(valor, int) and valor < len(fila):
                    fila_ordenada.append(fila[valor])
                else:
                    fila_ordenada.append("")
            else:
                fila_ordenada.append("")
        filas_formateadas.append(fila_ordenada)

    return columnas, filas_formateadas


def format_second_qr_to_tab(qr_data):
    """Convierte los datos del QR secundario a formato tabulado para mantener compatibilidad."""
    # Creamos un array con 16 campos vacíos (como el formato original)
    fields = [""] * 16
    
    # Asignamos los valores en las posiciones correspondientes
    fields[0] = qr_data["nro_ticket"]  # Nº Ticket
    fields[4] = "Cliente"  # Cliente (placeholder)
    fields[15] = "0"  # Kg Netos (placeholder)
    
    # Convertimos a texto tabulado
    return "\t".join(fields)

