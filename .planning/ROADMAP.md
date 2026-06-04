# K-Progress — 개발 로드맵

## 프로젝트: K-Progress (k_pro) — 건설사업부 성과 관제탑
**기술 스택**: Python + Streamlit + Supabase (PostgreSQL) + SAC API (MSSQL ERP)
**배포 목표**: 사내망 공유 서버 → 팀 전체 URL 단일 접속

---

## Phase 0 — 프로젝트 초기 세팅 ✅
- AI 하네스 세팅 (CLAUDE.md, 슬래시 명령어, 훅, Notion MCP 등)
- 완료일: 2026-05-20

---

## Phase 1 — 종합 성과 관제탑 MVP ✅
- 진행률 역산 엔진 (K-IFRS 15호 기준)
- SQLite 기반 샘플 DB + 5개 프로젝트 데이터
- 탭1: 요약 카드 · 매출액 비교 차트 · 전체 테이블
- 완료일: 2026-05-26
- 핵심 산출물: core/engine.py, database/db.py, pages/tab1_dashboard.py, app.py

---

## UI 프로토타입 ✅ (2026-06-02)
- 스타일 가이드 기반 랜딩 페이지 (landing.html)
- 앱 UI 목업 (app_ui.html) — 상단 GNB + 좌측 사이드바 3단 토글 + 종합 대시보드
- 확정 메뉴: 메인 / 프로젝트 등록 / 프로젝트 관리(진행·준공) / 건설사업부 P&L
- 완료일: 2026-06-02

---

## Phase 2 — Supabase 마이그레이션 🔜
**Goal**: SQLite → Supabase 전환으로 멀티유저 동시 접속 기반 구축
**Success Criteria**:
1. Supabase DB에 모든 테이블 스키마 생성 완료
2. 기존 5개 샘플 프로젝트 데이터 이관 완료
3. 탭1 대시보드가 Supabase 데이터로 Phase 1과 동일하게 동작
4. .env.local에 Supabase 환경변수 설정 완료

**요구사항**: INFRA-01~05
**전제 조건**: Supabase 공용 계정 정보 수령 (홍세민 PM)

---

## Phase 3 — 탭2: 프로젝트 상세 관리 ⏸
**Goal**: 계약 이력·원가 상세·Excel 업로드·파일 보관함 구현
**Success Criteria**:
1. 탭1 프로젝트 클릭 → 탭2 상세 페이지 진입
2. 원계약 + 변경계약 이력 등록 및 타임라인 표시
3. 직접비·간접비 항목별 입력 → 탭1 수익률 자동 갱신
4. Excel 파일 업로드 → 파싱 → DB 저장 정상 동작
5. 계약서 PDF 업로드 → Supabase Storage 저장 · 다운로드

**요구사항**: CONTRACT-01~04, COST-01~03, UPLOAD-01~04, FILE-01~04

---

## Phase 4 — 탭3: 지식 자산 공유 ⏸
**Goal**: 준공 프로젝트 아카이브 및 Lessons Learned 지식 자산화
**Success Criteria**:
1. 준공 프로젝트 목록 조회 및 Lessons Learned 등록
2. 키워드·공종·금액대 기준 검색 동작
3. 준공 데이터 삭제 불가 처리 (영구 보존)

**요구사항**: KNOW-01~05

---

## Phase 5 — SAC API 연동 ⏸
**Goal**: ERP MSSQL 실데이터 자동 연동 (수동 입력 탈피)
**Success Criteria**:
1. KUMKANG_API_KEY 인증으로 SAC API 정상 호출
2. ERP 매출·수금 실적 자동 갱신
3. 시스템 역산 vs ERP 실적 차이 자동 표시

**요구사항**: ERP-01~05
**전제 조건**: SAC API 정보 수령 (이영호 차장)

---

## Phase 6 — 배포 · 운영 ⏸
**Goal**: 사내망 서버 배포 및 팀 전체 접근 환경 구성
**Success Criteria**:
1. 사내망 URL로 팀 전체 접속 가능
2. 앱 재시작 없이 24시간 안정 운영

**요구사항**: OPS-01~04

---

> 각 Phase 시작 시 `/시작`, 완료 시 `/마무리` 명령 사용
> Supabase 계정 수령 즉시 Phase 2 착수 가능
