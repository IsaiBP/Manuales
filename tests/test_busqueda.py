import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import Thresholds
from busqueda import (ALGORITMOS, HEURISTICA, errores,
                      hill_climbing_umbrales, algoritmo_genetico_umbrales)


class SearchTests(unittest.TestCase):
    def test_bfs_desde_alerta(self):
        r = ALGORITMOS['BFS']('ALERTA ALTA')
        self.assertEqual(r['camino'][-1], 'NORMAL')
        self.assertEqual(r['aristas'], 1)  # ruta directa de una accion

    def test_ucs_costo_optimo(self):
        r = ALGORITMOS['UCS']('ALERTA ALTA')
        self.assertEqual(r['camino'], ['ALERTA ALTA', 'PRECAUCIÓN', 'NORMAL'])
        self.assertEqual(r['costo'], 3)  # pausa 15 min + ventilar

    def test_astar_optimo(self):
        r = ALGORITMOS['A*']('ALERTA ALTA')
        self.assertEqual(r['costo'], 3)
        self.assertEqual(r['camino'][-1], 'NORMAL')

    def test_greedy_no_optimo(self):
        # Greedy elige h=0 (NORMAL directo) sin mirar el costo acumulado.
        r = ALGORITMOS['Greedy']('ALERTA ALTA')
        self.assertEqual(r['costo'], 4)

    def test_heuristica_admisible(self):
        # h(n) nunca sobreestima el costo minimo real de UCS.
        for estado in ('PRECAUCIÓN', 'ALERTA ALTA'):
            self.assertLessEqual(HEURISTICA[estado],
                                 ALGORITMOS['UCS'](estado)['costo'])

    def test_hill_climbing_no_empeora(self):
        cfg, e, historial = hill_climbing_umbrales()
        self.assertIsInstance(cfg, Thresholds)
        self.assertLessEqual(e, errores())
        self.assertGreaterEqual(len(historial), 1)

    def test_genetico_resultados_validos(self):
        cfg, e, historial = algoritmo_genetico_umbrales(
            poblacion=10, generaciones=5, semilla=7)
        self.assertIsNotNone(cfg)
        self.assertGreater(cfg.eye_closed_high_seconds,
                           cfg.eye_closed_caution_seconds)
        self.assertLessEqual(e, len(historial) + 1)


if __name__ == '__main__':
    unittest.main()
