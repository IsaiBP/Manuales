# ============================================================
# GRAFICAS DE DRIVEGUARD AI
# ============================================================
# Ventana con graficas matplotlib incrustadas en Tkinter,
# siguiendo el estilo de las practicas (barra, linea con
# marcadores, promedio y anotaciones).
#
# Datos: data/eventos.csv (registros reales de la sesion).
# Si todavia no existe, usa ejemplo_eventos_simulados.csv
# y se indica que son datos de ejemplo.
# ============================================================
import csv
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ROOT = Path(__file__).resolve().parent
EVENTOS = ROOT / 'data' / 'eventos.csv'
EJEMPLO = ROOT / 'data' / 'ejemplo_eventos_simulados.csv'

BG = '#E9EEF5'
SURFACE = '#FFFFFF'
TEXT = '#1E2A3A'
ACCENT = '#2563EB'
COLORES_NIVEL = {'NORMAL': '#34D399', 'PRECAUCIÓN': '#FBBF24',
                 'ALERTA ALTA': '#FB7185', 'SIN ROSTRO': '#94A3B8'}


# ------------------------------------------------------------
# 1. LEER LOS REGISTROS
# ------------------------------------------------------------
def leer_eventos():
    """Devuelve (filas, es_ejemplo)."""
    archivo = EVENTOS if EVENTOS.exists() else EJEMPLO
    es_ejemplo = not EVENTOS.exists()
    with archivo.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f)), es_ejemplo


# ------------------------------------------------------------
# 2. FIGURA CON TEMA OSCURO
# ------------------------------------------------------------
def nueva_figura():
    fig = Figure(figsize=(6, 4), facecolor=SURFACE)
    ax = fig.add_subplot(111)
    ax.set_facecolor('#F7FAFD')
    ax.tick_params(colors=TEXT)
    for lado in ('bottom', 'left'):
        ax.spines[lado].set_color(TEXT)
    for lado in ('top', 'right'):
        ax.spines[lado].set_visible(False)
    ax.grid(linestyle='--', alpha=0.3, color=TEXT)
    return fig, ax


def pie(ax, nota):
    ax.set_xlabel(f'{nota}  |  Fuente: registros del prototipo (simulados)',
                  color='gray', fontsize=8)


# ------------------------------------------------------------
# 3. LAS TRES GRAFICAS
# ------------------------------------------------------------
def figura_niveles(filas):
    """Barras: cuantos eventos hay por cada nivel."""
    niveles = list(COLORES_NIVEL)
    conteo = [sum(1 for f in filas if f['nivel'] == n) for n in niveles]
    fig, ax = nueva_figura()
    ax.bar(niveles, conteo, color=[COLORES_NIVEL[n] for n in niveles])
    ax.set_title('Eventos por nivel de alerta', color=TEXT,
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('Cantidad de eventos', color=TEXT)
    for i, c in enumerate(conteo):
        ax.text(i, c + 0.05, str(c), ha='center', color=TEXT)
    ax.set_ylim(0, max(conteo + [1]) + 1)
    pie(ax, 'Cuenta las filas del CSV por nivel')
    return fig


def figura_puntuaciones(filas):
    """Linea: puntuacion de cada lectura y su promedio."""
    puntos = [int(float(f['puntuacion'])) for f in filas]
    x = list(range(1, len(puntos) + 1))
    fig, ax = nueva_figura()
    ax.plot(x, puntos, color=ACCENT, linewidth=2.5, marker='o',
            markerfacecolor='white', label='Puntuación')
    if puntos:
        promedio = sum(puntos) / len(puntos)
        ax.axhline(promedio, color='#FB7185', linestyle='--',
                   linewidth=2, label=f'Promedio = {promedio:.1f}')
        ax.legend(facecolor=SURFACE, labelcolor=TEXT)
    ax.set_title('Puntuación por lectura', color=TEXT,
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Lectura', color=TEXT)
    ax.set_ylabel('Puntos', color=TEXT)
    pie(ax, 'Cada punto es una fila del CSV')
    return fig


def figura_senales(filas):
    """Barras horizontales: senales de la ultima lectura."""
    ultima = filas[-1]
    nombres = ['Ojos (s)', 'Parpadeos', 'Bostezos', 'Inclinación (°)']
    valores = [float(ultima['ojos_cerrados_seg']),
               float(ultima['parpadeos_min']),
               float(ultima['bostezos_min']),
               float(ultima['inclinacion_grados'])]
    fig, ax = nueva_figura()
    ax.barh(nombres, valores, color=ACCENT)
    ax.set_title(f"Señales de la última lectura ({ultima['nivel']})",
                 color=TEXT, fontsize=14, fontweight='bold', pad=15)
    for i, v in enumerate(valores):
        ax.text(v, i, f'  {v:g}', va='center', color=TEXT)
    pie(ax, f"Escenario: {ultima['escenario']} · {ultima['fecha_hora']}")
    return fig


GRAFICAS = {
    'Eventos por nivel': figura_niveles,
    'Puntuación por lectura': figura_puntuaciones,
    'Señales de la última lectura': figura_senales,
}


# ------------------------------------------------------------
# 4. VENTANA CON LA GRAFICA INCRUSTADA
# ------------------------------------------------------------
class VentanaGraficas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('DriveGuard AI | Gráficas')
        self.geometry('900x620')
        self.minsize(760, 520)
        self.configure(bg=BG)
        self.transient(master)

        barra = tk.Frame(self, bg=SURFACE, padx=17, pady=11,
                         highlightbackground='#D5DEE9', highlightthickness=1)
        barra.pack(fill='x', padx=20, pady=(15, 0))
        tk.Label(barra, text='GRÁFICAS DE EVENTOS', fg=TEXT, bg=SURFACE,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        self.elegida = tk.StringVar(value='Eventos por nivel')
        ttk.Combobox(barra, textvariable=self.elegida, state='readonly',
                     values=list(GRAFICAS), width=28).pack(side='left', padx=12)
        tk.Button(barra, text='Actualizar', command=self.dibujar,
                  fg='white', bg='#1D6484', font=('Segoe UI', 9, 'bold'),
                  borderwidth=0, pady=5, padx=10).pack(side='left')
        self.nota = tk.Label(barra, text='', fg=ACCENT, bg=SURFACE,
                             font=('Segoe UI', 9))
        self.nota.pack(side='right')

        self.marco = tk.Frame(self, bg=SURFACE,
                              highlightbackground='#D5DEE9',
                              highlightthickness=1)
        self.marco.pack(fill='both', expand=True, padx=20, pady=15)
        self.canvas = None
        self.elegida.trace_add('write', lambda *_: self.dibujar())
        self.dibujar()

    def dibujar(self):
        filas, es_ejemplo = leer_eventos()
        self.nota.config(text='Datos de ejemplo (aún no hay registros)'
                         if es_ejemplo else f'{len(filas)} registro(s) en eventos.csv')
        fig = GRAFICAS[self.elegida.get()](filas)
        fig.tight_layout()
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.marco)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True,
                                         padx=10, pady=10)


def abrir_graficas(master):
    return VentanaGraficas(master)
