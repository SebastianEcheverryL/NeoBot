import serial
import time
import tkinter as tk
from tkinter import messagebox

# ---------- CONFIGURACIÓN ----------
PORT = "COM6"     # Puerto COM del Bluetooth(HC-06)
BAUDRATE = 9600


try:
    bluetooth = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print("✅ Conectado al robot vía Bluetooth")
except:
    messagebox.showerror("Error", "No se pudo conectar al Bluetooth")
    exit()

# ---------- FUNCIONES ----------
def enviar(comando):
    try:
        bluetooth.write(comando.encode())
        print(f"📤 Enviado: {comando}")
    except:
        messagebox.showerror("Error", "Conexión Bluetooth perdida")

def cerrar():
    enviar("STOP")
    bluetooth.close()
    ventana.destroy()

# ---------- INTERFAZ ----------
ventana = tk.Tk()
ventana.title("Control Robot Bluetooth")
ventana.geometry("300x350")
ventana.resizable(False, False)

titulo = tk.Label(ventana, text="🤖 Control del Robot", font=("Arial", 16))
titulo.pack(pady=10)

frame = tk.Frame(ventana)
frame.pack(pady=20)

btn_w = tk.Button(frame, text="↑ Adelante", width=12, height=2,
                  command=lambda: enviar("W"))
btn_w.grid(row=0, column=1, pady=5)

btn_a = tk.Button(frame, text="← Izquierda", width=12, height=2,
                  command=lambda: enviar("A"))
btn_a.grid(row=1, column=0, padx=5)

btn_stop = tk.Button(frame, text="■ STOP", width=12, height=2,
                     bg="red", fg="white",
                     command=lambda: enviar("STOP"))
btn_stop.grid(row=1, column=1, pady=5)

btn_d = tk.Button(frame, text="Derecha →", width=12, height=2,
                  command=lambda: enviar("D"))
btn_d.grid(row=1, column=2, padx=5)

btn_s = tk.Button(frame, text="↓ Atrás", width=12, height=2,
                  command=lambda: enviar("S"))
btn_s.grid(row=2, column=1, pady=5)

btn_salir = tk.Button(ventana, text="Salir", width=15,
                      command=cerrar)
btn_salir.pack(pady=15)

ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.mainloop()
