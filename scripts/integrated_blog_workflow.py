#!/usr/bin/env python3
"""
통합 블로그 워크플로우
블로그 에이전트 + 카피라이터 에이전트 협업 시스템
"""

import sqlite3
from pathlib import Path
from typing import Dict, List
import json

DB_PATH = Path("/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db")


class IntegratedBlogWorkflow:
    """통합 블로그 워크플로우 시스템"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_keyword_full_context(self, keyword_id: int) -> Dict:
        """키워드의 전체 컨텍스트 조회"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT k.keyword, k.sub_persona_id,
                   sp.sub_persona_name, sp.description, sp.content_strategy,
                   sp.template_id, sp.landing_url, sp.funnel_strategy, sp.cta_text,
                   sp.priority_level,
                   kt.search_volume_total, kt.competition_level, kt.avg_ad_count
            FROM keywords_master k
            JOIN sub_personas sp ON k.sub_persona_id = sp.sub_persona_id
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE k.keyword_id = ?
        """, (keyword_id,))

        row = cursor.fetchone()
        return dict(row) if row else {}

    def generate_copywriter_request_prompt(self, context: Dict) -> str:
        """
        카피라이터 에이전트에게 보낼 제목 생성 요청 프롬프트
        (간다 마사노리 카피 단어장 활용)
        """

        keyword = context['keyword']
        sub_persona = context['sub_persona_id']
        persona_name = context['sub_persona_name']
        volume = context['search_volume_total'] if context['search_volume_total'] else 0

        # 페르소나별 페인포인트와 욕구 정의
        persona_psychology = {
            '1-1': {
                'pain_point': '아이/반려동물 안전 걱정, 해킹 불안',
                'desire': '믿을 수 있는 제품으로 가족 안전 지키기',
                'fear': '해킹당해서 사생활 노출',
                'benefit': '24시간 안심 모니터링'
            },
            '2-1': {
                'pain_point': '설치 비용 부담, 업체 의존',
                'desire': '직접 설치해서 비용 절감',
                'fear': '잘못 설치해서 작동 안 함',
                'benefit': '비용 50% 절감, 성취감'
            },
            '3-1': {
                'pain_point': '어느 업체가 나은지 모름, 가격 불투명',
                'desire': '합리적 가격에 믿을 수 있는 업체',
                'fear': '바가지, 불친절한 서비스',
                'benefit': '객관적 비교로 현명한 선택'
            },
            '3-2': {
                'pain_point': '위약금 50~60만 원 폭탄, 기존 업체 불만, AS 불만',
                'desire': '위약금 부담 없이 더 좋은 서비스로 갈아타기',
                'fear': '평생 갇혀있어야 하나, 폐업해도 위약금 내야 함',
                'benefit': '위약금 0원 + 최신 AI CCTV'
            },
            '4-1': {
                'pain_point': '견적 받기 복잡, 업체마다 가격 천차만별',
                'desire': '빠르고 정확한 견적, 믿을 수 있는 시공',
                'fear': '공사 지연, 품질 불량',
                'benefit': '전문 시공, 합리적 가격'
            },
            '5-1': {
                'pain_point': '정보 부족',
                'desire': '정확한 정보',
                'fear': '잘못된 선택',
                'benefit': '올바른 정보'
            }
        }

        psych = persona_psychology.get(sub_persona, persona_psychology['5-1'])

        # 3-2는 특별 프롬프트
        if sub_persona == '3-2':
            return f"""# 카피라이터 요청: 블로그 제목 생성 (위약금 해방 캠페인)

## 1. 타겟 정보
- **키워드**: {keyword}
- **월간 검색량**: {volume:,}회
- **페르소나**: {persona_name} (3-2 이탈/고통)
- **우선순위**: 🔥 CRITICAL (최우선 타겟)

## 2. 고객 심리 분석

### Pain Point (고통)
{psych['pain_point']}

### Desire (욕구)
{psych['desire']}

### Fear (공포)
{psych['fear']}

### Benefit (이득)
{psych['benefit']}

## 3. 핵심 오퍼 (Offer)

**케어온 Un-carrier (위약금 해방) 전략**:
- 위약금 최대 50만 원 전액 지원
- 기존 장비 무상 철거 및 수거
- 월 렌탈료에서 차감 방식 (현금 지급 X)
- 조건: 케어온 36개월 신규 계약

**실제 예시**:
```
기존 위약금: 48만 원
케어온 월 렌탈료: 15,000원
지원 방식: 매월 10,000원씩 차감 (48개월)
실제 부담: 월 5,000원
```

## 4. 고객 여정 (Funnel)
```
블로그 검색 → 공포/해결 후킹 → CTA 클릭
→ 위약금 계산기 (/penalty-calculator)
→ "48만 원 지원 가능!" 결과
→ 안심케어플랜 랜딩 → 상담 신청
```

**CTA 텍스트**: "{context['cta_text']}"

## 5. 요청 사항

간다 마사노리의 '무조건 팔리는 카피 단어장' 기법을 활용하여,
다음 **3가지 유형**의 클릭을 부르는 블로그 제목을 **각 5개씩** 뽑아주세요.

### Type 1: [공포/문제 제기]
- 위약금 및 숨겨진 비용(철거비, 설치비 반환)을 찔러 위기감 조성
- "모르면 손해", "함정", "폭탄" 등의 단어 활용
- 고객이 "나 얘기네?" 하고 클릭하게 만들기

**예시**:
- "캡스 해지 위약금 54만 원? 이거 '설치비' 확인 안 하면 다 토해냅니다"
- "폐업해도 50만 원 뜯어가는 보안업체? 위약금 10%의 함정"

### Type 2: [이득/해결책]
- 위약금 대납 및 금전적 혜택을 직관적으로 제시
- "무료", "0원", "전액 지원" 등 강력한 오퍼 단어 사용
- 구체적 숫자로 신뢰도 확보

**예시**:
- "아직도 위약금 걱정하세요? 케어온이 50만 원 대신 내드립니다"
- "위약금 영수증만 찍어 보내세요. 0원으로 만들어 드립니다"

### Type 3: [타겟 필터링]
- "캡스/세콤 해지 고민 중인 사장님"을 콕 집어 호기심 유발
- "~라면", "~하는 분께" 등으로 타게팅
- 질문형 + 프라이밍 효과

**예시**:
- "[사장님 필독] 캡스 약정 남았는데 바꾸고 싶다면? '이것'만 확인하세요"
- "보안업체 위약금 때문에 참고 계신 분들께 (ft. 50만 원 지원)"

## 6. 제약 조건
- **플랫폼**: 네이버 블로그
- **제목 길이**: 30~50자 (모바일 노출 고려)
- **톤**: 공감하면서도 전문가적 해결책 제시
- **금지 단어**: 과장 표현 (100% 보장, 절대 등)

---

위 정보를 바탕으로 **총 15개 제목** (각 유형별 5개)을 생성해주세요.
"""

        # 일반 페르소나 프롬프트
        return f"""# 카피라이터 요청: 블로그 제목 생성

## 1. 타겟 정보
- **키워드**: {keyword}
- **월간 검색량**: {volume:,}회
- **페르소나**: {persona_name} ({sub_persona})

## 2. 고객 심리 분석

### Pain Point (고통)
{psych['pain_point']}

### Desire (욕구)
{psych['desire']}

### Fear (공포)
{psych['fear']}

### Benefit (이득)
{psych['benefit']}

## 3. 콘텐츠 전략
{context['content_strategy']}

## 4. 고객 여정 (Funnel)
```
블로그 검색 → 가치 제공 → CTA 클릭
→ {context['template_id']} ({context['landing_url']})
```

**CTA 텍스트**: "{context['cta_text']}"

## 5. 요청 사항

간다 마사노리의 '무조건 팔리는 카피 단어장' 기법을 활용하여,
다음 **3가지 유형**의 클릭을 부르는 블로그 제목을 **각 5개씩** 뽑아주세요.

### Type 1: [문제 제기/공감]
- 고객의 페인포인트를 정확히 찔러 "나 얘기네?" 반응 유도

### Type 2: [이득/솔루션]
- 얻을 수 있는 구체적 이득과 해결책 제시

### Type 3: [호기심/타겟팅]
- 특정 타겟을 필터링하면서 호기심 유발

## 6. 제약 조건
- **플랫폼**: 네이버 블로그
- **제목 길이**: 30~50자
- **톤**: 전문적이면서 친근한 톤

---

위 정보를 바탕으로 **총 15개 제목** (각 유형별 5개)을 생성해주세요.
"""

    def generate_full_blog_prompt(self, keyword_id: int) -> Dict:
        """
        완전한 블로그 작성 프롬프트 생성
        (제목 생성용 + 본문 작성용 분리)
        """

        context = self.get_keyword_full_context(keyword_id)

        if not context:
            return {}

        # 1. 카피라이터용 제목 생성 프롬프트
        title_prompt = self.generate_copywriter_request_prompt(context)

        # 2. 블로그 본문 작성 프롬프트
        if context['sub_persona_id'] == '3-2':
            body_prompt = self._generate_3_2_body_prompt(context)
        else:
            body_prompt = self._generate_standard_body_prompt(context)

        return {
            'keyword': context['keyword'],
            'sub_persona_id': context['sub_persona_id'],
            'persona_name': context['sub_persona_name'],
            'search_volume': context['search_volume_total'],
            'template_id': context['template_id'],
            'landing_url': context['landing_url'],
            'cta_text': context['cta_text'],
            'title_generation_prompt': title_prompt,
            'body_generation_prompt': body_prompt
        }

    def _generate_3_2_body_prompt(self, context: Dict) -> str:
        """3-2 전용 본문 생성 프롬프트"""
        return f"""# 블로그 본문 작성 요청 (위약금 해방 캠페인)

## 사전 작업
- 카피라이터 에이전트로부터 **15개 제목 후보** 받음
- 그 중 **가장 강력한 제목 1개** 선택 완료

## 본문 작성 가이드

### 구조 (총 1,500~2,000자)

#### 1. 도입부 (300자) - 고통 공감
```
[선택한 제목과 연결되는 문제 상황 묘사]

"{context['keyword']}"를 검색하셨다는 것은...
- 기존 업체 서비스에 불만이 있거나
- 위약금 때문에 해지를 망설이고 계시거나
- 고객센터 전화가 안 받혀서 답답하시거나

사장님, 혼자 고민하지 마세요.
```

#### 2. 본문 1 - 문제의 실체 (400자)
```
## 왜 보안업체 위약금은 이렇게 비쌀까?

- **36개월 약정의 함정**: 처음엔 싸다고 했는데...
- **중도 해지의 충격**: 위약금 10% + 설치비 반환 + 철거비
- **실제 사례**: "24개월 남았는데 58만 원 청구받았습니다"

[구체적 계산 예시 포함]
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
- **실제 부담: 월 5,000원**

[계산기 이미지나 표 삽입 권장]
```

#### 4. 본문 3 - 신뢰 구축 (300자)
```
## 왜 케어온은 이런 파격 혜택이 가능한가?

- **직영 시스템**: 대기업 마진(30~40%) 없음
- **장기 관점**: 고객과 함께 성장하는 철학
- **증명**: [실제 지원 사례 또는 자격증 이미지]
```

#### 5. 마무리 - 행동 유도 (200자)
```
## 지금 바로 상담받기

**CTA**: {context['cta_text']}
**링크**: {context['landing_url']}

추가:
- 카카오톡 상담: [링크]
- 전화 상담: 1588-XXXX

**"이제 위약금 때문에 참지 마세요."**
```

### SEO 최적화
- 키워드 '{context['keyword']}' 본문에 5-7회 자연스럽게 포함
- H2, H3 소제목에 관련 키워드 활용
- 메타 설명 (150자): "보안업체 위약금 때문에 갇혀계신가요? 케어온이 최대 50만 원 지원해드립니다"

### ⚠️ 주의사항
1. **과장 금지**: 실제 지원 가능 금액만
2. **투명성**: 케어온 약정 조건도 명시
3. **톤**: 공격적이지 않고 따뜻하게

---

위 가이드를 바탕으로 '{context['keyword']}' 블로그 본문을 작성해주세요.
"""

    def _generate_standard_body_prompt(self, context: Dict) -> str:
        """일반 페르소나 본문 생성 프롬프트"""
        return f"""# 블로그 본문 작성 요청

## 사전 작업
- 카피라이터 에이전트로부터 **15개 제목 후보** 받음
- 그 중 **가장 강력한 제목 1개** 선택 완료

## 타겟 정보
- **키워드**: {context['keyword']}
- **페르소나**: {context['persona_name']}
- **콘텐츠 전략**: {context['content_strategy']}

## 본문 구조 (1,500~2,000자)

1. **도입부** (200-300자): 검색 의도 공감
2. **본문** (1,000-1,500자): 구체적 정보 및 솔루션
3. **마무리** (200-300자): 요약 및 행동 유도

## CTA (행동 유도)
- **버튼 텍스트**: {context['cta_text']}
- **링크**: {context['landing_url']}
- **퍼널 전략**: {context['funnel_strategy']}

## SEO 최적화
- 키워드 '{context['keyword']}' 5-7회 자연스럽게 포함
- 메타 설명 150자 이내

---

위 가이드를 바탕으로 '{context['keyword']}' 블로그 본문을 작성해주세요.
"""

    def run_interactive_workflow(self):
        """인터랙티브 워크플로우 실행"""

        print("=" * 80)
        print("🚀 케어온 통합 블로그 워크플로우")
        print("=" * 80)

        # Step 1: 페르소나 선택
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT sub_persona_id, sub_persona_name, priority_level,
                   template_id, landing_url
            FROM sub_personas
            ORDER BY sub_persona_id
        """)

        personas = cursor.fetchall()

        print("\n📋 페르소나 목록:\n")
        for i, p in enumerate(personas, 1):
            icon = "🔥" if p[2] == "CRITICAL" else "📌"
            print(f"   {i}. {icon} {p[0]}: {p[1]}")
            print(f"      템플릿: {p[3]} → {p[4]}")
            print()

        # 선택
        while True:
            try:
                choice = input("선택할 페르소나 번호 또는 ID: ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(personas):
                        selected_persona = personas[idx]
                        break
                else:
                    selected_persona = next((p for p in personas if p[0] == choice), None)
                    if selected_persona:
                        break
                print("❌ 잘못된 입력입니다.")
            except KeyboardInterrupt:
                print("\n\n👋 종료합니다.")
                return

        sub_persona_id = selected_persona[0]
        print(f"\n✅ 선택: {sub_persona_id} - {selected_persona[1]}")

        # Step 2: 키워드 선택
        cursor.execute("""
            SELECT k.keyword_id, k.keyword, kt.search_volume_total
            FROM keywords_master k
            LEFT JOIN keyword_timeseries kt ON k.keyword_id = kt.keyword_id
            WHERE k.sub_persona_id = ?
            ORDER BY kt.search_volume_total DESC
            LIMIT 10
        """, (sub_persona_id,))

        keywords = cursor.fetchall()

        if not keywords:
            print("⚠️  해당 페르소나에 키워드가 없습니다.")
            return

        print(f"\n🔍 키워드 TOP 10:\n")
        print(f"{'번호':<4} {'키워드':<30} {'월간 검색량':>15}")
        print("-" * 55)

        for i, kw in enumerate(keywords, 1):
            volume = kw[2] if kw[2] else 0
            print(f"{i:<4} {kw[1]:<30} {volume:>13,}회")

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

        keyword_id = selected_keyword[0]
        print(f"\n✅ 선택: {selected_keyword[1]}")

        # Step 3: 통합 프롬프트 생성
        print("\n" + "=" * 80)
        print("📝 통합 블로그 워크플로우 프롬프트 생성")
        print("=" * 80)

        result = self.generate_full_blog_prompt(keyword_id)

        print("\n" + "🎯" * 40)
        print("STEP 1: 카피라이터 에이전트에게 전달")
        print("🎯" * 40 + "\n")
        print(result['title_generation_prompt'])

        print("\n\n" + "📝" * 40)
        print("STEP 2: 블로그 에이전트 (본문 작성)")
        print("📝" * 40 + "\n")
        print(result['body_generation_prompt'])

        # 저장
        save = input("\n💾 프롬프트를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            base_path = Path("/home/tlswk/careon/data/customers/cctv/keyword/prompts")
            base_path.mkdir(exist_ok=True)

            keyword_safe = result['keyword'].replace(' ', '_').replace('/', '_')

            # 제목 생성용
            title_file = base_path / f"1_TITLE_{result['sub_persona_id']}_{keyword_safe}.txt"
            with open(title_file, 'w', encoding='utf-8') as f:
                f.write(result['title_generation_prompt'])

            # 본문 작성용
            body_file = base_path / f"2_BODY_{result['sub_persona_id']}_{keyword_safe}.txt"
            with open(body_file, 'w', encoding='utf-8') as f:
                f.write(result['body_generation_prompt'])

            print(f"✅ 저장 완료:")
            print(f"   제목용: {title_file}")
            print(f"   본문용: {body_file}")

        print("\n" + "=" * 80)
        print("✅ 워크플로우 완료!")
        print("=" * 80)
        print("\n📋 다음 단계:")
        print("   1. STEP 1 프롬프트를 카피라이터 Gem에 입력")
        print("   2. 생성된 15개 제목 중 1개 선택")
        print("   3. STEP 2 프롬프트를 Claude/ChatGPT에 입력 (제목 포함)")
        print("   4. 블로그 발행\n")


def main():
    workflow = IntegratedBlogWorkflow()
    workflow.run_interactive_workflow()


if __name__ == "__main__":
    main()
