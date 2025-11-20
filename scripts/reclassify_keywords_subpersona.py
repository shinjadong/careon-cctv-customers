#!/usr/bin/env python3
"""
기존 키워드를 세부 페르소나로 재분류
특히 3-2 (이탈/고통) 고객을 정밀하게 식별
"""

import sqlite3
from pathlib import Path
import re

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")


def auto_label_sub_persona(keyword: str, parent_persona_id: int) -> tuple:
    """
    세부 페르소나 자동 라벨링

    Returns:
        (sub_persona_id, confidence_score)
    """

    keyword_lower = keyword.lower()

    # 🔥 핵심: 3번 페르소나 분리 (진입 vs 이탈)
    if parent_persona_id == 3:
        # 3-2: 이탈/고통 단계 키워드 패턴 (위약금 해방 타겟)
        pain_patterns = [
            r'위약금', r'해지', r'철거', r'고객센터', r'as\b', r'수리',
            r'약정', r'기간', r'만료', r'이전', r'불만', r'문의',
            r'출동', r'해약', r'해제', r'취소', r'환불',
            r'비용문의', r'요금문의', r'렌탈', r'렌트',
            r'변경', r'교체', r'철수', r'반납'
        ]

        for pattern in pain_patterns:
            if re.search(pattern, keyword_lower):
                return ('3-2', 0.9)  # 높은 신뢰도

        # 3-1: 진입/비교 단계 (기본값)
        return ('3-1', 0.7)

    # 나머지 페르소나는 단순 매핑
    mapping = {
        1: '1-1',
        2: '2-1',
        4: '4-1',
        5: '5-1'
    }

    return (mapping.get(parent_persona_id, '5-1'), 0.8)


def reclassify_all_keywords():
    """모든 키워드를 세부 페르소나로 재분류"""

    print("=" * 80)
    print("키워드 세부 페르소나 재분류")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 전체 키워드 조회
    cursor.execute("""
        SELECT keyword_id, keyword, persona_id
        FROM keywords_master
    """)

    keywords = cursor.fetchall()
    total = len(keywords)

    print(f"\n📊 전체 키워드 수: {total:,}개")
    print(f"⏳ 재분류 시작...\n")

    # 재분류 실행
    updated = 0
    sub_persona_stats = {}

    for row in keywords:
        keyword_id = row['keyword_id']
        keyword = row['keyword']
        parent_persona = row['persona_id']

        # 세부 페르소나 자동 라벨링
        sub_persona_id, confidence = auto_label_sub_persona(keyword, parent_persona)

        # DB 업데이트
        cursor.execute("""
            UPDATE keywords_master
            SET sub_persona_id = ?,
                confidence_score = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE keyword_id = ?
        """, (sub_persona_id, confidence, keyword_id))

        # 통계
        sub_persona_stats[sub_persona_id] = sub_persona_stats.get(sub_persona_id, 0) + 1
        updated += 1

        if updated % 100 == 0:
            print(f"   진행: {updated}/{total} ({updated/total*100:.1f}%)")

    conn.commit()

    print(f"\n✅ 재분류 완료: {updated:,}개")

    # 세부 페르소나별 통계
    print("\n" + "=" * 80)
    print("📊 세부 페르소나별 키워드 분포")
    print("=" * 80)

    cursor.execute("""
        SELECT sp.sub_persona_id, sp.sub_persona_name, sp.priority_level,
               COUNT(k.keyword_id) as cnt
        FROM sub_personas sp
        LEFT JOIN keywords_master k ON sp.sub_persona_id = k.sub_persona_id
        GROUP BY sp.sub_persona_id
        ORDER BY sp.sub_persona_id
    """)

    for row in cursor.fetchall():
        priority_icon = "🔥" if row[2] == "CRITICAL" else "📌"
        print(f"   {priority_icon} {row[0]}: {row[1]:<30} {row[3]:>6,}개")

    # 🔥 3-2 샘플 키워드 출력 (가장 중요!)
    print("\n" + "=" * 80)
    print("🔥 3-2 (이탈/고통) 키워드 샘플 20개 (위약금 해방 타겟)")
    print("=" * 80)

    cursor.execute("""
        SELECT k.keyword, kt.search_volume_total
        FROM keywords_master k
        LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
        WHERE k.sub_persona_id = '3-2'
        ORDER BY kt.search_volume_total DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    if rows:
        print(f"\n{'키워드':<30} {'월간 검색량':>15}")
        print("-" * 50)
        for row in rows:
            volume = row[1] if row[1] else 0
            print(f"{row[0]:<30} {volume:>13,}회")
    else:
        print("   ⚠️  3-2로 분류된 키워드가 없습니다!")

    # 3-1 샘플 키워드 출력
    print("\n" + "=" * 80)
    print("📌 3-1 (진입/비교) 키워드 샘플 20개")
    print("=" * 80)

    cursor.execute("""
        SELECT k.keyword, kt.search_volume_total
        FROM keywords_master k
        LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
        WHERE k.sub_persona_id = '3-1'
        ORDER BY kt.search_volume_total DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    if rows:
        print(f"\n{'키워드':<30} {'월간 검색량':>15}")
        print("-" * 50)
        for row in rows:
            volume = row[1] if row[1] else 0
            print(f"{row[0]:<30} {volume:>13,}회")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ 재분류 완료! 이제 3-2 타겟팅 준비 완료")
    print("=" * 80)
    print(f"\n💾 DB 위치: {DB_PATH}\n")


if __name__ == "__main__":
    reclassify_all_keywords()
