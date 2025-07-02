"""
Interfaz visual mínima - Cuadradito de estado
"""
import os
import threading
import queue
import sys

# Configurar variables de entorno para Tcl/Tk antes de importar tkinter
if sys.platform == "win32":
    os.environ['TCL_LIBRARY'] = r'C:\Users\Uidi\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'C:\Users\Uidi\AppData\Local\Programs\Python\Python313\tcl\tk8.6'

# Intentar importar tkinter con manejo de errores
try:
    import tkinter as tk
    TKINTER_DISPONIBLE = True
except ImportError:
    TKINTER_DISPONIBLE = False
    print("⚠️ Tkinter no está disponible. La interfaz visual estará deshabilitada.")
except Exception as e:
    TKINTER_DISPONIBLE = False
    print(f"⚠️ Error al importar tkinter: {e}")

class InterfazVisual:
    def __init__(self, config):
        self.config = config
        self.root = None
        self.canvas = None
        self.hilo_interfaz = None
        self.cola_comandos = queue.Queue()
        self._ejecutando = False
        
        # Colores para los estados
        self.colores = {
            'idle': '#00FF00',      # Verde
            'grabando': '#FF0000',   # Rojo
            'transcribiendo': '#0080FF'  # Azul
        }
        
        # Estado actual
        self.estado_actual = 'idle'
        
        # Verificar disponibilidad de tkinter
        if not TKINTER_DISPONIBLE:
            print("ℹ️ Interfaz visual deshabilitada. La aplicación funcionará sin indicador visual.")
            self.config['interfaz']['mostrar_indicador'] = False
        
    def iniciar(self):
        """Inicia la interfaz en un hilo separado"""
        if self.config['interfaz']['mostrar_indicador'] and TKINTER_DISPONIBLE:
            self._ejecutando = True
            self.hilo_interfaz = threading.Thread(target=self._ejecutar_interfaz)
            self.hilo_interfaz.daemon = True
            self.hilo_interfaz.start()
            
    def _ejecutar_interfaz(self):
        """Ejecuta la interfaz gráfica"""
        try:
            self.root = tk.Tk()
            
            # Configurar ventana
            self.root.overrideredirect(True)  # Sin bordes
            self.root.attributes('-topmost', True)  # Siempre visible
            self.root.attributes('-alpha', 0.9)  # Ligeramente transparente
            
            # Tamaño y posición
            size = 20
            x = self.config['interfaz'].get('posicion_x', 100)
            y = self.config['interfaz'].get('posicion_y', 100)
            self.root.geometry(f"{size}x{size}+{x}+{y}")
            
            # Canvas para el cuadrado
            self.canvas = tk.Canvas(
                self.root, 
                width=size, 
                height=size, 
                highlightthickness=0,
                bg='black'
            )
            self.canvas.pack()
            
            # Dibujar el cuadrado inicial
            self.cuadrado = self.canvas.create_rectangle(
                0, 0, size, size,
                fill=self.colores[self.estado_actual],
                outline='black',
                width=1
            )
            
            # Hacer la ventana arrastrable
            self.canvas.bind("<ButtonPress-1>", self._iniciar_arrastre)
            self.canvas.bind("<B1-Motion>", self._arrastrar)
            
            # Procesar comandos de la cola
            self._procesar_cola()
            
            # Iniciar el bucle principal
            self.root.mainloop()
            
        except Exception as e:
            print(f"❌ Error al crear interfaz visual: {e}")
            print("ℹ️ La aplicación continuará funcionando sin indicador visual.")
            self.config['interfaz']['mostrar_indicador'] = False
            self._ejecutando = False
        
    def _iniciar_arrastre(self, event):
        """Inicia el arrastre de la ventana"""
        self._x = event.x
        self._y = event.y
        
    def _arrastrar(self, event):
        """Arrastra la ventana"""
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
        # Actualizar configuración
        self.config['interfaz']['posicion_x'] = x
        self.config['interfaz']['posicion_y'] = y
        
    def _procesar_cola(self):
        """Procesa comandos de la cola"""
        try:
            while True:
                comando = self.cola_comandos.get_nowait()
                if comando['tipo'] == 'estado':
                    self._cambiar_color(comando['valor'])
                elif comando['tipo'] == 'cerrar':
                    self.root.quit()
                    return
        except queue.Empty:
            pass
            
        if self._ejecutando:
            self.root.after(100, self._procesar_cola)
            
    def _cambiar_color(self, estado):
        """Cambia el color del cuadrado"""
        if estado in self.colores and self.canvas:
            self.canvas.itemconfig(
                self.cuadrado, 
                fill=self.colores[estado]
            )
            self.estado_actual = estado
            
    def set_estado(self, estado):
        """Cambia el estado de la interfaz"""
        if TKINTER_DISPONIBLE and self._ejecutando:
            self.cola_comandos.put({'tipo': 'estado', 'valor': estado})
        else:
            # Mostrar estado en consola como alternativa
            estados_emoji = {
                'idle': '🟢',
                'grabando': '🔴',
                'transcribiendo': '🔵'
            }
            print(f"{estados_emoji.get(estado, '⚪')} Estado: {estado}")
            
    def actualizar_tiempo(self, mensaje):
        """Actualiza el tooltip con el tiempo (para futuras mejoras)"""
        # Por ahora solo cambiamos el título de la ventana
        if self.root and TKINTER_DISPONIBLE:
            self.cola_comandos.put({'tipo': 'titulo', 'valor': mensaje})
            
    def cerrar(self):
        """Cierra la interfaz"""
        self._ejecutando = False
        if self.root and TKINTER_DISPONIBLE:
            try:
                self.cola_comandos.put({'tipo': 'cerrar'})
            except:
                pass