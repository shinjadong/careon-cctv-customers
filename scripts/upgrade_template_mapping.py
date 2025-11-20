#!/usr/bin/env python3
"""
템플릿 매핑 시스템 추가
각 페르소나별 고객 여정(Customer Journey) DB화
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")

print("=" * 80)
print("🎯 템플릿 매핑 시스템 추가 (Customer Journey Mapping)")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 1: 컬럼 추가
print("\n📋 Step 1: sub_personas 테이블에 퍼널 정보 컬럼 추가...\n")

columns_to_add = [
    ("template_id", "VARCHAR(50)"),
    ("landing_url", "VARCHAR(200)"),
    ("funnel_strategy", "TEXT"),
    ("cta_text", "VARCHAR(200)")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"""
            ALTER TABLE sub_personas
            ADD COLUMN {col_name} {col_type}
        """)
        print(f"   ✅ {col_name} 컬럼 추가 완료")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print(f"   ℹ️  {col_name} 컬럼이 이미 존재합니다")
        else:
            raise

conn.commit()

# Step 2: 퍼널 전략 데이터 업데이트
print("\n📋 Step 2: 페르소나별 퍼널 전략 업데이트...\n")

funnel_mappings = [
    # 1-1: 홈캠 일반
    ('1-1',
     'TPL_HOMECAM_STORE',
     '/homecam-store',
     '홈캠 스마트스토어로 유도 → 제품 비교 후 즉시 구매 전환',
     '베스트 홈캠 TOP 10 보기'),

    # 2-1: DIY 일반
    ('2-1',
     'TPL_DIY_GUIDE',
     '/diy-installation-guide',
     'DIY 설치 가이드 영상 페이지 → 사용 제품 스토어 링크 유도',
     'DIY 설치 영상 보러가기'),

    # 3-1: 진입/비교 단계
    ('3-1',
     'TPL_COMPARISON',
     '/kt-vs-caps-comparison',
     'KT vs 캡스 vs 세콤 가격/서비스 비교표 → 일반 견적 문의 랜딩',
     'KT vs 캡스 정확한 비교 보기'),

    # 🔥 3-2: 이탈/고통 단계 (핵심!)
    ('3-2',
     'TPL_PENALTY_CALC',
     '/penalty-calculator',
     '위약금 계산기 웹 → (계산 후) → 안심케어플랜 랜딩 → 상담 신청',
     '내 위약금 0원으로 만들기'),

    # 4-1: B2B 일반
    ('4-1',
     'TPL_B2B_QUOTE',
     '/business-quote',
     'B2B 간편 견적 요청 폼 → 업체 매칭 → 전화 상담',
     '30초 견적 받기'),

    # 5-1: 기타
    ('5-1',
     'TPL_MAIN',
     '/',
     '메인 홈페이지 → 서비스 소개',
     '케어온 알아보기'),
]

for mapping in funnel_mappings:
    cursor.execute("""
        UPDATE sub_personas
        SET template_id = ?,
            landing_url = ?,
            funnel_strategy = ?,
            cta_text = ?
        WHERE sub_persona_id = ?
    """, (mapping[1], mapping[2], mapping[3], mapping[4], mapping[0]))

    priority_icon = "🔥" if mapping[0] == '3-2' else "📌"
    print(f"   {priority_icon} {mapping[0]}: {mapping[1]}")
    print(f"      경로: {mapping[2]}")
    print(f"      전략: {mapping[3]}")
    print(f"      CTA: '{mapping[4]}'")
    print()

conn.commit()

# Step 3: 검증
print("=" * 80)
print("✅ 템플릿 매핑 완료! 고객 여정 DB 검증")
print("=" * 80)

cursor.execute("""
    SELECT sub_persona_id, sub_persona_name, template_id,
           landing_url, cta_text, priority_level
    FROM sub_personas
    ORDER BY sub_persona_id
""")

print(f"\n{'ID':<6} {'페르소나':<25} {'템플릿':<25} {'우선순위':<10}")
print("-" * 80)

for row in cursor.fetchall():
    priority_icon = "🔥" if row[5] == "CRITICAL" else "📌"
    print(f"{row[0]:<6} {row[1]:<25} {row[2]:<25} {priority_icon} {row[5]}")
    print(f"       URL: {row[3]}")
    print(f"       CTA: {row[4]}")
    print()

# Step 4: 3-2 키워드 전체 퍼널 정보 조회
print("=" * 80)
print("🔥 3-2 키워드 전체 퍼널 정보 (샘플 5개)")
print("=" * 80)

cursor.execute("""
    SELECT k.keyword, sp.template_id, sp.landing_url,
           sp.cta_text, kt.search_volume_total
    FROM keywords_master k
    JOIN sub_personas sp ON k.sub_persona_id = sp.sub_persona_id
    LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
    WHERE k.sub_persona_id = '3-2'
    ORDER BY kt.search_volume_total DESC
    LIMIT 5
""")

print(f"\n{'키워드':<25} {'검색량':<12} {'템플릿':<25}")
print("-" * 70)

for row in cursor.fetchall():
    volume = row[4] if row[4] else 0
    print(f"{row[0]:<25} {volume:>10,}회  {row[1]:<25}")
    print(f"   → URL: {row[2]}")
    print(f"   → CTA: '{row[3]}'")
    print()

conn.close()

print("=" * 80)
print("✅ 고객 여정 매핑 완료!")
print("=" * 80)
print("\n💡 이제 AI가 키워드만 보고 '어디로 보낼지' 자동 판단 가능!")
print(f"💾 DB 위치: {DB_PATH}\n")
