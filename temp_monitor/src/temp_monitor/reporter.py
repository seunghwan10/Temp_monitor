"""③ 리포트 — 알람표 CSV 저장 + 구역별 온도 추이 차트(PNG)."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

# 한글 폰트 설정(있으면 사용, 없으면 무시)
for _cand in ["NanumGothic", "Malgun Gothic", "AppleGothic", "Noto Sans CJK KR"]:
    if any(_cand in f.name for f in font_manager.fontManager.ttflist):
        rcParams["font.family"] = _cand
        break
rcParams["axes.unicode_minus"] = False


def save_alarms(alarms: pd.DataFrame, out_dir: str | Path) -> Path:
    """알람 표를 out_dir/alarms.csv 로 저장하고 경로 반환."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "alarms.csv"
    alarms.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def plot_zone_trends(
    df: pd.DataFrame, alarms: pd.DataFrame, out_dir: str | Path
) -> Path:
    """구역별 온도 추이 라인차트를 그리고 알람 지점을 표시.

    out_dir/zone_trends.png 로 저장하고 경로 반환.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "zone_trends.png"

    zones = sorted(df["zone"].unique())
    n = len(zones)
    fig, axes = plt.subplots(n, 1, figsize=(11, 2.6 * max(n, 1)), sharex=True)
    if n == 1:
        axes = [axes]

    for ax, zone in zip(axes, zones):
        zdf = df[df["zone"] == zone].sort_values("timestamp")
        ax.plot(zdf["timestamp"], zdf["temp_c"], lw=1.0,
                color="#1f77b4", label="temp_c")

        if not alarms.empty:
            za = alarms[alarms["zone"] == zone]
            for rule, color, marker in [
                ("threshold", "#d62728", "x"),
                ("spike", "#ff7f0e", "o"),
            ]:
                pts = za[za["rule"] == rule]
                if not pts.empty:
                    ax.scatter(pts["timestamp"], pts["temp_c"],
                               s=28, c=color, marker=marker,
                               label=rule, zorder=5)
        ax.set_title(zone)
        ax.set_ylabel("°C")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)

    axes[-1].set_xlabel("timestamp")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def summarize(alarms: pd.DataFrame) -> pd.DataFrame:
    """구역별 이탈 건수·최대 일탈폭 요약 표 반환."""
    if alarms.empty:
        return pd.DataFrame(columns=["zone", "alarm_count", "threshold", "spike"])

    g = alarms.groupby("zone")
    summary = pd.DataFrame({
        "alarm_count": g.size(),
        "threshold": g.apply(
            lambda x: int((x["rule"] == "threshold").sum()), include_groups=False
        ),
        "spike": g.apply(
            lambda x: int((x["rule"] == "spike").sum()), include_groups=False
        ),
        "critical": g.apply(
            lambda x: int((x["severity"] == "critical").sum()), include_groups=False
        ),
    }).reset_index()
    return summary.sort_values("alarm_count", ascending=False).reset_index(drop=True)
