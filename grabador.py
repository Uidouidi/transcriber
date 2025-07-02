"""
Módulo de grabación de audio - Evolución de recorder.py
"""
import sounddevice as sd
import numpy as np
import wave
import os
from pathlib import Path

class Grabador:
    def __init__(self, config):
        self.config = config
        # Variables globales para el control (mantener como el original)
        self.is_recording = False
        self.fs = 44100  # Frecuencia de muestreo
        self.audio_data = []
        
        # Asegurar que el directorio de salida existe
        self.directorio_salida = Path(config['directorio_salida'])
        self.directorio_salida.mkdir(exist_ok=True)
        
    def start_recording(self):
        """Inicia la grabación"""
        self.is_recording = True
        self.audio_data = []
        print("🎙️ Grabación iniciada. Pulsa Alt + Shift + X para detener.")
        
    def stop_recording(self, filename="grabacion.wav"):
        """Detiene la grabación y guarda el archivo"""
        self.is_recording = False
        print("✅ Grabación detenida.")
        
        # Construir ruta completa del archivo
        filepath = self.directorio_salida / filename
        
        try:
            # Convertir la lista de fragmentos en un array
            if self.audio_data:
                audio = np.concatenate(self.audio_data, axis=0)
                
                # Guardar el audio en un archivo WAV
                with wave.open(str(filepath), 'wb') as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)  # 16 bits = 2 bytes
                    f.setframerate(self.fs)
                    f.writeframes(audio.tobytes())
                    
                print(f"💾 Archivo guardado: {filepath}")
                return str(filepath)
            else:
                print("⚠️ No hay datos de audio para guardar")
                return None
                
        except Exception as e:
            print(f"❌ Error al guardar archivo: {e}")
            return None
            
    def audio_callback(self, indata, frames, time, status):
        """Callback para capturar audio"""
        if status:
            print(f"⚠️ Estado del audio: {status}")
            
        if self.is_recording:
            self.audio_data.append(indata.copy())
            
    def iniciar_grabacion(self):
        """Hilo de grabación continua"""
        try:
            with sd.InputStream(
                samplerate=self.fs, 
                channels=1, 
                dtype=np.int16, 
                callback=self.audio_callback
            ):
                while self.is_recording:
                    sd.sleep(100)
        except Exception as e:
            print(f"❌ Error en la grabación: {e}")
            self.is_recording = False