"""① CSV 로드·검증 — timestamp, zone, temp_c."""
from __future__ import annotations
from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "zone", "temp_c"]


def load_readings(path: str | Path) -> pd.DataFrame:
    """온도 시계열 CSV를 DataFrame으로 읽는다.

    반환 컬럼: timestamp(datetime), zone(str), temp_c(float).
    필수 컬럼 누락 시 ValueError.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"입력 CSV를 찾을 수 없음: {path}")

    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["zone"] = df["zone"].astype(str)
    df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")

    return df[REQUIRED_COLUMNS]


def clean_readings(df: pd.DataFrame) -> pd.DataFrame:
    """정렬·중복 제거·결측 처리.

    - (zone, timestamp) 기준 정렬
    - 동일 키 중복 제거
    - temp_c 결측 행 제거(또는 보간) 후 반환
    """
    df = df.copy()

    # timestamp 자체가 결측인 행은 제거
    df = df.dropna(subset=["timestamp"])

    # (zone, timestamp) 기준 정렬
    df = df.sort_values(["zone", "timestamp"], kind="mergesort")

    # 동일 (zone, timestamp) 키 중복 제거 — 마지막 값 유지
    df = df.drop_duplicates(subset=["zone", "timestamp"], keep="last")

    # temp_c 결측 처리: 식품 안전 관점에서 단순 제거(보간으로 이상치를 숨기지 않음)
    df = df.dropna(subset=["temp_c"])

    return df.reset_index(drop=True)
