# 금강공업 DB 스키마 가이드

## ERP DB (MSSQL 2022)

### Detail 14개 테이블 구조
금강 ERP의 핵심 패턴: 메인 테이블 1개 + 상세 테이블 14개.

```sql
-- 예시 구조 (실제 테이블명은 SAC 확인 필요)
[메인테이블]
  - ID (PK)
  - 기본 정보 컬럼들

[메인테이블_Detail_01] ~ [메인테이블_Detail_14]
  - 메인ID (FK)
  - 상세 정보 컬럼들
```

### KV 테이블 패턴
```sql
-- chatbot_details 등 키-값 형태
CREATE TABLE chatbot_details (
  id INT PRIMARY KEY,
  key NVARCHAR(100),
  value NVARCHAR(MAX)
)
```

### MSSQL 제약사항
- 배열 미사용 (1NF 준수)
- JSON 컬럼 미사용
- Stored Procedure: 언양 수불 외에는 거의 없음

---

## 신규 서비스 DB (Supabase / PostgreSQL)

### k_pro 테이블 (미정 — Phase 2에서 설계)

```sql
-- 초안 예시
CREATE TABLE projects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  -- 건설 프로젝트 관련 컬럼 추가 예정
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Supabase 허용 패턴
- JSONB 컬럼 자유 사용 가능
- 배열 타입 사용 가능
- Row Level Security (RLS) 적용 권장

---

## 연동 구조
```
클라이언트 (Next.js)
    ↓
Vercel API Routes
    ├── Supabase 직접 조회 (신규 데이터)
    └── 금강 SAC API (ERP 데이터)
            ↓
        MSSQL (기존 ERP)
```

> 실제 테이블 정보는 SAC 이영호 차장에게 문의
