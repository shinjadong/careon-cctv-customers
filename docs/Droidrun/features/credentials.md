---

title: '자격 증명 관리'

description: '안전한 자격 증명 관리로 Droidrun 확장하기'

---

  

## 개요

  

비밀번호, API 키, 토큰을 위한 안전한 저장소입니다.

  

📖 **자격 증명(Credentials)**

├─ **정의**: 비밀번호, API 키 등 민감한 인증 정보를 안전하게 보관하는 시스템

├─ **쉬운 비유**: 금고에 중요한 열쇠를 보관하듯이 민감 정보를 보호

├─ **메커니즘**: YAML 파일이나 메모리에 저장하며 로그에 노출되지 않음

└─ **존재 이유**: 코드에 비밀번호를 하드코딩하지 않고 안전하게 관리하기 위함

  

- YAML 파일 또는 인메모리 딕셔너리에 저장

- 절대 로그에 기록되거나 노출되지 않음

- `type_secret` 도구로 자동 주입

- 간단한 문자열 또는 딕셔너리 형식

  

## 빠른 시작

  

### 방법 1: 인메모리 (SDK에 권장)

  

```python

import asyncio

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

async def main():

    # 자격 증명을 직접 정의

    credentials = {

        "MY_PASSWORD": "secret123",

        "API_KEY": "sk-1234567890"

    }

  

    config = DroidrunConfig()

  

    agent = DroidAgent(

        goal="내 앱에 로그인",

        config=config,

        credentials=credentials  # 직접 전달

    )

  

    result = await agent.run()

    print(result.success)

  

asyncio.run(main())

```

  

### 방법 2: YAML 파일

  

1. **자격 증명 파일 생성:**

  

```yaml

# credentials.yaml

secrets:

  # 딕셔너리 형식 (권장)

  MY_PASSWORD:

    value: "your_password_here"

    enabled: true

  

  GMAIL_PASSWORD:

    value: "gmail_pass_123"

    enabled: true

  

  # 간단한 문자열 형식 (자동 활성화)

  API_KEY: "sk-1234567890abcdef"

  

  # 비활성화된 시크릿

  OLD_PASSWORD:

    value: "old_pass"

    enabled: false  # 로드되지 않음

```

  

2. **config.yaml에서 활성화:**

  

```yaml

# config.yaml

credentials:

  enabled: true

  file_path: credentials.yaml

```

  

3. **코드에서 사용:**

  

```python

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

# Config가 파일에서 자격 증명 로드

config = DroidrunConfig.from_yaml("config.yaml")

  

agent = DroidAgent(

    goal="Gmail 로그인",

    config=config  # 자격 증명 자동 로드

)

```

  

---

  

## 에이전트의 자격 증명 사용 방법

  

자격 증명이 제공되면 `type_secret` 액션이 **자동으로 사용 가능**합니다:

  

### Executor/Manager 모드

```json

{

  "action": "type_secret",

  "secret_id": "MY_PASSWORD",

  "index": 5

}

```

  

### CodeAct 모드

```python

type_secret("MY_PASSWORD", index=5)

```

  

에이전트는 실제 값을 절대 보지 못하며 시크릿 ID만 봅니다.

  

---

  

## 예시: 로그인 자동화

  

```python

import asyncio

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

async def main():

    credentials = {

        "EMAIL_USER": "user@example.com",

        "EMAIL_PASS": "secret_password"

    }

  

    config = DroidrunConfig()

  

    agent = DroidAgent(

        goal="Gmail 열고 내 자격 증명으로 로그인",

        config=config,

        credentials=credentials

    )

  

    result = await agent.run()

    print(f"성공: {result.success}")

  

asyncio.run(main())

```

  

**에이전트가 수행하는 작업:**

1. Gmail 열기: `open_app("Gmail")`

2. 이메일 필드 클릭: `click(index=3)`

3. 이메일 입력: `type("user@example.com", index=3)`

4. 비밀번호 필드 클릭: `click(index=5)`

5. 비밀번호 안전하게 입력: `type_secret("EMAIL_PASS", index=5)`

6. 로그인 클릭: `click(index=7)`

  

## 자격 증명 vs 변수

  

| 기능 | 자격 증명 | 변수 |

|---------|------------|-----------|

| **목적** | 비밀번호, API 키 | 민감하지 않은 데이터 |

| **저장소** | YAML 또는 인메모리 | 인메모리만 |

| **로깅** | 절대 로그되지 않음 | 로그에 나타날 수 있음 |

| **접근** | `type_secret` 도구를 통해 | 공유 상태에서 |

| **보안** | 보호됨 | 보호 없음 |

  

**예시: 변수 사용**

```python

variables = {

    "target_email": "john@example.com",

    "subject_line": "월간 리포트"

}

  

agent = DroidAgent(

    goal="{{target_email}}에게 이메일 작성",

    config=config,

    variables=variables  # 민감하지 않은 정보

)

```

  

---

  

## 문제 해결

  

### 오류: Credential manager not initialized

  

**해결방법:**

```yaml

# config.yaml

credentials:

  enabled: true  # true여야 함

  file_path: credentials.yaml

```

  

또는:

```python

agent = DroidAgent(..., credentials={"PASSWORD": "secret"})

```

  

### 오류: Secret 'X' not found

  

**사용 가능한 시크릿 확인:**

```python

from droidrun.credential_manager import CredentialManager

  

cm = CredentialManager(credentials_path="credentials.yaml")

print(cm.list_available_secrets())

```

  

**YAML에서 확인:**

```yaml

secrets:

  X:

    value: "your_value"

    enabled: true  # true여야 함

```

  

---

  

## 관련 문서

  

자격 증명 설정은 [설정 가이드](/sdk/configuration)를 참조하세요.

  

민감하지 않은 데이터는 [커스텀 변수](/features/custom-variables)를 참조하세요.