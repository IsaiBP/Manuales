import sys
from pathlib import Path
import tempfile
import csv
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import Signals, Thresholds, evaluate, save_event


class AssessmentTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(evaluate(Signals()).level, 'NORMAL')

    def test_caution(self):
        self.assertEqual(evaluate(Signals(eye_closed_seconds=1.4)).level, 'PRECAUCIÓN')

    def test_high(self):
        self.assertEqual(evaluate(Signals(eye_closed_seconds=2.8)).level, 'ALERTA ALTA')

    def test_combined_indicators(self):
        self.assertEqual(evaluate(Signals(yawns_per_minute=3, head_tilt_degrees=27)).level,
                         'ALERTA ALTA')

    def test_no_face_is_not_drowsiness(self):
        self.assertEqual(evaluate(Signals(eye_closed_seconds=3, face_visible=False)).level,
                         'SIN ROSTRO')

    def test_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'eventos.csv'
            s = Signals()
            save_event(p, 'Conducción normal', s, evaluate(s))
            with p.open(newline='', encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['origen'], 'SIMULADO')


if __name__ == '__main__':
    unittest.main()
