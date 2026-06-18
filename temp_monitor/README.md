# 냉장·냉동창고 온도 모니터링 & 이상 알람 (프로토타입 뼈대)

대상 도메인: (주)살롬 동결건조 식품공장 — 냉장/냉동창고·급냉실·건조실 IoT 온도 모니터링


## 폴더 구조

temp_monitor/
├── README.md
├── requirements.txt
├── config/
│   └── zones.yaml            # 구역별 정상범위·임계 설정 (예시)
├── data/
│   └── sample_temps.csv      # 입력 샘플 (timestamp, zone, temp_c)
├── output/                   # 알람표 CSV·차트 PNG 출력 위치
└── src/temp_monitor/
    ├── __init__.py
    ├── config.py             # 설정 로드/검증
    ├── loader.py             # ① CSV 로드·검증
    ├── detector.py           # ② 임계 이탈 + 이동평균 급변 탐지
    ├── reporter.py           # ③ 알람표 저장 + 구역별 추이 차트
    └── cli.py                # 파이프라인 엔트리포인트
```

## 실행 (구현 완료 후)
```bash
pip install -r requirements.txt
python -m temp_monitor.cli --input data/sample_temps.csv --config config/zones.yaml --out output/
```
