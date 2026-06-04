"""
core/engine.py — 진행률 기반 매출액 역산 엔진
건설사업부 프로젝트 실행관리 핵심 비즈니스 로직

핵심 공식 (변경 금지):
  ① 전체 예상 실행원가 = 직접비(ERP) + 간접비(ERP)
  ② 진행률(%)         = 전체 예상 실행원가 / 총 실행예산
  ③ 시스템 산출 매출액 = 총 계약금액 × 진행률(%)
  ④ 시스템 산출 수익   = 시스템 산출 매출액 - 전체 예상 실행원가
  ⑤ 시스템 산출 수익률 = 시스템 산출 수익 / 시스템 산출 매출액
  ⑥ 경고 여부         = 시스템 산출 수익률(%) < 목표 수익률(%)

설계 원칙:
  - 순수 함수 — UI, DB 종속 없음
  - import pandas만 허용
  - 주석은 한국어, 비즈니스 용어 병기
"""

import pandas as pd


def calculate_project_metrics(
    project_code: str,
    revised_contract_amount: float,  # 변경 계약금액
    execution_budget: float,         # 총 실행예산
    target_profit_rate: float,       # 목표 수익률 (예: 0.08 = 8%)
    total_direct_cost: float,        # 직접비 합계
    total_indirect_cost: float,      # 간접비 합계
    total_collection: float,         # 수금액 누계
    total_erp_revenue: float         # ERP 매출액
) -> dict:
    """
    단일 프로젝트의 재무 지표를 계산합니다.

    핵심 공식에 따라 진행률을 산출하고,
    시스템 산출 매출액·수익·수익률·경고 여부를 반환합니다.

    Args:
        project_code          : 프로젝트 코드 (식별자)
        revised_contract_amount: 변경 계약금액 (원)
        execution_budget      : 총 실행예산 (원) — 진행률 분모
        target_profit_rate    : 목표 수익률 (소수, 예: 0.08)
        total_direct_cost     : 직접비 합계 (원) — ERP 집계값
        total_indirect_cost   : 간접비 합계 (원) — ERP 집계값
        total_collection      : 수금액 누계 (원)
        total_erp_revenue     : ERP 매출액 (원) — 괴리 비교용

    Returns:
        dict: 아래 키를 포함하는 지표 딕셔너리
            project_code          : 입력과 동일
            expected_execution_cost: 전체 예상 실행원가 (직접비 + 간접비)
            progress_rate         : 진행률 (0.0 ~ 1.0+, 예산 초과 허용)
            system_revenue        : 시스템 산출 매출액
            system_profit         : 시스템 산출 수익
            system_profit_rate    : 시스템 산출 수익률
            erp_revenue_diff      : ERP 매출액 - 시스템 산출 매출액 (괴리)
            collection_diff       : 수금액 - 시스템 산출 매출액 (미수금 지표)
            is_warning            : 수익률 경고 여부 (bool)
    """

    # ① 전체 예상 실행원가 = 직접비 + 간접비
    expected_execution_cost = total_direct_cost + total_indirect_cost

    # ② 진행률(%) = 전체 예상 실행원가 / 총 실행예산
    #    엣지 케이스: 실행예산이 0이면 ZeroDivisionError 방지 → 0.0 처리
    if execution_budget == 0:
        progress_rate = 0.0
    else:
        progress_rate = expected_execution_cost / execution_budget
    # 진행률 > 1.0 허용 — 예산 초과 현장은 그대로 표시

    # ③ 시스템 산출 매출액 = 총 계약금액 × 진행률
    system_revenue = revised_contract_amount * progress_rate

    # ④ 시스템 산출 수익 = 시스템 산출 매출액 - 전체 예상 실행원가
    system_profit = system_revenue - expected_execution_cost

    # ⑤ 시스템 산출 수익률 = 시스템 산출 수익 / 시스템 산출 매출액
    #    엣지 케이스: 시스템 산출 매출액이 0이면 ZeroDivisionError 방지 → 0.0 처리
    if system_revenue == 0:
        system_profit_rate = 0.0
    else:
        system_profit_rate = system_profit / system_revenue

    # ERP 매출액 괴리 = ERP 기록 매출액 - 시스템 산출 매출액
    # 양수: ERP가 더 크게 인식 (과인식), 음수: ERP가 더 작게 인식 (미인식)
    erp_revenue_diff = total_erp_revenue - system_revenue

    # 미수금 지표 = 수금액 - 시스템 산출 매출액
    # 음수: 미수금 존재 (매출보다 덜 받음), 양수: 선수금
    collection_diff = total_collection - system_revenue

    # ⑥ 경고 여부 = 시스템 산출 수익률 < 목표 수익률
    is_warning = system_profit_rate < target_profit_rate

    return {
        "project_code": project_code,
        "expected_execution_cost": expected_execution_cost,  # 전체 예상 실행원가
        "progress_rate": progress_rate,                      # 진행률
        "system_revenue": system_revenue,                    # 시스템 산출 매출액
        "system_profit": system_profit,                      # 시스템 산출 수익
        "system_profit_rate": system_profit_rate,            # 시스템 산출 수익률
        "erp_revenue_diff": erp_revenue_diff,                # ERP 매출 괴리
        "collection_diff": collection_diff,                  # 미수금 지표
        "is_warning": is_warning,                            # 경고 여부
    }


def calculate_all_projects(df: pd.DataFrame) -> pd.DataFrame:
    """
    전체 프로젝트 DataFrame에 재무 지표를 일괄 계산합니다.

    get_dashboard_data() 결과 DataFrame을 입력으로 받아,
    각 행에 calculate_project_metrics()를 적용하고
    지표 컬럼이 추가된 DataFrame을 반환합니다.

    입력 DataFrame 필수 컬럼:
        project_code            : 프로젝트 코드
        project_name            : 프로젝트명
        client                  : 발주처
        status                  : 진행 상태
        revised_contract_amount : 변경 계약금액 (원)
        execution_budget        : 총 실행예산 (원)
        target_profit_rate      : 목표 수익률 (소수)
        total_direct_cost       : 직접비 합계 (원)
        total_indirect_cost     : 간접비 합계 (원)
        total_collection        : 수금액 누계 (원)
        total_erp_revenue       : ERP 매출액 (원)

    추가되는 컬럼:
        expected_execution_cost : 전체 예상 실행원가
        progress_rate           : 진행률
        system_revenue          : 시스템 산출 매출액
        system_profit           : 시스템 산출 수익
        system_profit_rate      : 시스템 산출 수익률
        erp_revenue_diff        : ERP 매출 괴리
        collection_diff         : 미수금 지표
        is_warning              : 경고 여부

    Args:
        df: get_dashboard_data() 결과 DataFrame

    Returns:
        pd.DataFrame: 입력 컬럼 + 지표 컬럼이 추가된 DataFrame
    """

    # 빈 DataFrame 처리 — 컬럼만 추가하고 반환
    if df.empty:
        metric_columns = [
            "expected_execution_cost",
            "progress_rate",
            "system_revenue",
            "system_profit",
            "system_profit_rate",
            "erp_revenue_diff",
            "collection_diff",
            "is_warning",
        ]
        for col in metric_columns:
            df[col] = pd.Series(dtype=float if col != "is_warning" else bool)
        return df

    # 각 행에 calculate_project_metrics 적용 후 지표 dict → 컬럼으로 병합
    metrics_series = df.apply(
        lambda row: calculate_project_metrics(
            project_code=row["project_code"],
            revised_contract_amount=row["revised_contract_amount"],
            execution_budget=row["execution_budget"],
            target_profit_rate=row["target_profit_rate"],
            total_direct_cost=row["total_direct_cost"],
            total_indirect_cost=row["total_indirect_cost"],
            total_collection=row["total_collection"],
            total_erp_revenue=row["total_erp_revenue"],
        ),
        axis=1,
        result_type="expand",  # dict를 컬럼으로 자동 확장
    )

    # project_code는 이미 df에 존재하므로 중복 제거 후 병합
    metrics_series = metrics_series.drop(columns=["project_code"])

    result_df = pd.concat([df, metrics_series], axis=1)
    return result_df


# ---------------------------------------------------------------------------
# 자체 검증 블록 — 프로젝트 A 기준 (직접 실행 시 공식 검증)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 자체 검증 — 프로젝트 A 기준
    result = calculate_project_metrics(
        'TEST', 4500000000, 3800000000, 0.08,
        2200000000, 380000000, 1800000000, 2100000000
    )
    expected_progress = (2200000000 + 380000000) / 3800000000
    assert abs(result['progress_rate'] - expected_progress) < 0.001, "진행률 공식 오류"
    assert result['is_warning'] == False, "정상 프로젝트 경고 오류"
    print(f"진행률: {result['progress_rate']:.2%}")
    print(f"시스템 매출액: {result['system_revenue']:,.0f}원")
    print(f"시스템 수익률: {result['system_profit_rate']:.2%}")
    print(f"경고: {result['is_warning']}")
    print("공식 검증 PASS")

    # 추가 엣지 케이스 검증
    # 실행예산 0 → ZeroDivisionError 방지
    edge_zero_budget = calculate_project_metrics(
        'ZERO_BUDGET', 1000000000, 0, 0.10,
        500000000, 50000000, 0, 0
    )
    assert edge_zero_budget['progress_rate'] == 0.0, "실행예산 0 엣지 케이스 오류"
    print("\n실행예산 0 엣지 케이스 PASS")

    # 예산 초과 현장 — progress_rate > 1.0 허용
    edge_over_budget = calculate_project_metrics(
        'OVER_BUDGET', 1000000000, 500000000, 0.10,
        400000000, 200000000, 0, 0
    )
    assert edge_over_budget['progress_rate'] > 1.0, "예산 초과 진행률 오류"
    print(f"예산 초과 진행률: {edge_over_budget['progress_rate']:.2%} PASS")

    print("\n전체 엣지 케이스 검증 완료")
