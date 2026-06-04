# 프로젝트 컨텍스트

## 회사
- 회사명: 금강공업
- 사업 영역: 건축·산업설비 제조

## ERP Track 2 팀 구성 (AI가 알아야 할 존칭·역할)

### 이노베이터 그룹
- **PM**: 홍세민 — 이노베이터 총괄 매니저 · 공용 계정·인프라 운영 책임
- **이노베이터 7기**: 금강 사내 일반 직원 60명 (개인 자격 참여)
  - 사용 도구: 안티그래비티 (Free 또는 Pro 자율)

### 바이브코더 (선정 PL 4명)
이노베이터 중 선정된 프로젝트 리더. 신규 서비스 직접 빌드 책임.
- **홍세민 PM** — 이노베이터 PM 겸직
- **오흥철 PL** — CRM PoC 주축
- **장한나 PL** — 프로젝트 진행
- **김은지 PL** — 프로젝트 진행 (본 프로젝트 담당자)
- **염용래 PL** — 프로젝트 진행
- 사용 도구: 클로드 코드 + 안티그래비티 자유 활용
- 담당 환경: Vercel + Supabase (공용 계정)

### SAC (System Automation Center) ERP Track 2
기존 ERP 운영 + 대외 API 제공 책임. 정규 개발자 그룹.
- **총괄**: 이용철 부장 — SAC 부산 부장 · ERP Track 2 총괄
- **실무자 4명** (Track 2 직접 담당):
  - 이영호 차장 — 서버 · API 주담당
  - 이정혁 과장 — 보안 · 네트워크
  - 성준규 계장 — 실행 · 마이그레이션
  - 최준영 계장 — 부산 · 실행
- 참석 인원: SAC 전체 8명 (실무자 4명 외 4명은 참관자)
- 사용 도구: Visual Studio 2024 + 클로드 코드/코덱스 확장
- 담당 환경: 기존 ERP MSSQL · 구서버 Playground

### 협업 구조 (AI가 이해해야 할 관계)
```
이노베이터 60명 (개인 자격 참여)
         ↑ PM 관리
홍세민 PM → 바이브코더 4명 조율 (본인 포함)
         ↓ API 계약
SAC 5명 (총괄 이용철 + 담당 4명)
```
- 바이브코더 = 신규 서비스 구축 (Vercel/Supabase 영역)
- SAC = 기존 ERP 운영 + API 제공 (MSSQL/사내 서버 영역)
- 두 영역을 이어주는 것 = API 계약 (필요 서비스만 국한)

## 프로젝트
- **프로젝트명**: k_pro (K-Progress)
- **설명**: 건설사업부 프로젝트 실행관리 및 성과 관제탑 시스템
- **핵심 목적**: 재무·원가·매출·수익성 관제탑 — Python + Streamlit + SQLite
- **담당 PL**: 김은지

## 기술 스택 (K-Progress)
- **언어**: Python / **프레임워크**: Streamlit / **DB**: SQLite
- **아키텍처**: SPA (사이드바 내비 + 메인 영역 교체), Backend·Frontend 느슨한 결합

## ERP 환경
- DB 엔진: MSSQL 2022 (Always On AG) — 기존 ERP
- K-Progress DB: SQLite (ERP 연동 데이터 시뮬레이션)
- 기존 ERP DB 직접 수정 금지 — SAC API 경유만

## 도메인 용어 (필수 숙지)
- **수불**: 입출고 관리 (입고·출고·재고 흐름)
- **전표**: 회계 거래 기록 단위
- **KKV**: [회사 내부 정의 — 채워주세요]
- **DLS**: 모바일 ERP 시스템
- **언양**: 언양 공장 (수불 별도 운용)
- **POP**: 생산 정보 시스템 (ORACLE DB 기반)

## DB 패턴 (금강 ERP 특화)
- **Detail 14개 테이블 구조**: 메인 + 14개 상세 테이블 패턴
- **KV 테이블**: chatbot_details 등 키-값 형태
- **배열·JSON 정책**:
  - MSSQL: 배열·JSON 미사용 (1NF 준수)
  - Supabase: 자유롭게 사용 가능
- **Stored Procedure**: 언양 수불 외에는 거의 없음

## 코딩 스타일
- K-Progress: Python + Streamlit + SQLite
- 기존 ERP: C# + .NET Framework + WCF
- 주석: 한국어 우선
- 명명 규칙: snake_case (Python) · PascalCase (C#)
- 비즈니스 용어는 한글·영문 병기 (예: `execution_budget # 실행예산`)

## 금강 API 연결
- 운영 URL: KUMKANG_API_URL 환경변수로만 사용 (코드에 직접 하드코딩 금지)
- 인증: KUMKANG_API_KEY (서버 측에서만 사용, 클라이언트 노출 금지)
- 호출 경로: 클라이언트 → Vercel API Routes → 금강 API
- 접근 원칙: 필요한 서비스 API만 호출 (전체 래핑 X)

## 참고 문서
- `docs/ERP_용어집.md` — 도메인 용어 정의
- `docs/DB_스키마.md` — Detail 14개·KV 테이블 패턴 상세
- `docs/비즈니스_규칙.md` — "전표 마감 후 수정 금지" 등 규칙
- `examples/` — 모범 코드 샘플

## AI 작업 원칙
- 매 작업 전 본 파일 + 관련 docs/ 읽기
- 도메인 용어는 한글 + 영문 병기로 표현
- 기존 ERP DB 직접 수정 금지 — API 경유만
- 신규 서비스는 Supabase 자유, ERP 데이터는 SAC API로만 조회
- 트랜잭션 무결성 영역(회계·수불·전표) → MSSQL · 그 외 → Supabase

## Git / 버전 관리
- **원격 저장소**: `https://github.com/aptimerp/k-progress.git` (branch: `master`)
- **커밋 시점**: 사용자가 명시적으로 요청할 때만 커밋·푸시
- **커밋 제외 파일** (절대 커밋 금지):
  - `.env.local` — API 키·환경변수
  - `mcp.json` — Notion 토큰
  - `*.db`, `*.sqlite` — 로컬 DB
  - `.claude/settings.local.json` — 개인 설정
- **커밋 메시지 형식**: `feat/fix/docs/chore: 한국어 요약` + Co-Authored-By 트레일러
- **노션 마무리 업로드**: `mcp__notion-dueul__API-post-page` 로 자식 페이지 생성 (토글 형식)

## 워크플로우
- /시작 → /계획 → /실행 → /검증 → /마무리 5단계 준수
- 각 단계 산출물은 .planning/ 폴더에 보관
- 페이즈 종료 시 /마무리 명령으로 자동 정리
