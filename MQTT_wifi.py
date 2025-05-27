import serial
import time
import paho.mqtt.client as mqtt
import pytz
# Configuración del puerto serial
SERIAL_PORT = 'COM2'  # Cambia esto si usas otro puerto
BAUD_RATE = 9600

#Creacion de cliente MQTT
client = mqtt.Client()
client.connect("4.205.183.50",1883,60)

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.flushInput()
        print(f"Conexión establecida con {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Error al abrir {SERIAL_PORT}: {e}")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if "Corriente:" in line:
                        partes = line.split("Corriente:")[1].strip().split()
                        valor_str = partes[0]
                        unidad = partes[1] if len(partes) > 1 else "mA"

                        valor = float(valor_str)
                        print(valor_str, unidad)
                        # Identificar unidad
                        if unidad == "mA":
                            client.publish("Home/Device0/Unidad",unidad)
                            client.publish("Home/Device0/Current", valor_str)
                            print("Publicación de:",unidad," y corriente:", valor_str)


                        elif unidad in ["uA", "µA"]:
                            client.publish("Home/Device0/Unidad",unidad)
                            client.publish("Home/Device0/Current", valor/1000)
                            print("Publicación de:",unidad," y corriente:", valor/1000)

                        else:
                            print(f"{valor} (unidad desconocida)")
                except (UnicodeDecodeError, ValueError, IndexError):
                    print("Error al procesar los datos seriales")
                except Exception as e:
                    print(f"Error inesperado: {e}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario")
    finally:
        ser.close()
        print("Puerto serial cerrado")

if __name__ == "__main__":
    main()
