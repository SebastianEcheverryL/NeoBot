import time
import machine
import pyb

# -------- LED RGB ----------
pin_r = pyb.Pin("PB3")
pin_g = pyb.Pin("PB4")
pin_b = pyb.Pin("PB10")

tim_r = pyb.Timer(2, freq=1000)
tim_g = pyb.Timer(3, freq=1000)
tim_b = pyb.Timer(2, freq=1000)

ch_r = tim_r.channel(2, pyb.Timer.PWM, pin=pin_r)
ch_g = tim_g.channel(1, pyb.Timer.PWM, pin=pin_g)
ch_b = tim_b.channel(3, pyb.Timer.PWM, pin=pin_b)

def set_rgb(r, g, b):
    ch_r.pulse_width_percent(r)
    ch_g.pulse_width_percent(g)
    ch_b.pulse_width_percent(b)

# -------- BOTÓN --------
boton = machine.Pin("PB2", machine.Pin.IN, machine.Pin.PULL_UP)
modo = 0
ultimo_estado = 1
tiempo_ultimo_cambio = time.ticks_ms()

# -------- IMPORTAR MODOS --------
import bluetooth
import linea
import objetos

nombres_modos = {
    0: "Detección de objetos",
    1: "Seguidor de línea",
    2: "Bluetooth"
}

# -------- FUNCIÓN PARA CAMBIAR MODO --------
def leer_boton():
    global modo, ultimo_estado, tiempo_ultimo_cambio

    estado = boton.value()

    if ultimo_estado == 1 and estado == 0:
        if time.ticks_diff(time.ticks_ms(), tiempo_ultimo_cambio) > 300:
            modo = (modo + 1) % 3
            print("Modo cambiado a:", nombres_modos.get(modo, "Modo desconocido"))
            tiempo_ultimo_cambio = time.ticks_ms()

    ultimo_estado = estado

# -------- LOOP PRINCIPAL --------
modo_anterior = -1   # 🔑 SOLO ESTA LÍNEA ES NUEVA

while True:
    leer_boton()

    # 🔹 Detectar cambio de modo
    if modo != modo_anterior:
        if modo == 1:          # Seguidor de línea
            linea.calibrado = False
        modo_anterior = modo

    if modo == 0:
        set_rgb(100, 0, 0)  # Rojo = Detección de objetos
        objetos.loop()

    elif modo == 1:
        set_rgb(10, 0, 50)  # Verde = Seguidor de línea
        linea.loop()

    elif modo == 2:
        set_rgb(0, 0, 100)  # Azul = Bluetooth
        bluetooth.loop()

    time.sleep_ms(10)
