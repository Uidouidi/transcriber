"""
Controlador principal - Mantiene la lógica de control del main.py original
"""
import threading
import sys
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from grabador import Grabador
from transcriptor import Transcriptor
from gestor_teclado import GestorTeclado
from interfaz import InterfazVisual
from utils import (
    cargar_configuracion, 
    copiar_al_portapapeles, 
    notificar,
    guardar_transcripcion
)

class ControladorPrincipal:
    def __init__(self):
        # Cargar configuración
        self.config = cargar_configuracion()
        
        # Variables de control (mantener como en el original)
        self.grabando = False
        self.hilo_grabacion = None
        
        # Inicializar componentes
        self.grabador = Grabador(self.config)
        self.transcriptor = Transcriptor(self.config)
        self.gestor_teclado = GestorTeclado(self.config)
        self.interfaz = InterfazVisual(self.config)
        
        # ThreadPool para mejor gestión
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Configurar callbacks
        self.gestor_teclado.on_grabar = self.grabar_y_transcribir
        self.gestor_teclado.on_cerrar = self.cerrar_programa
        
        # Timer para notificaciones durante grabación
        self.timer_notificacion = None
        self.tiempo_inicio_grabacion = None
        
    def iniciar(self):
        """Inicia la aplicación"""
        print("⚡ Presiona Alt + Shift + X para iniciar/detener la grabación.")
        print("🛑 Presiona F8 para salir.")
        
        # Iniciar interfaz visual si está habilitada
        if self.config['interfaz']['mostrar_indicador']:
            self.interfaz.iniciar()
            
        # Iniciar gestor de teclado (bloquea hasta salir)
        self.gestor_teclado.iniciar()
        
    def grabar_y_transcribir(self):
        """Lógica original de grabación y transcripción"""
        if not self.grabando:
            # Inicia la grabación en un hilo aparte
            self.grabando = True
            self.tiempo_inicio_grabacion = time.time()
            print("🎙️ Grabación iniciada. Pulsa Alt + Shift + X para detener.")
            
            # Actualizar interfaz visual
            self.interfaz.set_estado('grabando')
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.audio_filename = f"{timestamp}.wav"
            
            self.grabador.start_recording()
            self.hilo_grabacion = threading.Thread(target=self.grabador.iniciar_grabacion)
            self.hilo_grabacion.start()
            
            # Iniciar timer de notificaciones
            self._iniciar_timer_notificacion()
            
        else:
            # Detener la grabación
            self.grabando = False
            self._detener_timer_notificacion()
            
            # Actualizar interfaz visual
            self.interfaz.set_estado('transcribiendo')
            
            audio_file = self.grabador.stop_recording(self.audio_filename)
            print("✅ Grabación detenida.")
            
            # Validar archivo de audio antes de transcribir
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                # Ejecutar transcripción en el ThreadPool
                future = self.executor.submit(self._procesar_transcripcion, audio_file)
            else:
                print("❌ Error: Archivo de audio inválido")
                notificar("Error al grabar audio")
                self.interfaz.set_estado('idle')
                
    def _procesar_transcripcion(self, audio_file):
        """Procesa la transcripción y guarda los resultados"""
        try:
            texto = self.transcriptor.transcribir_audio(audio_file)
            
            if texto:
                # Guardar según configuración
                if self.config['formatos_salida']['clipboard']:
                    copiar_al_portapapeles(texto)
                    
                if self.config['formatos_salida']['txt_file']:
                    guardar_transcripcion(texto, audio_file, self.config)
                    
                notificar("La transcripción está lista para pegar.")
                print(f"🗒️ Transcripción: {texto}")
            else:
                notificar("Error en la transcripción")
                
        except Exception as e:
            print(f"❌ Error al procesar transcripción: {e}")
            notificar("Error al procesar transcripción")
            
        finally:
            # Volver a estado idle
            self.interfaz.set_estado('idle')
            
    def _iniciar_timer_notificacion(self):
        """Inicia el timer para notificaciones periódicas"""
        minutos = self.config['notificar_cada_minutos']
        if minutos > 0:
            self.timer_notificacion = threading.Timer(
                minutos * 60, 
                self._notificar_tiempo_grabacion
            )
            self.timer_notificacion.start()
            
    def _detener_timer_notificacion(self):
        """Detiene el timer de notificaciones"""
        if self.timer_notificacion:
            self.timer_notificacion.cancel()
            self.timer_notificacion = None
            
    def _notificar_tiempo_grabacion(self):
        """Notifica el tiempo transcurrido de grabación"""
        if self.grabando and self.tiempo_inicio_grabacion:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio_grabacion)
            minutos = tiempo_transcurrido // 60
            segundos = tiempo_transcurrido % 60
            
            mensaje = f"Grabando: {minutos}:{segundos:02d}"
            self.interfaz.actualizar_tiempo(mensaje)
            notificar(mensaje)
            
            # Reiniciar timer
            self._iniciar_timer_notificacion()
            
    def cerrar_programa(self):
        """Lógica original de cierre limpio"""
        print("🛑 Cerrando programa...")
        
        # Detener timer de notificaciones
        self._detener_timer_notificacion()
        
        # Asegurar que la grabación esté detenida
        if self.grabando:
            print("🔴 Deteniendo grabación antes de salir...")
            self.grabando = False
            self.grabador.stop_recording()
            
        # Intentar liberar recursos del teclado
        try:
            print("🗑️ Liberando recursos del teclado...")
            self.gestor_teclado.detener()
        except Exception as e:
            print(f"⚠️ Error al liberar teclado: {e}")
            
        # Cerrar interfaz visual
        self.interfaz.cerrar()
        
        # Cerrar ThreadPool
        self.executor.shutdown(wait=False)
        
        # Asegurar el cierre de hilos activos (excluyendo el principal)
        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                print(f"🧵 Hilo activo detectado: {thread.name}")
                try:
                    thread.join(timeout=1)
                except RuntimeError:
                    print(f"❌ No se puede unir el hilo actual: {thread.name}")
                    
        # Liberar el modelo de Whisper
        try:
            self.transcriptor.liberar_modelo()
        except Exception as e:
            print(f"⚠️ Error al liberar el modelo: {e}")
            
        # Espera breve para liberación
        time.sleep(0.5)
        
        # Cierre forzado si persisten hilos activos
        if threading.active_count() > 1:
            print("💥 Cierre forzado por hilos persistentes.")
            os._exit(0)
            
        print("✅ Programa cerrado correctamente.")
        sys.exit(0)