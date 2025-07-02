"""
Utilidades - Fusión de clipboard.py, notifier.py y funciones de configuración
"""
import json
import os
from pathlib import Path
from datetime import datetime
import pyperclip
from plyer import notification

def cargar_configuracion():
    """Carga la configuración desde config.json"""
    config_path = Path("config.json")
    
    # Configuración por defecto
    config_default = {
        "atajos": {
            "grabar": "alt+shift+x",
            "cerrar": "f8"
        },
        "whisper_model": "base",
        "directorio_salida": "./grabaciones/",
        "notificar_cada_minutos": 5,
        "formatos_salida": {
            "clipboard": True,
            "txt_file": True,
            "json_with_metadata": False,
            "srt_subtitles": False
        },
        "interfaz": {
            "mostrar_indicador": True,
            "posicion_x": 100,
            "posicion_y": 100
        }
    }
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Fusionar con valores por defecto para campos faltantes
                return {**config_default, **config}
        else:
            # Crear archivo de configuración con valores por defecto
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_default, f, indent=4, ensure_ascii=False)
            print("📄 Archivo config.json creado con valores por defecto")
            return config_default
            
    except Exception as e:
        print(f"⚠️ Error al cargar configuración: {e}")
        return config_default

def copiar_al_portapapeles(texto):
    """Copia texto al portapapeles"""
    try:
        pyperclip.copy(texto)
        print("📋 Texto copiado al portapapeles.")
        return True
    except Exception as e:
        print(f"❌ Error al copiar: {e}")
        return False

def notificar(mensaje):
    """Muestra una notificación del sistema"""
    try:
        notification.notify(
            title="Transcripción Completa",
            message=mensaje,
            timeout=5,
            app_name="Transcriptor",
            app_icon=None  # Sin icono para evitar el sonido de alerta
        )
    except Exception as e:
        print(f"⚠️ Error al mostrar notificación: {e}")

def guardar_transcripcion(texto, audio_file, config):
    """Guarda la transcripción en archivo(s) según la configuración"""
    try:
        # Obtener el nombre base del archivo
        audio_path = Path(audio_file)
        base_name = audio_path.stem
        directorio = Path(config['directorio_salida'])
        
        # Guardar como archivo de texto
        if config['formatos_salida']['txt_file']:
            txt_path = directorio / f"{base_name}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"📝 Transcripción guardada en: {txt_path}")
            
        # Guardar como JSON con metadata
        if config['formatos_salida']['json_with_metadata']:
            json_path = directorio / f"{base_name}.json"
            metadata = {
                "audio_file": audio_file,
                "timestamp": datetime.now().isoformat(),
                "modelo": config['whisper_model'],
                "transcripcion": texto,
                "duracion_caracteres": len(texto),
                "palabras": len(texto.split())
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"📊 Metadata guardada en: {json_path}")
            
        # Guardar como subtítulos SRT
        if config['formatos_salida']['srt_subtitles']:
            srt_path = directorio / f"{base_name}.srt"
            # Crear un SRT simple con todo el texto
            srt_content = f"1\n00:00:00,000 --> 00:00:10,000\n{texto}\n"
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"🎬 Subtítulos guardados en: {srt_path}")
            
    except Exception as e:
        print(f"❌ Error al guardar transcripción: {e}")
        
def validar_directorio(directorio):
    """Valida y crea el directorio si no existe"""
    try:
        path = Path(directorio)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Error al crear directorio {directorio}: {e}")
        return False