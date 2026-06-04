# 프로젝트 학습 기록

## Phase 0 — 초기 세팅 (2026-05-20)

### 핵심 결정사항
- 3개 컨텍스트 파일 전략: CLAUDE.md · GEMINI.md · AGENTS.md 동일 내용으로 생성 → 어떤 AI 도구에서든 동일 컨텍스트
- 슬래시 명령어는 GSD 래퍼로 설계 → GSD 설치 여부와 무관하게 폴백 동작
- 노션 MCP: 공용 토큰 방식 (OAuth 아님) — 두을 AI 워크스페이스 전용

### 재사용 가능 패턴
- `.claude/commands/` 파일명 = 슬래시 명령어명 (한글 파일명 OK)
- `session-start.js` 훅: STATE.md 마지막 100줄 + ROADMAP.md 진행 중 페이즈만 출력
- `.env.local` + `.gitignore` 조합으로 API 키 보안 관리

### 환경 정보
- Notion MCP: 두을 AI 워크스페이스, 공용 부모 페이지 `27a09b4dcd5780cb8b75c96e2a290f08`
- 개인 할당 페이지: `35609b4dcd5781869aefe475807b37d9`
- GSD 설치 위치: `C:\Users\kuser\.claude\get-shit-done\`

### 미해결 이슈
- GitHub ID 미입력 (.claude/PROFILE.md 수동 채우기 필요)
- SAC API 정보 미수령 (이영호 차장에게 요청)
- Supabase 공용 계정 정보 미수령 (홍세민 PM에게 요청)

---

## 계획 세션 — Phase 1 계획 수립 (2026-05-22)

### 핵심 결정사항
- **기술 스택 확정**: Python + Streamlit + SQLite (Next.js/Supabase 아님)
- **아키텍처**: Backend(engine.py, db.py) ↔ Frontend(tab1_dashboard.py) 느슨한 결합
- **리서치 스킵 결정**: REQUIREMENTS.md가 충분히 상세해서 바로 계획 수립
- **진행률 역산 엔진 공식** (변경 금지 원칙):
  - 진행률 = (직접비 + 간접비) / 실행예산
  - 시스템 매출액 = 계약금액 × 진행률
  - 경고 = 시스템 수익률 < 목표 수익률

### 재사용 가능 패턴
- **샘플 데이터 설계 원칙**: 경고 케이스를 의도적으로 포함 (프로젝트 B — 예산 초과) → UI 경고 리스트 동작 검증용
- **DB 헬퍼 캡슐화**: UI 레이어가 SQL 직접 금지, `get_dashboard_data()` 단일 함수로 집계 뷰 제공
- **순수 함수 엔진**: `calculate_project_metrics()` — UI 종속 없음, assert로 단위 검증 가능
- **Streamlit SPA 패턴**: `st.radio` 사이드바 내비 + 조건 분기 라우팅 (탭2·3은 "준비중" 자리 확보)
- **plotly 폴백**: plotly 있으면 plotly, 없으면 `st.bar_chart` 폴백 처리

### Phase 1 태스크 요약 (실행 시 참조)
| 태스크 | 산출물 | Wave |
|--------|--------|------|
| T1 | database/schema.sql | Wave 1 (T3과 병렬) |
| T2 | database/seed_data.py | Wave 2 (T1 완료 후) |
| T3 | database/db.py | Wave 1 (T1과 병렬) |
| T4 | core/engine.py | Wave 3 (T3 완료 후) |
| T5 | pages/tab1_dashboard.py | Wave 4 (T4 완료 후) |
| T6 | app.py + requirements.txt | Wave 5 (T5 완료 후) |

### 미해결 이슈
- ~~Phase 1 실행 미착수~~ → 완료 ✅
- ~~Streamlit 설치 여부 미확인~~ → `python -m pip install` 로 설치 완료

---

## 실행 세션 — Phase 1 구현 완료 (2026-05-26)

### 핵심 결정사항
- **pip 실행**: Windows 환경에서 `pip` 대신 `python -m pip install` 사용
- **Windows CP949 인코딩**: 한글 출력 시 인코딩 오류 발생 → 기능엔 영향 없음, 무시
- **경고 트리거 핵심 이해**: 진행률 역산 공식에서 수익률 = (계약금액 - 실행예산) / 계약금액은 고정값 → 경고는 원가 초과가 아닌 "실행예산이 목표 수익률을 확보하지 못할 때" 발생
- **샘플 데이터 수정**: Project B execution_budget 10억 → 11.5억으로 조정해야 4.17% < 8% 경고 발생

### 재사용 가능 패턴
- **Streamlit 웹 프리뷰**: `mcp__Claude_Preview__preview_start("k-progress")` + `preview_screenshot` 조합
- **preview_screenshot 타임아웃 대응**: 서버 stop → start 재시작하면 새 브라우저 세션 생성되어 스크린샷 성공
- **`use_container_width` 대체**: Streamlit 최신 버전에서 `width='stretch'` 사용 (`use_container_width=True` deprecated)
- **launch.json 설정**: `.claude/launch.json` → `runtimeExecutable: python`, `runtimeArgs: ["-m", "streamlit", "run", "app.py", ...]`

### 환경 정보
- Python 3.14 (Windows) + Streamlit + pandas + plotly 설치 완료
- kprogress.db: 5개 프로젝트 (KK-2023-012, KK-2023-015, KK-2024-001, KK-2024-002, KK-2024-003)
- 앱 정상 구동 확인: port 8501

### 미해결 이슈 (Phase 2로 이관)
- 탭2 (프로젝트 상세 관리), 탭3 (지식 자산 공유) 미구현
- CLAUDE.md 웹 프리뷰 자동 표시 규칙 추가됨 → 다음 세션부터 자동 적용

---

## UI 프로토타입 세션 (2026-06-02)

### 핵심 결정사항
- **기술 스택 재확정**: SQLite → Supabase (PostgreSQL) 전환 결정 (멀티유저 동시접속 대비)
- **배포 방식**: 사내망 공유 서버 → 팀 전체 URL 단일 접속
- **파일 관리**: Supabase Storage (PDF·Excel 첨부파일)
- **데이터 입력**: Excel 일괄 업로드 우선 (기존 팀 워크플로우 수용)
- **앱 UI 확정 메뉴 구조**:
  - 메인 (종합 대시보드)
  - 프로젝트 등록 → 신규 프로젝트
  - 프로젝트 관리 → 진행 프로젝트 (현장 목록) / 준공 프로젝트 (2026년·2025년 이전)
  - 건설사업부 P&L → 종합 손익 현황 / 건설사업부 손익 / 사업계획대비 달성율

### 재사용 가능 패턴
- **스타일 가이드 디자인 토큰**:
  - Accent: `#2563EB` / Family palette: `#1D4ED8 → #06B6D4`
  - Card: `rounded-2xl` + `shadow 0 4px 12px rgba(0,0,0,.04)`
  - 버튼: `rounded-xl` + `transition all 300ms`
  - Navbar glass: `bg-white/80 backdrop-blur-md`
  - 섹션 라벨: `11px bold tracking 0.2em uppercase blue-600`
- **3단 사이드바 토글 패턴** (`.sb-item` → `.sb-sub` → `.sb-sub-toggle` + `.sb-sub2`):
  - `sbToggle()`: 1단→2단 열기
  - `sbToggle2()`: 2단→3단 열기 (진행/준공 내 현장 목록)
- **프리뷰 서버 구성**: `.claude/launch.json`에 `k-progress-landing` 설정 (port 8502, `python -m http.server`)
- **preview_screenshot 타임아웃 대응**: index.html을 리다이렉트 없이 직접 full 페이지로 사용할 것

### 산출물
- `landing.html` — 스타일 가이드 준수 마케팅/소개 페이지 (32KB)
- `app_ui.html` — 실제 앱 UI 목업 (39KB), 사이드바 3단 토글 + 대시보드
- `.planning/PROJECT.md` — 전략 컨텍스트 (신규 생성)
- `.planning/REQUIREMENTS.md` — REQ-ID 포함 Phase 2~6 요구사항
- `.planning/ROADMAP.md` — Phase 0~6 전체 로드맵

### 미해결 이슈
- Supabase 공용 계정 정보 미수령 (홍세민 PM) → Phase 2 착수 블로커
- SAC API 정보 미수령 (이영호 차장) → Phase 5 착수 블로커
- app_ui.html은 목업 (실제 Streamlit 구현 미착수)
