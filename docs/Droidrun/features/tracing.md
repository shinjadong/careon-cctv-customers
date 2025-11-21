---

title: '추적'

description: 'Phoenix 추적 및 궤적 기록 설정'

---

  

Droidrun은 두 가지 모니터링 기능을 제공합니다:

  

1. **Arize Phoenix 추적** - 실시간 LLM 및 에이전트 실행 추적

2. **궤적 기록** - 디버깅을 위한 로컬 스크린샷 및 UI 상태

  

📖 **추적(Tracing)**

├─ **정의**: 프로그램 실행 과정을 단계별로 기록하는 디버깅 도구

├─ **쉬운 비유**: 블랙박스처럼 에이전트가 무엇을 했는지 재생 가능하게 기록

├─ **메커니즘**: LLM 호출, 에이전트 결정, 도구 실행을 시간순으로 저장

└─ **존재 이유**: 에이전트 행동 분석, 오류 원인 파악, 성능 최적화

  

## 빠른 참조

  

```sh

# Phoenix 추적 활성화

droidrun run "작업" --tracing

  

# 궤적 기록 활성화

droidrun run "작업" --save-trajectory step

```

  

---

  

## Arize Phoenix 추적

  

Phoenix는 LLM 호출, 에이전트 실행, 도구 호출에 대한 실시간 추적을 제공합니다. 에이전트 동작 디버깅, 토큰 사용량 모니터링, 실행 흐름 분석에 사용하세요.

  

### 설정

  

**1. Phoenix 설치:**

  

```sh

uv pip install arize-phoenix

```

  

**2. Phoenix 서버 시작:**

  

```sh

phoenix serve

```

  

서버가 `http://localhost:6006`에서 시작되며 추적을 볼 수 있는 웹 UI를 제공합니다.

  

**3. Droidrun에서 추적 활성화:**

  

**CLI를 통해:**

  

```sh

droidrun run "설정 열기" --tracing

```

  

**config.yaml을 통해:**

  

```yaml

tracing:

  enabled: true

```

  

**코드를 통해:**

  

```python

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

config = DroidrunConfig()

config.tracing.enabled = True

  

agent = DroidAgent(goal="설정 열기", config=config)

agent.run()

```

  

**4. 추적 보기:**

  

`http://localhost:6006`으로 이동하여 다음을 확인하세요:

- 프롬프트, 응답, 토큰 수를 포함한 LLM 호출

- 에이전트 워크플로우 실행 (Manager, Executor, CodeAct)

- 도구 호출 및 결과

- 실행 시간 및 오류

  

Phoenix 사용에 대한 자세한 내용은 [Arize Phoenix 문서](https://docs.arize.com/phoenix)를 참조하세요.

  

### 설정

  

Phoenix를 커스터마이즈하기 위한 환경 변수 설정:

  

```sh

# 커스텀 Phoenix 서버 URL (기본값: http://127.0.0.1:6006)

export phoenix_url=http://localhost:6006

  

# 추적 구성을 위한 프로젝트 이름

export phoenix_project_name=my_droidrun_project

```

  

<Note>

환경 변수 이름은 소문자입니다: `phoenix_url` 및 `phoenix_project_name`.

</Note>

  

---

  

## 궤적 기록

  

궤적 기록은 오프라인 디버깅 및 분석을 위해 스크린샷과 UI 상태를 로컬에 저장합니다. 원격 측정(PostHog로 전송) 및 추적(Phoenix로 전송)과 달리 궤적은 컴퓨터에 남아 있습니다.

  

### 기록 레벨

  

| 레벨 | 저장 내용 | 사용 시기 |

|-------|--------------|-------------|

| `none` (기본값) | 없음 | 프로덕션 사용, 디스크 공간 절약 |

| `step` | 에이전트 단계당 스크린샷 + 상태 | 일반 디버깅, 대부분의 사용 사례에 권장 |

| `action` | 원자 액션당 스크린샷 + 상태 | 세부 디버깅, 모든 탭/스와이프/타이핑 캡처 |

  

**참고:** `action` 레벨은 `step` 레벨보다 훨씬 더 많은 파일을 생성합니다.

  

### 기록 활성화

  

**CLI를 통해:**

  

```sh

droidrun run "설정 열기" --save-trajectory step

```

  

**config.yaml을 통해:**

  

```yaml

logging:

  save_trajectory: step  # none | step | action

```

  

**코드를 통해:**

  

```python

from droidrun import DroidAgent

from droidrun.config_manager import DroidrunConfig

  

config = DroidrunConfig()

config.logging.save_trajectory = "action"

  

agent = DroidAgent(goal="설정 열기", config=config)

agent.run()

```

  

### 출력 위치

  

궤적은 작업 디렉토리의 `trajectories/`에 저장됩니다:

  

```

trajectories/

└── 2025-10-17_14-30-45_open_settings/

    ├── step_000_screenshot.png

    ├── step_000_state.json

    ├── step_001_screenshot.png

    └── step_001_state.json

```

  

각 궤적 폴더에는 다음이 포함됩니다:

- **스크린샷** - 각 단계/액션에서의 디바이스 화면 PNG 이미지

- **상태 파일** - 다음을 포함한 JSON 파일:

  - UI 접근성 트리 (ID, 텍스트, 경계가 있는 요소 계층)

  - 실행된 액션 (예: `click(5)`, `type("hello", 3)`)

  - 에이전트 추론 및 단계 번호

  - 디바이스 상태 (현재 앱 패키지, 액티비티)

  

이 파일을 사용하여:

- 에이전트가 특정 결정을 내린 이유 디버깅

- 실패한 실행 재생

- UI 요소 감지 문제 분석

- 에이전트 개선을 위한 학습 데이터셋 구축

  

---

  

## 관련 문서

  

- [설정 시스템](/sdk/configuration) - 추적 및 원격 측정 설정 구성

- [이벤트 및 워크플로우](/concepts/events-and-workflows) - 커스텀 모니터링 통합 구축

- [CLI 사용법](/guides/cli) - 모니터링을 위한 명령줄 플래그