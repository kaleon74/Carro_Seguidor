import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import random

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0
        self.last_output = 0

    def compute(self, error, dt):
        if dt <= 0:
            derivative = 0
        else:
            derivative = (error - self.prev_error) / dt * 0.7
        self.integral = max(-50, min(self.integral + error * dt, 50))
        raw_output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        smoothed_output = 0.3 * raw_output + 0.7 * self.last_output
        self.last_output = smoothed_output
        self.prev_error = error
        return smoothed_output

class LineFollowerCar:
    def __init__(self, canvas, max_laps=3):
        self.canvas = canvas
        self.car_x = 77
        self.car_y = 520
        self.car_angle = 270
        self.speed = 1.5
        self.sensor_distance = 30
        self.sensor_offset = 20
        self.pid = PIDController(3, 0.00001, 0.00001)
        self.last_time = time.time()
        self.trail = []
        self.last_angle_change = 0
        self.max_turn_rate = 3.0
        self.stopping = False
        
        # Sistema de contador de vueltas
        self.start_x = 77
        self.start_y = 520
        self.detection_radius = 30
        self.lap_count = 0
        self.max_laps = max_laps
        self.near_start = True
        self.lap_completed = False
        
        # Crear elementos visuales del contador
        self.lap_text = self.canvas.create_text(400, 50, 
                                              text=f"Vueltas: {self.lap_count}/{self.max_laps}", 
                                              font=("Arial", 16, "bold"), 
                                              fill="white")

        # Crear carro con nuevo estilo
        self.body = self.create_car_body()
        self.left_wheel = self.create_wheel()
        self.right_wheel = self.create_wheel()
        self.sensor_left = self.create_sensor()
        self.sensor_right = self.create_sensor()
        self.update_car()

    def create_car_body(self):
        return self.canvas.create_polygon([0,0,50,0,50,30,0,30], 
                                        fill='#FF6B35', outline='#F7931E', width=3)
    
    def create_wheel(self):
        return self.canvas.create_oval(0,0,14,14, 
                                     fill='#BDC3C7', outline='#85929E', width=2)
    
    def create_sensor(self):
        return self.canvas.create_oval(0,0,10,10, 
                                     fill='#27AE60', outline='#1E8449', width=2)

    def update_car(self):
        angle = math.radians(self.car_angle)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        coords = [
            self.car_x + 15*cos_a - 10*sin_a, self.car_y + 15*sin_a + 10*cos_a,
            self.car_x + 15*cos_a + 10*sin_a, self.car_y + 15*sin_a - 10*cos_a,
            self.car_x - 15*cos_a + 10*sin_a, self.car_y - 15*sin_a - 10*cos_a,
            self.car_x - 15*cos_a - 10*sin_a, self.car_y - 15*sin_a + 10*cos_a
        ]
        self.canvas.coords(self.body, *coords)
        self._update_wheel(self.left_wheel, -10, angle)
        self._update_wheel(self.right_wheel, 10, angle)
        sl, sr = self.get_sensor_positions()
        self.canvas.coords(self.sensor_left, sl[0]-5, sl[1]-5, sl[0]+5, sl[1]+5)
        self.canvas.coords(self.sensor_right, sr[0]-5, sr[1]-5, sr[0]+5, sr[1]+5)

    def _update_wheel(self, wheel, offset, angle):
        x = self.car_x + offset * math.sin(angle)
        y = self.car_y - offset * math.cos(angle)
        self.canvas.coords(wheel, x-7, y-7, x+7, y+7)

    def get_sensor_positions(self):
        a = math.radians(self.car_angle)
        fx = self.car_x + self.sensor_distance * math.cos(a)
        fy = self.car_y + self.sensor_distance * math.sin(a)
        ls = (fx - self.sensor_offset * math.sin(a), fy + self.sensor_offset * math.cos(a))
        rs = (fx + self.sensor_offset * math.sin(a), fy - self.sensor_offset * math.cos(a))
        return ls, rs


#Funcion que me define  y me lleva el contador de vueltas del carro
    def check_lap_completion(self):
        distance_to_start = math.sqrt((self.car_x - self.start_x)**2 + (self.car_y - self.start_y)**2)
        
        if distance_to_start <= self.detection_radius:
            if not self.near_start and not self.lap_completed:
                self.lap_count += 1
                self.lap_completed = True
                self.near_start = True
                
                self.canvas.itemconfig(self.lap_text, 
                                     text=f"Vueltas: {self.lap_count}/{self.max_laps}")
                
                if self.lap_count >= self.max_laps:
                    self.stopping = True
                    self.canvas.create_text(self.car_x, self.car_y - 40,
                                          text="¡HAS GANADO LA USTA RACING!🏁 ",
                                          font=("Arial", 14, "bold"),
                                          fill="green")
                    return True
                else:
                    self.canvas.create_text(self.car_x, self.car_y - 30, 
                                          text=f"¡Vuelta {self.lap_count} completada!", 
                                          font=("Arial", 10, "bold"),
                                          fill="blue")
        else:
            if distance_to_start > self.detection_radius * 1.5:
                self.near_start = False
                self.lap_completed = False
        
        return False

    def move(self):
        now = time.time()
        dt = now - self.last_time if now - self.last_time > 0 else 1e-3
        self.last_time = now

        if self.check_lap_completion():
            return
        
        if self.stopping:
            return

        sl, sr = self.get_sensor_positions()
        sc = ((sl[0]+sr[0])/2, (sl[1]+sr[1])/2)
            
        left_active = self.check_sensor(*sl)
        right_active = self.check_sensor(*sr)
        center_active = self.check_sensor(*sc)

        state = 'none'
        if left_active and right_active:
            state = 'both'
        elif left_active:
            state = 'left'
        elif right_active:
            state = 'right'
        elif center_active:
            state = 'center'

        if state == 'none':
            self.speed = 0.8
            if time.time() - self.last_angle_change > 0.5:
                self.last_angle_change = time.time()
                self.car_angle += 2 if int(time.time()*2)%2==0 else -2
        else:
            self.speed = 1.5 if state == 'both' else 1.3 if state=='center' else 1.0
            if state == 'left': error = 3
            elif state == 'right': error = -3

            #fondo juego de carreras
            elif state == 'center': error = 0.5 * self.pid.prev_error
            else: error = 0
            steering = self.pid.compute(error, dt)
            steering = max(-self.max_turn_rate, min(steering, self.max_turn_rate))
            self.car_angle += steering

        rad = math.radians(self.car_angle)
        self.car_x = max(20, min(self.car_x + self.speed*math.cos(rad), 780))
        self.car_y = max(20, min(self.car_y + self.speed*math.sin(rad), 580))
        self.trail.append((self.car_x, self.car_y))
        if len(self.trail)>100: self.trail.pop(0)
        self.update_car()

    def check_sensor(self, x, y):
        overlap = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        return guide_line in overlap


class ConfigWindow:
    def __init__(self):
        self.max_laps = 1  # Valor de Inicio de vueltas  por defecto
        self.config_window = tk.Tk()
        self.config_window.title("Carro Seguidor :D, SO 💻")
        self.config_window.geometry("500x550")
        self.config_window.configure(bg='#2C3E50')
        self.config_window.resizable(False, False)

        # Centrar la ventana
        self.center_window()

        self.create_config_interface()

    def center_window(self):
        self.config_window.update_idletasks()
        x = (self.config_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.config_window.winfo_screenheight() // 2) - (400 // 2)
        self.config_window.geometry(f"500x550+{x}+{y}")

    def create_config_interface(self):
        # Marco principal
        main_frame = tk.Frame(self.config_window, bg='#2C3E50', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Título
        title_label = tk.Label(main_frame, 
                              text=" CARRO SEGUIDOR DE LÍNEA\n🏎️",
                              font=("Arial", 18, "bold"),
                              fg='#F39C12',
                              bg='#2C3E50')
        title_label.pack(pady=(20, 20))
        

       # Subtítulo
        subtitle_label = tk.Label(main_frame,
                                 text="🔥USTA RACING 🔥",
                                 font=("Arial", 12),
                                 fg='#BDC3C7',
                                 bg='#2C3E50')
        subtitle_label.pack(pady=(0, 30))
        

        # Marco para la configuración de vueltas
        laps_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=2)
        laps_frame.pack(fill='x', pady=10)
        
        # Etiqueta para vueltas
        laps_label = tk.Label(laps_frame,
                             text="¿Cuántas vueltas debe completar el carro?",
                             font=("Arial", 12, "bold"),
                             fg='white',
                             bg='#34495E')
        laps_label.pack(pady=(15, 10))
        
        # Frame para el control de vueltas
        control_frame = tk.Frame(laps_frame, bg='#34495E')
        control_frame.pack(pady=(0, 15))
        
        # Botones de decremento/incremento y entrada
        self.laps_var = tk.StringVar(value="3")
        
        minus_btn = tk.Button(control_frame, text="-", font=("Arial", 14, "bold"),
                             width=3, bg='#E74C3C', fg='white',
                             activebackground='#C0392B',
                             command=self.decrease_laps)
        minus_btn.pack(side='left', padx=5)
        
        self.laps_entry = tk.Entry(control_frame, textvariable=self.laps_var,
                                  font=("Arial", 14, "bold"),
                                  width=5, justify='center',
                                  bg='white', fg='#2C3E50')
        self.laps_entry.pack(side='left', padx=10)
        
        plus_btn = tk.Button(control_frame, text="+", font=("Arial", 14, "bold"),
                            width=3, bg='#27AE60', fg='white',
                            activebackground='#1E8449',
                            command=self.increase_laps)
        plus_btn.pack(side='left', padx=5)
        
        # Información adicional
        info_label = tk.Label(main_frame,
                             text="¿ESTAS LISTO PARA LA CARRERA?🏆",
                             font=("Arial", 13),
                             fg='#95A5A6',
                             bg='#2C3E50',
                             justify='center')
        info_label.pack(pady=(15, 25))
        
        # Botones de acción
        button_frame = tk.Frame(main_frame, bg='#2C3E50')
        button_frame.pack(fill='x', pady=(10, 20))
        
        start_btn = tk.Button(button_frame, 
                             text="🚀 INICIAR CARRRERA",
                             font=("Arial", 12, "bold"),
                             bg='#3498DB', fg='white',
                             activebackground='#2980B9',
                             padx=12, pady=12,
                             command=self.start_simulation)
        start_btn.pack(pady=(10, 10),fill='both',expand=True)
        
        cancel_btn = tk.Button(button_frame,
                              text="❌ CANCELAR",
                              font=("Arial", 12, "bold"),
                              bg='#95A5A6', fg='white',
                              activebackground='#7F8C8D',
                              padx=12, pady=12,
                              command=self.cancel)
        cancel_btn.pack(fill='x')
        
        # Validación de entrada
        self.laps_entry.bind('<KeyRelease>', self.validate_input)
        
    def decrease_laps(self):
        try:
            current = int(self.laps_var.get())
            if current > 1:
                self.laps_var.set(str(current - 1))
        except ValueError:
            self.laps_var.set("1")
    
    def increase_laps(self):
        try:
            current = int(self.laps_var.get())
            if current < 99:
                self.laps_var.set(str(current + 1))
        except ValueError:
            self.laps_var.set("1")
    
    def validate_input(self, event=None):
        try:
            value = int(self.laps_var.get())
            if value < 1:     #Mnimo de vuletas 1
                self.laps_var.set("1")
            elif value > 10:  #maximo de vueltas 2
                self.laps_var.set("10")
        except ValueError:
            if self.laps_var.get() != "":
                self.laps_var.set("1")
    
    def start_simulation(self):
        try:
            self.max_laps = int(self.laps_var.get())
            if self.max_laps < 1:
                messagebox.showerror("Error", "El número de vueltas debe ser mayor a 0")
                return
            self.config_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número válido")
    
    def cancel(self):
        self.config_window.quit()
        exit()
    
    def run(self):
        self.config_window.mainloop()
        return self.max_laps

def create_simulation_window(max_laps):
    global guide_line
    
    # Ventana principal de simulación
    window = tk.Tk()
    window.title(f"🛣️  Carro Seguidor - {max_laps} Vueltas")
    canvas = tk.Canvas(window, width=800, height=600, bg='#2C3E50')
    canvas.pack()

    # Definir paradas para formar una pista
    stops = [(72, 276), (301, 103), (160, 466), (500, 180), (425, 454)]

    # Fondo y decoración
    from tkinter import PhotoImage  # arriba del todo

    # Cargar imagen de fondo
    imagen_fondo = PhotoImage(file="fondo.png")
    canvas.create_image(0, 0, anchor=tk.NW, image=imagen_fondo)

    #canvas.create_rectangle(0,0,800,600, fill='#34495E', stipple='gray25')

    # Pista base y línea guía
    track = canvas.create_line(
        [(45,520),(750,520),(766,461),(695,398),(382,462),(488,289),(580,319),(619,242),(594,220),(407,148),(290,209),(203,405),(115,441),(99,378),(184,291),(167,239),(295,115),(180,63),(15,402),(45,520)], 
        fill='#566573', width=20, smooth=True, capstyle=tk.ROUND
    )
    guide_line = canvas.create_line(
        [(45,520),(750,520),(766,461),(695,398),(382,462),(488,289),(580,319),(619,242),(594,220),(407,148),(290,209),(203,405),(115,441),(99,378),(184,291),(167,239),(295,115),(180,63),(15,402),(45,520)], 
        fill='black', width=10, smooth=True, joinstyle=tk.ROUND, capstyle=tk.ROUND
    )

    # Marcar punto de inicio/meta
    start_marker = canvas.create_oval(77-15, 520-15, 77+15, 520+15,
                                    fill='#E74C3C', outline='#C0392B', width=3)
    canvas.create_text(77, 520, text="START", font=("Arial", 8, "bold"), fill="white")

    # Dibujar estaciones
    for i, (x,y) in enumerate(stops, start=1):
        canvas.create_oval(x-15, y-15, x+15, y+15,
                           fill='#F1C40F', outline='#B7950B', width=3)
        canvas.create_text(x, y, text=f"S{i}", font=("Arial",12,"bold"))

    # Inicializar carro
    car = LineFollowerCar(canvas, max_laps=max_laps)
    canvas.create_text(400, 20, text=f"Seguidor de Línea - Meta: {max_laps} Vueltas", 
                      font=("Arial",14,"bold"), fill="white")

    # Botón de reinicio
    def restart_simulation():
        window.destroy()
        main()
    
    restart_btn = tk.Button(window, text="🔄 NUEVA CARRERA", 
                           font=("Arial", 12, "bold"),
                           bg='#9B59B6', fg='white',
                           command=restart_simulation)
    restart_btn.pack(pady=5)

    # Loop de simulación
    def game_loop():
        car.move()
        if random.random()>0.5 and not car.stopping:
            canvas.create_oval(car.car_x-1, car.car_y-1,
                               car.car_x+1, car.car_y+1,
                               fill='#F39C12', outline='')
        window.after(30, game_loop)

    game_loop()
    window.mainloop()

def main():
    # Crear y mostrar ventana de configuración
    config = ConfigWindow()
    max_laps = config.run()
    
    # Crear ventana de simulación con la configuración seleccionada
    create_simulation_window(max_laps)

if __name__ == "__main__":
    main()
