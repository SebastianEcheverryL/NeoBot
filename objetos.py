# modo_lab.py 
import time, machine, pyb
from hcsr04 import HCSR04

# === PINES MOTORES ===
ena_pin = machine.Pin("PA6", machine.Pin.OUT)
enb_pin = machine.Pin("PA5", machine.Pin.OUT)

pwm_a = machine.Pin("PB6")
pwm_b = machine.Pin("PA7")

tim_a = pyb.Timer(4, freq=2000)
ch_a = tim_a.channel(1, pyb.Timer.PWM, pin=pwm_a)

tim_b = pyb.Timer(3, freq=2000)
ch_b = tim_b.channel(2, pyb.Timer.PWM, pin=pwm_b)

# === SENSOR ULTRASONICO FRONTAL ===
sensor = HCSR04(
    trigger_pin=machine.Pin("PA9"),
    echo_pin=machine.Pin("PA8"),
    echo_timeout_us=30000
)

# ============================
# FUNCIONES DE MOVIMIENTO
# ============================

def adelante(speed=70):   # velocidad mayor
    ena_pin.low()      
    enb_pin.low()      
    ch_a.pulse_width_percent(speed)
    ch_b.pulse_width_percent(speed)

def detener():
    ch_a.pulse_width_percent(0)
    ch_b.pulse_width_percent(0)

def girar_derecha(speed=70):   # giro más rápido
    ena_pin.high()      
    enb_pin.low()       
    ch_a.pulse_width_percent(speed)
    ch_b.pulse_width_percent(speed)

# ============================
# DISTANCIA FRONTAL SEGURA
# ============================

def distancia_frontal():
    try:
        return sensor.distance_cm()
    except:
        return 999

# ============================
# LOOP PRINCIPAL
# ============================

def loop():
    # Límites
    OBSTACULO = 10
    LIBRE = 15           

    dist = distancia_frontal()
    print("Distancia:", dist)
    
    if dist > OBSTACULO:
        adelante(70)   
        return

    # Si está muy cerca → detener
    detener()
    time.sleep(0.1)

    # Evita el obstaculo girando a la derecha
    while distancia_frontal() < LIBRE:
        print("Evitando obstaculo")
        girar_derecha(60)  
        time.sleep(0.03)

    
    detener()
    time.sleep(0.05)
    adelante(70)  
