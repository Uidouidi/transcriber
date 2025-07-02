# Aplicación de Grabación y Transcripción v2.0

## 🚀 Características

- **Grabación de audio** con un solo atajo de teclado (Alt+Shift+X)
- **Transcripción automática** usando Whisper de OpenAI
- **Interfaz visual mínima**: Cuadradito de 20x20px que indica el estado
  - 🟢 Verde: Esperando (idle)
  - 🔴 Rojo: Grabando
  - 🔵 Azul: Transcribiendo
- **Copia automática al portapapeles** al finalizar
- **Guardado permanente** de archivos WAV y TXT con timestamp
- **Notificaciones del sistema** cada 5 minutos durante grabaciones largas
- **Configuración externa** via `config.json`
- **Manejo robusto de errores** y cierre limpio de recursos

## 📋 Requisitos

- Python 3.8+
- Las siguientes dependencias (ya instaladas según tu entorno):
  ```
  openai-whisper==20240930
  sounddevice==0.5.1
  keyboard==0.13.5
  pyperclip==1.9.0
  plyer==2.1.0
  numpy==2.2.5
  torch==2.7.0
  ```

## 🛠️ Instalación

1. Crea un directorio para la aplicación:
   ```bash
   mkdir transcriptor-v2
   cd transcriptor-v2
   ```

2. Copia todos los archivos Python en el directorio:
   - `main.py`
   - `controlador.py`
   - `grabador.py`
   - `transcriptor.py`
   - `gestor_teclado.py`
   - `interfaz.py`
   - `utils.py`
   - `config.json`

3. El directorio `grabaciones/` se creará automáticamente al ejecutar.

## 🎮 Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Atajos de teclado

- **Alt + Shift + X**: Iniciar/detener grabación
- **F8**: Cerrar la aplicación

### Flujo de trabajo

1. Ejecuta la aplicación
2. Aparecerá un cuadradito verde en la esquina superior izquierda
3. Presiona Alt+Shift+X para empezar a grabar (cuadradito se pone rojo)
4. Habla lo que necesites transcribir
5. Presiona Alt+Shift+X de nuevo para detener (cuadradito se pone azul)
6. La transcripción se copiará automáticamente al portapapeles
7. Los archivos se guardarán en `grabaciones/` con timestamp

## ⚙️ Configuración

Edita `config.json` para personalizar:

```json
{
    "atajos": {
        "grabar": "alt+shift+x",
        "cerrar": "f8"
    },
    "whisper_model": "base",
    "directorio_salida": "./grabaciones/",
    "notificar_cada_minutos": 5,
    "formatos_salida": {
        "clipboard": true,
        "txt_file": true,
        "json_with_metadata": false,
        "srt_subtitles": false
    },
    "interfaz": {
        "mostrar_indicador": true,
        "posicion_x": 100,
        "posicion_y": 100
    }
}
```

### Modelos de Whisper disponibles

- `tiny`: Más rápido, menos preciso
- `base`: Balance entre velocidad y precisión (recomendado)
- `small`: Más preciso, más lento
- `medium`: Alta precisión, requiere más recursos
- `large`: Máxima precisión, muy lento

## 🔧 Solución de problemas

### El programa no se cierra correctamente
- Usa F8 para un cierre limpio
- Si se congela, cierra la terminal

### No aparece el cuadradito visual
- Verifica que `"mostrar_indicador": true` en config.json
- En algunos sistemas Linux puede requerir permisos adicionales

### Error de permisos en Linux/Mac
- Ejecuta con sudo: `sudo python main.py`
- O configura permisos para captura de teclado global

### La transcripción está vacía
- Verifica que el micrófono esté funcionando
- Prueba con un modelo de Whisper diferente
- Revisa que el archivo WAV no esté vacío en `grabaciones/`

## 📁 Estructura de archivos generados

```
grabaciones/
├── 2025-06-13_14-30-25.wav    # Audio original
├── 2025-06-13_14-30-25.txt    # Transcripción
├── 2025-06-13_14-35-42.wav
└── 2025-06-13_14-35-42.txt
```

## 🔄 Diferencias con v1.0

- **Estructura modular**: Código separado en módulos específicos
- **Configuración externa**: No need modificar código para cambiar ajustes
- **Interfaz visual**: Indicador de estado siempre visible
- **Nombres con timestamp**: Archivos únicos para cada grabación
- **Notificaciones periódicas**: Útil para grabaciones largas
- **Mejor manejo de errores**: Recuperación ante fallos
- **ThreadPoolExecutor**: Gestión mejorada de hilos

## ⚠️ Notas importantes

- La aplicación requiere permisos de administrador en Windows para capturar teclas globalmente
- Los archivos WAV pueden ser grandes; considera limpiar periódicamente
- El modelo Whisper se carga en memoria al iniciar (puede tomar unos segundos)
- La posición del cuadradito se guarda automáticamente al arrastrarlo