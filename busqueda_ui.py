"""Ventana de plan de acción con algoritmos de búsqueda (demo educativa).

Se abre desde el panel principal con el nivel de riesgo actual como
estado inicial y NORMAL como objetivo.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from busqueda import (ALGORITMOS, GRAFO, HEURISTICA, LECTURAS_ETIQUETADAS,
                      errores, hill_climbing_umbrales,
                      algoritmo_genetico_umbrales)

BG = '#E9EEF5'
SURFACE = '#FFFFFF'
TEXT = '#1E2A3A'
MUTED = '#5B6B82'
ACCENT = '#2563EB'


class VentanaPlan(tk.Toplevel):
    def __init__(self, master, nivel_inicial):
        super().__init__(master)
        self.nivel = nivel_inicial
        self.title('DriveGuard AI | Plan de acción con búsqueda')
        self.geometry('980x640')
        self.minsize(860, 560)
        self.configure(bg=BG)
        self.transient(master)

        top = tk.Frame(self, bg=BG, padx=20, pady=10)
        top.pack(fill='x')
        tk.Label(top, text='PLAN DE ACCIÓN · BÚSQUEDA EN IA',
                 font=('Segoe UI', 14, 'bold'), fg=TEXT, bg=BG).pack(side='left')
        tk.Label(top, text='GRAFO DE ACCIONES · SIMULADO',
                 font=('Segoe UI', 9, 'bold'), fg=ACCENT, bg=BG).pack(side='right')

        config = tk.Frame(self, bg=SURFACE, padx=17, pady=11,
                          highlightbackground='#D5DEE9', highlightthickness=1)
        config.pack(fill='x', padx=20)
        tk.Label(config, text=f'Estado inicial (s0): {nivel_inicial}    '
                              f'Objetivo (G): NORMAL    '
                              f'h(s0) = {HEURISTICA[nivel_inicial]}',
                 font=('Segoe UI', 11), fg=TEXT, bg=SURFACE).pack(side='left')

        barra = tk.Frame(self, bg=SURFACE, padx=17, pady=11,
                         highlightbackground='#D5DEE9', highlightthickness=1)
        barra.pack(fill='x', padx=20, pady=(9, 0))
        tk.Label(barra, text='Algoritmo', fg=TEXT, bg=SURFACE,
                 font=('Segoe UI', 10, 'bold')).pack(side='left')
        self.algoritmo = tk.StringVar(value='A*')
        ttk.Combobox(barra, textvariable=self.algoritmo, state='readonly',
                     values=list(ALGORITMOS), width=8).pack(side='left', padx=8)
        self.boton(barra, 'Ejecutar', self.ejecutar, '#1D6484')
        self.boton(barra, 'Comparar los 5', self.comparar, '#166534')
        self.boton(barra, 'Calibrar (Hill Climbing)', self.hill, '#5B4A8A')
        self.boton(barra, 'Calibrar (Genético)', self.genetico, '#5B4A8A')

        contenido = tk.Frame(self, bg=BG, padx=20, pady=9)
        contenido.pack(fill='both', expand=True)

        izq = tk.Frame(contenido, bg=SURFACE, padx=15, pady=11,
                       highlightbackground='#D5DEE9', highlightthickness=1)
        izq.pack(side='left', fill='both', expand=True, padx=(0, 8))
        tk.Label(izq, text='SECUENCIA RECOMENDADA', fg=TEXT, bg=SURFACE,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        self.tabla = ttk.Treeview(izq, columns=('accion', 'destino', 'costo'),
                                  show='headings', height=6)
        for col, txt, w in (('accion', 'Acción', 300),
                            ('destino', 'Lleva a', 110),
                            ('costo', 'Costo', 60)):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor='w')
        self.tabla.pack(fill='x', pady=8)
        self.resumen = tk.Label(izq, text='', fg=ACCENT, bg=SURFACE,
                                font=('Segoe UI', 10, 'bold'), justify='left',
                                anchor='w', wraplength=430)
        self.resumen.pack(anchor='w', fill='x')
        tk.Label(izq, text='COMPARATIVA', fg=TEXT, bg=SURFACE,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(10, 0))
        self.cmp = ttk.Treeview(izq, columns=('alg', 'ruta', 'costo', 'exp'),
                                show='headings', height=5)
        for col, txt, w in (('alg', 'Alg.', 70), ('ruta', 'Ruta', 230),
                            ('costo', 'Costo', 60), ('exp', 'Expandidos', 90)):
            self.cmp.heading(col, text=txt)
            self.cmp.column(col, width=w, anchor='w')
        self.cmp.pack(fill='both', expand=True, pady=8)

        der = tk.Frame(contenido, bg=SURFACE, padx=15, pady=11,
                       highlightbackground='#D5DEE9', highlightthickness=1)
        der.pack(side='right', fill='both', expand=True, padx=(8, 0))
        tk.Label(der, text='REGISTRO DE LA BÚSQUEDA', fg=TEXT, bg=SURFACE,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        self.log = tk.Text(der, bg='#F7FAFD', fg=TEXT, font=('Consolas', 10),
                           relief='flat', wrap='word')
        scroll = ttk.Scrollbar(der, orient='vertical', command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side='left', fill='both', expand=True, pady=(8, 0))
        scroll.pack(side='right', fill='y', pady=(8, 0))

        self.ejecutar()

    def boton(self, padre, texto, comando, color):
        tk.Button(padre, text=texto, command=comando, fg='white', bg=color,
                  font=('Segoe UI', 9, 'bold'), borderwidth=0,
                  cursor='hand2', pady=6, padx=8).pack(side='left', padx=4)

    def escribir(self, lineas):
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, '\n'.join(lineas))

    def mostrar(self, r):
        self.tabla.delete(*self.tabla.get_children())
        if not r['camino']:
            self.resumen.config(text=f'{r["algoritmo"]}: no se encontró ruta a NORMAL.')
            return
        for i, (accion, destino) in enumerate(zip(r['acciones'], r['camino'][1:])):
            origen = r['camino'][i]
            costo = next(c for a, d, c in GRAFO[origen]
                         if a == accion and d == destino)
            self.tabla.insert('', 'end', values=(accion, destino, costo))
        self.resumen.config(text=f"{r['algoritmo']}  |  Ruta: "
                            f"{' → '.join(r['camino'])}\n"
                            f"Costo total: {r['costo']}  |  "
                            f"Estados expandidos: {r['cantidad_expandidos']}")
        self.escribir(r['registro'])

    def ejecutar(self):
        r = ALGORITMOS[self.algoritmo.get()](self.nivel)
        self.mostrar(r)

    def comparar(self):
        self.cmp.delete(*self.cmp.get_children())
        resultados = [ALGORITMOS[n](self.nivel) for n in ALGORITMOS]
        for r in resultados:
            self.cmp.insert('', 'end', values=(
                r['algoritmo'],
                ' → '.join(r['camino']) if r['camino'] else 'sin ruta',
                r['costo'], r['cantidad_expandidos']))
        self.mostrar(resultados[list(ALGORITMOS).index(self.algoritmo.get())]
                     if self.algoritmo.get() in ALGORITMOS else resultados[-1])

    def hill(self):
        cfg, e, historial = hill_climbing_umbrales()
        base = errores()
        self.escribir([f'Hill Climbing sobre blinks_caution_per_minute',
                       f'Errores con umbrales actuales: {base}',
                       f'Errores tras calibrar: {e}',
                       f'Parpadeos cautela calibrado: '
                       f'{cfg.blinks_caution_per_minute}/min',
                       '', 'Historial (valor, errores):'] +
                      [f'  {v}  →  {x} error(es)' for v, x in historial])
        self.resumen.config(text='Calibración ilustrativa sobre lecturas '
                            'simuladas; los umbrales no se guardan.')

    def genetico(self):
        cfg, e, historial = algoritmo_genetico_umbrales()
        self.escribir([f'Algoritmo genético · {len(LECTURAS_ETIQUETADAS)} '
                       f'lecturas etiquetadas',
                       f'Mejores errores por generación: {historial}',
                       '', 'Mejor conjunto de umbrales encontrado:',
                       f'  ojos precaución: {cfg.eye_closed_caution_seconds} s',
                       f'  ojos alto:       {cfg.eye_closed_high_seconds} s',
                       f'  parpadeos:       {cfg.blinks_caution_per_minute}/min',
                       f'  bostezos:        {cfg.yawns_caution_per_minute}/min',
                       f'  inclinación:     {cfg.head_tilt_caution_degrees}°',
                       f'  puntos alerta:   {cfg.high_score_min}'])
        self.resumen.config(text='Resultado ilustrativo con semilla fija; '
                            'la evaluación no cambia en la aplicación.')


def abrir_plan(master, nivel):
    if nivel == 'SIN ROSTRO':
        messagebox.showinfo('Sin plan disponible',
                            'SIN ROSTRO significa que no es posible evaluar.\n'
                            'Ajusta las señales antes de pedir un plan de acción.')
        return None
    if nivel == 'NORMAL':
        messagebox.showinfo('Sin riesgo',
                            'La lectura actual es NORMAL: no se requiere '
                            'una secuencia de acciones correctivas.')
        return None
    return VentanaPlan(master, nivel)
