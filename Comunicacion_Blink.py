import serial
import time
import requests

# Configuración de Blynk
BLYNK_AUTH_TOKEN = 'lvbS4x6Z3K1nkBEuCV1XucJskieoslxr'
BLYNK_URL = f'https://blynk.cloud/external/api/update'

# Configuración del puerto serial
SERIAL_PORT = 'COM2'
BAUD_RATE = 9600
rriente: 14.7000 
def connect_to_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.flushInput()
        print(f"Conexión establecida con {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"Error al abrir {SERIAL_PORT}: {e}")
        return None

def send_to_blynk(pin, value):
    """Envía datos a Blynk a un pin virtual específico"""
    params = {
        'token': BLYNK_AUTH_TOKEN,
        'pin': pin,
        'value': value
    }
    
    try:
        response = requests.get(BLYNK_URL, params=params)
        if response.status_code == 200:
            print(f"Dato enviado a Blynk en el pin {pin}: {value}")
        else:
            print(f"Error Blynk. Código: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar con Blynk: {e}")

def parse_serial_data(data):
    """Extrae la corriente y el modo del dato serial"""
    try:
        if "Corriente" in data and "Rama" in data:
            # Extraer el valor de la corriente
            parts = data.split("Corriente:")[1].split("|")[0].strip()
            current = float(parts.split()[0])
            
            # Determinar el modo
            if "Rama: Normal" in data:
                return current, "normal"
            elif "Rama: Deep Sleep" in data:
                return current, "deep_sleep"
        
        return None, None
    except (IndexError, ValueError) as e:
        print(f"Error al parsear datos: {e}")
        return None, None

def main():
    ser = connect_to_serial()
    if not ser:
        return

    start_time = time.time()
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Datos recibidos: {line}")
                    
                    current, mode = parse_serial_data(line)
                    if current is not None and mode is not None:
                        elapsed_time = time.time() - start_time
                        
                        # Enviar los datos a Blink dependiendo del modo
                        if mode == "normal":
                            print(f"Tiempo: {elapsed_time:.2f}s | Corriente: {current:.2f} mA | Modo: {mode}")
                            send_to_blynk('V1', current)  # Enviar a V1 en mA
                        elif mode == "deep_sleep":
                            print(f"Tiempo: {elapsed_time:.2f}s | Corriente: {current:.2f} µA | Modo: {mode}")
                            send_to_blynk('V2', current)  # Enviar a V2 en µA (ya está en microamperios)
                except UnicodeDecodeError:
                    print("Error al decodificar datos seriales")
                except Exception as e:
                    print(f"Error inesperado: {e}")
            
            time.sleep(0.1)  # Pequeña pausa para evitar sobrecarga
            
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario")
    finally:
        ser.close()
        print("Puerto serial cerrado")

if __name__ == "__main__":
    main()
