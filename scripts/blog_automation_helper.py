#!/usr/bin/env python3
"""
블로그 포스팅 자동화 헬퍼 스크립트
키워드 페르소나 DB 기반 포스팅 우선순위 계산 및 프롬프트 생성
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")


class BlogAutomationHelper:
    """블로그 자동화 헬퍼 클래스"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_top_keywords_by_volume(self, limit: int = 20, persona_id: Optional[int] = None) -> List[Dict]:
        """
        검색량 기준 TOP 키워드 조회

        Args:
            limit: 조회할 키워드 수
            persona_id: 특정 페르소나만 조회 (None이면 전체)

        Returns:
            키워드 정보 리스트
        """
        cursor = self.conn.cursor()

        persona_filter = ""
        params = [limit]
        if persona_id:
            persona_filter = "AND k.persona_id = ?"
            params.insert(0, persona_id)

        query = f"""
            SELECT k.keyword_id, k.keyword, k.persona_id, p.persona_name,
                   kt.search_volume_total, kt.competition_level,
                   kt.avg_ad_count, k.confidence_score
            FROM keywords_master k
            JOIN customer_personas p ON k.persona_id = p.persona_id
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE kt.search_volume_total > 0 {persona_filter}
            ORDER BY kt.search_volume_total DESC
            LIMIT ?
        """

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def calculate_posting_priority(self, keyword_id: int) -> float:
        """
        블로그 포스팅 우선순위 계산

        고려 요소:
        - 검색량 (40%)
        - 경쟁 정도 (30%)
        - 페르소나 신뢰도 (20%)
        - 광고 수 (10%)

        Returns:
            0-100 사이의 우선순위 점수
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT k.keyword, k.confidence_score, kt.search_volume_total,
                   kt.competition_level, kt.avg_ad_count
            FROM keywords_master k
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE k.keyword_id = ?
        """, (keyword_id,))

        row = cursor.fetchone()
        if not row:
            return 0.0

        score = 0.0

        # 1. 검색량 점수 (40점)
        volume = row['search_volume_total'] or 0
        if volume > 50000:
            score += 40
        elif volume > 10000:
            score += 35
        elif volume > 5000:
            score += 30
        elif volume > 1000:
            score += 20
        else:
            score += 10

        # 2. 경쟁 정도 점수 (30점) - 경쟁 낮을수록 높은 점수
        competition = row['competition_level'] or '중간'
        if competition == '낮음':
            score += 30
        elif competition == '중간':
            score += 20
        else:  # '높음'
            score += 10

        # 3. 페르소나 신뢰도 점수 (20점)
        confidence = row['confidence_score'] or 0.5
        score += confidence * 20

        # 4. 광고 수 점수 (10점) - 광고 많을수록 수익성 높음
        ad_count = row['avg_ad_count'] or 0
        if ad_count >= 10:
            score += 10
        elif ad_count >= 7:
            score += 7
        elif ad_count >= 5:
            score += 5
        else:
            score += 3

        return round(score, 2)

    def get_recommended_keywords_for_posting(self, limit: int = 10, min_volume: int = 1000) -> List[Dict]:
        """
        블로그 포스팅 추천 키워드 조회

        Args:
            limit: 조회할 키워드 수
            min_volume: 최소 검색량

        Returns:
            우선순위 점수와 함께 키워드 리스트
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT k.keyword_id, k.keyword, k.persona_id, p.persona_name,
                   kt.search_volume_total, kt.competition_level,
                   kt.avg_ad_count, k.confidence_score
            FROM keywords_master k
            JOIN customer_personas p ON k.persona_id = p.persona_id
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE kt.search_volume_total >= ?
            AND k.persona_id != 5
            ORDER BY kt.search_volume_total DESC
        """, (min_volume,))

        results = []
        for row in cursor.fetchall():
            keyword_data = dict(row)
            keyword_data['priority_score'] = self.calculate_posting_priority(row['keyword_id'])
            results.append(keyword_data)

        # 우선순위 점수로 정렬
        results.sort(key=lambda x: x['priority_score'], reverse=True)

        return results[:limit]

    def generate_blog_prompt(self, keyword_id: int) -> str:
        """
        페르소나 맞춤형 블로그 프롬프트 생성

        Args:
            keyword_id: 키워드 ID

        Returns:
            AI에게 전달할 블로그 작성 프롬프트
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT k.keyword, k.persona_id, p.persona_name, p.description,
                   p.characteristics, p.content_strategy,
                   kt.search_volume_total, kt.competition_level, kt.avg_ad_count
            FROM keywords_master k
            JOIN customer_personas p ON k.persona_id = p.persona_id
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE k.keyword_id = ?
        """, (keyword_id,))

        row = cursor.fetchone()
        if not row:
            return ""

        keyword = row['keyword']
        persona_name = row['persona_name']
        description = row['description']
        characteristics = row['characteristics']
        content_strategy = row['content_strategy']
        volume = row['search_volume_total']
        competition = row['competition_level']

        # 페르소나별 톤앤매너 및 콘텐츠 타입
        persona_templates = {
            1: {  # 홈캠 비교 고객
                'tone': '친근하고 상세한 비교 톤',
                'content_type': '제품 비교 리뷰',
                'structure': '도입부(고민 공감) → 비교 기준 설명 → 상세 제품 비교 → 추천 및 구매 가이드'
            },
            2: {  # DIY 고객
                'tone': '실용적이고 구체적인 가이드 톤',
                'content_type': 'DIY 설치 가이드',
                'structure': '필요성 설명 → 준비물 → 단계별 설치 가이드 → 팁 및 주의사항'
            },
            3: {  # 보안업체 비교 고객
                'tone': '객관적이고 전문적인 비교 톤',
                'content_type': '업체 비교 분석',
                'structure': '업체 소개 → 가격/서비스 비교 → 장단점 분석 → 선택 가이드'
            },
            4: {  # B2B CCTV 고객
                'tone': '전문적이고 기술적인 톤',
                'content_type': '기술 스펙 및 견적 가이드',
                'structure': '비즈니스 니즈 분석 → 기술 사양 설명 → 업체 선정 기준 → 견적 가이드'
            }
        }

        template = persona_templates.get(row['persona_id'], {
            'tone': '정보 전달 중심의 중립적 톤',
            'content_type': '일반 정보 제공',
            'structure': '주제 소개 → 상세 정보 → 관련 정보 → 마무리'
        })

        prompt = f"""# 블로그 포스팅 작성 요청

## 키워드 정보
- **타겟 키워드**: {keyword}
- **월간 검색량**: {volume:,}회
- **경쟁 정도**: {competition}
- **광고 경쟁도**: {row['avg_ad_count']}개 광고

## 고객 페르소나 분석
- **페르소나**: {persona_name}
- **고객 특징**: {characteristics}
- **고객 설명**: {description}

## 콘텐츠 전략
- **콘텐츠 타입**: {template['content_type']}
- **톤앤매너**: {template['tone']}
- **추천 전략**: {content_strategy}

## 작성 요구사항

### 글 구조
{template['structure']}

### SEO 최적화
- 제목에 타겟 키워드 포함 (자연스럽게)
- 본문에 키워드 5-7회 자연스럽게 포함
- 소제목(H2, H3)에 관련 키워드 활용
- 메타 설명 제안 (150자 이내)

### 글 길이 및 형식
- **총 길이**: 1,500-2,000자
- **도입부**: 200-300자 (검색 의도 공감 및 문제 제기)
- **본문**: 1,000-1,500자 (구체적 정보 및 솔루션 제공)
- **마무리**: 200-300자 (요약 및 행동 유도)

### 콘텐츠 품질 기준
1. **검색 의도 충족**: 사용자가 이 키워드로 검색한 이유를 정확히 파악하고 답변
2. **정보의 정확성**: 사실에 기반한 정보 제공 (추측이나 과장 금지)
3. **실용성**: 독자가 바로 활용할 수 있는 구체적인 정보
4. **신뢰성**: 전문적이면서도 이해하기 쉬운 설명
5. **행동 유도**: 다음 단계로의 자연스러운 유도 (구매, 상담, 추가 정보 탐색 등)

### 페르소나별 핵심 포인트
{self._get_persona_specific_points(row['persona_id'])}

## 출력 형식

```markdown
# [SEO 최적화된 제목]

[도입부: 검색 의도 공감 및 문제 제기]

## [소제목 1]
[본문 내용]

## [소제목 2]
[본문 내용]

## [소제목 3]
[본문 내용]

[마무리: 요약 및 행동 유도]

---
**메타 설명**: [150자 이내 요약]
**추천 태그**: #태그1 #태그2 #태그3
```

위 정보를 바탕으로 '{keyword}' 키워드에 최적화된 블로그 포스팅을 작성해주세요.
"""

        return prompt

    def _get_persona_specific_points(self, persona_id: int) -> str:
        """페르소나별 핵심 포인트 생성"""
        points = {
            1: """
- 제품 비교 시 가격대별, 용도별로 구분하여 설명
- 실제 사용 후기나 경험 기반 추천
- 구매 시 고려사항 및 주의점 강조
- "추천", "베스트", "TOP" 등의 표현 활용
""",
            2: """
- 단계별로 명확한 설치 가이드 제공
- 필요한 도구 및 준비물 명시
- 사진이나 도식으로 설명 가능한 부분 표시
- 초보자도 따라할 수 있는 쉬운 설명
- 흔한 실수 및 해결 방법 포함
""",
            3: """
- 객관적인 업체 비교 (가격, 서비스, 고객 평가)
- 각 업체의 장단점 명확히 제시
- 고객센터, A/S 정보 등 실용 정보 포함
- 계약 시 주의사항 안내
""",
            4: """
- 기술 사양 및 스펙 상세 설명
- 비즈니스 규모별 추천 시스템
- 설치 견적 산출 방법 안내
- ROI 및 비용 대비 효과 분석
- 관련 법규나 규제 정보 포함
"""
        }
        return points.get(persona_id, "- 정확하고 유용한 정보 제공\n- 독자의 검색 의도 충족")

    def export_keyword_list_for_posting(self, filename: str = "posting_keywords.csv"):
        """
        블로그 포스팅용 키워드 리스트 CSV 출력

        Args:
            filename: 출력 파일명
        """
        import csv

        keywords = self.get_recommended_keywords_for_posting(limit=50)

        output_path = Path("/home/tlswk/careon/data/customers/cctv/keyword") / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'keyword', 'persona_name', 'search_volume_total',
                'competition_level', 'priority_score'
            ], extrasaction='ignore')
            writer.writeheader()
            writer.writerows(keywords)

        print(f"✅ 키워드 리스트 출력 완료: {output_path}")
        return output_path


def main():
    """메인 함수"""
    helper = BlogAutomationHelper()

    print("=" * 80)
    print("블로그 포스팅 자동화 헬퍼")
    print("=" * 80)

    # 1. 추천 키워드 TOP 20 조회
    print("\n📊 블로그 포스팅 추천 키워드 TOP 20\n")

    keywords = helper.get_recommended_keywords_for_posting(limit=20)

    print(f"{'순위':<4} {'키워드':<20} {'페르소나':<25} {'검색량':<10} {'경쟁':<6} {'우선순위':<8}")
    print("-" * 100)

    for i, kw in enumerate(keywords, 1):
        print(f"{i:<4} {kw['keyword']:<20} {kw['persona_name']:<25} "
              f"{kw['search_volume_total']:>8,}회  {kw['competition_level']:<6} "
              f"{kw['priority_score']:>6.1f}점")

    # 2. 샘플 프롬프트 생성 (1위 키워드)
    if keywords:
        print("\n" + "=" * 80)
        print(f"샘플 프롬프트 생성: '{keywords[0]['keyword']}'")
        print("=" * 80)

        prompt = helper.generate_blog_prompt(keywords[0]['keyword_id'])
        print(prompt)

    # 3. CSV 출력
    print("\n" + "=" * 80)
    helper.export_keyword_list_for_posting()


if __name__ == "__main__":
    main()
