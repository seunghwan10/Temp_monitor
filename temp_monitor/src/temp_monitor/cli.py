"""파이프라인 엔트리포인트: 로드 → 탐지 → 리포트."""
from __future__ import annotations
import argparse
from pathlib import Path

from .config import load_config
from .loader import load_readings, clean_readings
from .detector import detect_anomalies
from .reporter import save_alarms, plot_zone_trends, summarize


def run(input_csv: str, config_path: str, out_dir: str) -> None:
    """전체 파이프라인 실행."""
    config = load_config(config_path)
    df = clean_readings(load_readings(input_csv))
    alarms = detect_anomalies(df, config)

    alarms_path = save_alarms(alarms, out_dir)
    chart_path = plot_zone_trends(df, alarms, out_dir)
    summary = summarize(alarms)

    print(f"입력 행 수      : {len(df)}")
    print(f"총 알람 건수    : {len(alarms)}")
    print(f"알람표 저장     : {alarms_path}")
    print(f"추이 차트 저장  : {chart_path}")
    print("\n[구역별 요약]")
    print(summary.to_string(index=False) if not summary.empty else "  (알람 없음)")


def main() -> None:
    p = argparse.ArgumentParser(description="냉장·냉동창고 온도 이상 알람")
    p.add_argument("--input", required=True, help="온도 시계열 CSV 경로")
    p.add_argument("--config", required=True, help="구역 설정 YAML 경로")
    p.add_argument("--out", default="output/", help="출력 디렉터리")
    args = p.parse_args()
    run(args.input, args.config, args.out)


if __name__ == "__main__":
    main()
