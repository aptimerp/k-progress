# PLAN.md — Phase 1: K-Progress 초기 구현

**Phase**: 01 — K-Progress 초기 구현  
**담당 PL**: 김은지  
**기준 문서**: REQUIREMENTS.md, ROADMAP.md  
**작성일**: 2026-05-22  

---

## Phase 1 목표

"지금 얼마를 벌고 있고, 앞으로 얼마를 벌 것인가?"에 답하는 관제탑의 첫 번째 작동 버전.  
SQLite 기반 ERP 시뮬레이션 데이터 위에 Streamlit SPA를 올리고, 진행률 역산 엔진으로 시스템 산출 매출액을 계산하여 탭1(종합 성과 관제탑)에 시각화한다.

---

## 성공 기준 (REQUIREMENTS.md 기반)

- [ ] 진행률 기반 매출액 역산 엔진이 공식대로 정확하게 동작한다
- [ ] 3탭 SPA 구조(사이드바 내비 + 메인 영역)가 정상 동작한다
- [ ] SQLite DB 스키마 완성 + 샘플 데이터 5개 프로젝트 입력 가능
- [ ] ERP 매출액 vs 시스템 산출 매출액 vs 수금액 비교 차트가 탭1에 구현된다

---

## 파일 구조 (산출물 전체)

```
D:\AX_TEAM\K_pro\
├── app.py                        # Streamlit 진입점 (SPA 라우터)
├── database/
│   ├── schema.sql                # SQLite DDL (5개 테이블)
│   ├── db.py                     # DB 연결·쿼리 헬퍼
│   └── seed_data.py              # 샘플 데이터 투입 스크립트
├── core/
│   └── engine.py                 # 진행률 역산 엔진 (핵심 비즈니스 로직)
└── pages/
    └── tab1_dashboard.py         # 탭1: 종합 성과 관제탑
```

---

## 의존성 그래프

```
T1 (스키마) ──→ T2 (샘플 데이터)
                     │
                     ▼
T3 (DB 헬퍼) ──────────→ T4 (역산 엔진) ──→ T5 (탭1 대시보드)
                                                    │
                                                    ▼
                                            T6 (SPA 뼈대 + 통합)
```

- T2는 T1 완료 후 실행 (스키마가 있어야 데이터 투입 가능)
- T4는 T3 완료 후 실행 (DB 헬퍼를 역산 엔진이 호출)
- T5는 T4 완료 후 실행 (역산 엔진 결과를 대시보드가 렌더링)
- T6은 T5 완료 후 실행 (탭1 완성 후 SPA로 조립)

**병렬 실행 가능**: T1+T3은 동시 착수 가능 (파일 충돌 없음)

---

## 태스크 상세

---

### T1 — SQLite DB 스키마 설계 및 생성

**산출물**: `database/schema.sql`

**구현 상세**:

5개 테이블을 아래 DDL 사양으로 생성한다. 모든 금액 필드는 REAL 타입, 날짜는 TEXT(ISO 8601), 상태는 TEXT CHECK 제약.

```
테이블 1: projects (프로젝트 기본 정보)
  - project_code        TEXT PRIMARY KEY          -- 프로젝트 코드 (예: KK-2024-001)
  - project_name        TEXT NOT NULL             -- 프로젝트명
  - client              TEXT NOT NULL             -- 발주처
  - contract_start      TEXT NOT NULL             -- 계약 시작일 (YYYY-MM-DD)
  - contract_end        TEXT NOT NULL             -- 계약 종료일 (YYYY-MM-DD)
  - initial_contract_amount  REAL NOT NULL        -- 최초 계약금액 (원)
  - revised_contract_amount  REAL NOT NULL        -- 변경 계약금액 (원)
  - execution_budget    REAL NOT NULL             -- 총 실행예산 / 목표 원가 (원)
  - target_profit_rate  REAL NOT NULL DEFAULT 0.08 -- 목표 수익률 (예: 0.08 = 8%)
  - status              TEXT CHECK(status IN ('진행중','준공','보류')) DEFAULT '진행중'
  - created_at          TEXT DEFAULT (datetime('now','localtime'))

테이블 2: direct_costs (직접비 — ERP 시뮬레이션)
  - id                  INTEGER PRIMARY KEY AUTOINCREMENT
  - project_code        TEXT NOT NULL REFERENCES projects(project_code)
  - cost_type           TEXT NOT NULL             -- 비용 유형: '인건비'|'자재비'|'외주비'|'기타'
  - amount              REAL NOT NULL             -- 금액 (원)
  - recorded_at         TEXT NOT NULL             -- 계상 일자 (YYYY-MM-DD)
  - description         TEXT                      -- 비고

테이블 3: indirect_costs (간접비 — ERP 시뮬레이션)
  - id                  INTEGER PRIMARY KEY AUTOINCREMENT
  - project_code        TEXT NOT NULL REFERENCES projects(project_code)
  - cost_type           TEXT NOT NULL             -- 비용 유형: '현장관리비'|'경비'|'기타'
  - amount              REAL NOT NULL             -- 금액 (원)
  - recorded_at         TEXT NOT NULL             -- 계상 일자 (YYYY-MM-DD)
  - description         TEXT                      -- 비고

테이블 4: collections (수금액 — 차수별 누계)
  - id                  INTEGER PRIMARY KEY AUTOINCREMENT
  - project_code        TEXT NOT NULL REFERENCES projects(project_code)
  - collection_round    INTEGER NOT NULL          -- 차수 (1, 2, 3...)
  - amount              REAL NOT NULL             -- 해당 차수 수금액 (원)
  - collected_at        TEXT NOT NULL             -- 수금일자 (YYYY-MM-DD)
  - description         TEXT                      -- 비고

테이블 5: erp_revenue (ERP 매출액 — 비교용)
  - id                  INTEGER PRIMARY KEY AUTOINCREMENT
  - project_code        TEXT NOT NULL REFERENCES projects(project_code)
  - amount              REAL NOT NULL             -- ERP 인식 매출액 (원)
  - period_start        TEXT NOT NULL             -- 기간 시작 (YYYY-MM-DD)
  - period_end          TEXT NOT NULL             -- 기간 종료 (YYYY-MM-DD)
  - description         TEXT                      -- 비고
```

각 테이블 생성 후 `CREATE INDEX`를 project_code에 추가한다 (FK 조회 성능).

**검증 기준**:
```bash
python -c "import sqlite3; conn=sqlite3.connect('kprogress.db'); cur=conn.cursor(); cur.execute(\"SELECT name FROM sqlite_master WHERE type='table'\"); print(cur.fetchall())"
```
출력 결과에 `projects, direct_costs, indirect_costs, collections, erp_revenue` 5개 테이블이 모두 포함되어야 한다.

**완료 기준**: schema.sql 실행 시 에러 없이 5개 테이블 생성. DB 파일(kprogress.db)이 프로젝트 루트에 생성됨.

---

### T2 — 샘플 데이터 투입 스크립트 작성

**의존성**: T1 완료 후  
**산출물**: `database/seed_data.py`

**구현 상세**:

건설 현장 특성이 살아있는 현실적인 샘플 5개 프로젝트를 삽입한다. 각 프로젝트는 서로 다른 상태(진행중/준공/보류)와 수익률 편차를 가져야 경고 리스트 테스트가 가능하다.

샘플 데이터 사양:

```
프로젝트 A (KK-2024-001): 진행중, 목표 수익률 달성 (정상)
  - 프로젝트명: 부산 해운대 물류센터 신축공사
  - 발주처: (주)부산물류
  - 계약금액: 4,500,000,000원 (변경 없음)
  - 실행예산: 3,800,000,000원
  - 직접비 합계: 약 2,200,000,000원 (인건비+자재비+외주비)
  - 간접비 합계: 약 380,000,000원
  - 수금 2차수, ERP 매출액 입력

프로젝트 B (KK-2024-002): 진행중, 목표 수익률 미달 (경고 대상)
  - 프로젝트명: 울산 언양 공장 증설공사
  - 발주처: 금강공업(주) 내부
  - 계약금액: 1,200,000,000원
  - 실행예산: 1,000,000,000원
  - 직접비+간접비가 실행예산을 초과하여 진행률 > 100% → 수익률 음수

프로젝트 C (KK-2023-015): 준공, 정상 완료
  - 프로젝트명: 경남 창원 산업단지 전기설비공사
  - 수금 완료, ERP 매출액 = 계약금액

프로젝트 D (KK-2024-003): 진행중, 초기 단계 (진행률 낮음)
  - 프로젝트명: 대구 북구 공동주택 기계설비공사
  - 직접비+간접비가 실행예산의 15% 수준 (초기)

프로젝트 E (KK-2023-012): 준공, 수익률 우수
  - 프로젝트명: 부산 사상 산업단지 소방공사
  - 목표 수익률 12% 이상 달성
```

스크립트 구조:
- `if __name__ == "__main__":` 블록에서 실행
- 기존 데이터 삭제 후 재삽입하는 `--reset` 옵션 지원
- 삽입 완료 후 각 테이블 row count를 출력하여 확인 가능하게 한다
- 금액은 모두 정수(원 단위)로 표현하되 REAL 컬럼에 저장

**검증 기준**:
```bash
python database/seed_data.py
```
실행 후 아래 출력이 나와야 한다:
```
[seed] projects: 5개 삽입 완료
[seed] direct_costs: N개 삽입 완료
[seed] indirect_costs: N개 삽입 완료
[seed] collections: N개 삽입 완료
[seed] erp_revenue: N개 삽입 완료
```

**완료 기준**: seed_data.py 실행 시 에러 없이 완료. 5개 프로젝트 중 최소 1개는 목표 수익률 미달 상태(경고 리스트 테스트 목적).

---

### T3 — DB 연결·쿼리 헬퍼 모듈 작성

**산출물**: `database/db.py`

**구현 상세**:

UI 레이어가 SQL을 직접 쓰지 않도록 데이터 액세스 계층(DAL)을 캡슐화한다. 모든 반환값은 `pd.DataFrame` 또는 `dict`로 통일한다.

아래 함수들을 구현한다:

```
get_connection() -> sqlite3.Connection
  - DB_PATH 상수를 통해 kprogress.db에 연결
  - row_factory = sqlite3.Row 설정 (컬럼명 접근 가능)

get_all_projects() -> pd.DataFrame
  - projects 테이블 전체 반환
  - 컬럼: project_code, project_name, client, status, target_profit_rate 등

get_project_summary(project_code: str) -> dict
  - 단일 프로젝트 기본 정보 반환

get_direct_costs_total(project_code: str) -> float
  - 직접비 합계 반환 (SUM)

get_indirect_costs_total(project_code: str) -> float
  - 간접비 합계 반환 (SUM)

get_collections_total(project_code: str) -> float
  - 수금액 누계 반환 (SUM)

get_erp_revenue_total(project_code: str) -> float
  - ERP 매출액 합계 반환 (SUM)

get_dashboard_data() -> pd.DataFrame
  - 탭1 대시보드용 집계 뷰 (전체 프로젝트)
  - 컬럼: project_code, project_name, client, status,
           revised_contract_amount, execution_budget, target_profit_rate,
           total_direct_cost,   # direct_costs SUM
           total_indirect_cost, # indirect_costs SUM
           total_collection,    # collections SUM
           total_erp_revenue    # erp_revenue SUM
  - LEFT JOIN으로 데이터 없는 프로젝트도 포함 (금액은 0.0)
```

구현 원칙:
- 모든 함수는 연결 열기-쿼리-닫기를 함수 내에서 처리 (컨텍스트 매니저 with 사용)
- 예외 발생 시 `raise` 후 호출자가 처리 (조용한 실패 금지)
- 주석: 한국어, 비즈니스 용어 병기 (예: `# 수금액(collections) 누계 합산`)

**검증 기준**:
```bash
python -c "from database.db import get_dashboard_data; df=get_dashboard_data(); print(df.columns.tolist()); print(len(df))"
```
컬럼 목록이 위 사양과 일치하고 row 수가 5이어야 한다.

**완료 기준**: db.py 임포트 시 에러 없음. get_dashboard_data() 호출 시 5행 DataFrame 반환.

---

### T4 — 진행률 역산 엔진 구현

**의존성**: T3 완료 후  
**산출물**: `core/engine.py`

**구현 상세**:

REQUIREMENTS.md의 핵심 비즈니스 공식을 순수 함수(pure function)로 구현한다. UI에 종속되지 않는 계산 레이어.

```
공식 (비즈니스 로직 — 변경 금지 원칙):
  ① 전체 예상 실행원가 = 직접비(ERP) + 간접비(ERP)
  ② 진행률(%) = 전체 예상 실행원가 / 총 실행예산
  ③ 시스템 산출 매출액 = 총 계약금액 × 진행률(%)
  ④ 시스템 산출 수익 = 시스템 산출 매출액 - 전체 예상 실행원가
  ⑤ 시스템 산출 수익률(%) = 시스템 산출 수익 / 시스템 산출 매출액
  ⑥ 경고 여부 = 시스템 산출 수익률(%) < 목표 수익률(%)
```

구현할 함수:

```
calculate_project_metrics(
    project_code: str,
    revised_contract_amount: float,  # 변경 계약금액
    execution_budget: float,         # 총 실행예산
    target_profit_rate: float,       # 목표 수익률 (예: 0.08)
    total_direct_cost: float,        # 직접비 합계
    total_indirect_cost: float,      # 간접비 합계
    total_collection: float,         # 수금액 누계
    total_erp_revenue: float         # ERP 매출액
) -> dict:
  반환 dict 키:
    - project_code: str
    - expected_execution_cost: float  # 전체 예상 실행원가
    - progress_rate: float            # 진행률 (0.0~1.0, 단 초과 가능)
    - system_revenue: float           # 시스템 산출 매출액
    - system_profit: float            # 시스템 산출 수익
    - system_profit_rate: float       # 시스템 산출 수익률
    - erp_revenue_diff: float         # ERP 매출액 - 시스템 산출 매출액 (괴리)
    - collection_diff: float          # 수금액 - 시스템 산출 매출액 (미수금)
    - is_warning: bool                # 경고 여부

calculate_all_projects(df: pd.DataFrame) -> pd.DataFrame
  - get_dashboard_data() 결과 DataFrame을 입력으로 받아
  - 각 행에 calculate_project_metrics 적용
  - 위 dict 키들을 새 컬럼으로 추가한 DataFrame 반환
  - 이 함수가 탭1 대시보드의 데이터 진입점
```

엣지 케이스 처리:
- execution_budget == 0 → progress_rate = 0.0 (ZeroDivisionError 방지)
- system_revenue == 0 → system_profit_rate = 0.0
- progress_rate > 1.0 허용 (예산 초과 현장은 그대로 표시)

**검증 기준**:
```bash
python -c "
from core.engine import calculate_project_metrics
result = calculate_project_metrics(
    'TEST', 4500000000, 3800000000, 0.08,
    2200000000, 380000000, 1800000000, 2100000000
)
print(f'진행률: {result[\"progress_rate\"]:.2%}')
print(f'시스템 매출액: {result[\"system_revenue\"]:,.0f}원')
print(f'경고: {result[\"is_warning\"]}')
assert abs(result['progress_rate'] - (2200000000+380000000)/3800000000) < 0.001
print('공식 검증 PASS')
"
```

**완료 기준**: assert 통과. 목표 수익률 미달 프로젝트에서 is_warning=True 반환 확인.

---

### T5 — 탭1: 종합 성과 관제탑 UI 구현

**의존성**: T4 완료 후  
**산출물**: `pages/tab1_dashboard.py`

**구현 상세**:

`render_tab1()` 함수 하나를 export한다. app.py에서 호출하는 방식으로 느슨하게 결합.

UI 구성 (위에서 아래 순서):

**섹션 1: 요약 카드 (st.metric 4개, 가로 배치)**
```
카드1: 전체 프로젝트 수 (projects 테이블 COUNT)
카드2: 진행중 현장 수 (status='진행중')
카드3: 준공 완료 현장 수 (status='준공')
카드4: 경고 현장 수 (is_warning=True인 프로젝트 수)
      → delta 색상: 경고 수가 0이면 녹색, 1 이상이면 빨간색
```

**섹션 2: 비교 차트 (st.bar_chart 또는 plotly)**
```
X축: project_name (프로젝트명 — 너무 길면 project_code 병기)
Y축: 금액 (원)
시리즈 3개 (범례):
  - 시스템 산출 매출액 (system_revenue) — 파란색
  - ERP 매출액 (total_erp_revenue) — 주황색
  - 수금액 (total_collection) — 녹색
차트 제목: "매출액 비교: 시스템 역산 vs ERP vs 수금"
금액 단위: 억원으로 환산 표시 (1억 = 100,000,000)
```

plotly 사용 시 `import plotly.express as px` + `st.plotly_chart(fig, use_container_width=True)`  
plotly 미설치 시 `st.bar_chart(df[['project_name','system_revenue','total_erp_revenue','total_collection']].set_index('project_name'))` 폴백 사용.

**섹션 3: 경고 리스트 (st.dataframe 또는 st.table)**
```
조건: is_warning=True인 프로젝트만 필터
컬럼 표시: 프로젝트명, 발주처, 진행률(%), 시스템 수익률(%), 목표 수익률(%), 괴리액(억원)
헤더 색: 빨간색 계열 강조 (st.error 또는 st.dataframe styler 활용)
경고 없을 시: st.success("현재 수익률 미달 현장이 없습니다.")
```

**섹션 4: 전체 프로젝트 현황 테이블**
```
columns: project_code, project_name, client, status,
         revised_contract_amount(억원), progress_rate(%), system_revenue(억원),
         total_erp_revenue(억원), system_profit_rate(%)
st.dataframe 사용, use_container_width=True
```

데이터 호출 순서 (render_tab1 내부):
```python
raw_df = get_dashboard_data()          # DB에서 집계 뷰 로드
metrics_df = calculate_all_projects(raw_df)  # 역산 엔진 적용
# 이후 metrics_df를 각 섹션에서 사용
```

**검증 기준**: `streamlit run app.py` 실행 후 탭1 클릭 시 요약 카드 4개, 비교 차트, 경고 리스트, 전체 테이블이 에러 없이 렌더링됨.

**완료 기준**: 브라우저에서 탭1 접속 시 5개 프로젝트 데이터가 정상 표시. 목표 수익률 미달 현장(프로젝트 B)이 경고 리스트에 출현.

---

### T6 — Streamlit SPA 뼈대 조립 및 통합

**의존성**: T5 완료 후  
**산출물**: `app.py`

**구현 상세**:

REQUIREMENTS.md의 SPA 구조: 왼쪽 사이드바 내비 + 우측 메인 영역 교체.

```python
# app.py 구조 (의사 코드 — 실제 코드로 구현)

st.set_page_config(
    page_title="K-Progress | 금강공업 프로젝트 관제탑",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바: 내비게이션
with st.sidebar:
    st.image 또는 st.title("K-Progress")
    st.caption("건설사업부 성과 관제탑")
    st.divider()
    selected_tab = st.radio(
        "메뉴",
        options=["탭1: 종합 성과 관제탑", "탭2: 프로젝트 상세 (준비중)", "탭3: 지식 자산 (준비중)"],
        key="nav"
    )

# 메인 영역: 탭 라우팅
if selected_tab == "탭1: 종합 성과 관제탑":
    from pages.tab1_dashboard import render_tab1
    render_tab1()
elif selected_tab == "탭2: 프로젝트 상세 (준비중)":
    st.info("Phase 2에서 구현 예정입니다.")
elif selected_tab == "탭3: 지식 자산 (준비중)":
    st.info("Phase 2에서 구현 예정입니다.")
```

추가 구현 사항:
- `requirements.txt` 생성: `streamlit`, `pandas`, `plotly` (버전 고정 권장)
- `database/` 및 `core/` 폴더에 `__init__.py` 빈 파일 생성 (Python 패키지화)
- `.env.local` 확인: KUMKANG_API_URL, KUMKANG_API_KEY 자리가 있는지 확인 (Phase 1에서는 미사용이나 구조 확보)
- app.py 최상단에 sys.path 조정 없이 상대 임포트가 동작하도록 `PYTHONPATH` 또는 실행 방법 README에 기재

**검증 기준**:
```bash
cd D:\AX_TEAM\K_pro
streamlit run app.py
```
- 브라우저 자동 열림 (localhost:8501)
- 사이드바에 3개 메뉴 항목 표시
- 탭1 클릭 시 T5 대시보드 렌더링
- 탭2, 탭3 클릭 시 "준비중" 안내 메시지 표시
- 콘솔 에러 없음

**완료 기준**: streamlit run app.py 정상 실행. 3탭 SPA 내비게이션 동작. 탭1 데이터 정상 표시.

---

## 실행 순서 요약

| 단계 | 태스크 | 병렬 가능 | 예상 컨텍스트 |
|------|--------|----------|--------------|
| Wave 1 | T1 + T3 | 동시 가능 | 각 ~15% |
| Wave 2 | T2 (T1 완료 후) | 단독 | ~10% |
| Wave 3 | T4 (T3 완료 후) | 단독 | ~20% |
| Wave 4 | T5 (T4 완료 후) | 단독 | ~25% |
| Wave 5 | T6 (T5 완료 후) | 단독 | ~10% |

---

## 리스크 및 대응

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| plotly 미설치 환경 | 중간 | T5에서 st.bar_chart 폴백 구현 필수 |
| 금액 정밀도 손실 (REAL 타입) | 낮음 | 단순 집계 수준이므로 Phase 1은 허용. Phase 3에서 DECIMAL 검토 |
| progress_rate > 1.0 (예산 초과) | 높음 (샘플 B) | engine.py에서 허용, UI에서 빨간색 강조 |
| sys.path 이슈 (패키지 임포트) | 중간 | `__init__.py` 생성 + streamlit run 루트 실행 지침 명시 |
| 샘플 데이터 재실행 시 중복 | 낮음 | seed_data.py에 DELETE 후 INSERT 패턴 적용 |

---

## 검수 체크리스트 (Phase 1 종료 시)

```
[ ] python -c "import sqlite3; ..." — 5개 테이블 확인
[ ] python database/seed_data.py — 에러 없이 완료
[ ] python -c "from database.db import get_dashboard_data; ..." — 5행 DataFrame
[ ] python -c "from core.engine import calculate_project_metrics; ... assert ..." — 공식 검증 PASS
[ ] streamlit run app.py — 브라우저 정상 열림
[ ] 탭1: 요약 카드 4개 표시 확인
[ ] 탭1: 비교 차트 (3개 시리즈) 표시 확인
[ ] 탭1: 프로젝트 B (언양 증설공사) 경고 리스트에 출현 확인
[ ] 탭2, 탭3: "준비중" 메시지 표시 확인
```

---

## Phase 2 예고 (참고용 — 본 계획 범위 외)

- 탭2: 첨부파일 보관함 + 설계변경 이력 타임라인 + Raw 데이터 그리드
- 탭3: 준공 현장 검색 + Lessons Learned 카드 + 유사 현장 매칭

---

> 이 PLAN.md는 `/실행` 명령 시 Claude가 T1부터 순서대로 참조합니다.  
> 태스크 완료 후 STATE.md의 Phase 1 이력을 업데이트하고, 전체 완료 시 `/마무리` 명령을 실행하세요.
