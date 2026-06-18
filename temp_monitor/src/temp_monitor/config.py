"""① 설정 로드/검증 — 구역별 정상범위·임계, 탐지 파라미터."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ZoneSpec:
    """한 구역의 정상 온도 범위(°C)."""
    name: str
    min_c: float
    max_c: float


@dataclass
class DetectionParams:
    """급변(스파이크) 탐지 파라미터."""
    spike_window: int   # 이동평균 창(샘플 수)
    spike_sigma: float  # 이동평균 ± sigma*표준편차 초과 시 알람


@dataclass
class Config:
    zones: dict[str, ZoneSpec]
    detection: DetectionParams


def load_config(path: str | Path) -> Config:
    """YAML 설정 파일을 읽어 Config로 변환한다.

    Raises:
        FileNotFoundError, ValueError: 파일 없음/필수 키 누락 시.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없음: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if "zones" not in raw or not raw["zones"]:
        raise ValueError("설정에 'zones' 키가 없거나 비어 있음")
    if "detection" not in raw:
        raise ValueError("설정에 'detection' 키가 없음")

    zones: dict[str, ZoneSpec] = {}
    for name, spec in raw["zones"].items():
        if spec is None or "min" not in spec or "max" not in spec:
            raise ValueError(f"구역 '{name}' 설정에 min/max 누락")
        min_c = float(spec["min"])
        max_c = float(spec["max"])
        if min_c > max_c:
            raise ValueError(f"구역 '{name}' min({min_c}) > max({max_c})")
        zones[str(name)] = ZoneSpec(name=str(name), min_c=min_c, max_c=max_c)

    det = raw["detection"]
    if "spike_window" not in det or "spike_sigma" not in det:
        raise ValueError("detection에 spike_window/spike_sigma 누락")
    window = int(det["spike_window"])
    sigma = float(det["spike_sigma"])
    if window < 2:
        raise ValueError("spike_window는 2 이상이어야 함")
    if sigma <= 0:
        raise ValueError("spike_sigma는 양수여야 함")

    detection = DetectionParams(spike_window=window, spike_sigma=sigma)
    return Config(zones=zones, detection=detection)
