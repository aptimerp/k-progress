#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K-Progress — 금강공업 건설사업부 프로젝트 실행관리 및 성과 관제탑
실행: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (패키지 임포트용)
sys.path.insert(0, str(Path(__file__).parent))

# ─────────────────────────────────────────────
# 페이지 설정 (반드시 가장 먼저 호출)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="K-Progress | 금강공업",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 사이드바: 내비게이션
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🏗️ K-Progress")
    st.caption("금강공업 건설사업부 성과 관제탑")
    st.divider()

    selected = st.radio(
        "메뉴 선택",
        options=[
            "📊 종합 성과 관제탑",
            "📁 프로젝트 상세 관리",
            "📚 지식 자산 공유",
        ],
        key="nav_menu"
    )

    st.divider()
    st.caption("K-Progress v0.1.0")
    st.caption("Phase 1 — 관제탑 초기 버전")

# ─────────────────────────────────────────────
# 메인 영역: 탭 라우팅
# ─────────────────────────────────────────────
if selected == "📊 종합 성과 관제탑":
    from pages.tab1_dashboard import render_tab1
    render_tab1()

elif selected == "📁 프로젝트 상세 관리":
    st.title("📁 프로젝트 상세 관리")
    st.info("🚧 Phase 2에서 구현 예정입니다.")
    st.markdown("""
    **Phase 2 구현 예정 기능:**
    - 계약서·수주보고서·실행계획서 첨부파일 보관함
    - 설계변경·원가변동 이력 타임라인
    - ERP 직접비·간접비·수금액 Raw Data 그리드
    """)

elif selected == "📚 지식 자산 공유":
    st.title("📚 지식 자산 공유 및 수주 전략")
    st.info("🚧 Phase 2에서 구현 예정입니다.")
    st.markdown("""
    **Phase 2 구현 예정 기능:**
    - 준공 현장 검색 (공종·발주처·이익률 필터)
    - Lessons Learned 카드 뷰
    - 유사 현장 매칭 시뮬레이션
    """)
