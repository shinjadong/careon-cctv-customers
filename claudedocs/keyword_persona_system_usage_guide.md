# 키워드 페르소나 시스템 사용 가이드

## 🎯 시스템 개요

블로그 포스팅 자동화를 위한 키워드-페르소나 매핑 및 시계열 추적 시스템이 구축되었습니다.

### 주요 기능

1. **고객 페르소나 분류**: 5가지 페르소나로 키워드 자동 분류
2. **시계열 추적**: 일자별 키워드 검색량 변화 추적
3. **우선순위 계산**: 블로그 포스팅 우선순위 자동 계산
4. **프롬프트 생성**: 페르소나 맞춤형 AI 블로그 작성 프롬프트 자동 생성

## 📊 데이터베이스 구조

### 위치
```
/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db
```

### 주요 테이블

1. **customer_personas**: 고객 페르소나 마스터 (5개)
2. **keywords_master**: 키워드 마스터 (1,692개)
3. **keyword_timeseries**: 시계열 데이터 (일자별 검색량)
4. **keyword_changes**: 변화 분석 (트렌드)
5. **blog_posts**: 블로그 포스팅 이력

### 페르소나 분류

| ID | 페르소나명 | 설명 | 키워드 수 |
|----|-----------|------|----------|
| 1 | 홈캠 비교 고객 | 홈캠 추천 비교를 원하는 개인 고객 | 253개 |
| 2 | DIY 고객 | 홈캠/CCTV 셀프 설치를 원하는 소규모 B2B | 104개 |
| 3 | 보안업체 비교 고객 | 에스원, 캡스, KT텔레캅 등 업체 비교 | 283개 |
| 4 | B2B CCTV 고객 | CCTV 설치 원하는 B2B (부가서비스 불필요) | 270개 |
| 5 | 기타/해당없음 | 위 분류에 속하지 않는 키워드 | 782개 |

### 검색량 통계 (2025-11-20 기준)

| 페르소나 | 키워드 수 | 총 검색량 |
|---------|----------|----------|
| 기타/해당없음 | 782개 | 797,200회 |
| 보안업체 비교 고객 | 283개 | 796,630회 |
| 홈캠 비교 고객 | 253개 | 222,430회 |
| B2B CCTV 고객 | 270개 | 84,730회 |
| DIY 고객 | 104개 | 12,740회 |

## 🚀 사용 방법

### 1. 블로그 포스팅 추천 키워드 조회

```bash
python3 scripts/blog_automation_helper.py
```

**출력 예시:**
```
순위   키워드                  페르소나                      검색량        경쟁     우선순위
1    캡스고객센터               보안업체 비교 고객              20,030회  낮음       88.0점
2    KT                   보안업체 비교 고객             635,700회  높음       77.0점
3    홈캠                   홈캠 비교 고객                73,400회  높음       77.0점
...
```

### 2. AI 블로그 프롬프트 생성

스크립트를 실행하면 1위 키워드에 대한 샘플 프롬프트가 자동 생성됩니다.

**프롬프트 구성:**
- 키워드 정보 (검색량, 경쟁도)
- 고객 페르소나 분석
- 콘텐츠 전략
- SEO 최적화 가이드
- 페르소나별 핵심 포인트

### 3. 키워드 리스트 CSV 출력

```
/home/tlswk/careon/data/customers/cctv/keyword/posting_keywords.csv
```

TOP 50 추천 키워드가 CSV로 출력됩니다.

## 📈 우선순위 계산 로직

블로그 포스팅 우선순위는 다음 요소를 기반으로 계산됩니다:

### 점수 배분 (총 100점)

1. **검색량 (40점)**
   - 50,000회 이상: 40점
   - 10,000~50,000회: 35점
   - 5,000~10,000회: 30점
   - 1,000~5,000회: 20점
   - 1,000회 미만: 10점

2. **경쟁 정도 (30점)**
   - 낮음: 30점
   - 중간: 20점
   - 높음: 10점

3. **페르소나 신뢰도 (20점)**
   - 자동 라벨링 신뢰도 기반 (0.0 ~ 1.0)
   - 점수 = 신뢰도 × 20

4. **광고 수 (10점)**
   - 10개 이상: 10점
   - 7~9개: 7점
   - 5~6개: 5점
   - 5개 미만: 3점

## 🔄 데이터 업데이트 워크플로우

### 일일 업데이트 (예정)

```bash
# 1. 신규 키워드 데이터 수집
python3 scripts/collect_keyword_data.py --date 2025-11-21

# 2. 자동 라벨링
python3 scripts/auto_label_keywords.py

# 3. 시계열 데이터 저장
python3 scripts/update_timeseries.py --date 2025-11-21

# 4. 트렌드 분석
python3 scripts/analyze_trends.py --period 7

# 5. 포스팅 추천
python3 scripts/blog_automation_helper.py
```

## 💡 페르소나별 콘텐츠 전략

### 1. 홈캠 비교 고객

**콘텐츠 타입:**
- 제품 비교 리뷰
- TOP 10 추천
- 가격대별 추천
- 용도별 추천

**톤앤매너:**
- 친근하고 상세한 비교 톤

**핵심 포인트:**
- 제품 비교 시 가격대별, 용도별로 구분
- 실제 사용 후기나 경험 기반 추천
- 구매 시 고려사항 및 주의점 강조

**예시 키워드:**
- 홈캠, 홈캠추천, 펫캠, 무선CCTV, 현관CCTV

### 2. DIY 고객

**콘텐츠 타입:**
- 설치 가이드
- DIY 튜토리얼
- 제품 세트 추천
- 셀프 설치 팁

**톤앤매너:**
- 실용적이고 구체적인 가이드 톤

**핵심 포인트:**
- 단계별로 명확한 설치 가이드 제공
- 필요한 도구 및 준비물 명시
- 초보자도 따라할 수 있는 쉬운 설명
- 흔한 실수 및 해결 방법 포함

**예시 키워드:**
- CCTV설치, 설치방법, DIY, 자가설치, CCTV세트

### 3. 보안업체 비교 고객

**콘텐츠 타입:**
- 업체 비교
- 가격 비교
- 서비스 분석
- 고객센터 정보

**톤앤매너:**
- 객관적이고 전문적인 비교 톤

**핵심 포인트:**
- 객관적인 업체 비교 (가격, 서비스, 고객 평가)
- 각 업체의 장단점 명확히 제시
- 고객센터, A/S 정보 등 실용 정보 포함
- 계약 시 주의사항 안내

**예시 키워드:**
- KT, 캡스, 에스원, 세콤, ADT, 텔레캅, 캡스고객센터

### 4. B2B CCTV 고객

**콘텐츠 타입:**
- 업체 견적 가이드
- 설치 업체 비교
- 기술 스펙 분석
- 대량 구매 정보

**톤앤매너:**
- 전문적이고 기술적인 톤

**핵심 포인트:**
- 기술 사양 및 스펙 상세 설명
- 비즈니스 규모별 추천 시스템
- 설치 견적 산출 방법 안내
- ROI 및 비용 대비 효과 분석

**예시 키워드:**
- CCTV설치업체, 견적, NVR, DVR, IP카메라

## 🛠️ 스크립트 목록

### 1. setup_keyword_persona_db.py
- **기능**: DB 초기화 및 페르소나 테이블 생성
- **실행**: `python3 scripts/setup_keyword_persona_db.py`

### 2. migrate_keyword_data.py
- **기능**: 기존 엑셀 데이터를 DB로 마이그레이션
- **실행**: `python3 scripts/migrate_keyword_data.py`

### 3. blog_automation_helper.py
- **기능**: 블로그 포스팅 추천 및 프롬프트 생성
- **실행**: `python3 scripts/blog_automation_helper.py`

## 📝 Python API 사용 예시

```python
from scripts.blog_automation_helper import BlogAutomationHelper

# 헬퍼 초기화
helper = BlogAutomationHelper()

# TOP 10 추천 키워드 조회
keywords = helper.get_recommended_keywords_for_posting(limit=10)

for kw in keywords:
    print(f"{kw['keyword']}: {kw['priority_score']}점")

# 특정 키워드의 프롬프트 생성
keyword_id = keywords[0]['keyword_id']
prompt = helper.generate_blog_prompt(keyword_id)
print(prompt)

# CSV 출력
helper.export_keyword_list_for_posting("my_keywords.csv")
```

## 🔮 향후 개선 계획

### Phase 2: 시계열 추적 강화
- [ ] 일일 자동 데이터 수집 스크립트
- [ ] 트렌드 분석 및 알림 시스템
- [ ] 변화율 기반 긴급 포스팅 추천

### Phase 3: AI 통합
- [ ] AI 블로그 자동 생성 (Claude API)
- [ ] 포스팅 성과 추적 및 피드백
- [ ] 라벨링 정확도 자동 개선

### Phase 4: 대시보드
- [ ] 웹 대시보드 구축
- [ ] 실시간 키워드 모니터링
- [ ] 포스팅 스케줄 관리

## ❓ FAQ

### Q1: 새로운 키워드 데이터를 추가하려면?

```python
# migrate_keyword_data.py 스크립트 수정
# INTEGRATED_FILE 경로를 새 파일로 변경
# 실행: python3 scripts/migrate_keyword_data.py
```

### Q2: 페르소나 분류를 수정하려면?

```sql
-- DB에 직접 접근
sqlite3 /home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db

-- 키워드 페르소나 변경
UPDATE keywords_master
SET persona_id = 1, labeling_method = 'manual'
WHERE keyword = '홈캠';
```

### Q3: 자동 라벨링 규칙을 수정하려면?

`migrate_keyword_data.py`의 `auto_label_keyword()` 함수 수정

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:
1. 시스템 설계 문서: `/home/tlswk/careon/claudedocs/keyword_persona_system_design.md`
2. 이 사용 가이드: `/home/tlswk/careon/claudedocs/keyword_persona_system_usage_guide.md`
3. DB 위치: `/home/tlswk/careon/data/customers/cctv/keyword/keyword_persona.db`
