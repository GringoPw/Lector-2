class QRData:
    def __init__(self):
        self.datos_escaneados = []
    
    def add_data(self, data):
        self.datos_escaneados.append(data)
        return len(self.datos_escaneados) - 1  # Return index of added data
    
    def get_data(self, index):
        if 0 <= index < len(self.datos_escaneados):
            return self.datos_escaneados[index]
        return None
    
    def clear(self):
        self.datos_escaneados.clear()