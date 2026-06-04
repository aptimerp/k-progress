"""
pages/tab1_dashboard.py — 탭1: 종합 성과 관제탑 UI
건설사업부 프로젝트 실행관리 및 성과 관제탑 (K-Progress)

담당 PL: 김은지
생성일: 2026-05-26
"""

import streamlit as st
import pandas as pd

from database.db import get_dashboard_data
from core.engine import calculate_all_projects


def render_tab1():
    """탭1: 종합 성과 관제탑 렌더링"""

    # ------------------------------------------------------------------
    # 데이터 로딩 — DB 오류 시 경고 안내 후 조기 반환
    # ------------------------------------------------------------------
    try:
        with st.spinner("데이터 로딩 중..."):
            raw_df = get_dashboard_data()          # DB 집계 뷰 로드
            metrics_df = calculate_all_projects(raw_df)  # 역산 엔진 적용
    except Exception as e:
        st.warning(
            "DB 데이터를 불러오지 못했습니다. "
            "kprogress.db 파일이 없거나 접근할 수 없습니다.\n\n"
            f"오류 상세: {e}"
        )
        return

    # ------------------------------------------------------------------
    # 섹션 1: 요약 카드 (전체·진행중·준공·경고 현장 수)
    # ------------------------------------------------------------------
    st.subheader("요약")

    total_count = len(metrics_df)
    active_count = int((metrics_df['status'] == '진행중').sum())
    done_count = int((metrics_df['status'] == '준공').sum())
    warning_count = int(metrics_df['is_warning'].sum())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="전체 프로젝트 수",
            value=f"{total_count}개"
        )

    with col2:
        st.metric(
            label="진행중 현장 수",
            value=f"{active_count}개"
        )

    with col3:
        st.metric(
            label="준공 완료 현장 수",
            value=f"{done_count}개"
        )

    with col4:
        # 경고 수에 따라 delta 색상 분기
        if warning_count == 0:
            st.metric(
                label="경고 현장 수",
                value=f"{warning_count}개",
                delta="정상"
            )
        else:
            st.metric(
                label="경고 현장 수",
                value=f"{warning_count}개",
                delta=f"{warning_count}개 주의",
                delta_color="inverse"
            )

    st.divider()

    # ------------------------------------------------------------------
    # 섹션 2: 매출액 비교 차트 (시스템 역산 vs ERP vs 수금)
    # ------------------------------------------------------------------
    st.subheader("📊 매출액 비교: 시스템 역산 vs ERP vs 수금")

    try:
        import plotly.express as px

        # 억원 단위 환산 (1억 = 100,000,000)
        chart_df = metrics_df[
            ['project_name', 'system_revenue', 'total_erp_revenue', 'total_collection']
        ].copy()
        chart_df['시스템 산출 매출액(억)'] = chart_df['system_revenue'] / 1e8
        chart_df['ERP 매출액(억)'] = chart_df['total_erp_revenue'] / 1e8
        chart_df['수금액(억)'] = chart_df['total_collection'] / 1e8

        fig = px.bar(
            chart_df,
            x='project_name',
            y=['시스템 산출 매출액(억)', 'ERP 매출액(억)', '수금액(억)'],
            barmode='group',
            color_discrete_map={
                '시스템 산출 매출액(억)': '#1f77b4',
                'ERP 매출액(억)': '#ff7f0e',
                '수금액(억)': '#2ca02c'
            }
        )
        fig.update_layout(
            xaxis_title="프로젝트",
            yaxis_title="금액 (억원)",
            legend_title="구분"
        )
        st.plotly_chart(fig, width='stretch')

    except ImportError:
        # plotly 미설치 시 st.bar_chart 폴백
        chart_df = metrics_df.set_index('project_name')[
            ['system_revenue', 'total_erp_revenue', 'total_collection']
        ]
        chart_df.columns = ['시스템 매출액', 'ERP 매출액', '수금액']
        st.bar_chart(chart_df)

    st.divider()

    # ------------------------------------------------------------------
    # 섹션 3: 경고 리스트 — 수익률 미달 현장
    # ------------------------------------------------------------------
    st.subheader("⚠️ 수익률 미달 현장")

    warning_df = metrics_df[metrics_df['is_warning'] == True]

    if warning_df.empty:
        st.success("현재 수익률 미달 현장이 없습니다.")
    else:
        st.error(f"⚠ {len(warning_df)}개 현장이 목표 수익률 미달입니다.")

        # 표시할 컬럼 선택 및 포맷
        display_warning = warning_df[
            ['project_name', 'client', 'progress_rate',
             'system_profit_rate', 'target_profit_rate', 'system_profit']
        ].copy()
        display_warning.columns = [
            '프로젝트명', '발주처', '진행률(%)',
            '시스템 수익률(%)', '목표 수익률(%)', '수익(원)'
        ]

        # 비율 → 백분율 변환 (0.08 → 8.0)
        display_warning['진행률(%)'] = (display_warning['진행률(%)'] * 100).round(1)
        display_warning['시스템 수익률(%)'] = (display_warning['시스템 수익률(%)'] * 100).round(1)
        display_warning['목표 수익률(%)'] = (display_warning['목표 수익률(%)'] * 100).round(1)

        # 수익(원) 천 단위 구분 쉼표 포맷
        display_warning['수익(원)'] = display_warning['수익(원)'].apply(lambda x: f"{x:,.0f}")

        st.dataframe(display_warning, width='stretch')

    st.divider()

    # ------------------------------------------------------------------
    # 섹션 4: 전체 프로젝트 현황 테이블
    # ------------------------------------------------------------------
    st.subheader("📋 전체 프로젝트 현황")

    display_all = metrics_df[
        ['project_code', 'project_name', 'client', 'status',
         'revised_contract_amount', 'progress_rate',
         'system_revenue', 'total_erp_revenue', 'system_profit_rate']
    ].copy()
    display_all.columns = [
        '코드', '프로젝트명', '발주처', '상태',
        '계약금액(억)', '진행률(%)', '시스템매출(억)', 'ERP매출(억)', '수익률(%)'
    ]

    # 억원 단위 환산 및 백분율 변환
    display_all['계약금액(억)'] = (display_all['계약금액(억)'] / 1e8).round(1)
    display_all['진행률(%)'] = (display_all['진행률(%)'] * 100).round(1)
    display_all['시스템매출(억)'] = (display_all['시스템매출(억)'] / 1e8).round(1)
    display_all['ERP매출(억)'] = (display_all['ERP매출(억)'] / 1e8).round(1)
    display_all['수익률(%)'] = (display_all['수익률(%)'] * 100).round(1)

    st.dataframe(display_all, width='stretch')
