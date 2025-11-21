---

title: '앱 인스트럭션 카드'

description: '앱 카드는 에이전트에게 앱별 지식을 제공하여 앱을 더 효과적으로 조작할 수 있게 합니다. 특정 앱 작업 시 자동으로 로드되어 탐색 및 복잡한 작업의 성공률을 향상시킵니다.'

---

  

## 앱 카드란?

  

앱 카드는 **앱별 인스트럭션 가이드**로, 에이전트가 앱을 효과적으로 사용하는 방법을 학습할 수 있게 합니다. 에이전트가 다음을 이해하도록 돕는 치트 시트라고 생각하면 됩니다:

  

- 앱의 UI 탐색 방법

- 버튼과 기능의 위치

- 앱별 단축키와 제스처

- 검색 구문과 필터 (Gmail 같은 앱)

- 일반적인 워크플로우와 모범 사례

  

**예시:** 에이전트가 Gmail을 열면 자동으로 Gmail 앱 카드를 로드하고 다음을 학습합니다:

- 작성 버튼이 우측 하단에 있음

- 검색이 `from:sender@email.com` 또는 `has:attachment` 같은 필터를 지원함

- 우측으로 스와이프하면 보관, 좌측으로 스와이프하면 삭제됨

  

이러한 지식은 에이전트가 작업을 더 빠르고 안정적으로 완료하도록 돕습니다.

  

---

  

## 앱 카드를 사용하는 이유

  

**앱 카드 없이:**

- 에이전트가 익숙하지 않은 앱 탐색 방법을 추측함

- 시행착오로 시간과 토큰 낭비

- 복잡한 워크플로우에서 성공률 저하

  

**앱 카드 사용 시:**

- ✅ 에이전트가 기능 위치를 정확히 파악

- ✅ 일반 작업에서 첫 시도 성공

- ✅ 토큰 사용량 감소 (탐색 필요성 감소)

- ✅ 앱별 특성 더 잘 처리

  

---

  

## 빠른 시작

  

Droidrun에는 앱 카드 작동 방식을 보여주는 샘플 Gmail 앱 카드가 포함되어 있습니다:

  

```bash

# 앱 카드는 기본적으로 활성화됨

droidrun run "john@example.com에게 이메일 보내기" --reasoning

```

  

에이전트가 Gmail을 열면 Gmail 앱 카드가 자동으로 로드되어 워크플로우를 안내합니다.

  

**포함된 샘플 앱 카드:**

- **Gmail** (`com.google.android.gm`) - 이메일 탐색, 검색, 작성

  

이것을 템플릿으로 사용하여 다른 앱용 카드를 만들 수 있습니다(아래 "커스텀 앱 카드 만들기" 참조).

  

---

  

## 앱 카드 작동 방식

  

### 자동 로딩

  

1. **감지:** 에이전트가 현재 포그라운드 앱 감지 (예: Gmail)

2. **로딩:** Droidrun이 해당 패키지명에 대한 앱 카드 로드

3. **주입:** 앱 카드 내용이 에이전트 프롬프트에 추가됨

4. **가이드:** 에이전트가 인스트럭션을 사용하여 더 나은 결정 수행

  

**기술적 참고사항:** 앱 카드는 비동기적으로 로드되어 메모리에 캐시됩니다. 로딩은 백그라운드에서 발생하며 에이전트 실행을 차단하지 않습니다.

  

### 언제 사용되나요?

  

앱 카드는 추론 모드(`--reasoning` 플래그 또는 config에서 `reasoning: true`)로 실행할 때 **Manager 에이전트**가 사용합니다:

  

```bash

# 앱 카드 활성화 (Manager가 계획 수립 시 사용)

droidrun run "읽지 않은 모든 이메일 보관" --reasoning

  

# 앱 카드 미사용 (직접 실행 모드)

droidrun run "버튼 탭"

```

  

---

  

## 커스텀 앱 카드 만들기

  

즐겨 사용하는 앱을 위한 앱 카드를 추가하고 싶으신가요? 방법은 다음과 같습니다:

  

### 단계 1: 패키지명 찾기

  

```bash

# 모든 앱 가져오기

adb shell pm list packages

  

# 특정 앱 검색

adb shell pm list packages | grep 키워드

```

  

**일반적인 패키지명:**

- Chrome: `com.android.chrome`

- WhatsApp: `com.whatsapp`

- Instagram: `com.instagram.android`

- YouTube: `com.google.android.youtube`

  

### 단계 2: 파일 생성

  

앱 카드 디렉토리와 파일을 생성합니다:

  

```bash

mkdir -p config/app_cards

touch config/app_cards/app_cards.json

touch config/app_cards/chrome.md

```

  

**예시 구조:**

  

```markdown

# Chrome 앱 가이드

  

## 탐색

- 상단에 URL 입력을 위한 주소 표시줄

- 설정과 기록을 위한 점 세 개 메뉴 (우측 상단)

- 탭 간 전환을 위한 탭 버튼 (우측 상단)

  

## 검색

- 주소 표시줄에 직접 쿼리 입력

- 마이크 아이콘을 통한 음성 검색 사용

  

## 일반 작업

- **새 탭**: 탭 버튼 탭 → 플러스 아이콘

- **탭 닫기**: 탭 전환기에서 탭을 스와이프하여 제거

- **새로고침**: 페이지 상단에서 아래로 당기기

- **북마크**: 점 세 개 메뉴 → 북마크

  

## 팁

- 점 세 개 메뉴를 통해 시크릿 모드 사용 가능

- 점 세 개 메뉴 → 다운로드를 통해 다운로드 접근 가능

```

  

### 단계 3: 앱 카드 등록

  

`config/app_cards/app_cards.json`에 앱 매핑을 추가합니다:

  

```json

{

  "com.google.android.gm": "gmail.md",

  "com.android.chrome": "chrome.md"

}

```

  

**하위 디렉토리 사용:**

  

```json

{

  "com.whatsapp": "social/whatsapp.md",

  "com.instagram.android": "social/instagram.md"

}

```

  

### 단계 4: 테스트

  

```bash

droidrun run "Chrome 열고 droidrun 검색" --reasoning --debug

```

  

다음 로그 메시지를 확인하세요:

```

Loaded app card for com.android.chrome from config/app_cards/chrome.md

```

  

---

  

## 설정

  

앱 카드는 기본적으로 활성화되며 `config/app_cards/`에서 로드됩니다:

  

```yaml

agent:

  app_cards:

    enabled: true

    app_cards_dir: config/app_cards

```

  

**비활성화:**

```yaml

agent:

  app_cards:

    enabled: false

```

  

---

  

## 앱 카드 모범 사례

  

### 콘텐츠 가이드라인

  

**해야 할 것:**

- 간결하고 실행 가능하게 작성

- UI 패턴과 워크플로우에 집중

- 검색 구문과 특수 기능 포함

- 일반적인 함정이나 특이사항 언급

- 글머리 기호와 명확한 제목 사용

  

**하지 말아야 할 것:**

- 긴 설명이나 장황한 글 작성

- 모든 기능을 설명

- 자주 변경되는 정보 포함 (버전별 세부사항)

- 일반적인 Android 지식 중복 (에이전트는 이미 탭, 스와이프 등을 알고 있음)

  

### 예시: 좋은 vs 나쁜

  

**❌ 나쁜 예 (너무 장황):**

```markdown

Gmail은 Google이 개발한 이메일 애플리케이션입니다. 이메일을 보내고 받는 등 많은 기능이 있습니다. 이메일을 작성하려면 먼저 Gmail이 플로팅 액션 버튼이 있는 머티리얼 디자인 인터페이스를 사용한다는 것을 이해해야 합니다. 플로팅 액션 버튼은 원형 버튼인데...

```

  

**✅ 좋은 예 (간결하고 실행 가능):**

```markdown

## 이메일 작성

- 플로팅 작성 버튼 탭 (우측 하단)

- 받는 사람, 제목, 본문 입력

- 종이비행기 아이콘으로 전송 (우측 상단)

```

  

---

  

## 문제 해결

  

### 앱 카드가 로드되지 않음

  

**다음을 확인하세요:**

  

1. **패키지명이 올바른가요?**

   ```bash

   adb shell dumpsys window windows | grep -E 'mCurrentFocus'

   ```

  

2. **app_cards.json에서 매핑이 올바른가요?**

   ```json

   {

     "com.your.app": "yourapp.md"

   }

   ```

  

3. **마크다운 파일이 존재하나요?**

   ```bash

   ls config/app_cards/yourapp.md

   ```

  

4. **앱 카드가 활성화되어 있나요?**

   ```yaml

   agent:

     app_cards:

       enabled: true

   ```

  

5. **추론 모드를 사용하고 있나요?**

   ```bash

   droidrun run "명령어" --reasoning

   ```

  

### 디버그 모드

  

`--debug`로 실행하여 앱 카드 로딩을 확인하세요:

  

```bash

droidrun run "Gmail 열기" --reasoning --debug

```

  

다음 로그 메시지를 확인하세요:

```

Loaded app_cards.json with 2 entries

Loaded app card for com.google.android.gm from config/app_cards/gmail.md

```

  

---

  

## 관련 문서

  

- [CLI 사용법](/guides/cli) - Droidrun CLI 명령어 참조

- [설정](/sdk/configuration) - 설정 시스템 세부사항

- [에이전트 아키텍처](/concepts/architecture) - 에이전트 작동 방식

- [Manager 에이전트](/sdk/droid-agent#manager-agent) - 앱 카드를 사용하는 에이전트

  

---

  

**잘 작성된 앱 카드로 에이전트를 앱 전문가로 만드세요!**