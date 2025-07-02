"""
Gestor de atajos de teclado
"""
import keyboard
import threading

class GestorTeclado:
    def __init__(self, config):
        self.config = config
        self.on_grabar = None  # Callback para grabar
        self.on_cerrar = None  # Callback para cerrar
        self._activo = False
        
    def iniciar(self):
        """Inicia el gestor de teclado"""
        self._activo = True
        
        # Obtener atajos de la configuración
        atajo_grabar = self.config['atajos']['grabar']
        atajo_cerrar = self.config['atajos']['cerrar']
        
        # Asignar los atajos de teclado
        keyboard.add_hotkey(atajo_grabar, self._manejar_grabar)
        keyboard.add_hotkey(atajo_cerrar, self._manejar_cerrar)
        
        # Esperar eventos (bloquea)
        keyboard.wait()
        
    def _manejar_grabar(self):
        """Maneja el atajo de grabación"""
        if self.on_grabar and self._activo:
            # Ejecutar en un hilo separado para no bloquear
            threading.Thread(target=self.on_grabar).start()
            
    def _manejar_cerrar(self):
        """Maneja el atajo de cierre"""
        if self.on_cerrar and self._activo:
            self._activo = False
            self.on_cerrar()
            
    def detener(self):
        """Detiene el gestor y libera recursos"""
        self._activo = False
        try:
            keyboard.unhook_all()
        except Exception as e:
            print(f"⚠️ Error al liberar hooks de teclado: {e}")