DroidAgent - Android 또는 iOS 기기에서 사용자의 목표를 달성하기 위한 작업 계획 및 실행을 조율하는 래퍼 클래스입니다.

<a id="droidrun.agent.droid.droid_agent.DroidAgent"></a>

## DroidAgent

```python
class DroidAgent(Workflow)
```

사용자의 목표를 달성하기 위해 에이전트들 간의 조율을 담당하는 래퍼 클래스입니다.

**아키텍처:**
- `reasoning=False`일 때: CodeActAgent를 직접 사용하여 즉시 실행
- `reasoning=True`일 때: ManagerAgent(계획) + ExecutorAgent(액션) + ScripterAgent(오프-디바이스 작업) 사용

> 📖 **DroidAgent 아키텍처 이해**
> 
> **Wrapper 클래스란?**
> - 여러 복잡한 에이전트들을 하나의 간단한 인터페이스로 묶어주는 역할
> - 사용자는 DroidAgent만 사용하면, 내부적으로 적절한 에이전트들이 협업
> 
> **두 가지 실행 모드:**
> 
> **Direct 모드** (`reasoning=False`):
> ```
> 사용자 목표 → CodeActAgent → Python 코드 생성 → 실행
> ```
> - 빠름
> - 간단한 작업에 적합
> - 예: "설정 앱 열기", "스크린샷 찍기"
> 
> **Reasoning 모드** (`reasoning=True`):
> ```
> 사용자 목표 → ManagerAgent (계획 수립)
>              ↓
>        ExecutorAgent (단계별 실행)
>              ↓
>        ScripterAgent (필요시 오프-디바이스 작업)
> ```
> - 느림
> - 복잡한 다단계 작업에 적합
> - 예: "카카오톡 열고 홍길동에게 메시지 보내고 확인하기"
> 
> **언제 어떤 모드를 사용할까?**
> - 1-2 단계 작업 → Direct 모드
> - 3단계 이상 또는 조건부 작업 → Reasoning 모드
> - 외부 API 호출 필요 → Reasoning 모드 (ScripterAgent 활용)

<a id="droidrun.agent.droid.droid_agent.DroidAgent.__init__"></a>

#### DroidAgent.\_\_init\_\_

```python
def __init__(
    goal: str,
    config: DroidrunConfig | None = None,
    llms: dict[str, LLM] | LLM | None = None,
    tools: "Tools | None" = None,
    custom_tools: dict | None = None,
    credentials: dict | None = None,
    variables: dict | None = None,
    output_model: Type[BaseModel] | None = None,
    prompts: dict[str, str] | None = None,
    timeout: int = 1000
)
```

DroidAgent 래퍼를 초기화합니다.

**인자(Arguments):**

- `goal` _str_ - 실행할 사용자의 목표 또는 명령
- `config` _DroidrunConfig | None_ - 전체 구성 객체 (llms가 제공되지 않으면 필수). 에이전트 설정, LLM 프로필, 기기 구성 등을 포함합니다.
- `llms` _dict[str, LLM] | LLM | None_ - 선택적 LLM 구성:
  - `dict[str, LLM]`: 에이전트별 LLM, 키: "manager", "executor", "codeact", "text_manipulator", "app_opener", "scripter", "structured_output"
  - `LLM`: 모든 에이전트가 사용할 단일 LLM 인스턴스
  - `None`: config.llm_profiles에서 LLM을 로드합니다
- `tools` _Tools | None_ - 미리 구성된 Tools 인스턴스 (AdbTools 또는 IOSTools). None이면 config에서 도구를 생성합니다.
- `custom_tools` _dict | None_ - 커스텀 도구 정의. 형식: `{"tool_name": {"signature": "...", "description": "...", "function": callable}}`. 자동 생성된 자격 증명 도구와 병합됩니다.
- `credentials` _dict | None_ - 직접 자격 증명 매핑 `{"SECRET_ID": "value"}`. None이면 사용 가능한 경우 config.credentials에서 자격 증명을 로드합니다.
- `variables` _dict | None_ - 실행 중 접근 가능한 커스텀 변수. shared_state.custom_variables에서 사용 가능합니다.
- `output_model` _Type[BaseModel] | None_ - 최종 답변에서 구조화된 출력을 추출하기 위한 Pydantic 모델. 제공되면 최종 답변이 이 모델로 파싱됩니다.
- `prompts` _dict[str, str] | None_ - 기본값을 오버라이드할 커스텀 Jinja2 프롬프트 템플릿. 키: "codeact_system", "codeact_user", "manager_system", "executor_system", "scripter_system". 값: Jinja2 템플릿 문자열 (파일 경로 아님).
- `timeout` _int_ - 워크플로 타임아웃(초) (기본값: 1000)

> 📖 **파라미터 상세 해설**
> 
> **goal** (필수):
> ```python
> # 명확하고 구체적으로 작성
> goal="설정 앱 열기"  # 좋음
> goal="설정"          # 모호함
> 
> # 다단계 작업
> goal="카카오톡 열고 홍길동에게 '안녕하세요' 메시지 보내기"
> 
> # 조건부 작업
> goal="배터리가 20% 이하면 절전 모드 켜기"
> ```
> 
> **config vs llms**:
> - `config`만 제공: LLM 프로필에서 자동 로드 (권장)
> - `llms`만 제공: 에러 (config 필수)
> - 둘 다 제공: llms가 config의 LLM 프로필을 오버라이드
> 
> **custom_tools** (커스텀 도구):
> ```python
> def my_api_call(endpoint: str) -> str:
>     """API를 호출합니다."""
>     return requests.get(endpoint).text
> 
> custom_tools = {
>     "my_api_call": {
>         "signature": "my_api_call(endpoint: str) -> str",
>         "description": "외부 API를 호출하여 데이터를 가져옵니다",
>         "function": my_api_call
>     }
> }
> ```
> 
> **credentials** (자격 증명):
> - 자동으로 `get_username()`, `get_password()` 등의 함수로 변환
> - 에이전트가 실행 중 호출 가능
> 
> **variables** (변수):
> - 에이전트 실행 중 공유되는 컨텍스트
> - 커스텀 도구에서 접근 가능
> 
> **output_model** (구조화된 출력):
> - Pydantic 모델로 결과를 타입 안전하게 파싱
> - API 통합, 데이터 검증에 유용
> 
> **timeout** (타임아웃):
> - 기본 1000초 (약 16분)
> - 복잡한 작업: 1800-3600초
> - 간단한 작업: 300-600초

**기본 초기화 패턴 (권장):**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 기본 구성으로 초기화
config = DroidrunConfig()

# 에이전트 생성 (LLM은 config.llm_profiles에서 로드됨)
agent = DroidAgent(
    goal="Chrome 열고 Droidrun 검색하기",
    config=config
)

# 에이전트 실행
result = await agent.run()
```

> 💡 **기본 패턴 사용 시나리오**
> 
> **장점**:
> - 가장 간단함
> - 빠른 프로토타이핑
> - 기본 설정으로 대부분 작동
> 
> **적합한 경우**:
> - 처음 DroidRun 사용
> - 빠른 테스트
> - 간단한 자동화

**YAML에서 로드 (선택사항):**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# config.yaml에서 구성 로드
config = DroidrunConfig.from_yaml("config.yaml")

# 에이전트 생성 (LLM은 config.llm_profiles에서 로드됨)
agent = DroidAgent(
    goal="Chrome 열고 Droidrun 검색하기",
    config=config
)

# 에이전트 실행
result = await agent.run()
```

> 💡 **YAML 구성 사용 시나리오**
> 
> **장점**:
> - 환경별 설정 관리 (dev, test, prod)
> - 버전 관리 용이
> - 팀원 간 설정 공유
> 
> **config.yaml 예시**:
> ```yaml
> agent:
>   max_steps: 30
>   reasoning: true
> 
> llm_profiles:
>   manager:
>     provider: OpenAI
>     model: gpt-4o
>   executor:
>     provider: GoogleGenAI
>     model: models/gemini-2.5-flash
> 
> device:
>   serial: emulator-5554
> ```

**커스텀 LLM 딕셔너리 패턴:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

# 구성 초기화
config = DroidrunConfig()

# 커스텀 LLM 생성
llms = {
    "manager": Anthropic(model="claude-sonnet-4-5-latest", temperature=0.2),
    "executor": Anthropic(model="claude-sonnet-4-5-latest", temperature=0.1),
    "codeact": OpenAI(model="gpt-4o", temperature=0.2),
    "text_manipulator": OpenAI(model="gpt-4o-mini", temperature=0.3),
    "app_opener": OpenAI(model="gpt-4o-mini", temperature=0.0),
    "scripter": OpenAI(model="gpt-4o", temperature=0.1),
    "structured_output": OpenAI(model="gpt-4o-mini", temperature=0.0),
}

# 커스텀 LLM으로 에이전트 생성
agent = DroidAgent(
    goal="John에게 메시지 보내기",
    llms=llms,
    config=config
)

result = await agent.run()
```

> 💡 **에이전트별 LLM 최적화 전략**
> 
> **역할별 모델 선택 기준**:
> 
> **manager** (계획 수립):
> - 고급 모델 권장 (GPT-4o, Claude Sonnet)
> - temperature: 0.2 (안정적 계획)
> - 이유: 전체 작업의 방향 결정
> 
> **executor** (액션 선택):
> - 중간 모델 (Gemini Flash, Claude Sonnet)
> - temperature: 0.1 (정확한 선택)
> - 이유: 빠른 응답 + 정확성
> 
> **codeact** (코드 생성):
> - 고급 모델 (GPT-4o, Gemini Pro)
> - temperature: 0.2
> - 이유: 정확한 Python 코드 필요
> 
> **text_manipulator** (텍스트 입력):
> - 저렴한 모델 (GPT-4o-mini, Gemini Flash)
> - temperature: 0.3 (약간의 변형 허용)
> - 이유: 단순 텍스트 처리
> 
> **app_opener** (앱 실행):
> - 최저가 모델 (GPT-4o-mini)
> - temperature: 0.0 (정확한 패키지명)
> - 이유: 매우 단순한 작업
> 
> **scripter** (오프-디바이스 스크립트):
> - 고급 모델 (GPT-4o)
> - temperature: 0.1
> - 이유: API 호출, 데이터 처리 등 복잡한 작업
> 
> **structured_output** (출력 추출):
> - 중간 모델 (GPT-4o-mini, Gemini Flash)
> - temperature: 0.0 (정확한 파싱)
> - 이유: JSON 스키마 준수

**단일 LLM 패턴:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig
from llama_index.llms.openai import OpenAI

# 구성 초기화
config = DroidrunConfig()

# 모든 에이전트가 사용할 동일한 LLM
llm = OpenAI(model="gpt-4o", temperature=0.2)

agent = DroidAgent(
    goal="스크린샷 찍고 저장하기",
    llms=llm,
    config=config
)

result = await agent.run()
```

> 💡 **단일 LLM 사용 시나리오**
> 
> **장점**:
> - 설정 간단
> - 비용 예측 쉬움
> - 일관된 동작
> 
> **단점**:
> - 모든 역할에 같은 모델
> - 비용 최적화 어려움
> - 성능 최적화 제한
> 
> **적합한 경우**:
> - 프로토타입 단계
> - 단순한 자동화
> - 빠른 테스트
> - 비용보다 개발 속도 우선

**커스텀 도구 및 자격 증명:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 구성 초기화
config = DroidrunConfig()

# 커스텀 도구 정의
def search_database(query: str) -> str:
    """로컬 데이터베이스를 검색합니다."""
    # 구현 내용
    return f"검색 결과: {query}"

custom_tools = {
    "search_database": {
        "signature": "search_database(query: str) -> str",
        "description": "로컬 데이터베이스에서 정보를 검색합니다",
        "function": search_database
    }
}

# 자격 증명 직접 제공
credentials = {
    "GMAIL_USERNAME": "user@gmail.com",
    "GMAIL_PASSWORD": "secret123"
}

agent = DroidAgent(
    goal="데이터베이스 검색하고 결과 이메일로 보내기",
    config=config,
    custom_tools=custom_tools,
    credentials=credentials
)

result = await agent.run()
```

> 💡 **커스텀 도구 실전 예시**
> 
> **API 통합 도구**:
> ```python
> import requests
> 
> def get_weather(city: str) -> str:
>     """날씨 정보를 가져옵니다."""
>     response = requests.get(f"https://api.weather.com/{city}")
>     return f"온도: {response.json()['temp']}°C"
> 
> custom_tools = {
>     "get_weather": {
>         "signature": "get_weather(city: str) -> str",
>         "description": "특정 도시의 현재 날씨를 조회합니다",
>         "function": get_weather
>     }
> }
> 
> # 사용: "서울 날씨 확인하고 카카오톡으로 알려줘"
> ```
> 
> **데이터 처리 도구**:
> ```python
> import pandas as pd
> 
> def analyze_sales(file_path: str) -> dict:
>     """매출 데이터를 분석합니다."""
>     df = pd.read_csv(file_path)
>     return {
>         "total": df['amount'].sum(),
>         "average": df['amount'].mean(),
>         "top_product": df.groupby('product')['amount'].sum().idxmax()
>     }
> 
> custom_tools = {
>     "analyze_sales": {
>         "signature": "analyze_sales(file_path: str) -> dict",
>         "description": "매출 CSV 파일을 분석하여 통계를 반환합니다",
>         "function": analyze_sales
>     }
> }
> ```
> 
> **자격 증명 활용**:
> ```python
> # 에이전트가 자동으로 생성하는 함수들:
> # get_gmail_username() → "user@gmail.com"
> # get_gmail_password() → "secret123"
> 
> # goal에서 사용:
> goal="Gmail 앱 열고 로그인하기"
> # 에이전트가 자동으로 get_gmail_username(), get_gmail_password() 호출
> ```

**구조화된 출력 추출:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig
from pydantic import BaseModel, Field

# 구성 초기화
config = DroidrunConfig()

# 출력 스키마 정의
class WeatherInfo(BaseModel):
    """날씨 정보."""
    temperature: float = Field(description="섭씨 온도")
    condition: str = Field(description="날씨 상태")
    humidity: int = Field(description="습도 퍼센트")

agent = DroidAgent(
    goal="날씨 앱 열고 현재 날씨 가져오기",
    config=config,
    output_model=WeatherInfo
)

result = await agent.run()

# 구조화된 출력 접근
if result.success and result.structured_output:
    weather = result.structured_output  # WeatherInfo 객체
    print(f"온도: {weather.temperature}°C")
    print(f"상태: {weather.condition}")
```

> 💡 **구조화된 출력 활용 시나리오**
> 
> **데이터 수집 자동화**:
> ```python
> class ProductInfo(BaseModel):
>     name: str
>     price: float
>     stock: int
>     rating: float
> 
> agent = DroidAgent(
>     goal="쇼핑 앱에서 첫 번째 상품 정보 가져오기",
>     config=config,
>     output_model=ProductInfo
> )
> 
> result = await agent.run()
> product = result.structured_output
> 
> # 데이터베이스에 저장하거나 API로 전송
> save_to_database(product)
> ```
> 
> **폼 데이터 추출**:
> ```python
> class FormData(BaseModel):
>     name: str
>     email: str
>     phone: str
>     address: str
> 
> agent = DroidAgent(
>     goal="프로필 화면에서 사용자 정보 추출",
>     config=config,
>     output_model=FormData
> )
> ```
> 
> **테스트 검증**:
> ```python
> class LoginResult(BaseModel):
>     success: bool
>     error_message: str = None
> 
> agent = DroidAgent(
>     goal="앱에 로그인 시도",
>     config=config,
>     output_model=LoginResult
> )
> 
> result = await agent.run()
> assert result.structured_output.success, "로그인 실패"
> ```

<a id="droidrun.agent.droid.droid_agent.DroidAgent.run"></a>

#### DroidAgent.run

```python
async def run(*args, **kwargs) -> ResultEvent
```

DroidAgent 워크플로를 실행합니다.

**반환값(Returns):**

- `ResultEvent` - 다음 속성을 가진 결과 객체:
  - `success` (bool): 작업이 성공적으로 완료되면 True
  - `reason` (str): 성공 메시지 또는 실패 이유
  - `steps` (int): 실행된 단계 수
  - `structured_output` (Any): 파싱된 Pydantic 모델 (output_model이 제공된 경우, 그렇지 않으면 None)

**사용법:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 구성 초기화
config = DroidrunConfig()

# 에이전트 생성 및 실행
agent = DroidAgent(goal="...", config=config)
result = await agent.run()

print(f"성공: {result.success}")
print(f"이유: {result.reason}")
print(f"단계: {result.steps}")
```

> 💡 **결과 처리 패턴**
> 
> **기본 처리**:
> ```python
> result = await agent.run()
> 
> if result.success:
>     print(f"✓ 성공: {result.reason}")
>     print(f"실행 단계: {result.steps}")
> else:
>     print(f"✗ 실패: {result.reason}")
> ```
> 
> **구조화된 출력과 함께**:
> ```python
> result = await agent.run()
> 
> if result.success and result.structured_output:
>     data = result.structured_output
>     print(f"추출된 데이터: {data}")
>     # 타입 안전성 보장
>     process_data(data)  # IDE 자동완성 지원
> ```
> 
> **에러 처리**:
> ```python
> try:
>     result = await agent.run()
>     if not result.success:
>         log_error(f"에이전트 실패: {result.reason}")
>         send_alert(result.reason)
> except TimeoutError:
>     print("타임아웃 발생")
> except Exception as e:
>     print(f"예외 발생: {e}")
> ```

**이벤트 스트리밍:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 구성 초기화
config = DroidrunConfig()

agent = DroidAgent(goal="...", config=config)

# 이벤트가 발생할 때마다 스트리밍
async for event in agent.run_event_stream():
    if isinstance(event, ManagerInputEvent):
        print("Manager가 계획 중...")
    elif isinstance(event, ExecutorInputEvent):
        print("Executor가 액션 수행 중...")
    elif isinstance(event, TapActionEvent):
        print(f"요소 탭: ({event.x}, {event.y})")
    elif isinstance(event, ResultEvent):
        # 최종 결과
        print(f"성공: {event.success}")
        print(f"이유: {event.reason}")
```

> 💡 **이벤트 스트리밍 활용**
> 
> **실시간 진행 상황 표시**:
> ```python
> async for event in agent.run_event_stream():
>     if isinstance(event, ManagerPlanEvent):
>         print(f"📋 계획: {event.plan}")
>     elif isinstance(event, TapActionEvent):
>         print(f"👆 탭: ({event.x}, {event.y})")
>     elif isinstance(event, InputTextActionEvent):
>         print(f"⌨️  입력: {event.text}")
>     elif isinstance(event, SwipeActionEvent):
>         print(f"👉 스와이프: {event.direction}")
> ```
> 
> **로깅 및 모니터링**:
> ```python
> events_log = []
> 
> async for event in agent.run_event_stream():
>     events_log.append({
>         "type": type(event).__name__,
>         "timestamp": datetime.now(),
>         "data": event.__dict__
>     })
>     
>     # 실시간 로그 전송
>     send_to_monitoring_system(event)
> ```
> 
> **디버깅**:
> ```python
> async for event in agent.run_event_stream():
>     print(f"[{type(event).__name__}] {event}")
>     
>     if isinstance(event, ExecutorActionResultEvent):
>         if "error" in event.result.lower():
>             print(f"⚠️  액션 실패: {event.result}")
>             # 스크린샷 캡처하거나 추가 디버깅
> ```

## 이벤트 타입

DroidAgent는 실행 중 다양한 이벤트를 발생시킵니다:

**워크플로 이벤트:**
- `StartEvent` - 워크플로 시작됨
- `ManagerInputEvent` - Manager 계획 단계 시작됨
- `ManagerContextEvent` - Manager가 계획을 위한 컨텍스트 받음
- `ManagerResponseEvent` - Manager 중간 응답
- `ManagerPlanEvent` - Manager가 계획 생성함
- `ManagerPlanDetailsEvent` - Manager 계획 세부사항
- `ExecutorInputEvent` - Executor 액션 단계 시작됨
- `ExecutorContextEvent` - Executor가 컨텍스트 받음
- `ExecutorResponseEvent` - Executor 중간 응답
- `ExecutorActionEvent` - Executor 액션 세부사항
- `ExecutorActionResultEvent` - Executor 액션 결과 세부사항
- `ExecutorResultEvent` - Executor가 액션 완료함
- `ScripterExecutorInputEvent` - ScripterAgent 시작됨
- `ScripterExecutorResultEvent` - ScripterAgent 완료됨
- `CodeActExecuteEvent` - CodeActAgent 시작됨 (direct 모드)
- `CodeActResultEvent` - CodeActAgent 완료됨
- `FinalizeEvent` - 워크플로 마무리 중
- `StopEvent` - 워크플로 완료됨

**액션 이벤트:**
- `TapActionEvent` - UI 요소 탭됨
- `SwipeActionEvent` - 스와이프 제스처 수행됨
- `DragActionEvent` - 드래그 제스처 수행됨
- `InputTextActionEvent` - 텍스트 입력
- `KeyPressActionEvent` - 키 누르기 액션
- `StartAppEvent` - 앱 실행됨

**상태 이벤트:**
- `ScreenshotEvent` - 스크린샷 캡처됨
- `RecordUIStateEvent` - UI 상태 기록됨
- `MacroEvent` - 매크로 액션 기록됨

> 📖 **이벤트 타입 분류 이해**
> 
> **워크플로 이벤트** (에이전트 내부 작동):
> - 에이전트들 간의 통신과 상태 전환
> - 계획 수립, 액션 선택, 스크립트 실행 등
> - 디버깅과 워크플로 이해에 유용
> 
> **액션 이벤트** (실제 기기 조작):
> - 사용자가 볼 수 있는 실제 동작
> - 탭, 스와이프, 텍스트 입력 등
> - 테스트 검증과 동작 재현에 유용
> 
> 
> **상태 이벤트** (상태 기록):
> - 스크린샷 캡처, UI 상태 기록
> - 궤적 재생과 분석에 유용
> - 매크로 녹화 기능
> 
> **이벤트 활용 시나리오**:
> 
> **진행률 표시**:
> ```python
> total_steps = 0
> current_step = 0
> 
> async for event in agent.run_event_stream():
>     if isinstance(event, ManagerPlanEvent):
>         total_steps = len(event.plan)
>     elif isinstance(event, ExecutorResultEvent):
>         current_step += 1
>         print(f"진행률: {current_step}/{total_steps}")
> ```
> 
> **액션 히스토리 기록**:
> ```python
> actions = []
> 
> async for event in agent.run_event_stream():
>     if isinstance(event, (TapActionEvent, SwipeActionEvent, InputTextActionEvent)):
>         actions.append({
>             "type": type(event).__name__,
>             "timestamp": datetime.now(),
>             "details": event.__dict__
>         })
> 
> # 나중에 재현 가능
> ```
> 
> **실패 지점 파악**:
> ```python
> async for event in agent.run_event_stream():
>     if isinstance(event, ResultEvent):
>         if not event.success:
>             print(f"실패한 단계: {event.steps}")
>             print(f"실패 이유: {event.reason}")
>             # 마지막 스크린샷 확인
> ```

## 구성

DroidAgent는 계층적 구성 시스템을 사용합니다. 자세한 내용은 [구성 가이드](/v4/sdk/configuration)를 참조하세요.

**주요 구성 옵션:**

```yaml
agent:
  max_steps: 15           # 최대 실행 단계
  reasoning: false        # Manager/Executor 워크플로 활성화

  codeact:
    vision: false         # 스크린샷 분석 활성화
    safe_execution: false # 코드 실행 제한

  manager:
    vision: false         # 스크린샷 분석 활성화

  executor:
    vision: false         # 스크린샷 분석 활성화

device:
  serial: null            # 기기 시리얼 (null = 자동 감지)
  platform: android       # "android" 또는 "ios"
  use_tcp: false          # TCP vs content provider

logging:
  debug: false            # 디버그 로깅
  save_trajectory: none   # 궤적 저장: "none", "step", "action"

tracing:
  enabled: false          # Arize Phoenix 추적
```

> 📖 **구성 옵션 상세 해설**
> 
> **agent.max_steps** (최대 단계):
> - 무한 루프 방지
> - 간단한 작업: 5-15 단계
> - 복잡한 작업: 30-50 단계
> - 매우 복잡: 100+ 단계
> ```python
> # 복잡한 작업을 위한 설정
> config = DroidrunConfig(
>     agent=AgentConfig(max_steps=50)
> )
> ```
> 
> **agent.reasoning** (추론 모드):
> - `false`: CodeAct 직접 모드 (빠름)
> - `true`: Manager → Executor 워크플로 (정확함)
> ```python
> # 복잡한 작업
> config = DroidrunConfig(
>     agent=AgentConfig(reasoning=True)
> )
> ```
> 
> **vision** (비전 모드):
> - `false`: 텍스트 기반 UI 트리만 (저렴함)
> - `true`: 스크린샷 포함 (비용 증가)
> ```python
> # 시각적 요소 인식 필요 시
> config = DroidrunConfig(
>     agent=AgentConfig(
>         codeact=CodeActConfig(vision=True)
>     )
> )
> ```
> 
> **safe_execution** (안전 실행):
> - `false`: 모든 Python 코드 허용
> - `true`: 위험한 imports/builtins 제한
> ```python
> # 프로덕션 환경
> config = DroidrunConfig(
>     agent=AgentConfig(
>         codeact=CodeActConfig(safe_execution=True)
>     )
> )
> ```
> 
> **device.serial** (기기 시리얼):
> - `null`: 자동으로 첫 번째 기기 선택
> - `"emulator-5554"`: 특정 에뮬레이터
> - `"ABC123DEF"`: USB 연결 기기
> - `"192.168.1.100:5555"`: 무선 ADB
> 
> **device.use_tcp** (TCP 통신):
> - `false`: Content provider 모드 (안정적, 느림)
> - `true`: TCP 모드 (빠름, 포트 포워딩 필요)
> ```bash
> # TCP 사용 시 사전 설정
> adb forward tcp:8080 tcp:8080
> ```
> 
> **logging.save_trajectory** (궤적 저장):
> - `"none"`: 저장 안 함 (빠름)
> - `"step"`: 단계별 저장 (중간)
> - `"action"`: 액션별 저장 (디버깅, 느림)
> ```python
> # 디버깅 모드
> config = DroidrunConfig(
>     logging=LoggingConfig(
>         debug=True,
>         save_trajectory="action"
>     )
> )
> ```
> 
> **tracing.enabled** (추적):
> - Arize Phoenix 통합
> - LLM 호출 추적 및 분석
> - 성능 모니터링

## 고급 사용법

**커스텀 Tools 인스턴스:**

```python
from droidrun import DroidAgent, DeviceConfig
from droidrun.config_manager import DroidrunConfig

# 기기 설정으로 구성 초기화
device_config = DeviceConfig(serial="emulator-5554", use_tcp=True)
config = DroidrunConfig(device=device_config)

agent = DroidAgent(
    goal="설정 열기",
    config=config,
)

result = await agent.run()
```

> 💡 **커스텀 Tools 시나리오**
> 
> **특정 기기 지정**:
> ```python
> # 여러 기기 중 하나 선택
> devices = ["emulator-5554", "emulator-5556"]
> 
> for device_serial in devices:
>     config = DroidrunConfig(
>         device=DeviceConfig(serial=device_serial)
>     )
>     agent = DroidAgent(goal="테스트 실행", config=config)
>     result = await agent.run()
>     print(f"{device_serial}: {result.success}")
> ```
> 
> **TCP 고속 통신**:
> ```python
> # 포트 포워딩 설정 후 TCP 사용
> import subprocess
> subprocess.run(["adb", "forward", "tcp:8080", "tcp:8080"])
> 
> config = DroidrunConfig(
>     device=DeviceConfig(
>         serial="emulator-5554",
>         use_tcp=True  # 고속 모드
>     )
> )
> ```
> 
> **iOS 기기**:
> ```python
> config = DroidrunConfig(
>     device=DeviceConfig(
>         platform="ios",
>         serial="http://localhost:8100"
>     )
> )
> 
> agent = DroidAgent(goal="iOS 작업", config=config)
> ```

**커스텀 변수:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 구성 초기화
config = DroidrunConfig()

agent = DroidAgent(
    goal="컨텍스트를 사용하여 작업 완료",
    config=config,
    variables={
        "user_name": "Alice",
        "project_id": "12345",
        "api_endpoint": "https://api.example.com"
    }
)

result = await agent.run()
```

> 💡 **커스텀 변수 활용 패턴**
> 
> **환경별 설정**:
> ```python
> env = "production"  # or "development"
> 
> agent = DroidAgent(
>     goal="배포 작업",
>     config=config,
>     variables={
>         "env": env,
>         "api_url": f"https://api.{env}.example.com",
>         "timeout": 30 if env == "production" else 60,
>         "debug": env == "development"
>     }
> )
> ```
> 
> **사용자 컨텍스트**:
> ```python
> agent = DroidAgent(
>     goal="개인화된 작업",
>     config=config,
>     variables={
>         "user_name": current_user.name,
>         "user_email": current_user.email,
>         "preferences": current_user.preferences,
>         "last_login": current_user.last_login.isoformat()
>     }
> )
> ```
> 
> **동적 데이터**:
> ```python
> from datetime import datetime
> 
> agent = DroidAgent(
>     goal="일일 리포트 생성",
>     config=config,
>     variables={
>         "today": datetime.now().strftime("%Y-%m-%d"),
>         "report_id": generate_report_id(),
>         "recipients": get_recipients_list()
>     }
> )
> ```
> 
> **커스텀 도구에서 변수 사용**:
> ```python
> def custom_tool(param: str) -> str:
>     # shared_state.custom_variables에서 접근
>     api_url = shared_state.custom_variables["api_endpoint"]
>     user_name = shared_state.custom_variables["user_name"]
>     
>     response = requests.post(
>         f"{api_url}/action",
>         json={"user": user_name, "param": param}
>     )
>     return response.text
> ```

변수는 실행 전체에서 shared_state.custom_variables에서 접근 가능하며 커스텀 도구나 스크립트에서 참조할 수 있습니다.

**커스텀 프롬프트:**

```python
from droidrun import DroidAgent
from droidrun.config_manager import DroidrunConfig

# 구성 초기화
config = DroidrunConfig()

# 커스텀 Jinja2 템플릿으로 기본 프롬프트 오버라이드
custom_prompts = {
    "codeact_system": "당신은 {{ platform }} 기기를 위한 전문 에이전트입니다...",
    "manager_system": "당신은 계획 에이전트입니다. 목표: {{ instruction }}..."
}

agent = DroidAgent(
    goal="특화된 작업 완료",
    config=config,
    prompts=custom_prompts
)

result = await agent.run()
```

사용 가능한 프롬프트 키: "codeact_system", "codeact_user", "manager_system", "executor_system", "scripter_system"

> 💡 **커스텀 프롬프트 고급 활용**
> 
> **도메인 특화 프롬프트**:
> ```python
> ecommerce_prompts = {
>     "codeact_system": """
>     당신은 전자상거래 앱 전문 자동화 에이전트입니다.
>     
>     중요 규칙:
>     - 결제 전 항상 금액 확인
>     - 배송 주소 정확히 입력
>     - 쿠폰 적용 가능 여부 체크
>     - 재고 확인 필수
>     
>     플랫폼: {{ platform }}
>     목표: {{ instruction }}
>     """,
>     "manager_system": """
>     전자상거래 작업 계획 수립:
>     1. 상품 검색 및 확인
>     2. 장바구니 추가
>     3. 결제 정보 입력
>     4. 최종 확인 및 주문
>     
>     목표: {{ instruction }}
>     """
> }
> ```
> 
> **다국어 프롬프트**:
> ```python
> korean_prompts = {
>     "codeact_system": """
>     당신은 한국어 Android 앱 자동화 전문가입니다.
>     한글 UI 요소를 정확히 인식하고 처리하세요.
>     
>     목표: {{ instruction }}
>     현재 날짜: {{ device_date }}
>     """,
>     "executor_system": """
>     다음 단계를 실행하세요: {{ step }}
>     
>     한글 텍스트 입력 시 주의:
>     - 특수문자 정확히 입력
>     - 자동완성 고려
>     """
> }
> ```
> 
> **Jinja2 템플릿 변수**:
> ```python
> custom_prompts = {
>     "codeact_system": """
>     플랫폼: {{ platform }}           # "android" 또는 "ios"
>     목표: {{ instruction }}          # 사용자 goal
>     날짜: {{ device_date }}          # 기기 현재 시간
>     앱 카드: {{ app_card }}           # 현재 앱 가이드
>     상태: {{ state }}                 # 기기 UI 상태
>     히스토리: {{ history }}           # 이전 액션들
>     """
> }
> ```
> 
> **프롬프트 파일 관리**:
> ```python
> # prompts/ecommerce_system.jinja2
> with open("prompts/ecommerce_system.jinja2") as f:
>     ecommerce_system = f.read()
> 
> with open("prompts/ecommerce_manager.jinja2") as f:
>     ecommerce_manager = f.read()
> 
> agent = DroidAgent(
>     goal="상품 구매",
>     config=config,
>     prompts={
>         "codeact_system": ecommerce_system,
>         "manager_system": ecommerce_manager
>     }
> )
> ```

## 주의사항

- **Config 요구사항**: `config` 또는 `llms` 중 하나는 반드시 제공되어야 합니다. `llms`가 제공되지 않으면 프로필에서 LLM을 로드하기 위해 `config`가 필요합니다.
- **Vision 모드**: vision 활성화(agent_config.*.vision = True)는 스크린샷이 LLM에 전송되므로 토큰 사용량을 증가시킵니다.
- **Reasoning 모드**: `reasoning=True`는 복잡한 계획을 위해 Manager/Executor 워크플로를 사용합니다. `reasoning=False`는 직접 실행을 위해 CodeActAgent를 사용합니다.
- **Safe execution**: 활성화되면 CodeActAgent와 ScripterAgent에서 imports와 builtins를 제한합니다 (safe_execution 구성 참조).
- **Timeout**: 기본값은 1000초입니다. 장시간 실행 작업의 경우 증가시키세요.
- **Credentials**: 자격 증명은 자동으로 커스텀 도구로 주입됩니다 (예: `get_username()`, `get_password()`).

> 📖 **주의사항 상세 해설**
> 
> **1. Config vs LLMs 요구사항**:
> ```python
> # ✅ 올바른 패턴
> config = DroidrunConfig()
> agent = DroidAgent(goal="...", config=config)
> 
> # ✅ 올바른 패턴
> agent = DroidAgent(goal="...", llms=llm, config=config)
> 
> # ❌ 잘못된 패턴
> agent = DroidAgent(goal="...", llms=llm)  # config 없음 → 에러
> ```
> 
> **2. Vision 모드 비용 고려**:
> ```python
> # 토큰 사용량 예시 (GPT-4o 기준)
> 
> # Vision 모드 OFF (텍스트만):
> # - UI 트리: ~1000-3000 토큰
> # - 비용: ~$0.01-0.03 per request
> 
> # Vision 모드 ON (텍스트 + 스크린샷):
> # - UI 트리: ~1000-3000 토큰
> # - 스크린샷: ~2000-4000 토큰 (해상도에 따라)
> # - 비용: ~$0.03-0.07 per request
> 
> # 15단계 작업 기준:
> # Vision OFF: $0.15-0.45
> # Vision ON: $0.45-1.05
> ```
> 
> **Vision 모드 선택 기준**:
> ```python
> # Vision 필요:
> goal = "빨간색 버튼 클릭"  # 색상 인식
> goal = "이미지에서 텍스트 읽기"  # OCR 필요
> goal = "아이콘 찾아서 클릭"  # 시각적 요소
> 
> # Vision 불필요:
> goal = "설정 앱 열기"  # 텍스트 기반
> goal = "Wi-Fi 켜기"  # UI 트리로 충분
> goal = "메시지 입력"  # 텍스트 작업
> ```
> 
> **3. Reasoning 모드 선택**:
> ```python
> # Direct 모드 (reasoning=False):
> # - 속도: 빠름 (1-2분)
> # - 적합: 단순 작업 (1-3 단계)
> # - 예: "설정 열기", "앱 실행"
> 
> # Reasoning 모드 (reasoning=True):
> # - 속도: 느림 (3-10분)
> # - 적합: 복잡한 작업 (5+ 단계)
> # - 예: "이메일 보내고 확인하기"
> 
> config = DroidrunConfig(
>     agent=AgentConfig(
>         reasoning=False if simple_task else True
>     )
> )
> ```
> 
> **4. Safe Execution 설정**:
> ```python
> # 개발 환경 (모든 코드 허용):
> config = DroidrunConfig(
>     agent=AgentConfig(
>         codeact=CodeActConfig(safe_execution=False)
>     )
> )
> 
> # 프로덕션 환경 (제한):
> config = DroidrunConfig(
>     agent=AgentConfig(
>         codeact=CodeActConfig(safe_execution=True)
>     ),
>     safe_execution=SafeExecutionConfig(
>         allowed_modules=["json", "requests", "datetime"],
>         blocked_modules=["os", "sys", "subprocess"]
>     )
> )
> ```
> 
> **5. Timeout 설정**:
> ```python
> # 작업 복잡도별 권장 timeout:
> 
> # 간단한 작업 (1-5 단계):
> timeout = 300  # 5분
> 
> # 보통 작업 (5-15 단계):
> timeout = 1000  # 16분 (기본값)
> 
> # 복잡한 작업 (15-30 단계):
> timeout = 1800  # 30분
> 
> # 매우 복잡한 작업 (30+ 단계):
> timeout = 3600  # 1시간
> 
> agent = DroidAgent(
>     goal="복잡한 작업",
>     config=config,
>     timeout=1800
> )
> ```
> 
> **6. Credentials 자동 주입**:
> ```python
> agent = DroidAgent(
>     goal="Gmail 로그인",
>     config=config,
>     credentials={
>         "GMAIL_USERNAME": "user@gmail.com",
>         "GMAIL_PASSWORD": "secret123",
>         "API_KEY": "sk-..."
>     }
> )
> 
> # 에이전트가 자동으로 생성하는 함수들:
> # - get_gmail_username() → "user@gmail.com"
> # - get_gmail_password() → "secret123"
> # - get_api_key() → "sk-..."
> 
> # LLM이 필요 시 자동으로 호출:
> # "Gmail 앱 열고 로그인해" 
> # → get_gmail_username()과 get_gmail_password() 호출
> ```

---

## 요약

**DroidAgent의 핵심:**

1. **Wrapper 클래스**: 여러 에이전트를 하나의 인터페이스로 통합
2. **두 가지 모드**: Direct (빠름) vs Reasoning (정확함)
3. **유연한 구성**: Config, LLMs, Tools, Credentials 등 모두 커스터마이징 가능
4. **이벤트 스트리밍**: 실행 과정을 실시간으로 모니터링
5. **구조화된 출력**: Pydantic 모델로 타입 안전한 결과 추출

**일반적인 사용 패턴:**

```python
# 1. 최소 구성 (빠른 시작)
agent = DroidAgent(goal="작업")
result = await agent.run()

# 2. 기본 구성
config = DroidrunConfig()
agent = DroidAgent(goal="작업", config=config)
result = await agent.run()

# 3. 커스텀 LLM
agent = DroidAgent(goal="작업", llms=custom_llms, config=config)
result = await agent.run()

# 4. 고급 구성
agent = DroidAgent(
    goal="작업",
    config=config,
    llms=llms,
    custom_tools=tools,
    credentials=creds,
    variables=vars,
    output_model=Model
)
result = await agent.run()
```

**다음 단계:**
- [Configuration 가이드](./configuration)에서 모든 설정 옵션 확인
- [AdbTools 문서](./adb-tools)에서 기기 제어 방법 학습
- [빠른 시작](../quickstart)으로 첫 에이전트 실행
- [예제 코드](https://github.com/droidrun/droidrun/tree/main/examples)로 실전 패턴 학습

---
