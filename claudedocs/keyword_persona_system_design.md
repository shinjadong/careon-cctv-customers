# 키워드 페르소나 추적 시스템 설계

## 📋 시스템 개요

블로그 포스팅 자동화를 위한 키워드-페르소나 매핑 및 시계열 추적 시스템

## 🎯 고객 페르소나 분류 (메인 DB)

### 페르소나 정의

| ID | 페르소나명 | 설명 | 특징 |
|----|-----------|------|------|
| 1 | 홈캠 비교 고객 | 홈캠 추천 비교를 원하는 개인 고객 | 제품 비교, 리뷰, 추천 콘텐츠 선호 |
| 2 | DIY 고객 | 홈캠/CCTV 셀프 설치를 원하는 소규모 B2B | 설치 가이드, 튜토리얼, 제품 세트 관심 |
| 3 | 보안업체 비교 고객 | 에스원, 캡스, KT텔레캅 등 업체 비교 | 업체 비교, 가격, 서비스 정보 필요 |
| 4 | B2B CCTV 고객 | CCTV 설치 원하는 B2B (부가서비스 불필요) | 설치 견적, 업체 정보, 기술 스펙 중심 |
| 5 | 기타/해당없음 | 위 분류에 속하지 않는 키워드 | 일반 정보성 콘텐츠 |

### 페르소나별 콘텐츠 전략

```yaml
persona_1_홈캠비교:
  content_type:
    - "제품 비교 리뷰"
    - "TOP 10 추천"
    - "가격대별 추천"
    - "용도별 추천"
  keywords_pattern:
    - "홈캠", "추천", "비교"
    - "가정용", "실내", "무선"
    - "펫캠", "아기", "반려동물"

persona_2_DIY:
  content_type:
    - "설치 가이드"
    - "DIY 튜토리얼"
    - "제품 세트 추천"
    - "셀프 설치 팁"
  keywords_pattern:
    - "설치", "셀프", "DIY"
    - "자가설치", "설치방법"
    - "세트", "4채널", "8채널"

persona_3_보안업체:
  content_type:
    - "업체 비교"
    - "가격 비교"
    - "서비스 분석"
    - "고객센터 정보"
  keywords_pattern:
    - "KT", "캡스", "에스원", "세콤", "ADT"
    - "텔레캅", "뷰가드", "기가아이즈"
    - "가격", "비용", "고객센터"

persona_4_B2B:
  content_type:
    - "업체 견적 가이드"
    - "설치 업체 비교"
    - "기술 스펙 분석"
    - "대량 구매 정보"
  keywords_pattern:
    - "설치업체", "견적", "비용"
    - "매장", "사무실", "공장"
    - "NVR", "DVR", "IP카메라"

persona_5_기타:
  content_type:
    - "일반 정보"
    - "뉴스/트렌드"
    - "법률/규제 정보"
  keywords_pattern:
    - "CCTV종류", "역사"
    - "법률", "규제", "가이드라인"
```

## 📊 데이터베이스 스키마

### 1. 고객 페르소나 마스터 테이블 (customer_personas)

```sql
CREATE TABLE customer_personas (
    persona_id INTEGER PRIMARY KEY,
    persona_name VARCHAR(100) NOT NULL,
    description TEXT,
    characteristics TEXT,
    content_strategy TEXT,
    target_keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 키워드 마스터 테이블 (keywords_master)

```sql
CREATE TABLE keywords_master (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(200) NOT NULL UNIQUE,
    persona_id INTEGER,
    confidence_score FLOAT DEFAULT 0.0,
    labeling_method VARCHAR(50), -- 'manual', 'auto', 'ai'
    source_file VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES customer_personas(persona_id)
);

-- 인덱스 생성
CREATE INDEX idx_keyword ON keywords_master(keyword);
CREATE INDEX idx_persona ON keywords_master(persona_id);
```

### 3. 키워드 시계열 추적 테이블 (keyword_timeseries)

```sql
CREATE TABLE keyword_timeseries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER NOT NULL,
    record_date DATE NOT NULL,
    search_volume_pc INTEGER DEFAULT 0,
    search_volume_mobile INTEGER DEFAULT 0,
    search_volume_total INTEGER DEFAULT 0,
    avg_click_pc FLOAT DEFAULT 0.0,
    avg_click_mobile FLOAT DEFAULT 0.0,
    avg_ctr_pc FLOAT DEFAULT 0.0,
    avg_ctr_mobile FLOAT DEFAULT 0.0,
    competition_level VARCHAR(20),
    avg_ad_count INTEGER DEFAULT 0,
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords_master(keyword_id),
    UNIQUE(keyword_id, record_date)
);

-- 인덱스 생성
CREATE INDEX idx_keyword_date ON keyword_timeseries(keyword_id, record_date);
CREATE INDEX idx_date ON keyword_timeseries(record_date);
```

### 4. 키워드 변화 분석 테이블 (keyword_changes)

```sql
CREATE TABLE keyword_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER NOT NULL,
    analysis_date DATE NOT NULL,
    period_days INTEGER DEFAULT 7, -- 7일, 30일, 90일 등
    volume_change_pct FLOAT,
    volume_change_abs INTEGER,
    trend VARCHAR(20), -- 'increasing', 'decreasing', 'stable'
    alert_level VARCHAR(20), -- 'high', 'medium', 'low'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords_master(keyword_id)
);

-- 인덱스 생성
CREATE INDEX idx_keyword_trend ON keyword_changes(keyword_id, analysis_date);
```

### 5. 블로그 포스팅 이력 테이블 (blog_posts)

```sql
CREATE TABLE blog_posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER NOT NULL,
    persona_id INTEGER NOT NULL,
    title VARCHAR(500),
    content TEXT,
    target_date DATE,
    status VARCHAR(20), -- 'draft', 'scheduled', 'published'
    post_url VARCHAR(500),
    performance_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords_master(keyword_id),
    FOREIGN KEY (persona_id) REFERENCES customer_personas(persona_id)
);

-- 인덱스 생성
CREATE INDEX idx_post_keyword ON blog_posts(keyword_id);
CREATE INDEX idx_post_persona ON blog_posts(persona_id);
CREATE INDEX idx_post_status ON blog_posts(status);
```

## 🤖 자동 라벨링 시스템

### 라벨링 로직

```python
def auto_label_keyword(keyword: str, search_volume: int) -> tuple[int, float]:
    """
    키워드를 자동으로 페르소나에 라벨링

    Returns:
        (persona_id, confidence_score)
    """

    # 규칙 기반 매칭
    rules = {
        1: ['홈캠', '추천', '비교', '가정용', '실내', '펫캠', '무선',
            '엘지홈캠', 'LG홈캠', '국산홈캠', '스마트홈캠'],
        2: ['설치', 'DIY', '셀프', '자가설치', '설치방법', '세트',
            '4채널', '8채널', 'CCTV세트', 'IP카메라추천'],
        3: ['KT', '캡스', '에스원', '세콤', 'ADT', '텔레캅',
            '뷰가드', '기가아이즈', '고객센터', '비용', 'KTCCTV'],
        4: ['설치업체', '견적', 'NVR', 'DVR', '매장', '사무실',
            'IP카메라', '공장', '학교', '병원', '업소용'],
        5: ['도로', '버스', '실시간', '종류', '법률', 'CCTV확인']
    }

    keyword_lower = keyword.lower()
    scores = {pid: 0.0 for pid in range(1, 6)}

    # 키워드 매칭 점수 계산
    for persona_id, patterns in rules.items():
        for pattern in patterns:
            if pattern.lower() in keyword_lower:
                scores[persona_id] += 1.0

    # 가장 높은 점수의 페르소나 선택
    best_persona = max(scores.items(), key=lambda x: x[1])

    if best_persona[1] == 0:
        return (5, 0.3)  # 기타로 분류, 낮은 신뢰도

    confidence = min(best_persona[1] / 3.0, 1.0)  # 정규화

    return (best_persona[0], confidence)
```

## 📈 시계열 분석 및 알림 시스템

### 트렌드 분석 로직

```python
def analyze_keyword_trend(keyword_id: int, days: int = 7) -> dict:
    """
    키워드 트렌드 분석

    Returns:
        {
            'trend': 'increasing' | 'decreasing' | 'stable',
            'change_pct': float,
            'change_abs': int,
            'alert_level': 'high' | 'medium' | 'low'
        }
    """

    # 지난 N일간의 데이터 조회
    # 변화율 계산
    # 알림 레벨 결정

    # 예시:
    # - 50% 이상 증가: high alert, 긴급 포스팅 필요
    # - 20-50% 증가: medium alert, 포스팅 고려
    # - 20% 미만 변화: low alert, 모니터링

    pass
```

### 포스팅 우선순위 알고리즘

```python
def calculate_posting_priority(keyword_id: int) -> float:
    """
    블로그 포스팅 우선순위 계산

    고려 요소:
    - 검색량 증가율 (40%)
    - 절대 검색량 (30%)
    - 경쟁 정도 (20%)
    - 최근 포스팅 여부 (10%)

    Returns:
        0.0 ~ 100.0 우선순위 점수
    """

    score = 0.0

    # 1. 검색량 증가율 (40점)
    trend_data = get_trend_data(keyword_id, days=7)
    if trend_data['change_pct'] > 50:
        score += 40
    elif trend_data['change_pct'] > 20:
        score += 30
    elif trend_data['change_pct'] > 0:
        score += 20

    # 2. 절대 검색량 (30점)
    volume = get_latest_volume(keyword_id)
    if volume > 10000:
        score += 30
    elif volume > 5000:
        score += 20
    elif volume > 1000:
        score += 10

    # 3. 경쟁 정도 (20점)
    competition = get_competition_level(keyword_id)
    if competition == '낮음':
        score += 20
    elif competition == '중간':
        score += 10

    # 4. 최근 포스팅 여부 (10점)
    days_since_post = get_days_since_last_post(keyword_id)
    if days_since_post > 30:
        score += 10
    elif days_since_post > 14:
        score += 5

    return score
```

## 🔄 데이터 수집 및 업데이트 워크플로우

### 일일 업데이트 프로세스

```
1. 키워드 데이터 수집
   ↓
2. 신규 키워드 자동 라벨링
   ↓
3. 시계열 데이터 저장
   ↓
4. 트렌드 분석 실행
   ↓
5. 변화 감지 및 알림
   ↓
6. 포스팅 우선순위 계산
   ↓
7. 포스팅 스케줄 생성
```

### 주간 리뷰 프로세스

```
1. 상위 트렌딩 키워드 리포트
   ↓
2. 페르소나별 검색량 변화 분석
   ↓
3. 포스팅 성과 분석
   ↓
4. 라벨링 정확도 검증
   ↓
5. 다음 주 포스팅 전략 수립
```

## 📝 블로그 자동화 연동

### AI 프롬프트 구조

```python
def generate_blog_prompt(keyword_id: int, persona_id: int) -> str:
    """
    페르소나 맞춤형 블로그 프롬프트 생성
    """

    keyword_data = get_keyword_data(keyword_id)
    persona_data = get_persona_data(persona_id)
    trend_data = get_trend_data(keyword_id)

    prompt = f"""
    # 블로그 포스팅 생성 요청

    ## 타겟 정보
    - 키워드: {keyword_data['keyword']}
    - 검색량: {keyword_data['search_volume']}
    - 트렌드: {trend_data['trend']} ({trend_data['change_pct']}% 변화)

    ## 고객 페르소나
    - 페르소나: {persona_data['name']}
    - 특징: {persona_data['characteristics']}
    - 관심사: {persona_data['interests']}

    ## 콘텐츠 요구사항
    - 콘텐츠 타입: {persona_data['preferred_content_type']}
    - 톤앤매너: {persona_data['tone']}
    - 길이: 1500-2000자
    - SEO 최적화: 키워드 자연스럽게 5-7회 포함

    ## 구조
    1. 도입부: 검색 의도 공감 (200자)
    2. 본문: 구체적 정보 제공 (1000-1500자)
    3. 마무리: 행동 유도 (CTA) (200-300자)

    위 정보를 바탕으로 블로그 포스팅을 작성해주세요.
    """

    return prompt
```

## 📊 대시보드 및 모니터링

### 주요 지표

1. **키워드 성과**
   - 일일/주간/월간 검색량 변화
   - 트렌딩 키워드 TOP 20
   - 페르소나별 검색량 분포

2. **포스팅 성과**
   - 발행된 포스팅 수
   - 페르소나별 포스팅 분포
   - 포스팅 스케줄 진행률

3. **시스템 성과**
   - 자동 라벨링 정확도
   - 데이터 수집 안정성
   - 알림 정확도

## 🚀 구현 우선순위

### Phase 1: 기반 구축 (1-2주)
- [x] 고객 페르소나 정의
- [ ] DB 스키마 생성
- [ ] 기존 데이터 마이그레이션
- [ ] 자동 라벨링 시스템 구현

### Phase 2: 시계열 추적 (2-3주)
- [ ] 데이터 수집 파이프라인 구축
- [ ] 트렌드 분석 로직 구현
- [ ] 알림 시스템 구축

### Phase 3: 자동화 (3-4주)
- [ ] 블로그 프롬프트 생성기
- [ ] 우선순위 알고리즘 구현
- [ ] 스케줄링 시스템

### Phase 4: 최적화 (4주~)
- [ ] 대시보드 구축
- [ ] AI 라벨링 정확도 개선
- [ ] 성과 분석 및 피드백 루프
