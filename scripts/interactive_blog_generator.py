#!/usr/bin/env python3
"""
인터랙티브 블로그 원고 생성기
페르소나 선택 → 키워드 추천 → 원고 제목 & 본문 프롬프트 생성
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")


class InteractiveBlogGenerator:
    """인터랙티브 블로그 생성기"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_sub_personas(self) -> List[Dict]:
        """세부 페르소나 목록 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT sub_persona_id, sub_persona_name, description,
                   priority_level, content_strategy
            FROM sub_personas
            ORDER BY sub_persona_id
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_keywords_by_sub_persona(self, sub_persona_id: str, limit: int = 10) -> List[Dict]:
        """세부 페르소나별 키워드 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT k.keyword_id, k.keyword, k.confidence_score,
                   kt.search_volume_total, kt.competition_level, kt.avg_ad_count
            FROM keywords_master k
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE k.sub_persona_id = ?
            AND kt.search_volume_total > 0
            ORDER BY kt.search_volume_total DESC
            LIMIT ?
        """, (sub_persona_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def generate_un_carrier_prompt(self, keyword: str, search_volume: int) -> str:
        """
        🔥 3-2 전용: 위약금 해방(Un-carrier) 전략 프롬프트
        """
        return f"""# 🔥 위약금 해방 캠페인 블로그 작성 요청

## 타겟 키워드
**메인 키워드**: {keyword}
**월간 검색량**: {search_volume:,}회
**고객 상태**: 이탈/고통 단계 (🔥 최우선 타겟)

## 고객 페르소나 분석
**현재 상황**: 기존 보안업체(캡스, 세콤, KT텔레캅 등)에 불만이 있거나, 위약금 문제로 갇혀있는 고객

**고객의 고통**:
- 기존 업체 서비스에 불만 (응답 느림, AS 부실, 요금 비쌈)
- 갈아타고 싶지만 **위약금 폭탄(50~60만 원)**이 무서움
- "내가 바보같이 36개월 약정을 했구나..." 후회
- "도대체 어디로 갈아타야 하지?" 막막함

## 🎯 케어온 Un-carrier 전략

### Hook (낚시바늘)
"사장님, 그 위약금 저희가 부담하겠습니다."

### 핵심 메시지
1. **위약금 공포 공감**: "50만 원 위약금, 누가 낼 수 있나요?"
2. **케어온 솔루션**: "위약금 명세서만 주세요. 최대 50만 원 지원"
3. **실제 혜택**: 기존 장비 반납 + 케어온 36개월 신규 계약 = 위약금 월할부 차감
4. **차별점**: 대기업이 절대 못하는, 중소기업만의 혁신적 서비스

### 작성 구조

#### 1. 도입부 (300자) - 고통 공감
```
"{keyword}"를 검색하셨다는 것은...
[기존 업체에 대한 불만/위약금 고민 구체화]
사장님, 혼자 고민하지 마세요.
```

#### 2. 본문 1 - 문제의 실체 (400자)
```
## 왜 보안업체 위약금은 이렇게 비쌀까?

- 36개월 약정의 함정
- 중도 해지 시 장비 철거비 + 남은 기간 위약금
- 실제 사례: "24개월 남았는데 58만 원 청구"
```

#### 3. 본문 2 - 케어온 솔루션 (500자)
```
## 케어온의 파격 제안: "위약금 해방"

### 이렇게 진행됩니다
1. 기존 업체 위약금 명세서 받기
2. 케어온에 제출
3. 케어온 신규 계약 체결 (36개월)
4. **위약금 최대 50만 원을 월 렌탈료에서 차감**

### 실제 예시
- 기존 위약금: 48만 원
- 케어온 월 렌탈료: 15,000원
- 지원 방식: 48개월 동안 매월 10,000원씩 차감
- **실제 부담: 월 5,000원 (정상 15,000원)**
```

#### 4. 본문 3 - 신뢰 구축 (300자)
```
## 왜 케어온은 이런 파격 혜택이 가능한가?

- 대기업 마진(30~40%)이 없는 직영 시스템
- 장기 고객 확보를 통한 안정적 수익 구조
- "고객이 바뀌면 시장이 바뀐다" 철학
```

#### 5. 마무리 - 행동 유도 (200자)
```
## 지금 바로 상담받기

- 무료 위약금 계산: [링크]
- 카카오톡 상담: [링크]
- 전화 상담: 1588-XXXX

**"이제 위약금 때문에 참지 마세요."**
```

## SEO 최적화
- 제목: "{keyword} 해결? 케어온 위약금 해방 프로그램"
- 메타 설명: "보안업체 위약금 때문에 갇혀계신가요? 케어온이 최대 50만 원 지원해드립니다. 지금 바로 상담받으세요."
- 키워드 밀도: 본문에 5-7회 자연스럽게 포함
- 소제목(H2, H3) 활용

## ⚠️ 주의사항
1. **과장 금지**: 실제 지원 가능한 금액과 조건을 명확히
2. **법적 검토**: 위약금 대납 관련 법적 이슈 확인 필요
3. **투명성**: 케어온 약정 조건도 명확히 안내
4. **톤 조절**: 공격적이지 않고 따뜻하게 공감하는 톤

## 📊 예상 효과
- **타겟**: 위약금 때문에 갇혀있던 잠재 고객 직격탄
- **차별화**: 경쟁사가 절대 못하는 전략
- **전환율**: 일반 포스팅 대비 3~5배 예상

---

위 전략을 바탕으로 '{keyword}' 키워드에 최적화된 **위약금 해방 캠페인** 블로그를 작성해주세요.
"""

    def generate_standard_prompt(self, keyword: str, sub_persona_id: str,
                                  persona_info: Dict, search_volume: int) -> str:
        """일반 페르소나용 프롬프트"""

        content_strategies = {
            '1-1': {
                'type': '제품 비교 & 추천',
                'structure': '도입부(고민 공감) → 비교 기준 → TOP 제품 비교 → 추천 및 구매 가이드',
                'tone': '친근하고 상세한 비교 톤'
            },
            '2-1': {
                'type': 'DIY 설치 가이드',
                'structure': '필요성 설명 → 준비물 → 단계별 설치 가이드 → 팁 및 주의사항',
                'tone': '실용적이고 구체적인 가이드 톤'
            },
            '3-1': {
                'type': '업체 비교 분석',
                'structure': '업체 소개 → 가격/서비스 비교 → 장단점 분석 → 선택 가이드',
                'tone': '객관적이고 전문적인 비교 톤'
            },
            '4-1': {
                'type': 'B2B 기술 스펙 & 견적 가이드',
                'structure': '비즈니스 니즈 분석 → 기술 사양 → 업체 선정 기준 → 견적 가이드',
                'tone': '전문적이고 기술적인 톤'
            },
            '5-1': {
                'type': '일반 정보 제공',
                'structure': '주제 소개 → 상세 정보 → 관련 정보 → 마무리',
                'tone': '중립적이고 정보 전달 중심의 톤'
            }
        }

        strategy = content_strategies.get(sub_persona_id, content_strategies['5-1'])

        return f"""# 블로그 포스팅 작성 요청

## 타겟 키워드
**메인 키워드**: {keyword}
**월간 검색량**: {search_volume:,}회
**세부 페르소나**: {sub_persona_id} - {persona_info['sub_persona_name']}

## 고객 페르소나 분석
**고객 설명**: {persona_info['description']}
**콘텐츠 전략**: {persona_info['content_strategy']}

## 작성 전략
**콘텐츠 타입**: {strategy['type']}
**톤앤매너**: {strategy['tone']}
**구조**: {strategy['structure']}

## 작성 요구사항

### 글 구조
{strategy['structure']}

### SEO 최적화
- 제목에 타겟 키워드 자연스럽게 포함
- 본문에 키워드 5-7회 자연스럽게 포함
- 소제목(H2, H3)에 관련 키워드 활용
- 메타 설명 제안 (150자 이내)

### 글 길이 및 형식
- **총 길이**: 1,500-2,000자
- **도입부**: 200-300자 (검색 의도 공감)
- **본문**: 1,000-1,500자 (구체적 정보 제공)
- **마무리**: 200-300자 (요약 및 행동 유도)

### 품질 기준
1. 검색 의도 정확히 충족
2. 사실 기반 정보 (추측/과장 금지)
3. 즉시 활용 가능한 실용 정보
4. 전문적이면서 이해하기 쉬운 설명
5. 자연스러운 행동 유도

## 출력 형식

```markdown
# [SEO 최적화된 제목]

[도입부]

## [소제목 1]
[본문 내용]

## [소제목 2]
[본문 내용]

## [소제목 3]
[본문 내용]

[마무리]

---
**메타 설명**: [150자 이내]
**추천 태그**: #태그1 #태그2 #태그3
```

위 정보를 바탕으로 '{keyword}' 키워드에 최적화된 블로그를 작성해주세요.
"""

    def run_interactive(self):
        """인터랙티브 모드 실행"""

        print("=" * 80)
        print("🚀 케어온 블로그 자동 생성기")
        print("=" * 80)

        # Step 1: 세부 페르소나 선택
        print("\n📋 세부 페르소나 목록:\n")

        personas = self.get_sub_personas()

        for i, p in enumerate(personas, 1):
            priority_icon = "🔥" if p['priority_level'] == "CRITICAL" else "📌"
            print(f"   {i}. {priority_icon} {p['sub_persona_id']}: {p['sub_persona_name']}")
            print(f"      {p['description']}")
            print()

        # 페르소나 선택
        while True:
            try:
                choice = input("선택할 페르소나 번호 (1-6) 또는 ID (예: 3-2): ").strip()

                # 번호 입력
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(personas):
                        selected_persona = personas[idx]
                        break
                # ID 입력
                else:
                    selected_persona = next((p for p in personas if p['sub_persona_id'] == choice), None)
                    if selected_persona:
                        break

                print("❌ 잘못된 입력입니다. 다시 시도하세요.")
            except KeyboardInterrupt:
                print("\n\n👋 종료합니다.")
                return

        sub_persona_id = selected_persona['sub_persona_id']

        print(f"\n✅ 선택: {sub_persona_id} - {selected_persona['sub_persona_name']}")

        # Step 2: 키워드 조회
        print(f"\n🔍 {sub_persona_id} 키워드 TOP 10 조회 중...\n")

        keywords = self.get_keywords_by_sub_persona(sub_persona_id, limit=10)

        if not keywords:
            print(f"⚠️  {sub_persona_id}에 해당하는 키워드가 없습니다.")
            return

        print(f"{'번호':<4} {'키워드':<30} {'월간 검색량':>15} {'경쟁도':<6}")
        print("-" * 60)

        for i, kw in enumerate(keywords, 1):
            volume = kw['search_volume_total'] if kw['search_volume_total'] else 0
            competition = kw['competition_level'] if kw['competition_level'] else '중간'
            print(f"{i:<4} {kw['keyword']:<30} {volume:>13,}회  {competition:<6}")

        # 키워드 선택
        while True:
            try:
                kw_choice = input(f"\n선택할 키워드 번호 (1-{len(keywords)}): ").strip()
                kw_idx = int(kw_choice) - 1
                if 0 <= kw_idx < len(keywords):
                    selected_keyword = keywords[kw_idx]
                    break
                print("❌ 잘못된 번호입니다.")
            except (ValueError, KeyboardInterrupt):
                print("\n\n👋 종료합니다.")
                return

        print(f"\n✅ 선택: {selected_keyword['keyword']} ({selected_keyword['search_volume_total']:,}회)")

        # Step 3: 프롬프트 생성
        print("\n" + "=" * 80)
        print("📝 블로그 원고 프롬프트 생성 중...")
        print("=" * 80 + "\n")

        keyword = selected_keyword['keyword']
        volume = selected_keyword['search_volume_total'] if selected_keyword['search_volume_total'] else 0

        # 3-2는 특별 프롬프트
        if sub_persona_id == '3-2':
            prompt = self.generate_un_carrier_prompt(keyword, volume)
        else:
            prompt = self.generate_standard_prompt(keyword, sub_persona_id, selected_persona, volume)

        print(prompt)

        # Step 4: 저장 옵션
        save = input("\n💾 프롬프트를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"blog_prompt_{sub_persona_id}_{keyword.replace(' ', '_')}.txt"
            output_path = Path("/home/tlswk/careon/data/customers/cctv/keyword") / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prompt)

            print(f"✅ 저장 완료: {output_path}")

        print("\n" + "=" * 80)
        print("✅ 완료! 위 프롬프트를 Claude/ChatGPT에 붙여넣으세요.")
        print("=" * 80)


def main():
    """메인 함수"""
    generator = InteractiveBlogGenerator()
    generator.run_interactive()


if __name__ == "__main__":
    main()
