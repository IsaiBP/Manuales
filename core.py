"""Lógica de DriveGuard AI (demo educativa basada en datos SIMULADOS)."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv


@dataclass(frozen=True)
class Signals:
    eye_closed_seconds: float = 0.0
    blinks_per_minute: int = 15
    yawns_per_minute: int = 0
    head_tilt_degrees: float = 0.0
    face_visible: bool = True


@dataclass(frozen=True)
class Thresholds:
    eye_closed_caution_seconds: float = 1.2
    eye_closed_high_seconds: float = 2.5
    blinks_caution_per_minute: int = 28
    yawns_caution_per_minute: int = 3
    head_tilt_caution_degrees: float = 25.0
    high_score_min: int = 4


@dataclass(frozen=True)
class Assessment:
    level: str
    score: int
    reasons: tuple[str, ...]
    message: str


def evaluate(signals: Signals, thresholds: Thresholds | None = None) -> Assessment:
    """Reglas ilustrativas, NO un modelo de IA ni umbrales clínicos validados."""
    cfg = thresholds or Thresholds()
    if not signals.face_visible:
        return Assessment('SIN ROSTRO', 0, ('No se detecta el rostro',),
                          'No es posible evaluar. Ajusta la posición de la cámara.')
    reasons: list[str] = []
    score = 0
    if signals.eye_closed_seconds >= cfg.eye_closed_high_seconds:
        score += 4
        reasons.append('Cierre prolongado de ojos')
    elif signals.eye_closed_seconds >= cfg.eye_closed_caution_seconds:
        score += 2
        reasons.append('Ojos cerrados más de lo habitual')
    if signals.blinks_per_minute >= cfg.blinks_caution_per_minute:
        score += 1
        reasons.append('Frecuencia de parpadeo elevada')
    if signals.yawns_per_minute >= cfg.yawns_caution_per_minute:
        score += 2
        reasons.append('Bostezos frecuentes')
    if abs(signals.head_tilt_degrees) >= cfg.head_tilt_caution_degrees:
        score += 2
        reasons.append('Inclinación pronunciada de la cabeza')
    if score >= cfg.high_score_min:
        return Assessment('ALERTA ALTA', score, tuple(reasons),
                          '¡Advertencia! Detente en un lugar seguro y descansa.')
    if score >= 2:
        return Assessment('PRECAUCIÓN', score, tuple(reasons),
                          'Se observan señales de cansancio. Considera hacer una pausa.')
    return Assessment('NORMAL', score, tuple(reasons),
                      'Sin señales destacadas en los datos simulados.')


FIELDNAMES = ['fecha_hora', 'origen', 'escenario', 'nivel', 'puntuacion',
              'ojos_cerrados_seg', 'parpadeos_min', 'bostezos_min',
              'inclinacion_grados', 'rostro_visible', 'motivos']


def save_event(file_path: str | Path, scenario: str, signals: Signals,
               result: Assessment, origin: str = 'SIMULADO') -> None:
    """Guarda solamente métricas sintéticas; no utiliza fotografías ni video."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not file_path.exists() or file_path.stat().st_size == 0
    with file_path.open('a', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerow({
            'fecha_hora': datetime.now().isoformat(timespec='seconds'),
            'origen': origin,
            'escenario': scenario,
            'nivel': result.level,
            'puntuacion': result.score,
            'ojos_cerrados_seg': round(signals.eye_closed_seconds, 2),
            'parpadeos_min': signals.blinks_per_minute,
            'bostezos_min': signals.yawns_per_minute,
            'inclinacion_grados': round(signals.head_tilt_degrees, 2),
            'rostro_visible': signals.face_visible,
            'motivos': '; '.join(result.reasons),
        })
