from machine import Pin, UART
import pyb
import time

# ===== MOTORES =====
ena_pin = Pin("PA6", Pin.OUT)
enb_pin = Pin("PA5", Pin.OUT)

pwm_a = Pin("PB6")
pwm_b = Pin("PA7")

tim_a = pyb.Timer(4, freq=3000)
ch_a = tim_a.channel(1, pyb.Timer.PWM, pin=pwm_a)

tim_b = pyb.Timer(3, freq=3000)
ch_b = tim_b.channel(2, pyb.Timer.PWM, pin=pwm_b)

def detener():
    ch_a.pulse_width_percent(0)
    ch_b.pulse_width_percent(0)
    ena_pin.low()
    enb_pin.low()

def adelante(s=80):
    ena_pin.low()
    enb_pin.low()
    ch_a.pulse_width_percent(s)
    ch_b.pulse_width_percent(s)

def atras(s=80):
    ena_pin.high()
    enb_pin.high()
    ch_a.pulse_width_percent(s)
    ch_b.pulse_width_percent(s)

def girar_izquierda(s=80):
    ena_pin.low()
    enb_pin.high()
    ch_a.pulse_width_percent(s)
    ch_b.pulse_width_percent(s)

def girar_derecha(s=80):
    ena_pin.high()
    enb_pin.low()
    ch_a.pulse_width_percent(s)
    ch_b.pulse_width_percent(s)

# ===== BLUETOOTH =====
uart = UART(6, 9600)
last_cmd_time = time.ticks_ms()

def loop():
    """
    Esta función se llama EN CADA CICLO del main.
    No tiene while True, para que no bloquee el programa.
    """
    global last_cmd_time

    if uart.any():
        cmd = uart.read(1).decode().strip().upper()
        last_cmd_time = time.ticks_ms()

        if cmd == "W":
            adelante()
        elif cmd == "S":
            atras()
        elif cmd == "A":
            girar_izquierda()
        elif cmd == "D":
            girar_derecha()
        elif cmd == "X":
            detener()

    # autostop
    if time.ticks_diff(time.ticks_ms(), last_cmd_time) > 2000:
        detener()
        last_cmd_time = time.ticks_ms()
