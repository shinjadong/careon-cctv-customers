#!/usr/bin/env python3
"""
세부 페르소나(Sub-persona) 체계 도입
3-2 (이탈/고통) 고객 타게팅을 위한 DB 업그레이드
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")

print("=" * 80)
print("세부 페르소나 체계 도입 (Sub-persona Upgrade)")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 1: 컬럼 추가
print("\n📋 Step 1: sub_persona_id 컬럼 추가...")

try:
    cursor.execute("""
        ALTER TABLE keywords_master
        ADD COLUMN sub_persona_id VARCHAR(10)
    """)
    print("   ✅ sub_persona_id 컬럼 추가 완료")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("   ℹ️  sub_persona_id 컬럼이 이미 존재합니다")
    else:
        raise

conn.commit()

# Step 2: 세부 페르소나 정의 테이블 생성
print("\n📋 Step 2: 세부 페르소나 정의 테이블 생성...")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sub_personas (
        sub_persona_id VARCHAR(10) PRIMARY KEY,
        parent_persona_id INTEGER,
        sub_persona_name VARCHAR(100),
        description TEXT,
        keywords_pattern TEXT,
        content_strategy TEXT,
        priority_level VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_persona_id) REFERENCES customer_personas(persona_id)
    )
""")

# 세부 페르소나 데이터 삽입
sub_personas = [
    # 1번: 홈캠 비교 고객
    ('1-1', 1, '홈캠 일반',
     '홈캠 추천 및 비교를 원하는 일반 고객',
     '홈캠, 추천, 비교, 가정용, 펫캠, 무선',
     '제품 비교 리뷰, 추천 콘텐츠',
     'medium'),

    # 2번: DIY 고객
    ('2-1', 2, 'DIY 일반',
     '셀프 설치를 원하는 고객',
     '설치, 셀프, DIY, 자가설치, 설치방법',
     '설치 가이드, 튜토리얼',
     'medium'),

    # 3번: 보안업체 비교 고객 (핵심 분리)
    ('3-1', 3, '진입/비교 단계',
     '브랜드를 고민하거나 신규 가입 가격을 알아보는 고객',
     '가격, 비용, 추천, 종류, 설치비, 견적, (브랜드명)',
     '가격 비교, 서비스 비교, 일반 정보',
     'medium'),

    ('3-2', 3, '이탈/고통 단계 🔥',
     '기존 업체에 불만이 있거나 해지/위약금 문제로 고통받는 전환 고객 (위약금 해방 전략 타겟)',
     '위약금, 해지, 철거, 고객센터, AS, 불만, 약정, 이전, 수리, 기간, 만료',
     '위약금 해결, 고통 공감, 전환 유도, Un-carrier 캠페인',
     'CRITICAL'),

    # 4번: B2B CCTV 고객
    ('4-1', 4, 'B2B 일반',
     'CCTV 설치를 원하는 B2B 고객',
     '설치업체, 견적, NVR, DVR, 매장, 사무실',
     '기술 스펙, 견적 가이드',
     'medium'),

    # 5번: 기타
    ('5-1', 5, '기타',
     '위 분류에 속하지 않는 키워드',
     'CCTV종류, 역사, 법률, 규제',
     '일반 정보',
     'low'),
]

for sp in sub_personas:
    cursor.execute("""
        INSERT OR REPLACE INTO sub_personas
        (sub_persona_id, parent_persona_id, sub_persona_name, description,
         keywords_pattern, content_strategy, priority_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sp)
    print(f"   ✅ {sp[0]}: {sp[2]}")

conn.commit()

# Step 3: 통계 출력
print("\n" + "=" * 80)
print("✅ 세부 페르소나 체계 업그레이드 완료!")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM sub_personas")
print(f"\n📊 세부 페르소나 수: {cursor.fetchone()[0]}개")

cursor.execute("""
    SELECT sub_persona_id, sub_persona_name, priority_level
    FROM sub_personas
    ORDER BY sub_persona_id
""")
print(f"\n📋 세부 페르소나 목록:")
for row in cursor.fetchall():
    priority_icon = "🔥" if row[2] == "CRITICAL" else "📌"
    print(f"   {priority_icon} {row[0]}: {row[1]} ({row[2]})")

conn.close()

print(f"\n💾 DB 위치: {DB_PATH}\n")
