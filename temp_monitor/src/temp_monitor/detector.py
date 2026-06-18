"""② 이상 탐지 — 임계 범위 이탈 + 이동평균 대비 급변(스파이크)."""
from __future__ import annotations
import pandas as pd
from .config import Config

# 알람 표 스키마: timestamp, zone, temp_c, rule, severity
ALARM_COLUMNS = ["timestamp", "zone", "temp_c", "rule", "severity"]

# critical 경계: 정상범위를 이 폭(°C) 이상 벗어나면 critical, 그 미만은 warn
_CRITICAL_MARGIN_C = 2.0


def detect_threshold(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """구역별 정상범위(min~max)를 벗어난 행을 알람으로 반환.

    rule="threshold", severity는 일탈폭에 따라 'warn'/'critical'.
    """
    rows = []
    for zone, spec in config.zones.items():
        zdf = df[df["zone"] == zone]
        if zdf.empty:
            continue
        below = zdf["temp_c"] < spec.min_c
        above = zdf["temp_c"] > spec.max_c
        out = zdf[below | above]
        for _, r in out.iterrows():
            if r["temp_c"] < spec.min_c:
                dev = spec.min_c - r["temp_c"]
            else:
                dev = r["temp_c"] - spec.max_c
            severity = "critical" if dev >= _CRITICAL_MARGIN_C else "warn"
            rows.append({
                "timestamp": r["timestamp"],
                "zone": zone,
                "temp_c": r["temp_c"],
                "rule": "threshold",
                "severity": severity,
            })
    return pd.DataFrame(rows, columns=ALARM_COLUMNS)


def detect_spike(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """구역별 이동평균±(sigma*std)를 벗어난 급변을 알람으로 반환.

    rule="spike". 창 크기·sigma는 config.detection 사용.
    """
    window = config.detection.spike_window
    sigma = config.detection.spike_sigma
    rows = []
    for zone in config.zones:
        zdf = df[df["zone"] == zone].sort_values("timestamp")
        if len(zdf) < window:
            continue
        roll = zdf["temp_c"].rolling(window=window, min_periods=window)
        mean = roll.mean()
        std = roll.std()
        upper = mean + sigma * std
        lower = mean - sigma * std
        mask = (zdf["temp_c"] > upper) | (zdf["temp_c"] < lower)
        mask = mask.fillna(False)
        out = zdf[mask]
        for _, r in out.iterrows():
            rows.append({
                "timestamp": r["timestamp"],
                "zone": zone,
                "temp_c": r["temp_c"],
                "rule": "spike",
                "severity": "warn",
            })
    return pd.DataFrame(rows, columns=ALARM_COLUMNS)


def detect_anomalies(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """threshold + spike 알람을 합쳐 ALARM_COLUMNS 형식으로 반환."""
    th = detect_threshold(df, config)
    sp = detect_spike(df, config)
    alarms = pd.concat([th, sp], ignore_index=True)
    if alarms.empty:
        return pd.DataFrame(columns=ALARM_COLUMNS)
    alarms = alarms.sort_values(["timestamp", "zone", "rule"], kind="mergesort")
    return alarms.reset_index(drop=True)
