def obtener_titulo(tipo_transferenciaKeyValue):
    tipo_transferencia = ""  # Inicializar tipo_transferencia

    # Obtener un valor sin conocer la clave
    for valor in tipo_transferenciaKeyValue.values():
        if valor:  # Verificar que el valor no esté vacío
            tipo_transferencia = valor
            break  # Salir del bucle una vez que se encuentra el primer valor no vacío

    return tipo_transferencia  # Devolver el tipo de entrega
