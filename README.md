# Lector QR - Ticket B - JP 2025

## Descripción General

🔧 Desarrollo Personalizado para Optimizar la Carga de Datos

Esta herramienta fue creada específicamente para automatizar el ingreso de información desde tickets de balanza mediante códigos QR, reemplazando la carga manual en planillas de control. Ahorra tiempo, reduce errores y se adapta a los procesos internos de la empresa.

Lector QR es una aplicación de escritorio desarrollada en Python que permite escanear, procesar y gestionar códigos QR relacionados con tickets de balanza para la industria algodonera. La aplicación está diseñada para manejar dos tipos de códigos QR:

1. **QR Primario**: Contiene información completa del ticket (≥ 21 campos)
2. **QR Secundario**: Contiene información complementaria (entre 9 y 21 campos)

La aplicación permite visualizar los datos en una tabla, realizar cálculos automáticos, editar valores manualmente y exportar la información al portapapeles para su uso en otras aplicaciones como Excel.

## Características Principales

- Interfaz gráfica moderna con CustomTkinter
- Procesamiento automático de códigos QR
- Detección inteligente del tipo de QR (primario o secundario)
- Cálculos automáticos de valores derivados (fibra neta, rinde, etc.)
- Edición manual de campos específicos
- Exportación de datos al portapapeles
- Manejo de errores y validaciones

## Estructura del Proyecto

El proyecto sigue una arquitectura MVC (Modelo-Vista-Controlador):

```
Lector 2/
├── main.py                  # Punto de entrada de la aplicación
├── qr_processor.py          # Procesamiento de códigos QR
├── utils.py                 # Funciones de utilidad
├── controllers/
│   └── qr_controller.py     # Controlador para la lógica de negocio
├── models/
│   └── qr_data.py           # Modelo de datos
└── ui/
    ├── input_frame.py       # Componente UI para entrada de datos
    ├── table_frame.py       # Componente UI para la tabla de datos
    └── button_frame.py      # Componente UI para botones de acción
```

## Funciones Detalladas

### Módulo Principal (main.py)

- **QRApp**: Clase principal que inicializa la aplicación y coordina los componentes.
  - `__init__(root)`: Inicializa la aplicación con la ventana raíz.
  - `setup_ui()`: Configura los componentes de la interfaz de usuario.
  - `scan_qr(qr_text)`: Procesa el texto del código QR escaneado.
  - `clear_table()`: Limpia la tabla de datos.
  - `copy_selected_row()`: Copia la fila seleccionada al portapapeles.

### Procesamiento de QR (qr_processor.py)

- **process_qr(qr_text)**: Procesa el texto del código QR primario y devuelve los datos formateados.
- **process_qr_type2(qr_text, qr_fields)**: Procesa el texto del código QR secundario.
- **extract_date(fecha_str)**: Extrae día, mes y año de una cadena de fecha.
- **has_dtv(numero_remito)**: Verifica si un número de remito contiene "DTV".
- **format_data(datos_escaneados)**: Formatea los datos para exportación.
- **format_second_qr_to_tab(qr_data)**: Convierte los datos del QR secundario a formato tabulado.

### Utilidades (utils.py)

- **extract_date(fecha_str)**: Extrae componentes de fecha de diferentes formatos.
- **has_dtv(numero_remito)**: Verifica si un remito contiene "DTV".
- **inicializar_configuracion(archivo)**: Crea o reinicia el archivo de configuración.
- **cargar_configuracion(archivo)**: Carga la configuración desde un archivo.

### Controlador QR (controllers/qr_controller.py)

- **QRController**: Clase que maneja la lógica de negocio.
  - `process_qr(qr_text)`: Procesa el texto del QR y actualiza el modelo.
  - `process_secondary_qr(qr_text, table_frame)`: Procesa un QR secundario y actualiza la tabla.
  - `update_calculations(item, values)`: Actualiza los cálculos para una fila.
  - `calculate_fibra_neta(values)`: Calcula la fibra neta.
  - `calculate_rinde(fibra_neta, kg_netos)`: Calcula el rinde.
  - `calculate_rinde_semilla(kg_netos)`: Calcula el rinde de semilla.
  - `copy_row_to_clipboard(selection, get_values_func, get_index_func)`: Copia una fila al portapapeles.
  - `clear_data()`: Limpia los datos del modelo.

### Modelo de Datos (models/qr_data.py)

- **QRData**: Clase que almacena y gestiona los datos escaneados.
  - `add_data(data)`: Agrega nuevos datos al modelo.
  - `get_data(index)`: Obtiene datos por índice.
  - `clear()`: Limpia todos los datos.

### Componentes de UI

#### InputFrame (ui/input_frame.py)

- **InputFrame**: Marco para la entrada de datos de QR.
  - `setup_ui()`: Configura los elementos de la interfaz.
  - `on_scan(event)`: Maneja el evento de escaneo.
  - `clear_entry()`: Limpia el campo de entrada.

#### TableFrame (ui/table_frame.py)

- **TableFrame**: Marco para la tabla de datos.
  - `parse_qr_data(qr_string)`: Parsea los datos del QR.
  - `calculate_derived_values(values)`: Calcula valores derivados.
  - `find_and_update_row(ticket_number, qr_data)`: Busca y actualiza una fila.
  - `process_qr_code(qr_string)`: Procesa un código QR completo.
  - `setup_ui()`: Configura la interfaz de la tabla.
  - `setup_style()`: Configura el estilo visual.
  - `save_current_edit()`: Guarda la edición actual.
  - `on_cell_click(event)`: Maneja el clic en una celda.
  - `add_row(data)`: Agrega una nueva fila.
  - `highlight_empty_fields(item)`: Resalta campos vacíos.
  - `clear()`: Limpia la tabla.
  - `get_selection()`: Obtiene la selección actual.
  - `get_item_values(item)`: Obtiene los valores de un ítem.
  - `get_item_index(item)`: Obtiene el índice de un ítem.

#### ButtonFrame (ui/button_frame.py)

- **ButtonFrame**: Marco para los botones de acción.
  - `setup_ui()`: Configura los botones.

## Flujo de Trabajo

1. El usuario escanea un código QR en el campo de entrada.
2. La aplicación detecta automáticamente si es un QR primario o secundario.
3. Si es un QR primario, se agrega una nueva fila a la tabla.
4. Si es un QR secundario, se busca la fila correspondiente por número de ticket y se actualiza.
5. Los cálculos automáticos se realizan para valores derivados (fibra neta, rinde, etc.).
6. El usuario puede editar manualmente ciertos campos haciendo clic en ellos.
7. El usuario puede copiar una fila seleccionada al portapapeles para usarla en Excel.

## Tipos de Códigos QR Soportados

### QR Primario (≥ 21 campos)
Contiene información completa del ticket, incluyendo:
- Número de ticket de balanza
- Fecha
- Sucursal
- Desmote
- Cliente
- Productor
- CUIT del cliente
- Número de remito
- Transporte
- Chofer
- DNI del chofer
- Patentes
- Pesos (fibra bruta, tara, fibra neta)
- Tipo de semilla
- Tipo de cosecha
- Procedencia
- Presentación

### QR Secundario (entre 9 y 21 campos)
Contiene información complementaria como:
- Número de ticket
- Fecha de desmote
- Fibra bruta
- Resto/agregado
- Fibra neta
- Rinde
- Cantidad de fardos
- Número de fardo inicial/final

## Requisitos

- Python 3.6 o superior
- CustomTkinter
- Tkinter
- pyperclip

## Uso

1. Ejecute `main.py` para iniciar la aplicación.
2. Escanee un código QR primario para agregar un nuevo registro.
3. Escanee un código QR secundario para actualizar un registro existente.
4. Edite manualmente los campos haciendo clic en ellos.
5. Seleccione una fila y haga clic en "Copiar Fila" para copiar los datos al portapapeles.
6. Utilice "Limpiar Tabla" para eliminar todos los registros.

## Notas Adicionales

- La aplicación maneja automáticamente la conversión de unidades (kg a toneladas).
- Los valores negativos en los códigos QR se indican con un apóstrofe (') que se convierte a signo menos (-).
- La aplicación calcula automáticamente la tara de fardo (2 kg por fardo).
- Los campos editables son: Nº FDO INICIAL, Nº FDO FINAL, FIBRA-BRUTA, RESTO y AGREGADO.
