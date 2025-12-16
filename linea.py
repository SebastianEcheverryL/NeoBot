import pyb
import machine
import time

# =====================================================
# CONFIGURACIÓN MOTORES (L298)
# =====================================================
ena_pin = machine.Pin("PA6", machine.Pin.OUT)
enb_pin = machine.Pin("PA5", machine.Pin.OUT)

pwm_a = machine.Pin("PB6")
pwm_b = machine.Pin("PA7")

tim_a = pyb.Timer(4, freq=2000)
ch_a = tim_a.channel(1, pyb.Timer.PWM, pin=pwm_a)

tim_b = pyb.Timer(3, freq=2000)
ch_b = tim_b.channel(2, pyb.Timer.PWM, pin=pwm_b)

# =====================================================
# SENSORES QTR
# =====================================================
sensors = [
    machine.ADC(machine.Pin("PA0")),
    machine.ADC(machine.Pin("PA1")),
    machine.ADC(machine.Pin("PA4")),
    machine.ADC(machine.Pin("PB0")),
    machine.ADC(machine.Pin("PC1")),
    machine.ADC(machine.Pin("PC0"))
]

NUM = len(sensors)

# =====================================================
# VARIABLES DE CALIBRACIÓN
# =====================================================
min_vals = [65535] * NUM
max_vals = [0] * NUM
UMBRAL = [20000] * NUM

calibrado = False

# =====================================================
# PARÁMETROS DE TORQUE Y VELOCIDAD
# =====================================================
PWM_MIN = 35      #torque mínimo
PWM_MAX = 80

BASE_SPEED = 75   # velocidad base alta
CURVE_SLOW = 40   # reducción máxima en curva

# =====================================================
# LECTURA SENSORES
# =====================================================
def leer_raw():
    return [s.read_u16() for s in sensors]

# =====================================================
# CALIBRACIÓN AUTOMÁTICA
# =====================================================
def calibrar_automatico(t_ms=5000, vel=40):
    global UMBRAL, min_vals, max_vals

    print(">>> Calibración automática iniciada")

    min_vals = [65535] * NUM
    max_vals = [0] * NUM

    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < t_ms:
        ena_pin.low()
        enb_pin.high()
        ch_a.pulse_width_percent(vel)
        ch_b.pulse_width_percent(vel)

        valores = leer_raw()
        for i in range(NUM):
            if valores[i] < min_vals[i]:
                min_vals[i] = valores[i]
            if valores[i] > max_vals[i]:
                max_vals[i] = valores[i]

        time.sleep_ms(20)

    ch_a.pulse_width_percent(0)
    ch_b.pulse_width_percent(0)
    ena_pin.low()
    enb_pin.low()

    UMBRAL = [(min_vals[i] + max_vals[i]) // 2 for i in range(NUM)]
    print("Umbrales:", UMBRAL)

# =====================================================
# PID
# =====================================================
Kp = 0.028
Ki = 0.00
Kd = 0.22

integral = 0
last_error = 0

def pid(error):
    global integral, last_error
    integral += error
    derivative = error - last_error
    last_error = error
    return Kp * error + Ki * integral + Kd * derivative

# =====================================================
# CONTROL DE MOTORES
# =====================================================
def set_motors(base, corr):
    corr = max(-40, min(40, corr))

    left = base - corr
    right = base + corr

    left = max(PWM_MIN, min(PWM_MAX, int(left)))
    right = max(PWM_MIN, min(PWM_MAX, int(right)))

    ena_pin.low()
    enb_pin.low()

    ch_a.pulse_width_percent(left)
    ch_b.pulse_width_percent(right)

# =====================================================
# POSICIÓN DE LÍNEA
# =====================================================
weights = [-3, -2, -1, 1, 2, 3]

def get_pos(binarios):
    if sum(binarios) == 0:
        return 0

    suma = 0
    total = 0
    for i in range(NUM):
        suma += binarios[i] * weights[i]
        total += binarios[i]

    return (suma / total) * 100

# =====================================================
# LOOP SEGUIDOR DE LÍNEA
# =====================================================
def loop():
    global calibrado

    if not calibrado:
        calibrar_automatico()
        calibrado = True

    valores = leer_raw()
    binarios = [1 if valores[i] < UMBRAL[i] else 0 for i in range(NUM)]

    pos = get_pos(binarios)
    corr = pid(pos)

    base_speed = BASE_SPEED - min(abs(pos) / 3, CURVE_SLOW)

    print("POS:", pos, "CORR:", corr, "VEL:", base_speed)

    set_motors(base_speed, corr)
