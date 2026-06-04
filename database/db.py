"""
database/db.py — K-Progress DB 연결 및 쿼리 헬퍼 모듈
건설사업부 프로젝트 실행관리 및 성과 관제탑 (K-Progress)

담당 PL: 김은지
생성일: 2026-05-26
"""

import sqlite3
import pandas as pd
from pathlib import Path

# DB 파일 경로 — 프로젝트 루트의 kprogress.db
DB_PATH = Path(__file__).parent.parent / "kprogress.db"


# =============================================================
# 기본 연결 헬퍼
# =============================================================

def get_connection() -> sqlite3.Connection:
    """SQLite 연결 반환.

    row_factory = sqlite3.Row 설정으로 컬럼명 접근 가능.
    호출자가 with 구문으로 감싸서 사용하거나, 반환된 conn.close()를 직접 호출해야 함.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 컬럼명으로 dict-like 접근 가능
    return conn


# =============================================================
# 프로젝트(projects) 조회
# =============================================================

def get_all_projects() -> pd.DataFrame:
    """projects 테이블 전체 조회.

    반환: 전체 프로젝트 목록 (pd.DataFrame)
    컬럼: project_code, project_name, client, contract_start, contract_end,
           initial_contract_amount, revised_contract_amount, execution_budget,
           target_profit_rate, status, created_at
    """
    sql = "SELECT * FROM projects ORDER BY created_at DESC"
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)


def get_project_summary(project_code: str) -> dict:
    """단일 프로젝트 기본 정보 반환.

    Args:
        project_code: 프로젝트 코드 (예: KK-2024-001)

    반환: 프로젝트 행을 dict로 반환. 존재하지 않으면 빈 dict 반환.
    """
    sql = "SELECT * FROM projects WHERE project_code = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (project_code,))
        row = cursor.fetchone()
        if row is None:
            return {}
        # sqlite3.Row → dict 변환
        return dict(row)


# =============================================================
# 직접비(direct_costs) 집계
# =============================================================

def get_direct_costs_total(project_code: str) -> float:
    """직접비(direct_costs) 합계 반환.

    인건비·자재비·외주비 등 프로젝트 직접 투입 원가의 누계 합계.

    Args:
        project_code: 프로젝트 코드

    반환: 직접비 합계 금액(원). 데이터 없으면 0.0.
    """
    sql = "SELECT COALESCE(SUM(amount), 0.0) FROM direct_costs WHERE project_code = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (project_code,))
        result = cursor.fetchone()
        return float(result[0])


# =============================================================
# 간접비(indirect_costs) 집계
# =============================================================

def get_indirect_costs_total(project_code: str) -> float:
    """간접비(indirect_costs) 합계 반환.

    현장관리비·경비 등 프로젝트 간접 원가의 누계 합계.

    Args:
        project_code: 프로젝트 코드

    반환: 간접비 합계 금액(원). 데이터 없으면 0.0.
    """
    sql = "SELECT COALESCE(SUM(amount), 0.0) FROM indirect_costs WHERE project_code = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (project_code,))
        result = cursor.fetchone()
        return float(result[0])


# =============================================================
# 수금액(collections) 집계
# =============================================================

def get_collections_total(project_code: str) -> float:
    """수금액(collections) 누계 합계 반환.

    프로젝트 차수별 수금 실적(기성·준공금 포함)의 누계 합산.

    Args:
        project_code: 프로젝트 코드

    반환: 수금액 누계 합계(원). 데이터 없으면 0.0.
    """
    sql = "SELECT COALESCE(SUM(amount), 0.0) FROM collections WHERE project_code = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (project_code,))
        result = cursor.fetchone()
        return float(result[0])


# =============================================================
# ERP 매출액(erp_revenue) 집계
# =============================================================

def get_erp_revenue_total(project_code: str) -> float:
    """ERP 매출액(erp_revenue) 합계 반환.

    ERP 시스템에서 인식한 기간별 매출액의 합계 (수금 기반 매출과의 비교 분석용).

    Args:
        project_code: 프로젝트 코드

    반환: ERP 매출액 합계(원). 데이터 없으면 0.0.
    """
    sql = "SELECT COALESCE(SUM(amount), 0.0) FROM erp_revenue WHERE project_code = ?"
    with get_connection() as conn:
        cursor = conn.execute(sql, (project_code,))
        result = cursor.fetchone()
        return float(result[0])


# =============================================================
# 대시보드 집계 뷰 (탭1 — 전체 현황)
# =============================================================

def get_dashboard_data() -> pd.DataFrame:
    """탭1 대시보드용 집계 뷰 — 전체 프로젝트 LEFT JOIN 집계.

    projects 마스터 기준으로 4개 원가·수금 테이블을 LEFT JOIN 집계.
    데이터가 없는 프로젝트도 포함 (금액 컬럼은 0.0 처리).

    반환 컬럼:
        project_code           — 프로젝트 코드
        project_name           — 프로젝트명
        client                 — 발주처
        status                 — 상태 (진행중/준공/보류)
        revised_contract_amount — 변경 계약금액(원)
        execution_budget       — 실행예산 / 목표 원가(원)
        target_profit_rate     — 목표 수익률
        total_direct_cost      — 직접비(direct_costs) SUM
        total_indirect_cost    — 간접비(indirect_costs) SUM
        total_collection       — 수금액(collections) SUM
        total_erp_revenue      — ERP 매출액(erp_revenue) SUM
    """
    sql = """
        SELECT
            p.project_code,
            p.project_name,
            p.client,
            p.status,
            p.revised_contract_amount,
            p.execution_budget,
            p.target_profit_rate,
            COALESCE(SUM(dc.amount), 0.0) AS total_direct_cost,
            COALESCE(SUM(ic.amount), 0.0) AS total_indirect_cost,
            COALESCE(SUM(col.amount), 0.0) AS total_collection,
            COALESCE(SUM(er.amount), 0.0) AS total_erp_revenue
        FROM projects p
        LEFT JOIN direct_costs dc ON p.project_code = dc.project_code
        LEFT JOIN indirect_costs ic ON p.project_code = ic.project_code
        LEFT JOIN collections col ON p.project_code = col.project_code
        LEFT JOIN erp_revenue er ON p.project_code = er.project_code
        GROUP BY p.project_code
        ORDER BY p.created_at DESC
    """
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)
