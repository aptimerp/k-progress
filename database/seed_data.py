#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K-Progress 샘플 데이터 투입 스크립트
실행: python database/seed_data.py [--reset]

5개 프로젝트 데이터를 SQLite DB에 삽입한다.
--reset 옵션 사용 시 기존 데이터를 삭제한 뒤 재삽입한다.
"""

import sqlite3
import argparse
from pathlib import Path

# 경로 설정
DB_PATH = Path(__file__).parent.parent / "kprogress.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


# =============================================================
# 샘플 데이터 정의
# =============================================================

# 프로젝트 기본 정보 (projects 테이블)
PROJECTS = [
    {
        "project_code":            "KK-2024-001",
        "project_name":            "부산 해운대 물류센터 신축공사",
        "client":                  "(주)부산물류",
        "contract_start":          "2024-03-01",
        "contract_end":            "2025-08-31",
        "initial_contract_amount": 4500000000,   # 최초 계약금액 (원)
        "revised_contract_amount": 4500000000,   # 변경 계약금액 (원)
        "execution_budget":        3800000000,   # 실행예산 (원)
        "target_profit_rate":      0.08,          # 목표 수익률 8%
        "status":                  "진행중",
    },
    {
        "project_code":            "KK-2024-002",
        "project_name":            "울산 언양 공장 증설공사",
        "client":                  "금강공업(주) 내부",
        "contract_start":          "2024-01-15",
        "contract_end":            "2025-03-31",
        "initial_contract_amount": 1200000000,
        "revised_contract_amount": 1200000000,
        "execution_budget":        1150000000,   # 실행예산 — 구조적 수익률 4.2% < 목표 8% → 경고 발생
        # 역산 공식: 수익률 = (계약금액 - 실행예산) / 계약금액 = (1.2억 - 1.15억) / 1.2억 = 4.2%
        "target_profit_rate":      0.08,
        "status":                  "진행중",
    },
    {
        "project_code":            "KK-2023-015",
        "project_name":            "경남 창원 산업단지 전기설비공사",
        "client":                  "창원산단관리공단",
        "contract_start":          "2023-04-01",
        "contract_end":            "2024-03-31",
        "initial_contract_amount": 2800000000,
        "revised_contract_amount": 2900000000,   # 변경 계약금액 (설계 변경)
        "execution_budget":        2400000000,
        "target_profit_rate":      0.10,          # 목표 수익률 10%
        "status":                  "준공",
    },
    {
        "project_code":            "KK-2024-003",
        "project_name":            "대구 북구 공동주택 기계설비공사",
        "client":                  "(주)대구주택건설",
        "contract_start":          "2024-10-01",
        "contract_end":            "2026-06-30",
        "initial_contract_amount": 3200000000,
        "revised_contract_amount": 3200000000,
        "execution_budget":        2700000000,
        "target_profit_rate":      0.08,
        "status":                  "진행중",
    },
    {
        "project_code":            "KK-2023-012",
        "project_name":            "부산 사상 산업단지 소방공사",
        "client":                  "사상산업단지조합",
        "contract_start":          "2023-01-01",
        "contract_end":            "2023-12-31",
        "initial_contract_amount": 1800000000,
        "revised_contract_amount": 1850000000,   # 소규모 변경 계약
        "execution_budget":        1600000000,
        "target_profit_rate":      0.10,          # 목표 수익률 10% — 수익률 우수 프로젝트
        "status":                  "준공",
    },
]

# 직접비 내역 (direct_costs 테이블)
# 구성: (project_code, cost_type, amount, recorded_at)
DIRECT_COSTS = [
    # KK-2024-001 부산 해운대 물류센터 신축공사
    ("KK-2024-001", "인건비", 900000000, "2024-06-30"),
    ("KK-2024-001", "자재비", 800000000, "2024-09-30"),
    ("KK-2024-001", "외주비", 500000000, "2024-12-31"),

    # KK-2024-002 울산 언양 공장 증설공사
    # 직접비 합계 1,050,000,000 + 간접비 합계 230,000,000 = 1,280,000,000 > 실행예산 1,000,000,000 → 경고
    ("KK-2024-002", "인건비", 450000000, "2024-06-30"),
    ("KK-2024-002", "자재비", 380000000, "2024-09-30"),
    ("KK-2024-002", "외주비", 220000000, "2024-12-31"),

    # KK-2023-015 경남 창원 산업단지 전기설비공사 (준공)
    ("KK-2023-015", "인건비", 1100000000, "2023-12-31"),
    ("KK-2023-015", "자재비",  700000000, "2023-12-31"),
    ("KK-2023-015", "외주비",  300000000, "2024-03-31"),

    # KK-2024-003 대구 북구 공동주택 기계설비공사 (초기 단계)
    ("KK-2024-003", "인건비", 120000000, "2024-12-31"),
    ("KK-2024-003", "자재비", 180000000, "2024-12-31"),

    # KK-2023-012 부산 사상 산업단지 소방공사 (준공, 수익률 우수)
    ("KK-2023-012", "인건비", 600000000, "2023-06-30"),
    ("KK-2023-012", "자재비", 450000000, "2023-09-30"),
    ("KK-2023-012", "외주비", 250000000, "2023-12-31"),
]

# 간접비 내역 (indirect_costs 테이블)
# 구성: (project_code, cost_type, amount, recorded_at)
INDIRECT_COSTS = [
    # KK-2024-001 부산 해운대 물류센터 신축공사
    ("KK-2024-001", "현장관리비", 250000000, "2024-12-31"),
    ("KK-2024-001", "경비",       130000000, "2024-12-31"),

    # KK-2024-002 울산 언양 공장 증설공사
    ("KK-2024-002", "현장관리비", 150000000, "2024-12-31"),
    ("KK-2024-002", "경비",        80000000, "2024-12-31"),

    # KK-2023-015 경남 창원 산업단지 전기설비공사 (준공)
    ("KK-2023-015", "현장관리비", 200000000, "2024-03-31"),
    ("KK-2023-015", "경비",       100000000, "2024-03-31"),

    # KK-2024-003 대구 북구 공동주택 기계설비공사 (초기 단계)
    ("KK-2024-003", "현장관리비", 80000000, "2024-12-31"),

    # KK-2023-012 부산 사상 산업단지 소방공사 (준공, 수익률 우수)
    ("KK-2023-012", "현장관리비", 120000000, "2023-12-31"),
    ("KK-2023-012", "경비",        60000000, "2023-12-31"),
]

# 수금 내역 (collections 테이블)
# 구성: (project_code, collection_round, amount, collected_at)
COLLECTIONS = [
    # KK-2024-001 부산 해운대 물류센터 신축공사
    ("KK-2024-001", 1, 1800000000, "2024-07-01"),  # 1차 기성
    ("KK-2024-001", 2,  900000000, "2024-12-01"),  # 2차 기성

    # KK-2024-002 울산 언양 공장 증설공사
    ("KK-2024-002", 1, 500000000, "2024-07-01"),   # 1차 기성

    # KK-2023-015 경남 창원 산업단지 전기설비공사 (준공)
    ("KK-2023-015", 1, 1000000000, "2023-08-01"),  # 1차 기성
    ("KK-2023-015", 2, 1000000000, "2023-12-01"),  # 2차 기성
    ("KK-2023-015", 3,  900000000, "2024-04-01"),  # 준공금

    # KK-2024-003 대구 북구 공동주택 기계설비공사 (초기 단계)
    ("KK-2024-003", 1, 500000000, "2024-12-01"),   # 1차 기성

    # KK-2023-012 부산 사상 산업단지 소방공사 (준공, 수익률 우수)
    ("KK-2023-012", 1, 700000000, "2023-04-01"),   # 1차 기성
    ("KK-2023-012", 2, 700000000, "2023-08-01"),   # 2차 기성
    ("KK-2023-012", 3, 450000000, "2024-01-15"),   # 준공금
]

# ERP 매출 내역 (erp_revenue 테이블)
# 구성: (project_code, amount, period_start, period_end)
ERP_REVENUE = [
    # KK-2024-001 부산 해운대 물류센터 신축공사
    ("KK-2024-001", 2100000000, "2024-01-01", "2024-12-31"),

    # KK-2024-002 울산 언양 공장 증설공사
    ("KK-2024-002", 800000000, "2024-01-01", "2024-12-31"),

    # KK-2023-015 경남 창원 산업단지 전기설비공사 (준공)
    ("KK-2023-015", 2900000000, "2023-04-01", "2024-03-31"),

    # KK-2024-003 대구 북구 공동주택 기계설비공사 (초기 단계)
    ("KK-2024-003", 380000000, "2024-10-01", "2024-12-31"),

    # KK-2023-012 부산 사상 산업단지 소방공사 (준공, 수익률 우수)
    ("KK-2023-012", 1850000000, "2023-01-01", "2023-12-31"),
]


# =============================================================
# DB 초기화 및 데이터 투입 함수
# =============================================================

def init_db(conn: sqlite3.Connection) -> None:
    """schema.sql을 읽어 테이블을 생성한다. (DROP IF EXISTS → CREATE)"""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    # DROP 순서는 외래키 참조 역순 (자식 → 부모)
    drop_statements = [
        "DROP TABLE IF EXISTS erp_revenue;",
        "DROP TABLE IF EXISTS collections;",
        "DROP TABLE IF EXISTS indirect_costs;",
        "DROP TABLE IF EXISTS direct_costs;",
        "DROP TABLE IF EXISTS projects;",
    ]
    cursor = conn.cursor()
    for stmt in drop_statements:
        cursor.execute(stmt)

    # schema.sql 전체 실행 (CREATE TABLE IF NOT EXISTS 구문 포함)
    conn.executescript(schema_sql)
    print("[init] 스키마 초기화 완료")


def delete_all_data(conn: sqlite3.Connection) -> None:
    """기존 데이터를 외래키 참조 역순으로 전부 삭제한다."""
    cursor = conn.cursor()
    tables = ["erp_revenue", "collections", "indirect_costs", "direct_costs", "projects"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    print("[reset] 기존 데이터 삭제 완료")


def insert_projects(cursor: sqlite3.Cursor) -> None:
    """projects 테이블에 샘플 프로젝트 5개를 삽입한다."""
    sql = """
        INSERT INTO projects (
            project_code, project_name, client,
            contract_start, contract_end,
            initial_contract_amount, revised_contract_amount,
            execution_budget, target_profit_rate, status
        ) VALUES (
            :project_code, :project_name, :client,
            :contract_start, :contract_end,
            :initial_contract_amount, :revised_contract_amount,
            :execution_budget, :target_profit_rate, :status
        )
    """
    cursor.executemany(sql, PROJECTS)


def insert_direct_costs(cursor: sqlite3.Cursor) -> None:
    """direct_costs 테이블에 직접비 내역을 삽입한다."""
    sql = """
        INSERT INTO direct_costs (project_code, cost_type, amount, recorded_at)
        VALUES (?, ?, ?, ?)
    """
    cursor.executemany(sql, DIRECT_COSTS)


def insert_indirect_costs(cursor: sqlite3.Cursor) -> None:
    """indirect_costs 테이블에 간접비 내역을 삽입한다."""
    sql = """
        INSERT INTO indirect_costs (project_code, cost_type, amount, recorded_at)
        VALUES (?, ?, ?, ?)
    """
    cursor.executemany(sql, INDIRECT_COSTS)


def insert_collections(cursor: sqlite3.Cursor) -> None:
    """collections 테이블에 수금 내역을 삽입한다."""
    sql = """
        INSERT INTO collections (project_code, collection_round, amount, collected_at)
        VALUES (?, ?, ?, ?)
    """
    cursor.executemany(sql, COLLECTIONS)


def insert_erp_revenue(cursor: sqlite3.Cursor) -> None:
    """erp_revenue 테이블에 ERP 매출 내역을 삽입한다."""
    sql = """
        INSERT INTO erp_revenue (project_code, amount, period_start, period_end)
        VALUES (?, ?, ?, ?)
    """
    cursor.executemany(sql, ERP_REVENUE)


def print_row_counts(conn: sqlite3.Connection) -> None:
    """각 테이블의 삽입 행 수를 출력한다."""
    cursor = conn.cursor()

    tables = [
        ("projects",      "projects"),
        ("direct_costs",  "direct_costs"),
        ("indirect_costs","indirect_costs"),
        ("collections",   "collections"),
        ("erp_revenue",   "erp_revenue"),
    ]
    for label, table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"[seed] {label}: {count}개 삽입 완료")


# =============================================================
# 메인 실행 블록
# =============================================================

def main() -> None:
    # 커맨드라인 옵션 파싱
    parser = argparse.ArgumentParser(
        description="K-Progress 샘플 데이터 투입 스크립트"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="기존 데이터를 삭제하고 스키마를 재생성한 뒤 데이터를 다시 투입한다.",
    )
    args = parser.parse_args()

    # DB 연결 (파일 없으면 자동 생성)
    db_exists = DB_PATH.exists()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # 외래키 제약 활성화

    try:
        if not db_exists or args.reset:
            # DB가 없거나 --reset 옵션: 스키마 초기화 (DROP → CREATE)
            init_db(conn)
        elif args.reset:
            # --reset만 단독: 데이터만 삭제 (스키마 유지)
            delete_all_data(conn)

        # 데이터 투입 (projects → direct_costs → indirect_costs → collections → erp_revenue)
        cursor = conn.cursor()
        insert_projects(cursor)
        insert_direct_costs(cursor)
        insert_indirect_costs(cursor)
        insert_collections(cursor)
        insert_erp_revenue(cursor)
        conn.commit()

        # 완료 후 row count 출력
        print_row_counts(conn)
        print(f"\n[seed] DB 경로: {DB_PATH.resolve()}")

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"[오류] 데이터 중복 또는 제약 위반: {e}")
        print("  힌트: --reset 옵션으로 재실행하면 기존 데이터를 지우고 다시 투입합니다.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
