---
title: 'Configuration'
description: '완전한 DroidAgent 구성 가이드 - 모든 파라미터, 최소 예시'
---

## 빠른 시작

```python
from droidrun import DroidAgent

# 최소 구성 (기본값 사용)
agent = DroidAgent(goal="설정 열기")
result = await agent.run()
```

---

## DroidAgent 파라미터

### 필수 파라미터

```python
DroidAgent(
    goal="작업 설명",  # 필수: 작업 설명
)
```

> 📖 **goal 파라미터**
> 
> **정의**: 에이전트가 수행할 작업을 자연어로 설명
> 
> **예시**:
> ```python
> # 간단한 작업
> goal="설정 앱 열기"
> 
> # 복잡한 다단계 작업
> goal="카카오톡 열고 홍길동에게 '안녕하세요' 메시지 보내기"
> 
> # 조건부 작업
> goal="배터리가 20% 이하면 절전 모드 켜기"
> 
> # 정보 수집
> goal="현재 Wi-Fi 연결 상태 확인하고 신호 강도 알려주기"
> ```

### 선택적 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `config` | `DroidrunConfig \| None` | `None` | 전체 구성 객체 (`llms`가 제공되지 않으면 프로필에서 LLM 로드) |
| `llms` | `dict[str, LLM] \| LLM \| None` | `None` | LLM - 에이전트별 딕셔너리, 모두에게 단일 LLM, 또는 None으로 config에서 로드 |
| `tools` | `Tools \| None` | `None` | Tools 인스턴스 (AdbTools/IOSTools) |
| `custom_tools` | `dict \| None` | `None` | 커스텀 도구 정의 |
| `credentials` | `dict \| None` | `None` | 자격 증명 시크릿 딕셔너리 |
| `variables` | `dict \| None` | `None` | 실행 중 접근 가능한 커스텀 변수 |
| `output_model` | `Type[BaseModel] \| None` | `None` | 구조화된 출력 추출을 위한 Pydantic 모델 |
| `prompts` | `dict[str, str] \| None` | `None` | 커스텀 Jinja2 프롬프트 템플릿 (파일 경로 아님) |
| `timeout` | `int` | `1000` | 워크플로 타임아웃(초) |

> 💡 **파라미터 조합 전략**
> 
> **최소 구성** (빠른 테스트):
> ```python
> agent = DroidAgent(goal="설정 열기")
> # 모든 기본값 사용
> ```
> 
> **LLM만 지정** (특정 모델 사용):
> ```python
> from llama_index.llms.openai import OpenAI
> llm = OpenAI(model="gpt-4o")
> 
> agent = DroidAgent(
>     goal="복잡한 작업",
>     llms=llm  # 모든 에이전트가 이 LLM 사용
> )
> ```
> 
> **완전 커스터마이징**:
> ```python
> agent = DroidAgent(
>     goal="고급 작업",
>     config=custom_config,
>     llms=llm_dict,
>     tools=custom_tools,
>     credentials={"API_KEY": "..."},
>     timeout=600
> )
> ```

---

## 구성 클래스

### AgentConfig

```python
from droidrun.config_manager import AgentConfig, CodeActConfig, ManagerConfig, ExecutorConfig, ScripterConfig, AppCardConfig

AgentConfig(
    # 핵심 설정
    max_steps=15,                    # 최대 실행 단계
    reasoning=True,                  # Manager/Executor 워크플로 활성화
    after_sleep_action=1.0,          # 액션 후 대기 시간(초)
    wait_for_stable_ui=0.3,          # UI 안정화 대기 시간(초)
    prompts_dir="config/prompts",    # 프롬프트 템플릿 디렉토리

    # 하위 구성
    codeact=CodeActConfig(...),
    manager=ManagerConfig(...),
    executor=ExecutorConfig(...),
    scripter=ScripterConfig(...),
    app_cards=AppCardConfig(...),
)
```

> 📖 **AgentConfig 핵심 파라미터**
> 
> **max_steps** (최대 단계):
> - 무한 루프 방지
> - 간단한 작업: 5-10 단계
> - 복잡한 작업: 20-30 단계
> - 매우 복잡: 50+ 단계
> 
> **reasoning** (추론 모드):
> - `False`: CodeAct 직접 모드 (빠름, 간단한 작업)
> - `True`: Manager → Executor 워크플로 (느림, 복잡한 작업)
> 
> **after_sleep_action** (액션 후 대기):
> - UI 반응 시간 확보
> - 빠른 기기: 0.5-1.0초
> - 느린 기기: 1.5-2.0초
> 
> **wait_for_stable_ui** (UI 안정화 대기):
> - 애니메이션 완료 대기
> - 일반적으로 0.3-0.5초

**CodeActConfig**
```python
CodeActConfig(
    vision=True,                    # 스크린샷 활성화
    system_prompt="system.jinja2",   # prompts_dir/codeact/의 파일명
    user_prompt="user.jinja2",       # prompts_dir/codeact/의 파일명
    safe_execution=True,            # imports/builtins 제한
)
```

> 📖 **CodeActConfig 상세**
> 
> **vision** (비전 모드):
> - `True`: 스크린샷을 LLM에게 전송
> - `False`: 텍스트 기반 UI 트리만
> - 비용/성능 트레이드오프 고려
> 
> **system_prompt / user_prompt**:
> - Jinja2 템플릿 파일명
> - `prompts_dir/codeact/` 안에 위치
> - 커스터마이징 가능
> 
> **safe_execution** (안전 실행):
> - `True`: 위험한 Python 코드 제한
> - `False`: 모든 코드 허용 (테스트 전용)
> - 프로덕션에서는 항상 `True` 권장

**ManagerConfig**
```python
ManagerConfig(
    vision=True,                    # 스크린샷 활성화
    system_prompt="system.jinja2",   # prompts_dir/manager/의 파일명
)
```

> 💡 **Manager vs Executor vs CodeAct**
> 
> **Manager** (계획자):
> - 역할: 작업을 단계로 분해
> - 입력: 목표, 현재 상태
> - 출력: 단계별 계획
> 
> **Executor** (실행자):
> - 역할: 단일 단계 실행
> - 입력: Manager의 단계 하나
> - 출력: 액션 선택
> 
> **CodeAct** (코드 생성자):
> - 역할: Python 코드 생성
> - 직접 모드 또는 Executor에 의해 호출
> - 출력: 실행 가능한 코드

**ExecutorConfig**
```python
ExecutorConfig(
    vision=True,                    # 스크린샷 활성화
    system_prompt="system.jinja2",   # prompts_dir/executor/의 파일명
)
```

**ScripterConfig**
```python
ScripterConfig(
    enabled=True,                    # 오프-디바이스 Python 실행 활성화
    max_steps=10,                    # 최대 scripter 단계
    execution_timeout=30.0,          # 코드 블록 타임아웃(초)
    system_prompt_path="system.jinja2",  # prompts_dir/scripter/의 파일명
    safe_execution=False,            # imports/builtins 제한
)
```

> 📖 **Scripter란?**
> 
> **정의**: 기기 외부(컴퓨터)에서 Python 코드를 실행하는 컴포넌트
> 
> **사용 사례**:
> - API 호출 (예: 날씨 정보 가져오기)
> - 데이터 처리 (예: CSV 분석)
> - 복잡한 계산
> - 외부 서비스 통합
> 
> **enabled** (활성화):
> - `True`: Scripter 사용 가능
> - `False`: 기기 내부 작업만
> 
> **execution_timeout**:
> - 코드 실행 최대 시간
> - API 호출 시간 고려
> - 일반적으로 10-30초

**AppCardConfig**
```python
AppCardConfig(
    enabled=True,                    # 앱별 지침 활성화
    mode="local",                    # "local" | "server" | "composite"
    app_cards_dir="config/app_cards",  # 앱 카드 파일 디렉토리
    server_url=None,                 # 서버 URL (server/composite 모드용)
    server_timeout=2.0,              # 서버 요청 타임아웃(초)
    server_max_retries=2,            # 서버 재시도 횟수
)
```

> 📖 **App Card란?**
> 
> **정의**: 특정 앱에 대한 사용 지침을 제공하는 파일
> 
> **예시** (카카오톡 앱 카드):
> ```yaml
> package: com.kakao.talk
> instructions: |
>   - 메시지 보내기: 하단 채팅 탭 → 대화방 선택 → 메시지 입력
>   - 친구 추가: 친구 탭 → 우측 상단 + 버튼
>   - 주의: 첫 화면에서 광고 팝업 닫기 필요
> ```
> 
> **mode 옵션**:
> - `local`: 로컬 파일만 사용
> - `server`: 서버에서 다운로드
> - `composite`: 로컬 우선, 없으면 서버
> 
> 자세한 내용은 [App Cards 가이드](../features/app-cards) 참조

---

### DeviceConfig

```python
from droidrun.config_manager import DeviceConfig

DeviceConfig(
    serial=None,          # 기기 시리얼/IP (None = 자동 감지)
    platform="android",   # "android" 또는 "ios"
    use_tcp=False,        # TCP vs content provider 통신
)
```

> 💡 **DeviceConfig 실전 설정**
> 
> **단일 기기 (자동 감지)**:
> ```python
> config = DeviceConfig()  # serial=None, 자동으로 첫 기기 선택
> ```
> 
> **특정 기기 지정**:
> ```python
> config = DeviceConfig(serial="emulator-5554")  # 에뮬레이터
> config = DeviceConfig(serial="ABC123DEF")      # USB 기기
> config = DeviceConfig(serial="192.168.1.100:5555")  # 무선 ADB
> ```
> 
> **iOS 기기**:
> ```python
> config = DeviceConfig(
>     platform="ios",
>     serial="http://localhost:8100"  # iOS Portal URL
> )
> ```
> 
> **TCP 모드** (고속 통신):
> ```python
> config = DeviceConfig(
>     serial="emulator-5554",
>     use_tcp=True  # 빠르지만 `adb forward` 필요
> )
> # 사전 설정: adb forward tcp:8080 tcp:8080
> ```

---

### LoggingConfig

```python
from droidrun.config_manager import LoggingConfig

LoggingConfig(
    debug=True,                   # 디버그 로그 활성화
    save_trajectory="none",        # "none" | "step" | "action"
    rich_text=False,               # 로그에 Rich 텍스트 포맷 사용
)
```

> 📖 **save_trajectory 모드 상세**
> 
> **"none"** (궤적 저장 안 함):
> - 스크린샷 캡처하지 않음
> - 빠른 실행
> - 프로덕션 환경
> 
> **"step"** (단계별 저장):
> - 각 주요 단계마다 캡처
> - 에이전트가 수동으로 `take_screenshot()` 호출
> - 중간 정도의 오버헤드
> 
> **"action"** (액션별 저장):
> - 모든 UI 액션마다 자동 캡처
> - `@Tools.ui_action` 데코레이터 작동
> - 디버깅에 최적
> - 느리고 많은 저장 공간 필요
> 
> **실무 권장**:
> ```python
> # 개발/디버깅
> save_trajectory="action", debug=True
> 
> # 테스트
> save_trajectory="step", debug=False
> 
> # 프로덕션
> save_trajectory="none", debug=False
> ```

---

### TracingConfig

```python
from droidrun.config_manager import TracingConfig

TracingConfig(
    enabled=True,  # Arize Phoenix 추적 활성화
)
```

> 📖 **Arize Phoenix란?**
> 
> **정의**: LLM 애플리케이션의 옵저버빌리티 플랫폼
> 
> **제공 기능**:
> - LLM 호출 추적
> - 프롬프트 및 응답 로깅
> - 성능 메트릭
> - 비용 분석
> 
> **사용 시나리오**:
> - 에이전트 행동 분석
> - 프롬프트 최적화
> - 비용 모니터링
> - 성능 병목 지점 파악

---

### TelemetryConfig

```python
from droidrun.config_manager import TelemetryConfig

TelemetryConfig(
    enabled=True,  # 익명 텔레메트리 활성화
)
```

> 💡 **텔레메트리 설정**
> 
> DroidRun 개선을 위한 익명화된 사용 데이터 수집
> 
> **수집 정보** (예상):
> - 사용된 기능
> - 오류 발생 빈도
> - 성능 메트릭
> 
> **수집하지 않는 정보**:
> - 개인 식별 정보
> - 작업 내용
> - 민감한 데이터
> 
> 자세한 내용은 [텔레메트리 가이드](../guides/telemetry) 참조

---

계속해서 나머지 부분을 번역하겠습니다:

### ToolsConfig

```python
from droidrun.config_manager import ToolsConfig

ToolsConfig(
    allow_drag=True,  # 드래그 도구 활성화
)
```

> 💡 **allow_drag 설정**
> 
> **True**: 드래그 제스처 사용 가능
> - 홈 화면 아이콘 이동
> - 파일 드래그 앤 드롭
> - 슬라이더 조절
> 
> **False**: 드래그 비활성화
> - iOS에서 제한적인 경우
> - 안정성 우선 시

---

### CredentialsConfig

```python
from droidrun.config_manager import CredentialsConfig

CredentialsConfig(
    enabled=True,                   # 자격 증명 관리자 활성화
    file_path="credentials.yaml",    # 자격 증명 파일 경로
)
```

> 📖 **Credentials 관리**
> 
> **파일 형식** (credentials.yaml):
> ```yaml
> USERNAME: "user@example.com"
> PASSWORD: "secret123"
> API_KEY: "sk-..."
> ```
> 
> **에이전트에서 사용**:
> ```python
> # 에이전트가 자동으로 자격 증명 액세스
> # get_username(), get_password() 함수 호출 가능
> ```
> 
> **보안 주의사항**:
> - `.gitignore`에 credentials.yaml 추가
> - 환경 변수 사용도 고려
> - 프로덕션에서는 시크릿 관리 서비스 사용

---

### SafeExecutionConfig

```python
from droidrun.config_manager import SafeExecutionConfig

SafeExecutionConfig(
    # Imports
    allow_all_imports=False,         # 모든 import 허용 (allowed_modules 무시)
    allowed_modules=[],              # 허용된 모듈명 (예: ["json", "requests"])
    blocked_modules=[                # 차단된 모듈 (우선순위 높음)
        "os", "sys", "subprocess", "shutil", "pathlib", "pty", "fcntl",
        "resource", "pickle", "shelve", "marshal", "imp", "importlib",
        "ctypes", "code", "codeop", "tempfile", "glob", "socket",
        "socketserver", "asyncio"
    ],

    # Builtins
    allow_all_builtins=False,        # 모든 내장 함수 허용 (allowed_builtins 무시)
    allowed_builtins=[],             # 허용된 내장 함수 (빈 리스트 = 안전한 기본값)
    blocked_builtins=[               # 차단된 내장 함수 (우선순위 높음)
        "open", "compile", "exec", "eval", "__import__",
        "breakpoint", "exit", "quit", "input"
    ],
)
```

> 📖 **SafeExecution이 필요한 이유**
> 
> **문제**: LLM이 생성한 코드는 위험할 수 있음
> ```python
> # LLM이 생성할 수 있는 위험한 코드:
> import os
> os.system("rm -rf /")  # 위험!
> 
> exec("악의적인 코드")   # 위험!
> open("/etc/passwd")     # 위험!
> ```
> 
> **해결**: SafeExecution으로 제한
> ```python
> # 안전한 설정
> config = SafeExecutionConfig(
>     allow_all_imports=False,
>     allowed_modules=["json", "math", "datetime"],  # 안전한 모듈만
>     blocked_builtins=["open", "exec", "eval"]      # 위험한 함수 차단
> )
> ```
> 
> **허용 전략**:
> ```python
> # 최소 권한
> allowed_modules=["json", "math"]
> 
> # 일반적인 사용
> allowed_modules=["json", "requests", "datetime", "re"]
> 
> # 개발 환경 (주의!)
> allow_all_imports=True  # 테스트 전용
> ```

---

## LLM 구성

### 단일 LLM (모든 에이전트)

```python
from llama_index.llms.gemini import Gemini

llm = Gemini(model="models/gemini-2.5-pro", temperature=0.2)
agent = DroidAgent(goal="...", llms=llm)
```

> 💡 **단일 LLM 사용 시나리오**
> 
> **장점**:
> - 간단한 설정
> - 비용 예측 쉬움
> - 일관된 동작
> 
> **단점**:
> - 모든 역할에 같은 모델
> - 최적화 어려움
> 
> **권장**:
> - 프로토타입
> - 간단한 자동화
> - 빠른 테스트

### 에이전트별 LLM

```python
from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini

agent = DroidAgent(
    goal="...",
    llms={
        "manager": OpenAI(model="gpt-4o"),                    # 계획
        "executor": Gemini(model="models/gemini-2.5-flash"),  # 액션 선택
        "codeact": Gemini(model="models/gemini-2.5-pro"),     # 코드 생성
        "text_manipulator": Gemini(model="models/gemini-2.5-flash"),  # 텍스트 입력
        "app_opener": OpenAI(model="gpt-4o-mini"),            # 앱 실행
        "scripter": Gemini(model="models/gemini-2.5-flash"),  # 오프-디바이스 스크립트
        "structured_output": Gemini(model="models/gemini-2.5-flash"),  # 출력 추출
    }
)
```

**LLM 키:**
- `manager` - 계획 (reasoning 모드만)
- `executor` - 액션 선택 (reasoning 모드만)
- `codeact` - 코드 생성 (direct 모드)
- `scripter` - 오프-디바이스 Python 실행
- `text_manipulator` - 텍스트 입력 헬퍼
- `app_opener` - 앱 실행 헬퍼
- `structured_output` - 최종 출력 추출

> 💡 **에이전트별 LLM 최적화 전략**
> 
> **비용 최적화**:
> ```python
> llms={
>     "manager": OpenAI("gpt-4o"),          # 계획은 정확해야 → 고급 모델
>     "executor": Gemini("gemini-flash"),    # 단순 선택 → 저렴한 모델
>     "codeact": Gemini("gemini-flash"),     # 코드 생성 → 중간 모델
>     "text_manipulator": Gemini("gemini-flash"),  # 텍스트 → 저렴
>     "app_opener": OpenAI("gpt-4o-mini"),   # 앱 이름 → 최저가
> }
> ```
> 
> **성능 최적화**:
> ```python
> llms={
>     "manager": OpenAI("gpt-4o"),          # 최고 성능
>     "executor": Gemini("gemini-2.5-pro"), # 높은 정확도
>     "codeact": Gemini("gemini-2.5-pro"),  # 복잡한 코드
>     # 나머지는 기본값
> }
> ```
> 
> **속도 최적화**:
> ```python
> llms = Gemini("gemini-2.5-flash")  # 모든 역할에 최고속 모델
> ```

---

## 커스텀 도구

```python
def my_tool(param: str) -> str:
    """도구 설명."""
    return f"결과: {param}"

agent = DroidAgent(
    goal="...",
    custom_tools={
        "my_tool": {
            "signature": "my_tool(param: str) -> str",
            "description": "도구 설명",
            "function": my_tool
        }
    }
)
```

> 💡 **커스텀 도구 실전 예시**
> 
> **API 호출 도구**:
> ```python
> import requests
> 
> def get_weather(city: str) -> str:
>     """도시의 현재 날씨를 가져옵니다."""
>     response = requests.get(f"https://api.weather.com/{city}")
>     return response.json()["temperature"]
> 
> custom_tools={
>     "get_weather": {
>         "signature": "get_weather(city: str) -> str",
>         "description": "특정 도시의 현재 날씨 정보를 가져옵니다",
>         "function": get_weather
>     }
> }
> 
> # 사용: "서울 날씨 확인하고 카카오톡으로 친구에게 알려줘"
> ```
> 
> **데이터 처리 도구**:
> ```python
> def analyze_csv(file_path: str) -> dict:
>     """CSV 파일을 분석합니다."""
>     import pandas as pd
>     df = pd.read_csv(file_path)
>     return {
>         "rows": len(df),
>         "columns": list(df.columns),
>         "summary": df.describe().to_dict()
>     }
> ```

---

## 자격 증명

### 딕셔너리 형식 (권장)
```python
agent = DroidAgent(
    goal="...",
    credentials={
        "USERNAME": "alice@example.com",
        "PASSWORD": "secret123"
    }
)
# 에이전트가 get_username(), get_password() 호출 가능
```

### Config 형식
```python
from droidrun.config_manager import DroidrunConfig, CredentialsConfig

config = DroidrunConfig(
    credentials=CredentialsConfig(
        enabled=True,
        file_path="config/credentials.yaml"
    )
)

agent = DroidAgent(
    goal="...",
    config=config
)
```

> 💡 **자격 증명 관리 베스트 프랙티스**
> 
> **개발 환경**:
> ```python
> # 딕셔너리로 직접 전달 (빠른 테스트)
> credentials={"USER": "test@example.com", "PASS": "test123"}
> ```
> 
> **프로덕션 환경**:
> ```python
> # 환경 변수 사용
> import os
> credentials={
>     "USERNAME": os.getenv("APP_USERNAME"),
>     "PASSWORD": os.getenv("APP_PASSWORD")
> }
> ```
> 
> **엔터프라이즈 환경**:
> ```python
> # 시크릿 관리 서비스 통합
> from vault_client import get_secret
> credentials={
>     "USERNAME": get_secret("app/username"),
>     "PASSWORD": get_secret("app/password")
> }
> ```

---

## 커스텀 변수

```python
agent = DroidAgent(
    goal="...",
    variables={
        "api_url": "https://api.example.com",
        "user_id": "12345",
        "custom_data": {"key": "value"}
    }
)
# shared_state.custom_variables에서 액세스
```

> 💡 **변수 활용 시나리오**
> 
> **설정값 전달**:
> ```python
> variables={
>     "api_url": "https://api.production.com",
>     "timeout": 30,
>     "retry_count": 3
> }
> ```
> 
> **동적 데이터**:
> ```python
> variables={
>     "today": datetime.now().strftime("%Y-%m-%d"),
>     "user_name": current_user.name,
>     "session_id": generate_session_id()
> }
> ```
> 
> **환경별 설정**:
> ```python
> env = "production"  # or "development"
> variables={
>     "api_url": f"https://api.{env}.com",
>     "debug": env == "development"
>> }
> ```

---

## 구조화된 출력

```python
from pydantic import BaseModel

class FlightInfo(BaseModel):
    airline: str
    flight_number: str
    confirmation_code: str

agent = DroidAgent(
    goal="항공편 예약하고 세부 정보 추출하기",
    output_model=FlightInfo
)
result = await agent.run()
print(result.structured_output.airline)  # 타입이 지정된 출력
```

> 📖 **Structured Output이란?**
> 
> **정의**: 자연어 결과를 구조화된 데이터로 자동 변환
> 
> **Pydantic 모델 활용**:
> ```python
> from pydantic import BaseModel, Field
> 
> class UserProfile(BaseModel):
>     name: str = Field(description="사용자 이름")
>     email: str = Field(description="이메일 주소")
>     phone: str = Field(description="전화번호")
>     verified: bool = Field(description="인증 여부")
> 
> agent = DroidAgent(
>     goal="프로필 화면에서 사용자 정보 추출",
>     output_model=UserProfile
> )
> 
> result = await agent.run()
> # 타입 안전성 보장
> user = result.structured_output
> print(user.name)   # str
> print(user.email)  # str
> print(user.verified)  # bool
> ```
> 
> **활용 시나리오**:
> 
> **데이터 수집 자동화**:
> ```python
> class ProductInfo(BaseModel):
>     name: str
>     price: float
>     stock: int
>     rating: float
> 
> # "쇼핑 앱에서 첫 번째 상품 정보 가져오기"
> # → 구조화된 ProductInfo 객체 반환
> ```
> 
> **폼 데이터 추출**:
> ```python
> class FormData(BaseModel):
>     fields: List[str]
>     values: Dict[str, str]
>     is_complete: bool
> 
> # "설정 폼의 모든 필드와 값 추출"
> ```
> 
> **API 응답 생성**:
> ```python
> class APIResponse(BaseModel):
>     status: str
>     data: dict
>     timestamp: str
> 
> # 자동화 결과를 API로 전송
> ```

---

## 커스텀 프롬프트

```python
custom_prompt = """
당신은 전문 모바일 에이전트입니다.
목표: {{ instruction }}
정확하고 효율적으로 작업하세요.
"""

agent = DroidAgent(
    goal="...",
    prompts={
        "codeact_system": custom_prompt,
        "codeact_user": "...",
        "manager_system": "...",
        "executor_system": "...",
        "scripter_system": "..."
    }
)
```

**템플릿 변수:**
- `{{ instruction }}` - 사용자의 목표
- `{{ device_date }}` - 기기 날짜/시간
- `{{ app_card }}` - 앱별 지침
- `{{ state }}` - 기기 상태
- `{{ history }}` - 액션 히스토리

> 💡 **프롬프트 커스터마이징 전략**
> 
> **도메인 특화**:
> ```python
> ecommerce_prompt = """
> 당신은 전자상거래 앱 전문 에이전트입니다.
> 
> 중요 규칙:
> - 결제 전 항상 금액 확인
> - 배송 주소 정확히 입력
> - 쿠폰 적용 가능 여부 체크
> 
> 목표: {{ instruction }}
> 현재 화면: {{ state }}
> """
> ```
> 
> **언어 및 스타일**:
> ```python
> formal_prompt = """
> You are a professional automation agent.
> Task: {{ instruction }}
> Requirements:
> - Verify each action before execution
> - Provide detailed logs
> - Handle errors gracefully
> """
> ```
> 
> **컨텍스트 주입**:
> ```python
> context_prompt = """
> 에이전트 정보:
> - 실행 환경: {{ device_date }}
> - 앱 가이드: {{ app_card }}
> - 이전 작업: {{ history }}
> 
> 현재 작업: {{ instruction }}
> 
> 위 정보를 참고하여 최적의 액션을 선택하세요.
> """
> ```
> 
> **프롬프트 파일 관리**:
> ```python
> # prompts/codeact_system.jinja2
> """
> {{ base_instructions }}
>
> 특수 지침:
> - 앱: {{ app_card }}
> - 날짜: {{ device_date }}
> """
> 
> # Python에서 로드
> with open("prompts/codeact_system.jinja2") as f:
>     custom_prompt = f.read()
> 
> agent = DroidAgent(
>     goal="...",
>     prompts={"codeact_system": custom_prompt}
> )
> ```

---

## 완전한 예시

```python
from droidrun import DroidAgent
from droidrun.config_manager import (
    DroidrunConfig, AgentConfig, CodeActConfig, DeviceConfig, 
    LoggingConfig, TracingConfig
)
from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from pydantic import BaseModel

# 구조화된 출력
class Output(BaseModel):
    name: str
    value: int

# 커스텀 도구
def send_email(to: str, subject: str) -> str:
    """이메일 전송."""
    return f"Sent to {to}"

# 구성 빌드
config = DroidrunConfig(
    agent=AgentConfig(
        max_steps=30,
        reasoning=True,
        after_sleep_action=1.5,
        codeact=CodeActConfig(vision=True, safe_execution=True)
    ),
    device=DeviceConfig(
        serial="emulator-5554",
        platform="android",
        use_tcp=False
    ),
    logging=LoggingConfig(
        debug=True,
        save_trajectory="action"
    ),
    tracing=TracingConfig(enabled=True),
)

agent = DroidAgent(
    goal="복잡한 작업",
    config=config,

    # LLM
    llms={
        "manager": OpenAI(model="gpt-4o"),
        "executor": Gemini(model="models/gemini-2.5-flash"),
        "codeact": Gemini(model="models/gemini-2.5-pro")
    },

    # 커스텀 도구
    custom_tools={
        "send_email": {
            "signature": "send_email(to: str, subject: str) -> str",
            "description": "이메일 전송",
            "function": send_email
        }
    },

    # 자격 증명
    credentials={"USERNAME": "alice", "PASSWORD": "secret"},

    # 변수
    variables={"api_url": "https://api.example.com"},

    # 구조화된 출력
    output_model=Output,

    # 타임아웃
    timeout=600
)

result = await agent.run()
```

> 💡 **완전한 예시 해설**
> 
> **이 구성의 특징**:
> 
> 1. **고급 기능 활성화**:
>    - reasoning=True → Manager-Executor 워크플로
>    - vision=True → 스크린샷 분석
>    - tracing=True → 실행 추적
> 
> 2. **LLM 최적화**:
>    - Manager: GPT-4o (계획)
>    - Executor: Gemini Flash (빠른 선택)
>    - CodeAct: Gemini Pro (정확한 코드)
> 
> 3. **디버깅 친화적**:
>    - debug=True
>    - save_trajectory="action"
>    - 모든 단계 추적 가능
> 
> 4. **확장 가능**:
>    - 커스텀 도구 추가
>    - 자격 증명 관리
>    - 구조화된 출력
> 
> **실무 적용**:
> ```python
> # 프로덕션용으로 수정
> config = DroidrunConfig(
>     agent=AgentConfig(
>         max_steps=30,
>         reasoning=True,
>         after_sleep_action=1.0  # 더 빠르게
>     ),
>     logging=LoggingConfig(
>         debug=False,              # 디버그 로그 끄기
>         save_trajectory="none"    # 궤적 저장 안 함
>     ),
>     tracing=TracingConfig(enabled=False),  # 추적 끄기
> )
> ```

---

## YAML 구성 (CLI)

CLI 사용 시 `config.yaml` 생성:

```yaml
agent:
  max_steps: 15
  reasoning: false
  after_sleep_action: 1.0
  wait_for_stable_ui: 0.3
  prompts_dir: config/prompts

  codeact:
    vision: false
    system_prompt: system.jinja2
    user_prompt: user.jinja2
    safe_execution: false

  manager:
    vision: false
    system_prompt: system.jinja2

  executor:
    vision: false
    system_prompt: system.jinja2

  scripter:
    enabled: true
    max_steps: 10
    execution_timeout: 30.0
    system_prompt_path: system.jinja2
    safe_execution: false

  app_cards:
    enabled: true
    mode: local
    app_cards_dir: config/app_cards
    server_url: null
    server_timeout: 2.0
    server_max_retries: 2

llm_profiles:
  manager:
    provider: GoogleGenAI
    model: models/gemini-2.5-pro
    temperature: 0.2
    kwargs:
      max_tokens: 8192

  executor:
    provider: GoogleGenAI
    model: models/gemini-2.5-flash
    temperature: 0.1
    kwargs:
      max_tokens: 4096

  codeact:
    provider: GoogleGenAI
    model: models/gemini-2.5-pro
    temperature: 0.2
    kwargs:
      max_tokens: 8192

  text_manipulator:
    provider: GoogleGenAI
    model: models/gemini-2.5-flash
    temperature: 0.3

  app_opener:
    provider: OpenAI
    model: gpt-4o-mini
    temperature: 0.0

  scripter:
    provider: GoogleGenAI
    model: models/gemini-2.5-flash
    temperature: 0.1

  structured_output:
    provider: GoogleGenAI
    model: models/gemini-2.5-flash
    temperature: 0.0

device:
  serial: null
  platform: android
  use_tcp: false

telemetry:
  enabled: true

tracing:
  enabled: false

logging:
  debug: false
  save_trajectory: none
  rich_text: false

safe_execution:
  allow_all_imports: false
  allowed_modules: []
  blocked_modules:
    - os
    - sys
    - subprocess
    - shutil
    - pathlib
    - pty
    - fcntl
    - resource
    - pickle
    - shelve
    - marshal
    - imp
    - importlib
    - ctypes
    - code
    - codeop
    - tempfile
    - glob
    - socket
    - socketserver
    - asyncio
  allow_all_builtins: false
  allowed_builtins: []
  blocked_builtins:
    - open
    - compile
    - exec
    - eval
    - __import__
    - breakpoint
    - exit
    - quit
    - input

tools:
  allow_drag: false

credentials:
  enabled: false
  file_path: credentials.yaml
```

> 💡 **YAML 구성 관리 팁**
> 
> **환경별 구성 파일**:
> ```
> config/
>   ├── config.yaml           # 기본 구성
>   ├── config.dev.yaml       # 개발 환경
>   ├── config.test.yaml      # 테스트 환경
>   └── config.prod.yaml      # 프로덕션 환경
> ```
> 
> **사용법**:
> ```bash
> # 개발 환경
> droidrun run "작업" --config config/config.dev.yaml
> 
> # 프로덕션
> droidrun run "작업" --config config/config.prod.yaml
> ```
> 
> **구성 병합**:
> ```yaml
> # config.base.yaml (공통 설정)
> agent:
>   max_steps: 15
>   prompts_dir: config/prompts
> 
> # config.prod.yaml (프로덕션 오버라이드)
> agent:
>   max_steps: 30  # 더 많은 단계 허용
> logging:
>   debug: false
>   save_trajectory: none
> ```

---

## CLI 오버라이드

```bash
# 에이전트 설정 오버라이드
droidrun run "작업" --steps 30 --reasoning --vision

# 기기 오버라이드
droidrun run "작업" --device emulator-5554 --tcp

# LLM 오버라이드 (모든 에이전트에 적용)
droidrun run "작업" --provider GoogleGenAI --model models/gemini-2.5-flash

# 로깅 오버라이드
droidrun run "작업" --debug --save-trajectory action --tracing

# 커스텀 구성 파일
droidrun run "작업" --config /path/to/config.yaml
```

**모든 CLI 플래그:**
- `--config PATH` - 커스텀 구성 파일
- `--device SERIAL` - 기기 시리얼/IP
- `--provider PROVIDER` - LLM 프로바이더 (OpenAI, Ollama, Anthropic, GoogleGenAI, DeepSeek)
- `--model MODEL` - LLM 모델명
- `--temperature FLOAT` - LLM temperature
- `--steps INT` - 최대 단계
- `--base_url URL` - API base URL (Ollama/OpenRouter용)
- `--api_base URL` - API base URL (OpenAI-like용)
- `--vision/--no-vision` - 모든 에이전트의 비전 활성화/비활성화
- `--reasoning/--no-reasoning` - 추론 모드 활성화/비활성화
- `--tracing/--no-tracing` - 추적 활성화/비활성화
- `--debug/--no-debug` - 디버그 로그 활성화/비활성화
- `--tcp/--no-tcp` - TCP 통신 활성화/비활성화
- `--save-trajectory none|step|action` - 궤적 저장 레벨
- `--ios` - iOS 기기에서 실행

> 💡 **CLI 플래그 실전 조합**
> 
> **빠른 테스트**:
> ```bash
> droidrun run "설정 열기"
> # 모든 기본값, 최소 구성
> ```
> 
> **디버깅 모드**:
> ```bash
> droidrun run "복잡한 작업" \
>   --debug \
>   --save-trajectory action \
>   --tracing \
>   --steps 50
> # 모든 정보 캡처
> ```
> 
> **프로덕션 실행**:
> ```bash
> droidrun run "작업" \
>   --config config.prod.yaml \
>   --no-debug \
>   --save-trajectory none \
>   --steps 30
> # 최소 오버헤드
> ```
> 
> **특정 기기 + 모델**:
> ```bash
> droidrun run "작업" \
>   --device emulator-5554 \
>   --provider OpenAI \
>   --model gpt-4o \
>   --vision \
>   --reasoning
> # 고급 모델로 복잡한 작업
> ```
> 
> **iOS 기기**:
> ```bash
> droidrun run "작업" \
>   --ios \
>   --device http://localhost:8100 \
>   --provider GoogleGenAI \
>   --model models/gemini-2.5-flash
> ```
> 
> **빠른 로컬 테스트** (Ollama):
> ```bash
> droidrun run "작업" \
>   --provider Ollama \
>   --model qwen2.5vl:3b \
>   --base_url http://localhost:11434 \
>   --vision
> ```

---

## 환경 변수

환경 변수를 통해 API 키 설정:

```bash
export GOOGLE_API_KEY=your-key
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
export DEEPSEEK_API_KEY=your-key
export DROIDRUN_CONFIG=/path/to/config.yaml  # 커스텀 구성 경로
```

> 💡 **환경 변수 관리 베스트 프랙티스**
> 
> **개발 환경** (.env 파일):
> ```bash
> # .env
> GOOGLE_API_KEY=your-key
> OPENAI_API_KEY=your-key
> DROIDRUN_CONFIG=config/config.dev.yaml
> DROIDRUN_DEVICE=emulator-5554
> ```
> 
> **로드하기**:
> ```python
> from dotenv import load_dotenv
> load_dotenv()
> 
> # 이제 모든 환경 변수 사용 가능
> agent = DroidAgent(goal="...")
> ```
> 
> **프로덕션 환경**:
> ```bash
> # Docker
> docker run -e GOOGLE_API_KEY=$GOOGLE_API_KEY myapp
> 
> # Kubernetes Secret
> kubectl create secret generic droidrun-keys \
>   --from-literal=GOOGLE_API_KEY=your-key
> 
> # CI/CD (GitHub Actions)
> - name: Run DroidRun
>   env:
>     GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
>   run: droidrun run "작업"
> ```
> 
> **환경별 구성**:
> ```bash
> # ~/.zshrc 또는 ~/.bashrc
> 
> # 개발 환경
> alias droidrun-dev='DROIDRUN_CONFIG=config.dev.yaml droidrun'
> 
> # 프로덕션 환경
> alias droidrun-prod='DROIDRUN_CONFIG=config.prod.yaml droidrun'
> 
> # 사용:
> droidrun-dev run "테스트 작업"
> droidrun-prod run "실제 작업"
> ```

---

## 요약

**DroidAgent 구성의 핵심:**

1. **최소 구성**: `goal`만 필수, 나머지는 기본값 사용
2. **계층적 구성**: Config 객체로 모든 설정 그룹화
3. **유연한 LLM**: 단일 또는 에이전트별 LLM 지정
4. **확장 가능**: 커스텀 도구, 자격 증명, 변수 추가
5. **CLI 지원**: YAML 구성 + 명령줄 오버라이드

**권장 워크플로:**

1. **프로토타입**: 최소 구성으로 시작
2. **개발**: YAML 구성 파일 + 환경 변수
3. **최적화**: 에이전트별 LLM 설정
4. **프로덕션**: 환경별 구성 파일 + 시크릿 관리

**다음 단계:**
- [Agent API 문서](./agent)에서 실행 방법 확인
- [빠른 시작 가이드](../quickstart)로 첫 에이전트 실행
- [예제 코드](https://github.com/droidrun/droidrun/tree/main/examples)로 실전 패턴 학습

---