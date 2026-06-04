-- =============================================================
-- K-Progress (K-Progress) SQLite 데이터베이스 스키마
-- 건설사업부 프로젝트 실행관리 및 성과 관제탑 시스템
-- 생성일: 2026-05-26
-- 담당 PL: 김은지
-- =============================================================

-- -------------------------------------------------------------
-- 테이블 1: projects (프로젝트 기본 정보)
-- 건설 프로젝트의 핵심 계약·예산 정보를 보관하는 마스터 테이블
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    project_code             TEXT    PRIMARY KEY,                          -- 프로젝트 코드 (예: KK-2024-001)
    project_name             TEXT    NOT NULL,                             -- 프로젝트명
    client                   TEXT    NOT NULL,                             -- 발주처
    contract_start           TEXT    NOT NULL,                             -- 계약 시작일 (YYYY-MM-DD)
    contract_end             TEXT    NOT NULL,                             -- 계약 종료일 (YYYY-MM-DD)
    initial_contract_amount  REAL    NOT NULL,                             -- 최초 계약금액 (원)
    revised_contract_amount  REAL    NOT NULL,                             -- 변경 계약금액 (원)
    execution_budget         REAL    NOT NULL,                             -- 총 실행예산 / 목표 원가 (원)
    target_profit_rate       REAL    NOT NULL DEFAULT 0.08,                -- 목표 수익률 (기본 8%)
    status                   TEXT    CHECK(status IN ('진행중','준공','보류')) DEFAULT '진행중', -- 프로젝트 상태
    created_at               TEXT    DEFAULT (datetime('now','localtime')) -- 등록 일시
);

-- -------------------------------------------------------------
-- 테이블 2: direct_costs (직접비 — ERP 시뮬레이션)
-- 인건비·자재비·외주비 등 프로젝트 직접 투입 원가 계상 내역
-- ERP MSSQL 데이터를 SQLite로 시뮬레이션한 테이블
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS direct_costs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,                        -- 내부 식별자
    project_code TEXT    NOT NULL REFERENCES projects(project_code),       -- 프로젝트 코드 (FK)
    cost_type    TEXT    NOT NULL,                                          -- 비용 유형: '인건비'|'자재비'|'외주비'|'기타'
    amount       REAL    NOT NULL,                                          -- 금액 (원)
    recorded_at  TEXT    NOT NULL,                                          -- 계상 일자 (YYYY-MM-DD)
    description  TEXT                                                       -- 비고
);

-- direct_costs 외래키 인덱스
CREATE INDEX IF NOT EXISTS idx_direct_costs_project_code
    ON direct_costs(project_code);

-- -------------------------------------------------------------
-- 테이블 3: indirect_costs (간접비 — ERP 시뮬레이션)
-- 현장관리비·경비 등 프로젝트 간접 원가 계상 내역
-- ERP MSSQL 데이터를 SQLite로 시뮬레이션한 테이블
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS indirect_costs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,                        -- 내부 식별자
    project_code TEXT    NOT NULL REFERENCES projects(project_code),       -- 프로젝트 코드 (FK)
    cost_type    TEXT    NOT NULL,                                          -- 비용 유형: '현장관리비'|'경비'|'기타'
    amount       REAL    NOT NULL,                                          -- 금액 (원)
    recorded_at  TEXT    NOT NULL,                                          -- 계상 일자 (YYYY-MM-DD)
    description  TEXT                                                       -- 비고
);

-- indirect_costs 외래키 인덱스
CREATE INDEX IF NOT EXISTS idx_indirect_costs_project_code
    ON indirect_costs(project_code);

-- -------------------------------------------------------------
-- 테이블 4: collections (수금액 — 차수별 누계)
-- 프로젝트 차수별 수금 실적 내역 (기성·준공금 포함)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS collections (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,                    -- 내부 식별자
    project_code     TEXT    NOT NULL REFERENCES projects(project_code),   -- 프로젝트 코드 (FK)
    collection_round INTEGER NOT NULL,                                      -- 차수 (1, 2, 3...)
    amount           REAL    NOT NULL,                                      -- 해당 차수 수금액 (원)
    collected_at     TEXT    NOT NULL,                                      -- 수금일자 (YYYY-MM-DD)
    description      TEXT                                                   -- 비고
);

-- collections 외래키 인덱스
CREATE INDEX IF NOT EXISTS idx_collections_project_code
    ON collections(project_code);

-- -------------------------------------------------------------
-- 테이블 5: erp_revenue (ERP 매출액 — 비교용)
-- ERP 시스템에서 인식한 기간별 매출액 (수금 기반 매출과의 비교 분석용)
-- ERP MSSQL 데이터를 SQLite로 시뮬레이션한 테이블
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp_revenue (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,                        -- 내부 식별자
    project_code TEXT    NOT NULL REFERENCES projects(project_code),       -- 프로젝트 코드 (FK)
    amount       REAL    NOT NULL,                                          -- ERP 인식 매출액 (원)
    period_start TEXT    NOT NULL,                                          -- 기간 시작 (YYYY-MM-DD)
    period_end   TEXT    NOT NULL,                                          -- 기간 종료 (YYYY-MM-DD)
    description  TEXT                                                       -- 비고
);

-- erp_revenue 외래키 인덱스
CREATE INDEX IF NOT EXISTS idx_erp_revenue_project_code
    ON erp_revenue(project_code);

-- =============================================================
-- 스키마 생성 완료
-- =============================================================
