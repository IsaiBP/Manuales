# DriveGuard AI — prototipo demostrativo en Python

**Importante:** este programa **no usa cámara ni inteligencia artificial**. Genera y evalúa **datos simulados** para demostrar la lógica del sistema. Es exclusivamente académico. No instalar ni usar como dispositivo de seguridad en un vehículo.

## Requisitos

- Python 3.11 o posterior, con `tkinter` disponible (habitualmente incluido en instalaciones estándar de Python para Windows).
- `matplotlib` para las gráficas de eventos: `pip install matplotlib`
- Pantalla de computadora; no requiere webcam ni Internet.

## Ejecutar

1. Descarga y descomprime `DriveGuardAI_Demo.zip`.
2. Abre una terminal en la carpeta `DriveGuardAI_Demo`.
3. Ejecuta:

```bash
python app.py
```

En algunos equipos Windows, se puede usar `py app.py`.

## Acceso local

Al abrir el programa aparece una ventana de acceso creada en `login.py`. En el primer uso, escribe un usuario y una contraseña de al menos ocho caracteres y pulsa **Crear cuenta**. Se abre el panel principal. En los siguientes usos, introduce esos mismos datos y pulsa **Entrar** o presiona Enter desde el campo de contraseña.

Se admite una sola cuenta local, guardada en `data/cuenta.json` con salt aleatorio y hash PBKDF2-HMAC-SHA256, no con la contraseña en texto plano. El archivo está excluido de Git. No se requieren paquetes externos. No hay recuperación de contraseña ni gestión de múltiples usuarios.

Este acceso es básico para la demostración: no protege el CSV frente a personas con acceso al equipo ni sustituye los permisos del sistema operativo. Los manuales Word generados antes de este cambio todavía no incluyen el login.

## Cómo hacer la demostración

1. Selecciona **Conducción normal** y observa el estado `NORMAL`.
2. Selecciona **Cansancio leve** y observa `PRECAUCIÓN`.
3. Selecciona **Somnolencia alta** y observa `ALERTA ALTA` y una señal sonora del sistema (si está disponible).
4. Selecciona **Rostro no visible** y observa `SIN ROSTRO`, que significa que la evaluación no es posible; **no** es una detección de somnolencia.
5. También puedes ajustar los controles manualmente o presionar **Iniciar demostración automática**.
6. Usa **Registrar lectura en CSV** para guardar un ejemplo y presentar el historial.
7. Con el estado en `PRECAUCIÓN` o `ALERTA ALTA`, abre **Plan de acción (búsqueda IA)** para ver la secuencia de acciones sugeridas calculada con BFS, DFS, UCS, Greedy o A*, comparar los cinco algoritmos y probar la calibración de umbrales con Hill Climbing y algoritmo genético.

## Búsqueda en IA (busqueda.py)

El proyecto aplica los temas de búsqueda sobre un grafo de acciones correctivas:

- **Problema de búsqueda** `P=(S,A,s0,G,C)`: estados = niveles de riesgo (`PRECAUCIÓN`, `ALERTA ALTA`), acciones = correcciones con costo en puntos, estado inicial = nivel actual, objetivo = `NORMAL`.
- **BFS / DFS**: encuentran una ruta de acciones sin usar costos ni heurística.
- **UCS**: ruta de menor costo acumulado `g(n)`.
- **Heurística** `h(n)`: puntos mínimos restantes estimados; admisible sobre el grafo.
- **Greedy**: elige solo por `h(n)` — puede dar una ruta más cara (4) que A* (3).
- **A***: `f(n) = g(n) + h(n)`, encuentra la ruta de menor costo.
- **Hill Climbing**: ajusta un umbral (`blinks_caution_per_minute`) para reducir errores en lecturas etiquetadas.
- **Algoritmo genético**: evoluciona los seis umbrales con torneo, cruza, mutación y semilla fija.

Costos, heurística y lecturas etiquetadas son ilustrativos para la demostración; no corresponden a tiempos reales ni a eficacia validada de las acciones.

## Archivos

```text
DriveGuardAI_Demo/
├── app.py              # Interfaz de escritorio (Tkinter)
├── login.py            # Acceso local con cuenta y contraseña
├── core.py             # Datos, reglas de evaluación y registro CSV
├── busqueda.py         # BFS, DFS, UCS, Greedy, A*, Hill Climbing y genético
├── busqueda_ui.py      # Ventana "Plan de acción" con los algoritmos
├── graficas.py         # Ventana de gráficas matplotlib sobre eventos.csv
├── requirements.txt    # Sin dependencias externas en el modo simulado
├── tests/
│   └── test_core.py    # Pruebas automatizadas
├── data/
│   └── .gitkeep        # eventos.csv se crea durante la ejecución
└── README.md
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Datos registrados

El archivo `data/eventos.csv` se crea automáticamente cuando cambia el estado a `PRECAUCIÓN`, `ALERTA ALTA` o `SIN ROSTRO`, o cuando el usuario selecciona **Registrar lectura en CSV**. No se guarda ningún video, imagen ni dato real de personas.

## Reglas ilustrativas (NO validadas)

- Ojos cerrados ≥ 1.2 s: +2 puntos.
- Ojos cerrados ≥ 2.5 s: +4 puntos, en lugar de los +2 anteriores.
- Parpadeos ≥ 28 por minuto: +1.
- Bostezos ≥ 3 por minuto: +2.
- Inclinación absoluta ≥ 25°: +2.
- 0–1 puntos: `NORMAL`; 2–3: `PRECAUCIÓN`; ≥ 4: `ALERTA ALTA`.
- Rostro no visible: `SIN ROSTRO`; no se infiere fatiga.

Estos valores fueron elegidos para facilitar la demostración y no deben describirse como umbrales médicos ni como resultado de entrenamiento o validación.

## Próxima etapa: cámara real

Implementar adquisición con OpenCV y detección de landmarks faciales con MediaPipe Face Landmarker, calibración por persona, manejo de iluminación y oclusiones, pruebas reproducibles, aviso de privacidad y tratamiento de pérdida de cámara. La tecnología permite extraer señales faciales, **no** identifica la somnolencia de forma infalible.

Referencia: https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python
