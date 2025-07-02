"""
Módulo de transcripción - Evolución de transcriber.py
"""
import whisper
import os
import logging

# Configurar logging para depuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Transcriptor:
    def __init__(self, config):
        self.config = config
        self.model = None
        self._cargar_modelo()
        
    def _cargar_modelo(self):
        """Carga el modelo Whisper una sola vez"""
        try:
            modelo_nombre = self.config.get('whisper_model', 'base')
            print(f"🔄 Cargando modelo Whisper '{modelo_nombre}' en CPU...")
            self.model = whisper.load_model(modelo_nombre, device="cpu")
            print("✅ Modelo cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar modelo: {e}")
            raise
            
    def transcribir_audio(self, filename):
        """Transcribe el archivo de audio"""
        print("📝 Transcribiendo...")
        
        # Validar que el archivo existe
        if not os.path.exists(filename):
            logger.error(f"Archivo no encontrado: {filename}")
            return ""
            
        # Validar tamaño del archivo
        file_size = os.path.getsize(filename)
        if file_size == 0:
            logger.error("Archivo de audio vacío")
            return ""
            
        logger.info(f"Tamaño del archivo: {file_size} bytes")
        
        try:
            # Transcripción optimizada usando el modelo cargado previamente
            result = self.model.transcribe(
                filename, 
                language="es", 
                fp16=False, 
                temperature=0.0
            )
            
            texto = result['text'].strip()
            
            # Log de segmentos para depuración si está vacío
            if not texto:
                logger.warning("Transcripción vacía")
                if 'segments' in result:
                    logger.info(f"Segmentos detectados: {len(result['segments'])}")
                    
            print("✅ Transcripción completa.")
            return texto
            
        except Exception as e:
            logger.error(f"Error al transcribir: {e}")
            # Intentar recuperación con diferentes parámetros
            try:
                logger.info("Intentando transcripción con parámetros alternativos...")
                result = self.model.transcribe(
                    filename,
                    language="es",
                    fp16=False,
                    temperature=0.5,  # Mayor temperatura para más diversidad
                    suppress_tokens=""  # No suprimir tokens
                )
                texto = result['text'].strip()
                logger.info("Transcripción alternativa exitosa")
                return texto
            except Exception as e2:
                logger.error(f"Fallo en transcripción alternativa: {e2}")
                return ""
                
    def liberar_modelo(self):
        """Libera el modelo de la memoria"""
        self.model = None
        print("🗑️ Modelo liberado de la memoria.")