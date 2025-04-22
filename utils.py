import os

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

# Lista de columnas esperadas
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

# Diccionario para asignar valores predeterminados
valores_por_defecto = {
    "ALGODÓN NETO EN TN": "=[@[ALGODÓN EN BRUTO TN]]-[@TARA]",
    "RINDE": "=[@[FIBRA NETA]]/[@[ALGODÓN NETO EN TN]]/1000",
    "PRECIOS": "=(([@RINDE]-$V$2)*100)*$X$2+[@[BASE]]",
    "TOTAL A PAGAR": "=[@IMPORTE LIQUIDACION]",
    "FIBRA NETA": "=[@[FIBRA-BRUTA]]+[@RESTO]-[@AGREGADO]-[@[TARA FARDO]]",
    "CANT.FDS.": "=[@Nº FDO FINAL]-[@Nº FDO INIC]+1",
    "IMPORTE S/IVA": "=[@ALGODÓN NETO EN TN]*[@PRECIOS]",
    "IVA4": "=+[@[IMPORTE S/IVA]]*21%",
    "IMPORTE LIQUIDACION": "=+[@[IMPORTE S/IVA]]+[@IVA4]-[@RETENCIONES]",
    "SALDO A PAGAR FLETES": "=+[@[FLETE A PAGAR]]-[@ANTICIPO3]",
    "NETO FLETES": "=[@ALGODÓN NETO EN TN]*[@[TARIFA FLETES]]",
    "DESCUENTO (Fl+C)": "=+[@[IMPORTE A PAGAR CARGADOR]]+[@[NETO FLETES]]",
    "RINDE SEMILLA(KGRS)": "=[@ALGODÓN NETO EN TN]*0.45"
}


def inicializar_configuracion(archivo="config.txt"):
    """Crea o reinicia config.txt con valores predeterminados si no existe o está vacío."""
    if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
        with open(archivo, "w", encoding="utf-8") as file:
            for columna in columnas:
                valor = valores_por_defecto.get(columna, "")
                file.write(f"{columna}={valor}\n")
        print("✅ Archivo config.txt inicializado con valores por defecto.")

def cargar_configuracion(archivo="config.txt"):
    """Carga la configuración desde config.txt y la completa si faltan valores."""
    inicializar_configuracion(archivo)  # Se asegura de que el archivo existe

    configuracion = {}
    
    with open(archivo, "r+", encoding="utf-8") as file:
        lineas = file.readlines()
        columnas_en_archivo = set()
        
        # Leer archivo y llenar configuración
        for linea in lineas:
            linea = linea.strip()
            if "=" in linea:
                columna, formula = linea.split("=", 1)
                columna = columna.strip()
                formula = formula.strip()
                configuracion[columna] = formula
                columnas_en_archivo.add(columna)

        # Si hay columnas faltantes, las agregamos al archivo
        faltantes = [col for col in columnas if col not in columnas_en_archivo]
        if faltantes:
            file.write("\n")  # Separador por estética
            for col in faltantes:
                valor = valores_por_defecto.get(col, "")
                file.write(f"{col}={valor}\n")
                configuracion[col] = valor

    return configuracion
