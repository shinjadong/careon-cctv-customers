---

title: '구조화된 출력'

description: 'Pydantic 모델을 사용하여 디바이스 상호작용에서 구조화된 데이터 추출하기'

---

  

---

  

## 빠른 시작

  

```python

import asyncio

from pydantic import BaseModel, Field

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

# 1. 출력 구조 정의

class ContactInfo(BaseModel):

    """디바이스의 연락처 정보."""

    name: str = Field(description="연락처의 전체 이름")

    phone: str = Field(description="전화번호")

    email: str = Field(description="이메일 주소", default="제공되지 않음")

  

# 2. output_model로 에이전트 생성

async def main():

    config = DroidrunConfig()

  

    agent = DroidAgent(

        goal="John Smith의 연락처 정보 찾기",

        config=config,

        output_model=ContactInfo,

    )

  

    # 3. 실행하고 구조화된 출력 접근

    result = await agent.run()

  

    if result.success and result.structured_output:

        contact: ContactInfo = result.structured_output

        print(f"이름: {contact.name}")

        print(f"전화: {contact.phone}")

        print(f"이메일: {contact.email}")

  

asyncio.run(main())

```

  

📖 **구조화된 출력(Structured Output)**

├─ **정의**: 자유 형식 텍스트를 Pydantic 모델로 정의된 구조화된 데이터로 변환

├─ **쉬운 비유**: 메모를 읽고 중요 정보만 양식에 정리하는 것처럼 데이터 추출

├─ **메커니즘**: LLM이 자연어 응답에서 스키마에 맞는 JSON 객체 생성

└─ **존재 이유**: API 통합, 데이터베이스 저장 등을 위한 일관된 데이터 형식 필요

  

---

  

## 작동 방식

  

### 2단계 프로세스

  

**1단계: 작업 실행**

- DroidAgent가 필요한 정보를 수집하면서 디바이스 액션 수행

- Pydantic 스키마가 시스템 프롬프트에 자동 주입됨

- 에이전트가 데이터를 포함한 자연어 답변으로 완료

  

**2단계: 추출 (완료 후)**

- `StructuredOutputAgent`가 최종 답변 텍스트 수신

- LLM의 `astructured_predict()`를 사용하여 모델로 데이터 추출

- 스키마에 대해 검증하고 타입이 지정된 객체 또는 `None` 반환

  

---

  

## 예시: 송장 추출

  

```python

from pydantic import BaseModel, Field

from typing import List

  

class Invoice(BaseModel):

    """송장 정보."""

    invoice_number: str = Field(description="송장 ID")

    vendor_name: str = Field(description="공급업체 이름")

    total_due: float = Field(description="달러 단위 총 금액")

  

agent = DroidAgent(

    goal="Gmail 열고 Acme Corp 이메일에서 송장 추출",

    config=DroidrunConfig(),

    output_model=Invoice,

)

  

result = await agent.run()

invoice = result.structured_output

print(f"송장 {invoice.invoice_number}: ${invoice.total_due}")

```

  

---

  

## 결과 처리

  

### 데이터 접근

  

```python

result = await agent.run()

  

if result.success:

    if result.structured_output:

        data = result.structured_output  # 타입이 지정된 Pydantic 객체

        print(f"추출됨: {data}")

    else:

        print(f"추출 실패, 텍스트 답변: {result.reason}")

else:

    print(f"작업 실패: {result.reason}")

```

  

### JSON으로 내보내기

  

```python

result = await agent.run()

  

if result.structured_output:

    # JSON으로 변환하고 저장

    json_str = result.structured_output.model_dump_json(indent=2)

    with open("output.json", "w") as f:

        f.write(json_str)

```

  

---

  

## 설정

  

### 커스텀 추출 LLM

  

기본적으로 추출은 `codeact` LLM을 사용합니다. 전용 `structured_output` 프로필을 지정하세요:

  

**config.yaml:**

```yaml

llm_profiles:

  codeact:

    provider: GoogleGenAI

    model: models/gemini-2.0-flash

    temperature: 0.3

  

  structured_output:

    provider: OpenAI

    model: gpt-4o-mini

    temperature: 0.0  # 일관된 추출을 위한 낮은 온도

```

  

**프로그래밍 방식:**

```python

from droidrun import load_llm

  

config = DroidrunConfig()

  

llms = {

    "codeact": load_llm("GoogleGenAI", "models/gemini-2.0-flash"),

    "structured_output": load_llm("OpenAI", "gpt-4o-mini"),

}

  

agent = DroidAgent(

    goal="Alice의 연락처 정보 추출",

    llms=llms,

    config=config,

    output_model=ContactInfo,

)

```

  

### 추론 모드

  

직접 및 추론 모드 모두에서 작동:

  

```python

# 직접 모드

config = DroidrunConfig()

config.agent.reasoning = False

  

agent = DroidAgent(

    goal="SF의 날씨 찾기",

    config=config,

    output_model=WeatherInfo,

)

  

# 추론 모드

config.agent.reasoning = True

  

agent = DroidAgent(

    goal="SF의 날씨 찾기",

    config=config,

    output_model=WeatherInfo,

)

```

  

---

  

## 모범 사례

  

**1. 명확한 필드 설명 추가** - LLM이 이것을 사용하여 무엇을 추출할지 이해:

```python

name: str = Field(description="주문을 한 고객의 전체 이름")

```

  

**2. 선택적 필드에 기본값 제공** - 추출 실패 방지:

```python

rating: Optional[float] = Field(description="고객 평점 (1-5)", default=None)

```

  

**3. 목표에서 데이터 수집 안내**:

```python

agent = DroidAgent(

    goal="연락처를 찾고 전화번호, 이메일, 전체 이름을 가져오기",

    config=config,

    output_model=ContactInfo,

)

```

  

---

  

## 문제 해결

  

**추출이 None을 반환:**

- `output_model`이 `DroidAgent`에 전달되었는지 확인

- 작업이 성공했는지 확인: `result.success`

- 디버그 로깅 활성화: `config.logging.debug = True`

  

**부분적이거나 잘못된 데이터:**

- 더 구체적인 필드 설명 추가

- 목표에서 필수 필드를 명시적으로 언급

  

**검증 오류:**

- 불확실한 필드에 `Optional`과 기본값 추가

  

---

  

## 고급

  

### 여러 항목

  

`List` 필드가 있는 모델을 사용하여 데이터 목록 추출:

  

```python

class ContactList(BaseModel):

    """여러 연락처."""

    contacts: List[ContactInfo] = Field(description="연락처 목록")

  

agent = DroidAgent(

    goal="John Smith와 Jane Doe의 연락처 찾기",

    config=config,

    output_model=ContactList,

)

```

  

### 워크플로우 통합

  

추출은 `DroidAgent.finalize()`에서 자동으로 발생:

  

```python

@step

async def finalize(self, ctx: Context, ev: FinalizeEvent) -> ResultEvent:

    result = ResultEvent(

        success=ev.success,

        reason=ev.reason,

        steps=self.shared_state.step_number,

        structured_output=None,

    )

  

    # 모델이 제공된 경우 추출

    if self.output_model is not None and ev.reason:

        structured_agent = StructuredOutputAgent(

            llm=self.structured_output_llm,

            pydantic_model=self.output_model,

            answer_text=ev.reason,

        )

        extraction_result = await (await structured_agent.run())

        if extraction_result["success"]:

            result.structured_output = extraction_result["structured_output"]

  

    return result

```

  

---

  

## 관련 문서

  

- [DroidAgent API](/sdk/droid-agent)

- [Pydantic 문서](https://docs.pydantic.dev/)

- [설정 가이드](/sdk/configuration)

- [커스텀 변수](/features/custom-variables)