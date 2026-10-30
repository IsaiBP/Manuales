"""Dashboard local de DriveGuard AI: PROTOTIPO SOLO CON DATOS SIMULADOS.

Ejecutar: python app.py
"""
from __future__ import annotations
import random
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
from core import Signals, evaluate, save_event, FIELDNAMES
from login import LoginApp

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / 'data' / 'eventos.csv'

SCENARIOS = {
    'Conducción normal': Signals(0.2, 16, 0, 5, True),
    'Cansancio leve': Signals(1.5, 24, 1, 12, True),
    'Somnolencia alta': Signals(3.0, 33, 4, 35, True),
    'Rostro no visible': Signals(0.0, 0, 0, 0, False),
}

# Paleta clara: azul marino + tarjetas blancas, pensada para leer bien.
COLORS = {'NORMAL': '#1FA971', 'PRECAUCIÓN': '#D98E1B',
          'ALERTA ALTA': '#E14E62', 'SIN ROSTRO': '#8496AD'}
BG = '#E9EEF5'          # fondo general gris azulado claro
SIDEBAR = '#1F3B63'     # menú lateral azul marino
SIDEBAR_ACTIVE = '#35619F'
SURFACE = '#FFFFFF'     # tarjetas blancas
CARD = '#F2F6FB'        # tarjetas internas suaves
TEXT = '#1E2A3A'        # texto casi negro azulado
MUTED = '#5B6B82'
ACCENT = '#2563EB'
LINE = '#D5DEE9'


class DemoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title('DriveGuard AI | Demostración')
        root.geometry('1180x760')
        root.minsize(1020, 720)
        root.configure(bg=BG)
        self.rng = random.Random(1234)
        self.running = False
        self.loading = False
        self.after_id = None
        self.auto_tick = 0
        self.last_level = 'NORMAL'
        self.scenario = tk.StringVar(value='Conducción normal')
        self.status = tk.StringVar(value='NORMAL')
        self.message = tk.StringVar(value='Esperando primera lectura simulada.')
        self.reason = tk.StringVar(value='Sin eventos')
        self.sim_state = tk.StringVar(value='SIMULACIÓN EN PAUSA')
        self.eye = tk.DoubleVar(value=0.2)
        self.blinks = tk.IntVar(value=16)
        self.yawns = tk.IntVar(value=0)
        self.tilt = tk.DoubleVar(value=5.0)
        self.visible = tk.BooleanVar(value=True)
        self.history: list[str] = []
        self.pages = {}
        self.make_menu()
        self.make_layout()
        self.apply_scenario(False)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

    # ========================================================
    # BARRA DE MENU SUPERIOR
    # ========================================================
    def make_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        archivo = tk.Menu(menu, tearoff=0)
        archivo.add_command(label='Registrar lectura en CSV', command=self.register)
        archivo.add_command(label='Ver ubicación de registros', command=self.show_path)
        archivo.add_command(label='Exportar CSV...', command=self.export_csv)
        archivo.add_separator()
        archivo.add_command(label='Salir', command=self.close)
        menu.add_cascade(label='Archivo', menu=archivo)

        demostracion = tk.Menu(menu, tearoff=0)
        for nombre in SCENARIOS:
            demostracion.add_command(label=nombre,
                                     command=lambda n=nombre: self.scenario.set(n)
                                     or self.apply_scenario(True))
        demostracion.add_separator()
        demostracion.add_command(label='Iniciar demostración automática', command=self.start)
        demostracion.add_command(label='Pausar demostración', command=self.stop)
        demostracion.add_separator()
        demostracion.add_command(label='Evaluar lectura actual', command=self.assess)
        menu.add_cascade(label='Demostración', menu=demostracion)

        herramientas = tk.Menu(menu, tearoff=0)
        herramientas.add_command(label='Plan de acción (búsqueda IA)',
                                 command=self.open_plan)
        herramientas.add_command(label='Gráficas de eventos',
                                 command=self.open_charts)
        menu.add_cascade(label='Herramientas', menu=herramientas)

        ayuda = tk.Menu(menu, tearoff=0)
        ayuda.add_command(label='Acerca de DriveGuard AI', command=self.about)
        menu.add_cascade(label='Ayuda', menu=ayuda)

    def about(self):
        messagebox.showinfo('Acerca de DriveGuard AI',
                            'DriveGuard AI · Prototipo educativo\n\n'
                            'Demostración con datos SIMULADOS: no usa cámara\n'
                            'ni un modelo de IA entrenado, y los umbrales no\n'
                            'están validados para uso en carretera.\n\n'
                            'Incluye un plan de acción calculado con\n'
                            'algoritmos de búsqueda (BFS, DFS, UCS,\n'
                            'Greedy y A*) y calibración de umbrales con\n'
                            'Hill Climbing y algoritmo genético.\n\n'
                            'Uso académico. Nunca probar durante la conducción.')

    # ========================================================
    # ESTRUCTURA: SIDEBAR + PAGINAS
    # ========================================================
    def make_layout(self):
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=210)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text='◉  DriveGuard AI', fg='white', bg=SIDEBAR,
                 font=('Segoe UI', 17, 'bold')).pack(anchor='w', padx=20, pady=(18, 2))
        tk.Label(sidebar, text='Sistema de monitoreo\n(prototipo simulado)',
                 fg='#AFC4E2', bg=SIDEBAR, font=('Segoe UI', 9),
                 justify='left').pack(anchor='w', padx=20, pady=(0, 15))
        tk.Frame(sidebar, bg='#3D5A86', height=1).pack(fill='x', padx=16, pady=(0, 10))

        self.nav = {}
        for nombre in ('Inicio', 'Registros', 'Ayuda'):
            b = tk.Button(sidebar, text=nombre, anchor='w',
                          command=lambda n=nombre: self.show(n),
                          bg=SIDEBAR, fg='white', activebackground=SIDEBAR_ACTIVE,
                          activeforeground='white', font=('Segoe UI', 11),
                          borderwidth=0, cursor='hand2', padx=20, pady=9)
            b.pack(fill='x')
            self.nav[nombre] = b

        tk.Label(sidebar, text='HERRAMIENTAS', fg='#AFC4E2', bg=SIDEBAR,
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=20, pady=(12, 0))
        for texto, comando in (('Plan de acción (búsqueda IA)', self.open_plan),
                               ('Gráficas de eventos', self.open_charts),
                               ('Exportar datos CSV', self.export_csv)):
            tk.Button(sidebar, text=texto, anchor='w', command=comando,
                      bg=SIDEBAR, fg='#DCE6F5', activebackground=SIDEBAR_ACTIVE,
                      activeforeground='white', font=('Segoe UI', 10),
                      borderwidth=0, cursor='hand2', padx=20, pady=7).pack(fill='x')

        tk.Label(sidebar, text='SIMULACIÓN', fg='white', bg='#35619F',
                 font=('Segoe UI', 9, 'bold'), padx=10, pady=4).pack(
            side='bottom', pady=18)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side='right', fill='both', expand=True)
        self.pages['Inicio'] = self.page_inicio()
        self.pages['Registros'] = self.page_registros()
        self.pages['Ayuda'] = self.page_ayuda()
        self.show('Inicio')

    def show(self, nombre):
        for pagina in self.pages.values():
            pagina.pack_forget()
        self.pages[nombre].pack(fill='both', expand=True)
        for nombre_nav, boton in self.nav.items():
            boton.config(bg=SIDEBAR_ACTIVE if nombre_nav == nombre else SIDEBAR)
        if nombre == 'Registros':
            self.refresh_records()

    # ========================================================
    # HELPERS VISUALES
    # ========================================================
    def panel(self, parent, **pack):
        frame = tk.Frame(parent, bg=SURFACE, highlightbackground=LINE,
                         highlightthickness=1, padx=17, pady=11)
        frame.pack(**pack)
        return frame

    def label(self, parent, text, size=11, color=TEXT, bold=False, **kw):
        return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'),
                        fg=color, bg=parent.cget('bg'), **kw)

    def button(self, parent, caption, callback, color):
        tk.Button(parent, text=caption, command=callback, fg='white', bg=color,
                  activebackground=ACCENT, activeforeground='white',
                  font=('Segoe UI', 10, 'bold'), borderwidth=0,
                  cursor='hand2', pady=8).pack(fill='x', pady=4)

    def card(self, parent, title, variable, unit):
        frame = tk.Frame(parent, bg=CARD, padx=14, pady=10,
                         highlightbackground=LINE, highlightthickness=1)
        self.label(frame, title, 8, MUTED, True).pack(anchor='w')
        value = tk.Frame(frame, bg=CARD)
        value.pack(anchor='w', pady=(4, 0))
        tk.Label(value, textvariable=variable, font=('Segoe UI', 18, 'bold'),
                 fg=ACCENT, bg=CARD).pack(side='left')
        self.label(value, ' ' + unit, 10, MUTED).pack(side='left')
        return frame

    # ========================================================
    # PAGINA INICIO
    # ========================================================
    def page_inicio(self):
        page = tk.Frame(self.content, bg=BG, padx=22, pady=15)

        top = tk.Frame(page, bg=BG)
        top.pack(fill='x', pady=(0, 10))
        self.label(top, 'Monitoreo del conductor', 18, TEXT, True).pack(side='left')
        self.label(top, 'Solo datos simulados · Uso académico',
                   9, MUTED).pack(side='right')

        content = tk.Frame(page, bg=BG)
        content.pack(fill='both', expand=True)
        left = tk.Frame(content, bg=BG)
        left.pack(side='left', fill='both', expand=True, padx=(0, 9))
        right = tk.Frame(content, bg=BG, width=330)
        right.pack(side='right', fill='both', padx=(9, 0))
        right.pack_propagate(False)

        state_panel = self.panel(left, fill='x', pady=(0, 9))
        self.label(state_panel, 'ESTADO DE MONITOREO', 10, MUTED, True).pack(anchor='w')
        self.state_label = tk.Label(state_panel, textvariable=self.status,
                                    font=('Segoe UI', 31, 'bold'), fg=COLORS['NORMAL'], bg=SURFACE)
        self.state_label.pack(anchor='w', pady=(8, 6))
        tk.Label(state_panel, textvariable=self.message, font=('Segoe UI', 12),
                 fg=TEXT, bg=SURFACE, anchor='w', justify='left', wraplength=560).pack(fill='x')
        tk.Label(state_panel, textvariable=self.reason, font=('Segoe UI', 10),
                 fg=MUTED, bg=SURFACE, anchor='w', justify='left', wraplength=560).pack(fill='x', pady=(10, 0))

        cards = tk.Frame(left, bg=BG)
        cards.pack(fill='x', pady=(0, 9))
        self.card(cards, 'OJOS CERRADOS', self.eye, 's').pack(
            side='left', fill='both', expand=True, padx=(0, 8))
        self.card(cards, 'PARPADEOS', self.blinks, '/min').pack(
            side='left', fill='both', expand=True, padx=(0, 8))
        self.card(cards, 'BOSTEZOS', self.yawns, '/min').pack(
            side='left', fill='both', expand=True, padx=(0, 8))
        self.card(cards, 'INCLINACIÓN', self.tilt, '°').pack(
            side='left', fill='both', expand=True)

        metrics = self.panel(left, fill='x', pady=(0, 9))
        self.label(metrics, 'DATOS DE ENTRADA  ·  AJUSTABLES', 12, TEXT, True).pack(anchor='w', pady=(0, 3))
        self.scale(metrics, 'Ojos cerrados (segundos)', self.eye, 0, 4, 0.1)
        self.scale(metrics, 'Parpadeos por minuto', self.blinks, 0, 45, 1)
        self.scale(metrics, 'Bostezos por minuto', self.yawns, 0, 7, 1)
        self.scale(metrics, 'Inclinación de cabeza (grados)', self.tilt, 0, 50, 1)
        tk.Checkbutton(metrics, text='Rostro visible', variable=self.visible,
                       bg=SURFACE, fg=TEXT, selectcolor='white', activebackground=SURFACE,
                       activeforeground=TEXT, font=('Segoe UI', 11),
                       command=self.assess).pack(anchor='w', pady=(8, 0))

        notes = self.panel(left, fill='both', expand=True)
        self.label(notes, 'NOTAS DE DEMOSTRACIÓN', 11, TEXT, True).pack(anchor='w')
        explanation = ('El sistema calcula un nivel de riesgo con reglas ilustrativas. '
                       'No analiza video ni utiliza una IA entrenada en esta versión. '
                       'Los valores y umbrales no están validados para uso en carretera.\n\n'
                       'El Plan de acción usa algoritmos de búsqueda (BFS, DFS, UCS, '
                       'Greedy y A*) sobre un grafo de acciones correctivas.')
        self.label(notes, explanation, 10, MUTED, wraplength=560, justify='left').pack(anchor='w', pady=(10, 0))

        controls = self.panel(right, fill='x', pady=(0, 9))
        self.label(controls, 'ESCENARIO', 12, TEXT, True).pack(anchor='w')
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('Drive.TCombobox', fieldbackground='white', padding=7)
        combo = ttk.Combobox(controls, textvariable=self.scenario, values=list(SCENARIOS),
                             state='readonly', style='Drive.TCombobox')
        combo.pack(fill='x', pady=(10, 10))
        combo.bind('<<ComboboxSelected>>', lambda _event: self.apply_scenario(True))
        self.button(controls, 'Evaluar lectura actual', self.assess, '#1D6484')
        self.button(controls, 'Iniciar demostración automática', self.start, '#1E7A46')
        self.button(controls, 'Pausar demostración', self.stop, '#A33A4C')
        self.button(controls, 'Registrar lectura en CSV', self.register, '#41628F')
        self.button(controls, 'Plan de acción (búsqueda IA)', self.open_plan, '#5B4A8A')
        self.button(controls, 'Gráficas de eventos', self.open_charts, '#4A6B8A')
        self.button(controls, 'Ver ubicación de registros', self.show_path, '#41628F')
        tk.Label(controls, textvariable=self.sim_state, fg=ACCENT, bg=SURFACE,
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(12, 0))

        hist = self.panel(right, fill='both', expand=True)
        self.label(hist, 'EVENTOS RECIENTES', 12, TEXT, True).pack(anchor='w', pady=(0, 8))
        self.hist_box = tk.Listbox(hist, bg='white', fg=TEXT, font=('Consolas', 10),
                                   selectbackground='#C9D9F2', selectforeground=TEXT,
                                   relief='flat', highlightthickness=0, activestyle='none')
        self.hist_box.pack(fill='both', expand=True)

        return page

    # ========================================================
    # PAGINA REGISTROS
    # ========================================================
    def page_registros(self):
        page = tk.Frame(self.content, bg=BG, padx=22, pady=15)

        top = tk.Frame(page, bg=BG)
        top.pack(fill='x', pady=(0, 10))
        self.label(top, 'Registros de eventos', 18, TEXT, True).pack(side='left')
        tk.Button(top, text='Actualizar', command=self.refresh_records,
                  fg='white', bg='#1D6484', font=('Segoe UI', 9, 'bold'),
                  borderwidth=0, cursor='hand2', padx=12, pady=4).pack(side='right', padx=(6, 0))
        tk.Button(top, text='Exportar CSV', command=self.export_csv,
                  fg='white', bg='#41628F', font=('Segoe UI', 9, 'bold'),
                  borderwidth=0, cursor='hand2', padx=12, pady=4).pack(side='right', padx=(6, 0))
        tk.Button(top, text='Ver gráficas', command=self.open_charts,
                  fg='white', bg='#4A6B8A', font=('Segoe UI', 9, 'bold'),
                  borderwidth=0, cursor='hand2', padx=12, pady=4).pack(side='right')

        tabla_panel = self.panel(page, fill='both', expand=True)
        self.label(tabla_panel, 'data/eventos.csv', 10, MUTED, True).pack(anchor='w', pady=(0, 6))
        columnas = ('fecha_hora', 'escenario', 'nivel', 'puntuacion', 'motivos')
        self.tabla = ttk.Treeview(tabla_panel, columns=columnas,
                                  show='headings', height=14)
        for col, txt, w in (('fecha_hora', 'Fecha y hora', 150),
                            ('escenario', 'Escenario', 140),
                            ('nivel', 'Nivel', 110),
                            ('puntuacion', 'Puntos', 60),
                            ('motivos', 'Motivos', 320)):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor='w')
        scroll = ttk.Scrollbar(tabla_panel, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        self.reg_nota = self.label(page, '', 9, MUTED)
        self.reg_nota.pack(anchor='w', pady=(8, 0))
        return page

    def refresh_records(self):
        self.tabla.delete(*self.tabla.get_children())
        if not EVENTS.exists():
            self.reg_nota.config(
                text='Aún no hay registros: usa "Registrar lectura en CSV" o cambia a un estado anormal.')
            return
        import csv
        with EVENTS.open(newline='', encoding='utf-8-sig') as f:
            filas = list(csv.DictReader(f))
        for fila in filas:
            self.tabla.insert('', 'end', values=(
                fila['fecha_hora'], fila['escenario'], fila['nivel'],
                fila['puntuacion'], fila['motivos']))
        self.reg_nota.config(text=f'{len(filas)} registro(s). El archivo permanece al cerrar la aplicación.')

    # ========================================================
    # PAGINA AYUDA
    # ========================================================
    def page_ayuda(self):
        page = tk.Frame(self.content, bg=BG, padx=22, pady=15)
        self.label(page, 'Ayuda y acerca del prototipo', 18, TEXT, True).pack(anchor='w', pady=(0, 10))

        panel = self.panel(page, fill='both', expand=True)
        texto = tk.Text(panel, bg='white', fg=TEXT, font=('Segoe UI', 10),
                        wrap='word', relief='flat', padx=10, pady=10)
        texto.insert('1.0',
            'QUÉ ES ESTE PROGRAMA\n'
            '-------------------\n'
            'DriveGuard AI es un prototipo educativo que SIMULA señales de cansancio '
            'del conductor. No usa cámara ni un modelo de IA entrenado.\n\n'
            'ESTADOS\n'
            '-------\n'
            'NORMAL (verde): sin señales destacadas en los datos simulados.\n'
            'PRECAUCIÓN (ámbar): se activaron algunas reglas de cansancio.\n'
            'ALERTA ALTA (rojo): puntuación alta; suena un aviso si el equipo lo permite.\n'
            'SIN ROSTRO (gris): no se puede evaluar; NO es somnolencia.\n\n'
            'CÓMO PROBARLO\n'
            '-------------\n'
            '1. En Inicio elige un escenario o mueve las barras.\n'
            '2. Pulsa "Evaluar lectura actual" o "Iniciar demostración automática".\n'
            '3. Guarda lecturas con "Registrar lectura en CSV" y revísalas en Registros.\n'
            '4. Con estado PRECAUCIÓN o ALERTA ALTA abre "Plan de acción" para ver la\n'
            '   secuencia de acciones calculada con BFS, DFS, UCS, Greedy y A*.\n\n'
            'TEMAS DE IA APLICADOS\n'
            '---------------------\n'
            '· Problema de búsqueda: niveles de riesgo como estados, acciones como aristas.\n'
            '· BFS, DFS, UCS: búsquedas ciegas y por costo sobre el grafo de acciones.\n'
            '· Heurística h(n), Greedy y A*: búsqueda informada hacia NORMAL.\n'
            '· Hill Climbing y algoritmo genético: calibración de umbrales.\n'
            '· TTK: componentes de la interfaz (combos, tablas).\n\n'
            'IMPORTANTE\n'
            '----------\n'
            'Uso académico en un entorno seguro. Nunca probar durante la conducción.\n'
            'Los umbrales y costos son ilustrativos; no están validados.\n')
        texto.config(state='disabled')
        texto.pack(fill='both', expand=True)
        return page

    # ========================================================
    # CONTROLES (igual que antes)
    # ========================================================
    def scale(self, parent, title, variable, minimum, maximum, step):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill='x', pady=(1, 0))
        self.label(row, title, 10, TEXT).pack(anchor='w')
        slider = tk.Scale(row, from_=minimum, to=maximum, resolution=step,
                          variable=variable, orient='horizontal', command=lambda _v: None if self.loading else self.assess(),
                          bg=SURFACE, fg=ACCENT, troughcolor=LINE,
                          highlightthickness=0, activebackground=ACCENT,
                          showvalue=True, length=400, width=8, sliderlength=17,
                          borderwidth=0, font=('Segoe UI', 9))
        slider.pack(fill='x')

    def signals(self):
        return Signals(self.eye.get(), self.blinks.get(), self.yawns.get(),
                       self.tilt.get(), self.visible.get())

    def apply_scenario(self, reevaluate=True):
        s = SCENARIOS[self.scenario.get()]
        self.loading = True
        self.eye.set(s.eye_closed_seconds)
        self.blinks.set(s.blinks_per_minute)
        self.yawns.set(s.yawns_per_minute)
        self.tilt.set(s.head_tilt_degrees)
        self.visible.set(s.face_visible)
        self.loading = False
        if reevaluate:
            self.assess()

    def assess(self):
        r = evaluate(self.signals())
        previous = self.last_level
        self.last_level = r.level
        self.status.set(r.level)
        self.message.set(r.message)
        self.reason.set('Señales: ' + (', '.join(r.reasons) if r.reasons else 'ninguna destacada'))
        self.state_label.configure(fg=COLORS[r.level])
        if r.level != previous:
            self.add_history(r.level)
            if r.level in ('PRECAUCIÓN', 'ALERTA ALTA', 'SIN ROSTRO'):
                save_event(EVENTS, self.scenario.get(), self.signals(), r)
            if r.level == 'ALERTA ALTA':
                try:
                    self.root.bell()
                except tk.TclError:
                    pass
        return r

    def add_history(self, level):
        stamp = datetime.now().strftime('%H:%M:%S')
        self.hist_box.insert(0, f'{stamp}  {level}')
        if self.hist_box.size() > 100:
            self.hist_box.delete(100, tk.END)

    def register(self):
        r = self.assess()
        save_event(EVENTS, self.scenario.get(), self.signals(), r)
        self.add_history('LECTURA REGISTRADA')
        messagebox.showinfo('Registro guardado', f'Lectura SIMULADA guardada en:\n{EVENTS}')

    def open_plan(self):
        from busqueda_ui import abrir_plan
        abrir_plan(self.root, self.last_level)

    def open_charts(self):
        from graficas import abrir_graficas
        abrir_graficas(self.root)

    def export_csv(self):
        if not EVENTS.exists():
            messagebox.showinfo('Sin registros',
                                'Todavía no existe eventos.csv para exportar.')
            return
        destino = filedialog.asksaveasfilename(
            title='Exportar registros', defaultextension='.csv',
            initialfile='eventos_driveguard.csv',
            filetypes=[('Archivo CSV', '*.csv')])
        if destino:
            shutil.copy(EVENTS, destino)
            messagebox.showinfo('Exportado', f'Copia guardada en:\n{destino}')

    def show_path(self):
        messagebox.showinfo('Ubicación de los datos',
                            'Los registros simulados se guardan en:\n'
                            f'{EVENTS}\n\nEl archivo se crea después de registrar un evento.')

    def start(self):
        if self.running:
            return
        self.running = True
        self.sim_state.set('SIMULACIÓN AUTOMÁTICA ACTIVA')
        self.auto_tick = 0
        self.next_tick()

    def next_tick(self):
        if not self.running:
            return
        sequence = ['Conducción normal'] * 4 + ['Cansancio leve'] * 3 + [
            'Somnolencia alta'] * 3 + ['Rostro no visible'] * 2
        scenario = sequence[self.auto_tick % len(sequence)]
        self.scenario.set(scenario)
        self.apply_scenario(False)
        s = SCENARIOS[scenario]
        if s.face_visible:
            self.loading = True
            self.eye.set(max(0, round(s.eye_closed_seconds + self.rng.uniform(-0.12, 0.12), 2)))
            self.blinks.set(max(0, s.blinks_per_minute + self.rng.randint(-2, 2)))
            self.loading = False
        self.assess()
        self.auto_tick += 1
        self.after_id = self.root.after(1700, self.next_tick)

    def stop(self):
        self.running = False
        self.sim_state.set('SIMULACIÓN EN PAUSA')
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def close(self):
        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    LoginApp(root, lambda: DemoApp(root))
    root.mainloop()


if __name__ == '__main__':
    main()
