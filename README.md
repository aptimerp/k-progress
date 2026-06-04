# K-Progress — 금강공업 건설사업부 성과 관제탑

## 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 샘플 데이터 투입
```bash
python database/seed_data.py
```

### 3. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

## 프로젝트 구조
- `app.py` — Streamlit 진입점 (SPA 라우터)
- `database/` — SQLite 스키마, DB 헬퍼, 샘플 데이터
- `core/engine.py` — 진행률 역산 엔진 (핵심 비즈니스 로직)
- `pages/` — 각 탭 UI 컴포넌트
