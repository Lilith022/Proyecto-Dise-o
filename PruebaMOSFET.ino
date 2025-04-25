#include <Wire.h>
#include <Adafruit_INA219.h>
#include <LiquidCrystal.h>

// Inicializar el objeto para el sensor INA219
Adafruit_INA219 ina219;
LiquidCrystal lcd(2, 3, 4, 5, 6, 7); // RS, EN, D4, D5, D6, D7

// Definición de pines
const int pinMA = 8;
const int pinMSP = 10;
const int botonManual = 11;
const int botonAuto = 12;
const int botonAlternar = 13;

// Variables de control
bool modoManual = false;
bool estadoMA = true;  // true = MA, false = MSP
unsigned long ultimaAlternancia = 0;
bool estadoBotonAnt = HIGH;

void setup() {
  Serial.begin(9600);  // Inicializa la comunicación serial a 9600 baudios
  lcd.begin(16, 2);    // Inicializa el LCD con 16 columnas y 2 filas
  lcd.print("Iniciando...");

  // Iniciar el sensor INA219
  if (!ina219.begin()) {
    lcd.clear();
    lcd.print("INA219 FAIL");
    while (1);  // Detiene el programa si falla el INA219
  }

  // Configurar pines de salida para las ramas y los botones
  pinMode(pinMA, OUTPUT);
  pinMode(pinMSP, OUTPUT);
  pinMode(botonManual, INPUT_PULLUP);
  pinMode(botonAuto, INPUT_PULLUP);
  pinMode(botonAlternar, INPUT_PULLUP);

  delay(1000);
  lcd.clear();

  // Activar la rama MA de manera predeterminada
  activarRama("MA");
}

void activarRama(String rama) {
  if (rama == "MA") {
    digitalWrite(pinMA, HIGH);  // Activa la rama MA
    digitalWrite(pinMSP, LOW); 
    delayMicroseconds(50); // Desactiva la rama MSP
  } else {
    digitalWrite(pinMA, LOW);   // Desactiva la rama MA
    digitalWrite(pinMSP, HIGH);
    delayMicroseconds(50); // Activa la rama MSP
  }
  
}

void loop() {
  // Botón para cambiar a modo manual
  if (digitalRead(botonManual) == LOW) {
    delay(50); 
    while (digitalRead(botonManual) == LOW);  // Espera hasta que se libere el botón
    delay(50);
    modoManual = true;
    activarRama(estadoMA ? "MA" : "MSP");
  }

  // Botón para cambiar a modo automático
  if (digitalRead(botonAuto) == LOW) {
    delay(50); 
    while (digitalRead(botonAuto) == LOW);  // Espera hasta que se libere el botón
    delay(50);
    modoManual = false;
    ultimaAlternancia = millis();  // Reinicia el temporizador
  }

  // Botón para alternar la rama en modo manual
  bool estadoBotonAct = digitalRead(botonAlternar);
  if (modoManual && estadoBotonAnt == HIGH && estadoBotonAct == LOW) {
    estadoMA = !estadoMA;
    activarRama(estadoMA ? "MA" : "MSP");
  }
  estadoBotonAnt = estadoBotonAct;

  // Alternancia automática entre las ramas cada 6 segundos
  if (!modoManual) {
    if (millis() - ultimaAlternancia > 5000) {
      estadoMA = !estadoMA;
      activarRama(estadoMA ? "MA" : "MSP");
      ultimaAlternancia = millis();
    }
  }

  // Lectura de corriente y voltaje
  float current_mA = ina219.getCurrent_mA(); 
  float voltage_V = ina219.getBusVoltage_V();

  // Convertir corriente a microamperios (uA)
  float current_uA = current_mA * 10;  // Convertir mA a uA

  // Mostrar en el LCD
  lcd.setCursor(0, 0);
  lcd.print("I:");
  lcd.print(current_uA, 4);  // Mostrar corriente en microamperios con 4 decimales
  lcd.print("uA ");

  // Mostrar el modo y la rama
  lcd.setCursor(0, 1);
  if (modoManual) {
    lcd.print("Manual ");
  } else {
    lcd.print("Auto   ");
  }

  if (estadoMA) {
    lcd.print("Normal");
  } else {
    lcd.print("Deep Sleep");
  }

  // Enviar los datos al puerto serial
  Serial.print("Corriente: ");
  Serial.print(current_uA, 4);  // Mostrar corriente en microamperios con 4 decimales
  Serial.print(" µA | Voltaje: ");
  Serial.print(voltage_V);
  Serial.print(" V | Modo: ");
  Serial.print(modoManual ? "Manual" : "Auto");
  Serial.print(" | Rama: ");
  Serial.println(estadoMA ? "Normal" : "Deep Sleep");

  delay(500);  // Retardo de medio segundo para evitar sobrecarga
}


