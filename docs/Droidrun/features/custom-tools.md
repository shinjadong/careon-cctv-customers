---

title: '커스텀 도구'

description: '커스텀 Python 함수로 Droidrun 확장하기'

---

  

## 개요

  

커스텀 도구는 기본 원자 액션(클릭, 타이핑, 스와이프)을 넘어 에이전트 기능을 확장하는 Python 함수입니다.

  

📖 **커스텀 도구(Custom Tools)**

├─ **정의**: 에이전트가 사용할 수 있는 사용자 정의 Python 함수

├─ **쉬운 비유**: 스마트폰 앱에 플러그인을 추가하듯이 에이전트에 새 기능 추가

├─ **메커니즘**: Python 함수를 정의하고 딕셔너리로 등록하면 에이전트가 호출 가능

└─ **존재 이유**: 외부 API 호출, 데이터 처리 등 도메인별 로직 구현

  

**사용 사례:**

- 외부 API 호출 (웹훅, REST 서비스)

- 데이터 처리 및 계산

- 데이터베이스 작업

- 도메인별 로직

  

---

  

## 빠른 시작

  

### 기본 예시

  

디바이스 접근 없는 간단한 커스텀 도구:

  

```python

import asyncio

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

def calculate_tax(amount: float, rate: float, **kwargs) -> str:

    """주어진 금액에 대한 세금 계산."""

    tax = amount * rate

    total = amount + tax

    return f"세금: ${tax:.2f}, 합계: ${total:.2f}"

  

custom_tools = {

    "calculate_tax": {

        "arguments": ["amount", "rate"],

        "description": "주어진 금액과 세율에 대한 세금 계산",

        "function": calculate_tax

    }

}

  

async def main():

    config = DroidrunConfig()

  

    agent = DroidAgent(

        goal="$100에 대한 8% 세율로 세금 계산",

        config=config,

        custom_tools=custom_tools

    )

  

    result = await agent.run()

    print(result.success, result.reason)

  

asyncio.run(main())

```

  

---

  

## 도구 구조

  

모든 커스텀 도구는 다음 형식을 따릅니다:

  

```python

custom_tools = {

    "tool_name": {

        "arguments": ["arg1", "arg2"],           # 파라미터 이름

        "description": "도구 설명...",            # LLM 프롬프트용

        "function": callable_function            # Python 함수

    }

}

```

  

**함수 시그니처:**

```python

def tool_name(arg1: type, arg2: type, *, tools=None, shared_state=None, **kwargs) -> str:

    """

    Args:

        arg1: 파라미터

        arg2: 또 다른 파라미터

        tools: Tools 인스턴스 (선택사항, 자동 주입)

        shared_state: DroidAgentState (선택사항, 자동 주입)

    """

    # 구현

    return "결과"

```

  

**핵심 사항:**

- `"arguments"`에는 사용자 인수만 나열 (`tools`나 `shared_state` 제외)

- `tools`와 `shared_state`는 키워드 인수로 자동 주입

- 하위 호환성을 위해 `**kwargs` 사용

- 반환 타입은 `str`이어야 함

  

---

  

## Tools 인스턴스 사용

  

`tools` 파라미터를 통해 디바이스 접근:

  

```python

def screenshot_and_count(*, tools=None, shared_state=None, **kwargs) -> str:

    """스크린샷을 찍고 UI 요소 개수 세기."""

    if not tools:

        return "오류: tools 인스턴스 필요"

  

    # 스크린샷 찍기

    screenshot_path, screenshot_bytes = tools.take_screenshot()

  

    # UI 상태 가져오기

    state = tools.get_state()

    element_count = len(state.get("ui_elements", []))

  

    return f"스크린샷 저장됨. {element_count}개 UI 요소 발견"

  

custom_tools = {

    "screenshot_and_count": {

        "arguments": [],

        "description": "스크린샷을 찍고 화면의 UI 요소 개수 세기",

        "function": screenshot_and_count

    }

}

```

  

**`tools`를 통해 사용 가능:**

- `tools.take_screenshot()` - 화면 캡처

- `tools.get_state()` - UI 계층 구조 가져오기

- `tools.tap_by_index(index)` - 요소 탭

- `tools.input_text(text, index)` - 텍스트 입력

- `tools.swipe(x1, y1, x2, y2)` - 스와이프 제스처

- AdbTools/IOSTools의 모든 메서드

  

---

  

## 공유 상태 사용

  

`shared_state`를 통해 에이전트 상태 접근:

  

```python

def check_action_history(action_name: str, *, tools=None, shared_state=None, **kwargs) -> str:

    """특정 액션이 최근에 수행되었는지 확인."""

    if not shared_state:

        return "오류: shared_state 필요"

  

    # 최근 액션 확인

    recent_actions = shared_state.action_history[-5:]

    already_done = any(a.get("action") == action_name for a in recent_actions)

  

    if already_done:

        return f"액션 '{action_name}'이(가) 이미 최근에 수행됨"

  

    # 단계 수 확인

    if shared_state.step_number > 10:

        return "경고: 작업이 너무 많은 단계를 사용 중"

  

    # 메모리 접근

    if "skip_validation" in shared_state.memory:

        return "메모리에 따라 검증 건너뜀"

  

    return f"액션 '{action_name}'이(가) 아직 수행되지 않음"

  

custom_tools = {

    "check_action_history": {

        "arguments": ["action_name"],

        "description": "특정 액션이 에이전트 기록에서 최근 수행되었는지 확인",

        "function": check_action_history

    }

}

```

  

**DroidAgentState 필드:**

- `step_number` - 현재 실행 단계

- `action_history` - 실행된 액션 목록

- `action_outcomes` - 액션별 성공/실패

- `memory` - 에이전트 메모리 딕셔너리

- `custom_variables` - 사용자 제공 변수

- `visited_packages` - 방문한 앱

- `current_package_name` - 현재 앱 패키지

- `plan` - 현재 Manager 계획

- `droidrun/agent/droid/events.py`에 더 많은 정보

  

---

  

## 일반 패턴

  

### API 통합

  

```python

import requests

  

def fetch_weather(city: str, **kwargs) -> str:

    """API에서 날씨 데이터 가져오기."""

    try:

        # OpenWeatherMap API 예시 사용

        api_key = "your_api_key"

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

  

        response = requests.get(url, timeout=10)

        response.raise_for_status()

  

        data = response.json()

        temp = data["main"]["temp"] - 273.15  # 섭씨로 변환

        weather = data["weather"][0]["description"]

  

        return f"{city}의 날씨: {weather}, {temp:.1f}°C"

    except Exception as e:

        return f"오류: {str(e)}"

  

custom_tools = {

    "fetch_weather": {

        "arguments": ["city"],

        "description": "주어진 도시의 현재 날씨 데이터 가져오기",

        "function": fetch_weather

    }

}

```

  

### 데이터베이스 쿼리

  

```python

import sqlite3

  

def query_database(query: str, **kwargs) -> str:

    """로컬 데이터베이스 쿼리."""

    try:

        conn = sqlite3.connect("app.db")

        cursor = conn.execute(query)

        results = cursor.fetchall()

        conn.close()

  

        return f"{len(results)}개 결과 발견"

    except Exception as e:

        return f"데이터베이스 오류: {str(e)}"

  

custom_tools = {

    "query_database": {

        "arguments": ["query"],

        "description": "로컬 데이터베이스에서 SQL 쿼리 실행 및 결과 반환",

        "function": query_database

    }

}

```

  

### 비동기 작업

  

```python

import aiohttp

  

async def fetch_async(url: str, **kwargs) -> str:

    """비동기로 데이터 가져오기."""

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(url, timeout=10) as response:

                data = await response.text()

                return f"{url}에서 {len(data)}바이트 가져옴"

    except Exception as e:

        return f"오류: {str(e)}"

  

custom_tools = {

    "fetch_async": {

        "arguments": ["url"],

        "description": "URL에서 비동기로 데이터 가져오기",

        "function": fetch_async

    }

}

```

  

---

  

## 모범 사례

  

### 1. 명확한 설명

구체적이고 명확한 설명 작성:

  

```python

# 좋음

"description": "JSON 데이터 페이로드와 함께 웹훅 URL로 POST 요청 전송"

  

# 나쁨

"description": "웹훅 전송"

```

  

### 2. 오류 처리

항상 예외 처리:

  

```python

def robust_tool(url: str, **kwargs) -> str:

    try:

        response = requests.get(url, timeout=10)

        response.raise_for_status()

        return f"성공: {response.status_code}"

    except requests.Timeout:

        return "오류: 요청 시간 초과"

    except requests.RequestException as e:

        return f"오류: {str(e)}"

    except Exception as e:

        return f"예상치 못한 오류: {str(e)}"

```

  

### 3. 인수 검증

처리 전 입력 검증:

  

```python

def validated_tool(count: int, **kwargs) -> str:

    if not isinstance(count, int):

        return "오류: count는 정수여야 함"

    if count < 0 or count > 100:

        return "오류: count는 0-100이어야 함"

  

    return f"{count}개 항목 처리됨"

```

  

### 4. 로깅

디버깅을 위한 Python 로깅 사용:

  

```python

import logging

logger = logging.getLogger("droidrun")

  

def logged_tool(data: str, **kwargs) -> str:

    logger.info(f"처리 중: {data[:50]}...")

    # 데이터 처리

    logger.info("완료")

    return "성공"

```

  

---

  

## 고급 예시

  

tools 인스턴스, shared state, 자격 증명 결합:

  

```python

import requests

  

def send_authenticated_request(

    url: str,

    data: str,

    *,

    tools=None,

    shared_state=None,

    **kwargs

) -> str:

    """자격 증명을 사용하여 인증된 API 요청 전송."""

    try:

        # tools 인스턴스를 통해 자격 증명 접근

        if not tools or not hasattr(tools, 'credential_manager'):

            return "오류: Credential manager 사용 불가"

  

        api_key = tools.credential_manager.get_credential("API_KEY")

  

        # 너무 많은 요청을 했는지 확인

        if shared_state and shared_state.step_number > 15:

            return "오류: API 호출이 너무 많음"

  

        # 인증된 요청 전송

        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.post(url, json={"data": data}, headers=headers, timeout=10)

        response.raise_for_status()

  

        return f"요청 성공: {response.status_code}"

    except Exception as e:

        return f"오류: {str(e)}"

  

custom_tools = {

    "send_authenticated_request": {

        "arguments": ["url", "data"],

        "description": "저장된 자격 증명을 사용하여 인증된 API 요청 전송",

        "function": send_authenticated_request

    }

}

  

# 자격 증명과 함께 사용

credentials = {"API_KEY": "sk-1234567890"}

  

agent = DroidAgent(

    goal="API로 데이터 전송",

    config=config,

    custom_tools=custom_tools,

    credentials=credentials

)

```

  

---

  

## 관련 문서

  

공유 상태 및 커스텀 도구 통합 이해를 위해 [에이전트 아키텍처](/concepts/architecture)를 참조하세요.