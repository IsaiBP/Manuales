from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
FECHA = '30/10/2026'


def field(p, instruction, placeholder=''):
    r = OxmlElement('w:r')
    begin = OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'), 'begin'); r.append(begin); p._p.append(r)
    r = OxmlElement('w:r'); text = OxmlElement('w:instrText'); text.set(qn('xml:space'), 'preserve'); text.text = instruction; r.append(text); p._p.append(r)
    r = OxmlElement('w:r'); sep = OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'), 'separate'); r.append(sep); p._p.append(r)
    if placeholder:
        p.add_run(placeholder)
    r = OxmlElement('w:r'); end = OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'), 'end'); r.append(end); p._p.append(r)


def table(d, heads, rows):
    t = d.add_table(rows=1, cols=len(heads)); t.style = 'Light Shading Accent 1'
    for c, v in zip(t.rows[0].cells, heads):
        c.text = str(v)
    for row in rows:
        for c, v in zip(t.add_row().cells, row):
            c.text = str(v)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
    d.add_paragraph()


def p(d, text):
    d.add_paragraph(text)


def h(d, text):
    d.add_heading(text, level=1)


def sub(d, text):
    d.add_heading(text, level=2)


def bullets(d, lines):
    for line in lines:
        d.add_paragraph(line, style='List Bullet')


def code(d, text):
    for line in text.splitlines():
        r = d.add_paragraph().add_run(line)
        r.font.name = 'Consolas'; r.font.size = Pt(9)


def imagen(d, nombre, caption):
    """Inserta la captura si existe en capturas/; si no, deja la marca."""
    ruta = ROOT / 'capturas' / nombre
    if ruta.exists():
        d.add_picture(str(ruta), width=Inches(5.8))
        d.add_paragraph(caption, style='Caption')
    else:
        ph = d.add_paragraph()
        ph.alignment = 1
        run = ph.add_run(f'[AQUÍ VA IMAGEN: {nombre}  →  {caption}]')
        run.bold = True
        run.font.color.rgb = RGBColor.from_string('B45309')


def base(kind, audience):
    d = Document(); sec = d.sections[0]
    sec.top_margin = Inches(.8); sec.bottom_margin = Inches(.8)
    sec.left_margin = Inches(.85); sec.right_margin = Inches(.85)
    normal = d.styles['Normal']; normal.font.name = 'Calibri'; normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(7)
    for name in ['Title', 'Heading 1', 'Heading 2']:
        d.styles[name].font.color.rgb = RGBColor.from_string('1F3B63')
    sec.header.paragraphs[0].text = 'DRIVEGUARD AI  |  Prototipo educativo de simulación'
    foot = sec.footer.paragraphs[0]; foot.alignment = 2
    foot.add_run('Versión documental 2.0  |  Página '); field(foot, ' PAGE ')
    d.add_paragraph('DRIVEGUARD AI', style='Title')
    d.add_paragraph(kind, style='Subtitle')
    p(d, 'Prototipo de escritorio con datos simulados\n'
         'Versión documental: 2.0\nFecha: 30 de octubre de 2026')
    p(d, 'Dirigido a: ' + audience)
    p(d, 'Autor o equipo: [Completar antes de entregar]\n'
         'Institución y asignatura: [Completar antes de entregar]\n'
         'Docente: [Completar antes de entregar]')
    p(d, 'Alcance: versión local en Python, Tkinter y matplotlib. No utiliza cámara '
         'ni un modelo de inteligencia artificial entrenado. No constituye un '
         'dispositivo de seguridad vial ni una herramienta de diagnóstico.')
    d.add_page_break(); h(d, 'Control de versiones')
    table(d, ['Versión', 'Fecha', 'Responsable', 'Descripción'], [
        ('1.0', '22/10/2026', '[Equipo]', 'Primer manual: simulador con evaluación por reglas y CSV.'),
        ('2.0', FECHA, '[Equipo]', 'Acceso con cuenta local, menú lateral y páginas, plan de acción con algoritmos de búsqueda, calibración de umbrales y gráficas.')])
    p(d, 'Registrar aquí cada revisión posterior con versión, fecha, responsable y cambios.')
    d.add_page_break(); h(d, 'Índice automático')
    field(d.add_paragraph(), ' TOC \\o "1-2" \\h \\z \\u ',
          'Para generar el índice: clic derecho aquí → Actualizar campos → Actualizar toda la tabla.')
    p(d, 'En Microsoft Word, actualizar el índice antes de entregar o exportar a PDF. '
         'Los encabezados usan estilos Título 1 y Título 2. Si Word solicita '
         'actualizar los campos al abrir, aceptar.')
    settings = d.settings.element
    upd = OxmlElement('w:updateFields'); upd.set(qn('w:val'), 'true'); settings.append(upd)
    d.add_page_break()
    return d


def glossary(d, technical=False):
    rows = [('Simulación', 'Representación mediante valores de ejemplo; no son mediciones de una persona.'),
            ('Escenario', 'Conjunto predefinido de valores para una demostración.'),
            ('Lectura', 'Conjunto de valores actuales que se evalúan.'),
            ('Umbral', 'Valor a partir del cual se aplica una regla.'),
            ('CSV', 'Archivo de texto con datos organizados en filas y columnas.'),
            ('Estado', 'Resultado de la evaluación: NORMAL, PRECAUCIÓN, ALERTA ALTA o SIN ROSTRO.'),
            ('Bitácora', 'Registro de eventos guardados con su fecha, señales y resultado.')]
    if technical:
        rows += [('Tkinter / TTK', 'Biblioteca de Python para interfaces gráficas y sus componentes.'),
                 ('Problema de búsqueda', 'Tupla P=(S,A,s0,G,C): estados, acciones, inicio, objetivo y costo.'),
                 ('Heurística h(n)', 'Estimación del costo que falta para llegar al objetivo.'),
                 ('A*', 'Búsqueda informada con f(n)=g(n)+h(n); óptima si h no sobreestima.'),
                 ('Hill Climbing', 'Optimización que se mueve al mejor vecino mientras mejore.'),
                 ('Algoritmo genético', 'Optimización que evoluciona una población con selección, cruza y mutación.'),
                 ('PBKDF2', 'Función de derivación de clave usada para el hash de la contraseña.'),
                 ('Persistencia', 'Conservación de datos en un archivo después de cerrar el programa.'),
                 ('Prueba unitaria', 'Comprobación automatizada de una parte específica del código.')]
    table(d, ['Término', 'Definición'], rows)


def technical():
    d = base('MANUAL TÉCNICO', 'personal que dará mantenimiento, desarrolladores y responsables de pruebas.')

    h(d, '1. Introducción')
    p(d, 'Este manual describe la operación interna, configuración, datos, pruebas y '
         'mantenimiento de DriveGuard AI. Su finalidad es permitir que otra persona '
         'comprenda el código, realice cambios controlados y verifique sus efectos '
         'sin atribuir al prototipo capacidades inexistentes.')
    p(d, 'La revisión comprende app.py, login.py, core.py, busqueda.py, busqueda_ui.py, '
         'graficas.py, requirements.txt, README.md, tests/ y el CSV de ejemplo. '
         'El programa demuestra reglas ilustrativas sobre cinco señales sintéticas, '
         'un plan de acción calculado con algoritmos de búsqueda clásicos de IA y '
         'calibración de umbrales por optimización. No captura video, no mide fatiga '
         'real ni transmite datos por red. El glosario se encuentra después de las '
         'referencias.')

    h(d, '2. Descripción general y requisitos funcionales y no funcionales')
    p(d, 'Aplicación local de escritorio con acceso por cuenta, menú lateral y tres '
         'páginas (Inicio, Registros, Ayuda). El usuario modifica señales o activa '
         'una secuencia automática; la interfaz muestra un estado y motivos. '
         'Determinados cambios y las lecturas solicitadas se agregan a un archivo '
         'CSV. Con nivel de riesgo activo puede pedirse un plan de acciones '
         'correctivas calculado por búsqueda, y los eventos pueden graficarse y '
         'exportarse.')
    table(d, ['ID', 'Requisito funcional', 'Situación actual'], [
        ('RF-01', 'Operar en modo demostración con identificación visible de datos simulados.', 'Implementado.'),
        ('RF-02', 'Ajustar ojos cerrados, parpadeos, bostezos, inclinación y visibilidad de rostro.', 'Implementado con controles gráficos y tarjetas de lectura.'),
        ('RF-03', 'Seleccionar cuatro escenarios predefinidos.', 'Implementado; también por menú Demostración.'),
        ('RF-04', 'Calcular estado y mostrar motivos con reglas conocidas.', 'Implementado en evaluate().'),
        ('RF-05', 'Mostrar alerta visual e intentar sonido al entrar en ALERTA ALTA.', 'Implementado; sonido dependiente del sistema.'),
        ('RF-06', 'Iniciar y pausar simulación automática.', 'Implementado con temporizador Tkinter.'),
        ('RF-07', 'Registrar lecturas manuales y cambios a niveles anormales en CSV.', 'Implementado; véanse condiciones en sección 7.'),
        ('RF-08', 'Distinguir SIN ROSTRO de una clasificación de cansancio.', 'Implementado.'),
        ('RF-09', 'Separar interfaz, lógica de negocio y módulos auxiliares.', 'Implementado en seis módulos.'),
        ('RF-10', 'Acceso por cuenta local antes de abrir el panel.', 'Implementado en login.py; una sola cuenta con hash PBKDF2.'),
        ('RF-11', 'Plan de acción mediante búsqueda: BFS, DFS, UCS, Greedy y A*.', 'Implementado en busqueda.py y busqueda_ui.py.'),
        ('RF-12', 'Calibración ilustrativa de umbrales con Hill Climbing y algoritmo genético.', 'Implementado; no persiste los umbrales.'),
        ('RF-13', 'Mostrar tabla de registros, gráficas y exportación de CSV.', 'Implementado en página Registros y graficas.py.'),
        ('RF-14', 'Disponer de pruebas automatizadas.', 'Implementado: 13 pruebas.'),
        ('RF-15', 'Configurar umbrales desde archivo o interfaz y persistirlos.', 'Futuro; solo por código o parámetro thresholds.'),
        ('RF-16', 'Capturar cámara y extraer puntos faciales.', 'Futuro; no forma parte de esta entrega.')])
    table(d, ['ID', 'Requisito no funcional', 'Alcance o evidencia'], [
        ('RNF-01', 'Usabilidad', 'Interfaz en español, menú lateral, texto y colores; sin evaluación formal de accesibilidad.'),
        ('RNF-02', 'Respuesta de interfaz', 'Programación de ciclos con after(); sin mediciones formales de latencia.'),
        ('RNF-03', 'Mantenibilidad', 'Seis módulos, README y 13 pruebas unitarias.'),
        ('RNF-04', 'Privacidad', 'Solo métricas sintéticas; sin fotos ni videos.'),
        ('RNF-05', 'Compatibilidad', 'Objetivo: Windows, Python 3.11+, Tkinter y matplotlib. Pruebas ejecutadas con Python 3.13.'),
        ('RNF-06', 'Robustez', 'Parcial: límites en controles; faltan validación del motor y manejo de fallos de escritura.'),
        ('RNF-07', 'Seguridad', 'Contraseña con hash PBKDF2 y salt; sin servicios externos ni credenciales de red.'),
        ('RNF-08', 'Honestidad técnica', 'Reglas y costos ilustrativos; no se informa precisión ni porcentaje de IA.')])

    h(d, '3. Arquitectura y tecnologías')
    code(d, 'Usuario\n'
            '  ↓ usuario y contraseña\n'
            'login.py — LoginApp / cuenta PBKDF2 en data/cuenta.json\n'
            '  ↓ acceso concedido\n'
            'app.py — DemoApp / Tkinter (sidebar + páginas)\n'
            '  ├─ Signals → core.evaluate() → Assessment\n'
            '  ├─ save_event() → data/eventos.csv\n'
            '  ├─ "Plan de acción" → busqueda_ui.py → busqueda.py\n'
            '  │       (BFS, DFS, UCS, Greedy, A*, Hill Climbing, Genético)\n'
            '  └─ "Gráficas" → graficas.py → matplotlib + eventos.csv')
    p(d, 'Todo ocurre en el bucle de eventos de Tkinter. No hay servidor, procesos '
         'de análisis de cámara ni servicio remoto. La escritura CSV es síncrona. '
         'Las ventanas de búsqueda y gráficas son Toplevel que se abren desde el '
         'panel o el menú lateral.')
    imagen(d, 'dashboard.png', 'Interfaz actual: menú lateral y página Inicio.')
    table(d, ['Tecnología', 'Uso'], [
        ('Python 3.11+', 'Lenguaje y biblioteca estándar.'),
        ('tkinter / ttk / messagebox / filedialog', 'Ventana, menú, páginas, controles, tablas y diálogos.'),
        ('dataclasses', 'Objetos inmutables Signals, Thresholds y Assessment.'),
        ('csv / pathlib / datetime / shutil', 'Persistencia, rutas, fecha local y exportación.'),
        ('heapq / deque / random', 'Estructuras de los algoritmos de búsqueda y optimización.'),
        ('hashlib / hmac / secrets / json', 'Hash de contraseña y archivo de cuenta.'),
        ('matplotlib', 'Gráficas de eventos incrustadas con FigureCanvasTkAgg.'),
        ('unittest / tempfile', 'Pruebas y archivos temporales.')])
    p(d, 'OpenCV, MediaPipe, NumPy, SQLite y FastAPI son propuestas de evolución; '
         'no son dependencias ni componentes de esta versión.')

    h(d, '4. Instalación de paqueterías y elementos requeridos')
    p(d, 'Sección limitada a dependencias y comprobaciones; no describe la '
         'instalación completa del sistema. Se presupone Python 3.11 o posterior.')
    code(d, 'pip install matplotlib\npython --version\npython -m tkinter')
    p(d, 'matplotlib es la única paquetería de terceros requerida (gráficas de '
         'eventos); requirements.txt la lista. El segundo comando de comprobación '
         'debe abrir una ventana de prueba de Tcl/Tk; si falta, reparar la '
         'instalación de Python incorporando Tcl/Tk, no instalar un paquete '
         'llamado "tkinter" con pip.')
    p(d, 'Para operar se necesita sesión gráfica, resolución que permita la '
         'ventana mínima de 1020 × 720 y permisos de escritura en la carpeta '
         'data (ahí se crean eventos.csv y cuenta.json). No requiere webcam ni '
         'conexión a Internet.')

    h(d, '5. Estructura del proyecto')
    code(d, 'DriveGuardAI_Demo/\n'
            '  app.py              # interfaz: login posterior, sidebar y páginas\n'
            '  login.py            # cuenta local y ventana de acceso\n'
            '  core.py             # Signals, Thresholds, Assessment, evaluate, save_event\n'
            '  busqueda.py         # grafo de acciones + algoritmos + calibración\n'
            '  busqueda_ui.py      # ventana "Plan de acción (búsqueda IA)"\n'
            '  graficas.py         # ventana de gráficas matplotlib\n'
            '  requirements.txt    # matplotlib\n'
            '  README.md\n'
            '  tests/\n'
            '    test_core.py      # 6 pruebas del motor y del CSV\n'
            '    test_busqueda.py  # 7 pruebas de algoritmos y calibración\n'
            '  data/\n'
            '    .gitkeep\n'
            '    ejemplo_eventos_simulados.csv   # datos de referencia\n'
            '    eventos.csv                     # se crea al registrar\n'
            '    cuenta.json                     # se crea en el primer acceso\n'
            '  capturas/           # imágenes de la versión anterior (tema oscuro)\n'
            '  generar_manuales.py # script que genera los documentos Word\n'
            '  __pycache__/        # caché de Python')
    table(d, ['Módulo', 'Responsabilidad'], [
        ('app.py', 'Navegación (sidebar + páginas Inicio/Registros/Ayuda), escenarios, tarjetas, historial, ciclo automático, exportación.'),
        ('login.py', 'Crear cuenta en el primer uso, autenticar y liberar el panel.'),
        ('core.py', 'Estructuras, reglas de puntuación y escritura CSV.'),
        ('busqueda.py', 'Definición del problema de búsqueda, cinco algoritmos, lecturas etiquetadas y optimización de umbrales.'),
        ('busqueda_ui.py', 'Ventana de plan de acción, comparativa de algoritmos y calibraciones.'),
        ('graficas.py', 'Tres gráficas sobre eventos.csv con tema claro.'),
        ('generar_manuales.py', 'Genera los documentos Word del proyecto.')])

    h(d, '6. Configuración')
    p(d, 'No existen config.json ni variables de entorno requeridas; la '
         'configuración vive en constantes del código. Respaldar antes de '
         'modificar y mantener cambios bajo control de versiones.')
    table(d, ['Parámetro', 'Ubicación', 'Valor o efecto'], [
        ('Umbrales', 'core.py / Thresholds', '1.2 s precaución ocular; 2.5 s cierre alto; 28 parpadeos/min; 3 bostezos/min; 25° inclinación; 4 puntos para alerta alta.'),
        ('Escenarios', 'app.py / SCENARIOS', 'Cuatro instancias de Signals.'),
        ('Ruta de registros', 'app.py / EVENTS', 'ROOT / data / eventos.csv.'),
        ('Cuenta de acceso', 'login.py / ACCOUNT', 'ROOT / data / cuenta.json; una sola cuenta.'),
        ('Grafo de acciones', 'busqueda.py / grafo', 'Aristas (acción, destino, costo) entre niveles.'),
        ('Heurística', 'busqueda.py / h', 'Puntos mínimos restantes: NORMAL 0, PRECAUCIÓN 1, ALERTA 2.'),
        ('Genes del genético', 'busqueda.py / GENES', 'Seis umbrales con mínimo, máximo y resolución.'),
        ('Periodo automático', 'app.py / next_tick()', 'after(1700, ...): intervalo nominal de 1700 ms.'),
        ('Aleatoriedad', 'app.py y busqueda.py', 'Semilla 1234 en la simulación y en el genético.'),
        ('Paleta', 'constantes de color en cada módulo de interfaz', 'Tema claro: azul marino y tarjetas blancas.')])
    p(d, 'evaluate() admite un objeto Thresholds alternativo por parámetro; la '
         'calibración con Hill Climbing o genético devuelve un Thresholds nuevo '
         'pero la aplicación no lo aplica ni lo guarda — es una demostración '
         'de la técnica de optimización.')

    h(d, '7. Modelo de datos')
    sub(d, '7.1 Objetos internos')
    table(d, ['Objeto', 'Atributos', 'Reglas'], [
        ('Signals', 'eye_closed_seconds: float; blinks_per_minute: int; yawns_per_minute: int; head_tilt_degrees: float; face_visible: bool', 'Valores predeterminados 0.0, 15, 0, 0.0, True. Dataclass congelada.'),
        ('Thresholds', 'Seis umbrales y high_score_min', 'Ver configuración. Dataclass congelada.'),
        ('Assessment', 'level: str; score: int; reasons: tuple; message: str', 'Resultado inmutable de evaluate().')])
    sub(d, '7.2 Archivos persistidos')
    table(d, ['Archivo', 'Formato', 'Contenido'], [
        ('data/eventos.csv', 'CSV utf-8-sig, once columnas definidas en FIELDNAMES', 'fecha_hora, origen, escenario, nivel, puntuacion, cinco señales y motivos. Se agrega al final; sin rotación ni deduplicación.'),
        ('data/cuenta.json', 'JSON', 'usuario, salt (hex) y hash PBKDF2-HMAC-SHA256 con 600 000 iteraciones. Una sola cuenta.'),])
    sub(d, '7.3 Cuándo se guardan los datos')
    bullets(d, [
        'Al entrar a PRECAUCIÓN, ALERTA ALTA o SIN ROSTRO se agrega una fila automática; no por cada ciclo.',
        'Volver a NORMAL aparece en el historial visual pero no en el CSV.',
        'Registrar lectura en CSV guarda el resultado actual, incluso NORMAL; en un cambio anormal puede haber fila automática y manual.',
        'El historial gráfico conserva hasta 100 entradas en memoria y no se restaura desde CSV.',
        'cuenta.json se crea una vez, en el primer acceso; borrarlo restablece la pantalla de creación de cuenta.'])

    h(d, '8. Módulos y API')
    sub(d, '8.1 core.py')
    table(d, ['Elemento', 'Entrada y retorno', 'Comportamiento'], [
        ('evaluate(signals, thresholds=None)', 'Signals y Thresholds opcional → Assessment', 'Reglas de puntuación; SIN ROSTRO corta antes de evaluar.'),
        ('save_event(file_path, scenario, signals, result, origin="SIMULADO")', 'path, texto, Signals, Assessment → None', 'Crea carpeta y agrega fila; propaga errores de acceso.'),
        ('FIELDNAMES', 'Lista de once cadenas', 'Define el orden del esquema CSV.')])
    sub(d, '8.2 login.py')
    table(d, ['Elemento', 'Comportamiento'], [
        ('create_account(usuario, contraseña, path)', 'Valida usuario no vacío y contraseña ≥ 8; guarda salt+hash con open("x") para no sobrescribir.'),
        ('authenticate(usuario, contraseña, path)', 'Lee cuenta.json y compara hashes con hmac.compare_digest.'),
        ('LoginApp(root, on_success)', 'Ventana de acceso; en primer uso crea cuenta y luego llama on_success.')])
    sub(d, '8.3 busqueda.py — problema de búsqueda y API')
    p(d, 'P = (S, A, s0, G, C): S = niveles de riesgo; A = acciones correctivas '
         'con costo (puntos que reducen); s0 = nivel actual de evaluate(); '
         'G = NORMAL; C = costo por arista. Cada algoritmo devuelve un '
         'diccionario con camino, acciones, costo, aristas, expandidos y registro.')
    table(d, ['Función', 'Estrategia y resultado en ALERTA ALTA'], [
        ('bfs(inicio)', 'Cola FIFO; ruta directa de 1 acción, costo 4.'),
        ('dfs(inicio)', 'Recursiva con retroceso; encuentra ALERTA → PRECAUCIÓN → NORMAL, costo 3.'),
        ('ucs(inicio)', 'heapq por g(n); óptimo: costo 3 vía PRECAUCIÓN.'),
        ('greedy(inicio)', 'heapq solo por h(n); elige el directo, costo 4 (no óptimo).'),
        ('astar(inicio)', 'heapq por f = g + h; óptimo costo 3.'),
        ('hill_climbing_umbrales(...)', 'Ajusta un umbral mientras reduzca errores.'),
        ('algoritmo_genetico_umbrales(...)', 'Evoluciona los seis umbrales; torneo, cruza, mutación, elitismo.'),
        ('errores(umbrales)', 'Lecturas etiquetadas mal clasificadas.')])
    p(d, 'La heurística h(n) es admisible: NORMAL 0, PRECAUCIÓN 1 y ALERTA ALTA 2, '
         'menor o igual al costo mínimo real hacia NORMAL.')
    sub(d, '8.4 Interfaz y ciclo de vida (app.py)')
    table(d, ['Elemento', 'Responsabilidad'], [
        ('show(nombre)', 'pack_forget() de todas las páginas y pack() de la elegida; resalta el botón del menú.'),
        ('refresh_records()', 'Carga eventos.csv en la tabla de la página Registros.'),
        ('export_csv()', 'Copia eventos.csv a una ruta elegida con filedialog + shutil.'),
        ('signals() / apply_scenario() / assess()', 'Construcción de señales, carga de escenario y evaluación con registro.'),
        ('start() / next_tick() / stop()', 'Ciclo automático de 12 ticks por vuelta con after(1700).'),
        ('open_plan() / open_charts()', 'Abren las ventanas Toplevel de búsqueda y gráficas.')])
    p(d, 'No hay endpoints, puertos, autenticación HTTP ni API pública de red.')

    h(d, '9. Pruebas')
    code(d, 'python -m unittest discover -s tests -v')
    p(d, 'Ejecución verificada: 13 pruebas, 13 correctas. Además se ejecuta '
         'python busqueda.py como demostración en consola de los cinco algoritmos.')
    table(d, ['Archivo', 'Casos cubiertos'], [
        ('tests/test_core.py', 'NORMAL, PRECAUCIÓN, ALERTA ALTA, indicadores combinados, SIN ROSTRO no es fatiga, escritura CSV con origen SIMULADO.'),
        ('tests/test_busqueda.py', 'Ruta BFS, óptimo UCS (costo 3), óptimo A*, no-optimalidad de Greedy (costo 4), heurística admisible, Hill Climbing no empeora y genético produce umbrales válidos.')])
    p(d, 'Pruebas manuales pendientes de evidencia: navegación del menú lateral, '
         'login en primer uso y accesos incorrectos, tabla y exportación de '
         'registros, gráficas con y sin CSV, sonido del sistema y cierre durante '
         'la simulación.')

    h(d, '10. Despliegue y mantenimiento')
    code(d, 'python app.py')
    p(d, 'Distribuir el código fuente con README, pruebas y recursos. No existe '
         'instalador, ejecutable empaquetado ni servicio. Colocar el proyecto '
         'en una ubicación con permisos de escritura; en Windows puede usarse '
         'py app.py.')
    bullets(d, [
        'Antes de cambiar: cerrar la aplicación y respaldar código y data/eventos.csv.',
        'Mantener el esquema CSV y el formato de cuenta.json compatibles o definir migración.',
        'Ejecutar las 13 pruebas y repetir los casos manuales afectados.',
        'Actualizar requisitos, manuales y control de versiones al cambiar comportamiento.',
        'Para restablecer el acceso: cerrar la app y borrar data/cuenta.json (se pierde la cuenta).',
        'El CSV crece indefinidamente: definir respaldo y retención; evitar dos instancias escribiendo a la vez.'])

    h(d, '11. Seguridad')
    bullets(d, [
        'Uso exclusivamente académico y estacionario; nunca durante la conducción.',
        'La contraseña se guarda como hash PBKDF2 con salt aleatorio y comparación en tiempo constante; no se guarda en texto plano y cuenta.json está excluido de Git.',
        'Es una cuenta local de demostración: no protege los archivos frente a alguien con acceso al equipo; usar permisos del sistema operativo.',
        'No hay servicios de red ni credenciales de terceros en el código.',
        'El CSV no está cifrado; si otros sistemas escriben textos externos, revisarlos antes de abrirlos en hojas de cálculo.',
        'Si se incorpora cámara o datos personales, reevaluar consentimiento, privacidad y retención antes de desplegar.'])

    h(d, '12. Solución de problemas')
    table(d, ['Síntoma', 'Causa probable', 'Acción'], [
        ('Olvidé la contraseña', 'No hay recuperación; es un hash.', 'Cerrar la app y borrar data/cuenta.json; el primer uso vuelve a pedir crear cuenta.'),
        ('Acceso denegado', 'Usuario o contraseña incorrectos.', 'Reintentar; verificar mayúsculas. Tras varios intentos, restablecer la cuenta.'),
        ('No module named matplotlib', 'Falta la dependencia de gráficas.', 'pip install matplotlib con el intérprete correcto.'),
        ('No module named tkinter', 'Distribución sin Tcl/Tk.', 'Probar python -m tkinter; reparar la instalación.'),
        ('No aparece eventos.csv', 'No hubo registro.', 'Pulsar Registrar lectura; revisar página Registros.'),
        ('PermissionError al registrar o entrar', 'Archivo bloqueado o carpeta sin escritura.', 'Cerrar el archivo en Excel; usar carpeta autorizada.'),
        ('Plan de acción no abre', 'Estado NORMAL o SIN ROSTRO.', 'Es lo esperado: el plan solo aplica con riesgo.'),
        ('Gráfica sin datos propios', 'Falta eventos.csv.', 'Usa el CSV de ejemplo; registrar lecturas para datos propios.'),
        ('No hay sonido', 'Sonidos del sistema desactivados.', 'Revisar audio; el aviso suena solo al entrar en alerta.'),
        ('El historial se vació', 'Solo existe en memoria.', 'Consultar el CSV o la página Registros.')])

    h(d, '13. Limitaciones y trabajo futuro')
    bullets(d, [
        'No hay captura de cámara, procesamiento facial, IA entrenada ni validación clínica o vial.',
        'La cuenta es única, sin roles ni recuperación; el login es de demostración.',
        'La calibración de umbrales es ilustrativa y no se persiste; no hay config.json ni pantalla de umbrales.',
        'El motor no valida rangos ni tipos en ejecución; la escritura CSV no maneja errores ni bloqueo entre instancias.',
        'Las pruebas automáticas no cubren la interfaz completa; faltan evidencias manuales documentadas.',
        'Trabajo futuro: multiusuario, persistencia de umbrales, manejo amigable de errores de archivo, módulo de cámara y evaluación real de algoritmos.'])

    h(d, 'Referencias')
    bullets(d, [
        'Código fuente del proyecto: app.py, login.py, core.py, busqueda.py, busqueda_ui.py, graficas.py, tests/; revisión local del 30/10/2026.',
        'Python Software Foundation. Graphical user interfaces with Tk. https://docs.python.org/3.12/library/tk.html',
        'Python Software Foundation. hashlib — Secure hashes and message digests. https://docs.python.org/3/library/hashlib.html',
        'Matplotlib. Embedding in Tk (FigureCanvasTkAgg). https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html',
        'Google AI Edge. Face landmark detection guide for Python. https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python — fase futura.',
        'OpenCV. Sitio oficial. https://opencv.org/ — fase futura.',
        'Russell, S. y Norvig, P. Artificial Intelligence: A Modern Approach — fundamentos de búsqueda (BFS, DFS, UCS, Greedy, A*, Hill Climbing, algoritmos genéticos).'])

    h(d, 'Glosario')
    glossary(d, True)

    h(d, 'Anexos')
    sub(d, 'Anexo A. Grafo de acciones del plan de búsqueda')
    code(d, 'PRECAUCIÓN ── ventilar(1) ──▶ NORMAL\n'
            '           ── pausa 15 min(2) ──▶ NORMAL\n'
            '           ── ignorar(3) ──▶ ALERTA ALTA\n'
            'ALERTA ALTA ── pausa 15 min(2) ──▶ PRECAUCIÓN\n'
            '            ── cambiar conductor(4) ──▶ NORMAL\n'
            '            ── detenerse y descansar(4) ──▶ NORMAL')
    sub(d, 'Anexo B. Comparativa de algoritmos desde ALERTA ALTA')
    table(d, ['Algoritmo', 'Ruta', 'Costo', 'Observación'], [
        ('BFS', 'ALERTA → NORMAL', 4, 'Menos acciones, no menor costo.'),
        ('DFS', 'ALERTA → PRECAUCIÓN → NORMAL', 3, 'Profundiza primero.'),
        ('UCS', 'ALERTA → PRECAUCIÓN → NORMAL', 3, 'Óptimo por g(n).'),
        ('Greedy', 'ALERTA → NORMAL', 4, 'Elige h=0 sin mirar costo.'),
        ('A*', 'ALERTA → PRECAUCIÓN → NORMAL', 3, 'Óptimo por f = g + h.')])
    sub(d, 'Anexo C. Capturas requeridas')
    p(d, 'Guardar en la carpeta capturas/ con estos nombres para que se '
         'incorporen al documento: login.png (acceso), dashboard.png '
         '(página Inicio), registros.png (tabla de eventos), graficas.png '
         '(ventana de gráficas) y plan_busqueda.png (plan de acción). '
         'Las imágenes previas de la carpeta corresponden al tema oscuro '
         'anterior; la interfaz actual usa tema claro con menú lateral.')
    imagen(d, 'registros.png', 'Página Registros.')
    imagen(d, 'plan_busqueda.png', 'Plan de acción con comparativa de algoritmos.')
    h(d, 'Lista de verificación antes de entregar')
    bullets(d, [
        '[ ] Completar autor, institución, docente y responsable.',
        '[ ] Actualizar todo el índice automático y revisar paginación.',
        '[ ] Confirmar las 13 secciones, referencias, glosario y anexos.',
        '[ ] Ejecutar las 13 pruebas y documentar pruebas manuales.',
        '[ ] Tomar capturas nuevas del tema claro si se requieren.',
        '[ ] Confirmar que las funciones futuras no se presentan como implementadas.',
        '[ ] Respaldar registros y comprobar permisos de data/.',
        '[ ] Revisar ortografía, saltos de página y enlaces.'])
    d.save(ROOT / 'Manual_Tecnico_DriveGuard_AI.docx')


def task(d, title, objective, steps, expected, warning):
    sub(d, title)
    p(d, 'Objetivo: ' + objective)
    p(d, 'Pasos:')
    for i, step in enumerate(steps, 1):
        p(d, f'{i}. {step}')
    p(d, 'Resultado esperado: ' + expected)
    p(d, 'Advertencias: ' + warning)


def user():
    d = base('MANUAL DE USUARIO', 'personas sin conocimientos técnicos que utilizarán la demostración.')

    h(d, '1. Introducción')
    p(d, 'DriveGuard AI permite observar cómo cambian avisos de ejemplo cuando se '
         'modifican señales relacionadas con cansancio. Es una demostración '
         'educativa: los valores los selecciona la persona o los genera la '
         'aplicación. No observa tus ojos, no accede a tu cámara y no sabe si '
         'estás cansado.')
    p(d, 'Este manual explica cómo entrar con tu cuenta, usar el menú lateral, '
         'probar escenarios, guardar lecturas, ver gráficas y pedir un plan de '
         'acción sugerido por algoritmos de búsqueda. No debe utilizarse al '
         'conducir.')

    h(d, '2. Antes de comenzar')
    bullets(d, [
        'Computadora con Windows y pantalla de al menos 1020 × 720.',
        'El equipo responsable deja listo Python y la carpeta del proyecto.',
        'No necesitas cámara ni Internet. Sí una cuenta que crearás la primera vez.',
        'Para guardar lecturas necesitas permiso de escritura en la carpeta data.',
        'Usa la demostración en un lugar seguro; nunca al conducir.'])

    h(d, '3. Primeros pasos')
    sub(d, '3.1 Crear tu cuenta (solo la primera vez)')
    p(d, '1. Abre la carpeta DriveGuardAI_Demo.\n'
         '2. En la barra de dirección escribe cmd y presiona Enter.\n'
         '3. Escribe python app.py y presiona Enter.\n'
         '4. Aparece la ventana de acceso: escribe un nombre de usuario y una '
         'contraseña de al menos 8 caracteres.\n'
         '5. Pulsa Crear cuenta. Se abre el panel principal.')
    imagen(d, 'login.png', 'Ventana de acceso: crear cuenta en el primer uso.')
    sub(d, '3.2 Entrar las siguientes veces')
    p(d, 'Escribe tu usuario y contraseña y pulsa Entrar (o Enter desde el campo '
         'de contraseña). Si el usuario o la contraseña son incorrectos verás un '
         'mensaje de acceso denegado.')
    sub(d, '3.3 Conocer la pantalla')
    imagen(d, 'dashboard.png', 'Página Inicio: menú lateral, estado, tarjetas y controles.')
    table(d, ['Área', 'Qué contiene'], [
        ('Menú lateral (azul)', 'Inicio, Registros, Ayuda y las herramientas: Plan de acción, Gráficas, Exportar datos.'),
        ('Inicio', 'Estado de monitoreo, tarjetas de señales, barras ajustables, escenario, botones e historial.'),
        ('Registros', 'Tabla con las lecturas guardadas en eventos.csv.'),
        ('Ayuda', 'Explicación del programa y de los estados.'),
        ('Barra de menú superior', 'Archivo, Demostración, Herramientas y Ayuda.')])
    sub(d, '3.4 Entender los estados')
    table(d, ['Estado', 'Color', 'Significado en la demostración'], [
        ('NORMAL', 'Verde', 'Sin señales destacadas en los valores simulados.'),
        ('PRECAUCIÓN', 'Ámbar', 'Los valores activan algunas reglas de ejemplo.'),
        ('ALERTA ALTA', 'Rojo', 'Puntuación alta; puede sonar un aviso.'),
        ('SIN ROSTRO', 'Gris', 'El ejemplo no puede evaluarse; no significa cansancio.')])

    h(d, '4. Funciones')
    task(d, '4.1 Moverte por el menú lateral',
         'Cambiar de sección en la aplicación.',
         ['Pulsa Inicio, Registros o Ayuda en el menú azul de la izquierda.',
          'Observa que el botón elegido se ilumina y cambia el contenido.'],
         'Se muestra la página elegida; las demás se ocultan.',
         'Las opciones Plan de acción, Gráficas y Exportar datos abren ventanas aparte.')
    task(d, '4.2 Seleccionar un escenario',
         'Cargar un conjunto de valores de ejemplo.',
         ['Ve a Inicio.', 'Si la demostración está activa, pulsa Pausar demostración.',
          'Abre la lista bajo ESCENARIO y elige un escenario.',
          'Observa el estado, el mensaje y los motivos.'],
         'Se cargan los controles y se evalúa el escenario.',
         'Cambiar a un estado anormal guarda un evento automáticamente.')
    task(d, '4.3 Ajustar señales y leer las tarjetas',
         'Probar cómo afectan los valores a la evaluación.',
         ['Mueve las barras: ojos cerrados, parpadeos, bostezos o inclinación.',
          'Mira cómo las tarjetas superiores muestran el valor actual en grande.',
          'Marca o desmarca Rostro visible.',
          'Revisa el estado y los motivos.'],
         'La pantalla reevalúa cada ajuste y las tarjetas se actualizan solas.',
         'Los valores son inventados; el nombre del escenario puede conservarse aunque lo modifiques.')
    task(d, '4.4 Iniciar y pausar la demostración automática',
         'Observar una secuencia de escenarios sin tocar controles.',
         ['Pulsa Iniciar demostración automática.',
          'Confirma que aparece SIMULACIÓN AUTOMÁTICA ACTIVA.',
          'Observa los cambios y pulsa Pausar demostración para detenerlos.'],
         'Los ejemplos avanzan aproximadamente cada 1.7 segundos y se repiten.',
         'Mientras está activa, los valores manuales son reemplazados por cada ciclo.')
    task(d, '4.5 Registrar una lectura en CSV',
         'Guardar los valores y el resultado actuales.',
         ['Pausa la demostración y deja la lectura que quieras guardar.',
          'Pulsa Registrar lectura en CSV.',
          'Lee el mensaje de confirmación.'],
         'Se crea o actualiza data/eventos.csv y aparece LECTURA REGISTRADA en el historial.',
         'Si el archivo está abierto en otro programa, puede impedirse la escritura.')
    task(d, '4.6 Revisar la tabla de registros',
         'Consultar todas las lecturas guardadas.',
         ['Pulsa Registros en el menú lateral.',
          'Revisa fecha, escenario, nivel, puntos y motivos de cada fila.',
          'Pulsa Actualizar si registraste algo hace poco.'],
         'Ves la lista completa de eventos guardados.',
         'Si no hay archivo todavía, aparece una nota explicativa.')
    imagen(d, 'registros.png', 'Página Registros con la tabla de eventos.')
    task(d, '4.7 Ver las gráficas',
         'Visualizar los eventos con gráficas.',
         ['Pulsa Gráficas de eventos en el menú lateral (o Herramientas).',
          'Elige el tipo: eventos por nivel, puntuación por lectura o señales de la última lectura.',
          'Registra más lecturas y pulsa Actualizar para renovar la gráfica.'],
         'Se abre una ventana con la gráfica elegida.',
         'Si aún no guardaste lecturas, se usan los datos de ejemplo y se indica.')
    imagen(d, 'graficas.png', 'Ventana de gráficas de eventos.')
    task(d, '4.8 Pedir un plan de acción',
         'Obtener una secuencia sugerida de acciones para bajar el riesgo.',
         ['En Inicio deja el estado en PRECAUCIÓN o ALERTA ALTA.',
          'Pulsa Plan de acción (búsqueda IA).',
          'Elige un algoritmo (BFS, DFS, UCS, Greedy o A*) y pulsa Ejecutar.',
          'Pulsa Comparar los 5 para ver las diferencias de ruta y costo.'],
         'Ves la lista de acciones sugeridas, la ruta por niveles, el costo total y el registro de la búsqueda.',
         'Los costos son ilustrativos. Con NORMAL o SIN ROSTRO no hay plan porque no hay riesgo o no se puede evaluar.')
    imagen(d, 'plan_busqueda.png', 'Ventana del plan de acción con la ruta y el registro de la búsqueda.')
    task(d, '4.9 Exportar los registros',
         'Guardar una copia del archivo CSV donde tú elijas.',
         ['Pulsa Exportar datos CSV en el menú lateral.',
          'Elige la carpeta y el nombre del archivo.',
          'Pulsa Guardar.'],
         'Se crea una copia de eventos.csv en el lugar elegido.',
         'Si todavía no hay registros, aparece un aviso y no se exporta nada.')
    task(d, '4.10 Cerrar sesión y salir',
         'Terminar la demostración.',
         ['Si deseas conservar una lectura, regístrala antes.',
          'Cierra la ventana con la X o usa Archivo → Salir.'],
         'La aplicación se cierra; el CSV y tu cuenta se conservan.',
         'Cerrar no guarda cada valor visible: solo lo registrado. Al volver a abrir, se pide tu contraseña.')

    h(d, '5. Flujos de trabajo')
    sub(d, '5.1 Demostración de los cuatro estados')
    p(d, '1. Entra y ve a Inicio.\n2. Selecciona Conducción normal → NORMAL.\n'
         '3. Selecciona Cansancio leve → PRECAUCIÓN.\n'
         '4. Selecciona Somnolencia alta → ALERTA ALTA (puede sonar).\n'
         '5. Selecciona Rostro no visible → SIN ROSTRO.\n'
         '6. Abre Plan de acción para ver las acciones sugeridas.')
    sub(d, '5.2 Guardar, graficar y exportar')
    p(d, '1. Registra varias lecturas con el botón Registrar lectura en CSV.\n'
         '2. Ve a Registros y pulsa Actualizar.\n'
         '3. Abre Gráficas y elige cada tipo.\n'
         '4. Pulsa Exportar datos CSV y guarda la copia.')
    sub(d, '5.3 Presentación automática')
    p(d, '1. En Inicio pulsa Iniciar demostración automática.\n'
         '2. Explica que los valores son simulados mientras avanza la secuencia.\n'
         '3. Pausa para comentar un estado y, con riesgo activo, muestra el plan de acción.\n'
         '4. Cierra al terminar.')

    h(d, '6. Errores y soluciones')
    table(d, ['Problema', 'Qué hacer'], [
        ('Olvidé mi contraseña', 'Cierra la app y borra el archivo data/cuenta.json. Al abrir de nuevo pedirá crear cuenta. No se puede recuperar.'),
        ('Acceso denegado', 'Revisa mayúsculas y vuelve a intentar. Si persiste, borra cuenta.json como se indica arriba.'),
        ('No abre o "python" no funciona', 'Verifica la carpeta y prueba py app.py. Si continúa, pide apoyo al responsable.'),
        ('Error sobre matplotlib', 'Falta la librería de gráficas: el responsable debe ejecutar pip install matplotlib.'),
        ('No veo la tabla de registros', 'Aún no se guardan lecturas: registra una y pulsa Actualizar.'),
        ('No puedo guardar o exportar', 'Cierra el CSV si está abierto en Excel e inténtalo otra vez.'),
        ('El plan de acción no abre', 'Solo funciona con PRECAUCIÓN o ALERTA ALTA; en NORMAL no hay riesgo que corregir.'),
        ('La gráfica muestra datos que no registré', 'Es el archivo de ejemplo porque aún no tienes eventos.csv propio.'),
        ('No escucho la alerta', 'Revisa el volumen; el sonido intenta sonar solo al entrar en alerta alta.'),
        ('El historial desapareció', 'Es normal al cerrar: el historial visual no se guarda; el CSV sí.')])

    h(d, '7. Preguntas frecuentes')
    for question, answer in [
        ('¿Usa inteligencia artificial o mi cámara?', 'No usa cámara ni un modelo entrenado. Sí incluye algoritmos de búsqueda clásicos (BFS, DFS, UCS, Greedy, A*) para sugerir acciones, pero sobre datos simulados.'),
        ('¿Para qué sirve el plan de acción?', 'Con riesgo activo, calcula la secuencia de acciones que regresa a NORMAL, mostrando cómo decide cada algoritmo.'),
        ('¿Por qué una opción dice "costo" menor que otra?', 'Cada acción tiene un costo ilustrativo; UCS y A* encuentran la secuencia más barata, Greedy puede elegir una más cara.'),
        ('¿Mi contraseña se guarda?', 'Se guarda protegida como un código matemático (hash), no como texto. Aun así, no uses una contraseña importante.'),
        ('¿NORMAL significa que puedo manejar?', 'No. Describe solo el resultado de valores simulados.'),
        ('¿Qué pasa si borro cuenta.json?', 'Se pierde tu cuenta y se vuelve a pedir crear una. Tus registros CSV no se borran.'),
        ('¿Puedo tener dos usuarios?', 'Esta versión admite una sola cuenta.'),
        ('¿Los datos se suben a Internet?', 'No. Todo queda en archivos dentro de la carpeta del proyecto.')]:
        sub(d, question)
        p(d, answer)

    h(d, '8. Recomendaciones')
    bullets(d, [
        'Usa la aplicación solo con fines educativos y nunca durante la conducción.',
        'Explica en toda presentación que las señales, los costos y las alertas son simulados.',
        'Pausa la demostración antes de modificar valores o guardar una lectura.',
        'Cierra el CSV en otros programas antes de registrar o exportar.',
        'No uses una contraseña importante: es una cuenta local de demostración.',
        'Reporta errores con su mensaje completo y no borres archivos salvo cuenta.json para restablecer el acceso.'])

    h(d, '9. Soporte')
    p(d, 'El equipo responsable debe completar estos datos antes de distribuir el manual.')
    table(d, ['Dato', 'Información'], [
        ('Responsable', '[Completar nombre del equipo o encargado]'),
        ('Correo o medio autorizado', '[Completar contacto real]'),
        ('Horario de atención', '[Completar]')])
    p(d, 'Al pedir ayuda indica: qué querías hacer, qué botón pulsaste, el mensaje '
         'exacto y si el archivo CSV estaba abierto en otro programa. No envíes '
         'contraseñas.')

    h(d, 'Glosario')
    glossary(d)

    h(d, 'Lista de verificación')
    bullets(d, [
        '[ ] Comprendo que se trata de una simulación, no de una medición real.',
        '[ ] Puedo crear mi cuenta y entrar al panel.',
        '[ ] Sé moverme por el menú lateral (Inicio, Registros, Ayuda).',
        '[ ] Identifico los cuatro estados y sus diferencias.',
        '[ ] Sé registrar lecturas, ver la tabla, las gráficas y exportar el CSV.',
        '[ ] Sé pedir el plan de acción con riesgo activo.',
        '[ ] Sé qué hacer si olvido la contraseña (borrar cuenta.json).',
        '[ ] No utilizaré la demostración mientras conduzco.'])
    d.save(ROOT / 'Manual_Usuario_DriveGuard_AI.docx')


def documento_temas():
    d = base('DOCUMENTO DE TEMAS DE IA APLICADOS',
             'compañeros del equipo: estudiar qué se hizo, dónde y cómo exponerlo.')

    h(d, '1. ¿Qué se construyó?')
    p(d, 'DriveGuard AI es un prototipo de asistencia a la conducción que, en su '
         'versión actual, trabaja solo con datos simulados: no usa cámara ni un '
         'modelo de IA entrenado. Sobre esa base se aplicaron los temas de '
         'búsqueda y optimización de la materia dentro del código real del '
         'proyecto, no como ejercicios aparte.')
    p(d, 'Este documento explica, tema por tema, dónde está aplicado, cómo '
         'funciona el código y cómo presentarlo en clase.')

    h(d, '2. Mapa del sistema')
    table(d, ['Archivo', 'Qué hace'], [
        ('app.py', 'Ventana principal: menú lateral, página Inicio (estado, tarjetas, escenarios, botones), Registros (tabla del CSV) y Ayuda.'),
        ('login.py', 'Acceso con usuario y contraseña guardados como hash; primer uso crea la cuenta.'),
        ('core.py', 'Reglas de puntuación: evaluate() convierte señales en NORMAL, PRECAUCIÓN, ALERTA ALTA o SIN ROSTRO; save_event() guarda el CSV.'),
        ('busqueda.py', '★ Archivo de los temas: grafo de acciones, BFS, DFS, UCS, Greedy, A*, Hill Climbing, algoritmo genético y lecturas etiquetadas.'),
        ('busqueda_ui.py', 'Ventana "Plan de acción" que ejecuta y compara los algoritmos.'),
        ('graficas.py', 'Tres gráficas matplotlib con los datos de eventos.csv.'),
        ('tests/', '13 pruebas automáticas: 6 del motor y 7 de búsqueda.')])
    code(d, 'login → app.py (sidebar)\n'
            '   Inicio: señales → core.evaluate() → estado + CSV\n'
            '   Plan de acción: nivel → busqueda.py → ruta de acciones\n'
            '   Registros: tabla del CSV · Gráficas: matplotlib')

    h(d, '3. Tema: problema de búsqueda (estructura P=(S,A,s0,G,C))')
    p(d, 'Dónde: secciones 1 y 2 de busqueda.py.')
    p(d, 'Cómo se aplicó: el "agente" es el sistema y el problema es devolver al '
         'conductor a un nivel seguro. Los niveles de riesgo son los estados y '
         'las acciones correctivas son las aristas con costo (puntos que reducen):')
    table(d, ['Elemento', 'En el proyecto'], [
        ('S (estados)', 'NORMAL, PRECAUCIÓN, ALERTA ALTA.'),
        ('A (acciones)', 'Ventilar y beber agua (1), Pausa de 15 min (2), Ignorar y continuar (3), Cambiar de conductor (4), Detenerse y descansar (4).'),
        ('s0 (inicial)', 'El nivel que devuelve evaluate() en ese momento.'),
        ('G (objetivo)', 'NORMAL.'),
        ('C (costo)', 'Puntos de riesgo que cada acción reduce; valor ilustrativo.')])
    code(d, 'grafo = {\n'
            "  'NORMAL': [],\n"
            "  'PRECAUCIÓN': [('Ventilar…','NORMAL',1), ('Pausa 15min','NORMAL',2), ('Ignorar','ALERTA ALTA',3)],\n"
            "  'ALERTA ALTA': [('Pausa 15min','PRECAUCIÓN',2), ('Cambiar conductor','NORMAL',4), ('Detenerse','NORMAL',4)]\n"
            '}')
    p(d, 'Para exponer: mostrar el grafo dibujado en el propio archivo (sección 1) '
         'y explicar que existe una acción "mala" (Ignorar) justamente para que '
         'los algoritmos tengan algo que decidir.')

    h(d, '4. Tema: BFS — búsqueda en anchura')
    p(d, 'Dónde: función bfs() en busqueda.py (sección 4).')
    p(d, 'Cómo funciona: usa una cola deque donde cada elemento es '
         '(estado, camino de estados, camino de acciones). Saca el primero que '
         'entró (popleft, FIFO), marca visitados y mete los vecinos. Encuentra '
         'la ruta con menos acciones, pero como las aristas tienen costos '
         'distintos no garantiza la más barata.')
    code(d, 'cola.append((inicio, [inicio], []))\n'
            'while cola:\n'
            '    actual, camino, acciones = cola.popleft()\n'
            '    if actual == OBJETIVO: return resultado(...)\n'
            '    for accion, destino, costo in grafo[actual]: ...')
    p(d, 'Resultado desde ALERTA ALTA: ruta directa (1 acción, costo 4).')

    h(d, '5. Tema: DFS — búsqueda en profundidad')
    p(d, 'Dónde: función dfs() en busqueda.py (sección 5), versión recursiva '
         'como en la práctica p21.')
    p(d, 'Cómo funciona: visita el estado, lo agrega al camino y pregunta si es '
         'el objetivo. Si no, entra recursivamente por cada vecino; si ninguna '
         'rama llega, retrocede (backtracking). No usa costo ni heurística: es '
         'ciega.')
    p(d, 'Resultado desde ALERTA ALTA: ALERTA → PRECAUCIÓN → NORMAL con costo 3, '
         'porque la primera acción de la lista baja a PRECAUCIÓN.')

    h(d, '6. Tema: UCS — búsqueda de costo uniforme')
    p(d, 'Dónde: función ucs() en busqueda.py (sección 6).')
    p(d, 'Cómo funciona: cola de prioridad con heapq donde la prioridad es '
         'g(n), el costo real acumulado. Siempre expande el camino más barato '
         'hasta ahora, por eso con costos positivos encuentra el óptimo.')
    code(d, 'pendientes = [(0, inicio, [inicio], [])]\n'
            'costo_total, actual, camino, acciones = heapq.heappop(pendientes)\n'
            'heapq.heappush(pendientes, (costo_total + costo, destino, ...))')
    p(d, 'Resultado desde ALERTA ALTA: costo 3 (pausa 15 min → ventilar). '
         'Aunque exista una acción directa de costo 4, UCS prefiere la ruta '
         'más barata.')

    h(d, '7. Tema: heurísticas')
    p(d, 'Dónde: tabla h en busqueda.py (sección 2), igual que la tabla '
         '"minutos caminando" de la práctica.')
    table(d, ['Estado', 'h(n)', 'Por qué es admisible'], [
        ('NORMAL', '0', 'Ya es la meta.'),
        ('PRECAUCIÓN', '1', 'La acción más barata cuesta 1.'),
        ('ALERTA ALTA', '2', 'El costo real mínimo es 3; h no lo sobreestima.')])
    p(d, 'Para exponer: una heurística admisible nunca promete menos de lo que '
         'realmente cuesta llegar; eso es lo que hace que A* sea óptimo. Hay '
         'una prueba automática (test_heuristica_admisible) que lo comprueba.')

    h(d, '8. Tema: Greedy — búsqueda voraz')
    p(d, 'Dónde: función greedy() en busqueda.py (sección 7), igual que GBFS.py.')
    p(d, 'Cómo funciona: misma cola de prioridad, pero la prioridad es solo '
         'h(n): el estado que "parece" más cerca de la meta. Como no mira lo '
         'ya recorrido, puede elegir mal.')
    p(d, 'Resultado desde ALERTA ALTA: toma la ruta directa porque NORMAL tiene '
         'h=0… y cuesta 4, peor que el óptimo 3. Es el ejemplo perfecto para '
         'mostrar la diferencia entre Greedy y A*.')

    h(d, '9. Tema: A* (f = g + h)')
    p(d, 'Dónde: función astar() en busqueda.py (sección 8).')
    p(d, 'Cómo funciona: la cola ordena por f(n) = g(n) + h(n). g es el costo '
         'real recorrido y h la estimación restante. Además lleva mejor_g para '
         'no reabrir un estado por un camino más caro.')
    code(d, 'pendientes = [(h[inicio], 0, inicio, [inicio], [])]\n'
            'f, g, actual, camino, acciones = heapq.heappop(pendientes)\n'
            'nuevo_g = g + costo\n'
            'heapq.heappush(pendientes, (nuevo_g + h[destino], nuevo_g, ...))')
    p(d, 'Resultado desde ALERTA ALTA: costo 3, la ruta óptima. '
         'Comparación rápida para la exposición: BFS=4, DFS=3, UCS=3, '
         'Greedy=4, A*=3.')

    h(d, '10. Tema: Hill Climbing')
    p(d, 'Dónde: función hill_climbing_umbrales() en busqueda.py (sección 10) '
         'y botón "Calibrar (Hill Climbing)" en la ventana del plan.')
    p(d, 'Cómo funciona: toma un umbral (por defecto parpadeos_caution), mide '
         'cuántas lecturas etiquetadas clasifica mal, prueba sus vecinos '
         '(valor−1 y valor+1) y se mueve al que tenga menos errores. Se '
         'repite hasta que ningún vecino mejora: la cima de la colina.')
    p(d, 'Datos: 14 lecturas etiquetadas con el nivel que debería dar '
         'evaluate(). fitness = cantidad de errores. Es ilustrativo: el '
         'umbral calibrado no se guarda en la aplicación.')

    h(d, '11. Tema: algoritmo genético')
    p(d, 'Dónde: funciones GENES, decodificar, gen_aleatorio, fitness y '
         'algoritmo_genetico_umbrales() en busqueda.py (sección 11).')
    table(d, ['Concepto genético', 'En el código'], [
        ('Cromosoma', 'Lista de 6 valores = los 6 umbrales de Thresholds.'),
        ('Fitness', 'Errores que comete ese conjunto de umbrales (menor es mejor).'),
        ('Población', '24 individuos aleatorios dentro de rangos por gen.'),
        ('Selección', 'Torneo de 3: se eligen 3 al azar y gana el de menos errores.'),
        ('Cruza', 'Corte de un punto: hijo = cabeza de p1 + cola de p2.'),
        ('Mutación', 'Con probabilidad 0.2, un gen se reemplaza por un valor aleatorio.'),
        ('Elitismo', 'El mejor pasa intacto a la siguiente generación.'),
        ('Reproducibilidad', 'Semilla fija 1234: mismo resultado siempre.')])
    p(d, 'Además decodificar() descarta cromosomas inválidos (el umbral "alto" '
         'de ojos debe ser mayor que el de "precaución").')

    h(d, '12. Tema: TTK (componentes de interfaz)')
    p(d, 'Dónde: toda la interfaz. Ejemplos concretos:')
    bullets(d, [
        'ttk.Combobox: escenario, selector de algoritmo y de gráfica.',
        'ttk.Treeview: tabla de registros y comparativa de algoritmos.',
        'ttk.Style + tema clam: estilo de los combos.',
        'ttk.Scrollbar: barra de la tabla y del registro.',
        'Menú superior tk.Menu + sidebar de tk.Button: la navegación.',
        'Páginas con pack()/pack_forget(): patrón de "pestañas caseras".'])

    h(d, '13. Cómo explicarlo en la exposición (guion sugerido)')
    p(d, '1. Contexto (30 seg): DriveGuard AI busca prevenir accidentes por '
         'somnolencia; esta versión simula las señales para poder estudiar la '
         'lógica sin cámara.\n'
         '2. Mostrar la app: login, escenario "Somnolencia alta" → ALERTA ALTA.\n'
         '3. Abrir Plan de acción: explicar el grafo (estados y acciones) y que '
         'la meta es NORMAL.\n'
         '4. Ejecutar BFS y A*: BFS da 1 acción cara; A* da la secuencia óptima '
         'de costo 3. Ahí se ve por qué la heurística importa.\n'
         '5. Comparar los 5: tabla de rutas y costos.\n'
         '6. Calibración: Hill Climbing ajusta un umbral y el genético los '
         'seis, midiendo errores sobre lecturas etiquetadas.\n'
         '7. Cerrar con honestidad: todo es simulado e ilustrativo; la fase de '
         'cámara es trabajo futuro.')
    imagen(d, 'dashboard.png', 'Captura sugerida para la exposición: panel principal.')
    imagen(d, 'plan_busqueda.png', 'Captura sugerida: comparativa de los cinco algoritmos.')
    p(d, 'Comando útil en vivo: python busqueda.py muestra los cinco algoritmos '
         'paso a paso en consola.')

    h(d, '14. Preguntas que podrían hacer y respuesta corta')
    table(d, ['Pregunta', 'Respuesta'], [
        ('¿Por qué Greedy falla?', 'Porque solo mira h(n); no suma lo ya gastado. Aquí elige la ruta directa de costo 4.'),
        ('¿Por qué A* sí encuentra el óptimo?', 'Combina g + h y la heurística es admisible.'),
        ('¿BFS no es más rápido?', 'Encuentra menos acciones, pero con aristas de distinto costo no es el más barato.'),
        ('¿El genético "aprende" de verdad?', 'Optimiza umbrales sobre lecturas de ejemplo; es ilustrativo y no se guarda.'),
        ('¿Esto es IA?', 'Son algoritmos clásicos de IA (búsqueda y optimización), no aprendizaje automático. La visión por cámara es fase futura.')])

    h(d, 'Glosario rápido')
    glossary(d, True)
    d.save(ROOT / 'Documento_Temas_IA_DriveGuard.docx')


if __name__ == '__main__':
    technical()
    user()
    documento_temas()
    print('Generados: Manual_Tecnico_DriveGuard_AI.docx, '
          'Manual_Usuario_DriveGuard_AI.docx y Documento_Temas_IA_DriveGuard.docx')
