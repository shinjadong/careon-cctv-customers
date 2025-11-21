## 개요

Droidrun CLI는 **LLM 에이전트**가 지원하는 자연어 명령을 사용하여 Android 및 iOS 기기를 제어할 수 있게 해줍니다.

> 📖 **개념 설명: LLM 에이전트**
> 
> 'LLM 에이전트'는 단순히 텍스트를 생성하는 것을 넘어, **목표를 달성하기 위해 스스로 생각하고(Reasoning), 계획을 세우며, 도구(여기서는 스마트폰 앱)를 사용할 수 있는** AI를 의미합니다. 
> 
> Droidrun에서는 이 에이전트가 "스포티파이 열어"라는 명령을 "스포티파이 앱 아이콘 찾기 → 탭하기" 같은 실제 기기 조작 단계로 변환해 실행합니다.

---

### 빠른 시작

```bash
# 기기 설정
droidrun setup

# 명령어 실행 (축약형 - "run" 필요 없음)
droidrun "스포티파이 열고 내 디스커버 위클리 재생해"

# 또는 명시적
droidrun run "방해금지 모드 켜줘"
```

<Note>

**자동 설정**: `config.yaml` 파일이 존재하지 않으면, Droidrun이 `config_example.yaml`로부터 자동으로 생성합니다.
**명령어 축약**: `droidrun "작업"`은 `droidrun run "작업"`과 동일합니다.

</Note>

> 📖 **개념 설명: config.yaml**
> 
> `.yaml` 파일은 설정(Configuration) 정보를 저장하는 데 자주 쓰이는 텍스트 파일 형식입니다. 
> 
> 여기서는 기본으로 사용할 LLM 모델, API 키, 기기 정보 등 Droidrun의 작동 방식을 미리 정해두는 '설정집' 역할을 합니다.

---

## 명령어

<Tabs>
<Tab title="run">

### 기기에서 자연어 명령 실행
**사용법:**
```bash
droidrun run "<command>" [OPTIONS]

# 축약형 (run 생략)
droidrun "<command>" [OPTIONS]
```

---

### 주요 플래그

| 플래그 | 설명 | 기본값 |
|--------|------|--------|
| `--provider`, `-p` | LLM 제공사 (GoogleGenAI, OpenAI, Anthropic 등) | 설정 파일 값 |
| `--model`, `-m` | 모델 이름 | 설정 파일 값 |
| `--device`, `-d` | 기기 시리얼 또는 IP | 자동 감지 |
| `--steps` | 최대 실행 단계 | 15 |
| `--reasoning` | 계획 모드 활성화 | false |
| `--vision` | 모든 에이전트에 비전(시각) 활성화 | 설정 파일 값 |
| `--tcp` | 콘텐츠 프로바이더 대신 TCP 사용 | false |
| `--debug` | 상세 로깅 | false |
| `--save-trajectory` | 실행 경로(Trajectory) 저장 (none, step, action) | none |
| `--config`, `-c` | 사용자 정의 설정 파일 경로 | `config.yaml` |

> 📖 **개념 설명: LLM 제공사 (Provider)**
> 
> 'LLM 제공사(Provider)'는 자연어 명령을 이해하고 처리할 '뇌'를 빌려주는 곳입니다. 
> 
> Google(Gemini), OpenAI(GPT-4o), Anthropic(Claude) 등이 있으며, 각각 성능, 비용, 응답 속도에 차이가 있어 사용자가 선택할 수 있습니다.

> 📖 **개념 설명: Reasoning (계획 모드)**
> 
> 이 옵션을 켜면, LLM 에이전트가 "존에게 왓츠앱 보내기" 같은 복잡한 요청을 받았을 때, 다음과 같이 **스스로 작업 계획을 세우고(Planning) 추론(Reasoning)하며** 단계를 실행합니다:
> 
> 1. 왓츠앱 열기
> 2. '존' 검색
> 3. 메시지 입력창 탭
> 4. '늦을 것 같아' 입력
> 5. 전송 버튼 누르기

> 📖 **개념 설명: Vision (비전)**
> 
> LLM이 스마트폰의 '화면'을 '볼 수 있게' 하는 기능입니다. 
> 
> 단순히 앱의 내부 구조(UI 트리)만 보는 것이 아니라, 실제 화면 스크린샷을 보고 "전송 버튼이 저기 있네" 또는 "이 아이콘은 스포티파이네"처럼 **시각적으로 앱을 이해하고 조작**할 수 있게 됩니다.

> 📖 **개념 설명: TCP vs. 콘텐츠 프로바이더**
> 
> Droidrun이 기기와 통신하는 방식입니다.
> 
> - **콘텐츠 프로바이더**: USB로 연결되었을 때 앱 간 데이터를 공유하는 표준 안드로이드 방식
> - **TCP**: Wi-Fi 등 네트워크를 통해 (주로 무선으로) 기기에 연결하고 명령을 보낼 때 사용하는 방식

> 📖 **개념 설명: Trajectory (실행 경로)**
> 
> 에이전트가 작업을 수행하며 거친 모든 '행동'과 '상태'의 기록입니다. 
> 
> "1단계: 화면 스크린샷 → 2단계: '설정' 버튼 클릭 → 3단계: 다음 화면 스크린샷..."과 같이 **전체 작업 과정을 저장**하여 나중에 분석하거나(디버깅) 다시 실행(매크로)할 수 있게 합니다.

---

### 예시

<Tabs>
<Tab title="기본">

```bash
# 간단한 명령
droidrun "설정 열어줘"

# 다단계 작업
droidrun "존에게 왓츠앱 보내: 나 늦을 것 같아"

# 특정 기기
droidrun "배터리 확인해줘" --device emulator-5554


# OpenAI
export OPENAI_API_KEY=your-key
droidrun "쇼핑 리스트 만들어줘" \
  --provider OpenAI \
  --model gpt-4o

# 앤트로픽 클로드
export ANTHROPIC_API_KEY=your-key
droidrun "최신 이메일에 답장해" \
  --provider Anthropic \
  --model claude-sonnet-4-5-latest

# 로컬 Ollama (무료)
droidrun "다크 모드 켜줘" \
  --provider Ollama \
  --model llama3.3:70b \
  --base_url http://localhost:11434
```
> 📖 **개념 설명: Ollama**
> 
> API 키가 필요한 외부 서비스(OpenAI 등)와 달리, Llama 3 같은 오픈소스 LLM을 '사용자 개인 컴퓨터'에 설치하고 실행할 수 있게 해주는 도구입니다. 
> 
> Droidrun이 이 로컬 모델을 사용하게 하면, API 비용이 들지 않고 개인정보가 외부로 나가지 않는 장점이 있습니다.
</Tab>
<Tab title="고급">

```bash
# 계획 모드를 사용한 복잡한 작업
droidrun "발신자별로 받은 편지함 정리해줘" \
  --reasoning \
  --vision \
  --steps 30

# 실패한 명령어 디버깅하기
droidrun "공항으로 가는 우버 예약해줘" \
  --debug \
  --save-trajectory action

# 무선 실행
droidrun "캐시 지워줘" \
  --device 192.168.1.100:5555 \
  --tcp

# 사용자 정의 설정 사용
droidrun "2단계 인증 활성화해줘" \
  --config /path/to/config.yaml
```
</Tab>
</Tabs>
---

### 제공사 옵션

| 제공사 | 설치 | 환경 변수 |
|--------|------|-----------|
| GoogleGenAI | `uv pip install 'droidrun[google]'` | `GOOGLE_API_KEY` |
| OpenAI | `uv pip install 'droidrun[openai]'` | `OPENAI_API_KEY` |
| Anthropic | `uv pip install 'droidrun[anthropic]'` | `ANTHROPIC_API_KEY` |
| DeepSeek | `uv pip install 'droidrun[deepseek]'` | `DEEPSEEK_API_KEY` |
| Ollama | `uv pip install 'droidrun[ollama]'` | 없음 (로컬) |

</Tab>
<Tab title="devices">

### 연결된 기기 목록 보기

```bash
droidrun devices
```

**출력 예시:**
```
Found 2 connected device(s):
  • emulator-5554
  • 192.168.1.100:5555
```

</Tab>
<Tab title="setup">
### Portal APK 설치
기기에 **Portal APK**를 설치합니다.

> 📖 **개념 설명: Portal APK**
> 
> 'APK'는 안드로이드 앱 설치 파일입니다. 
> 
> 'Portal'은 Droidrun의 CLI(PC)와 안드로이드 기기(스마트폰)를 연결해주는 '관문(Portal)' 역할을 하는 전용 앱입니다. 이 앱이 기기에 설치되어 있어야 CLI가 보낸 명령을 받아 화면을 클릭하거나 텍스트를 입력할 수 있습니다.

**사용법:**
```bash
# 기기 자동 감지
droidrun setup

# 특정 기기
droidrun setup --device emulator-5554

# 사용자 정의 APK
droidrun setup --path /path/to/portal.apk
```

**수행하는 작업:**

1. 최신 Portal APK 다운로드

2. 모든 권한과 함께 설치

3. **접근성 서비스** 자동 활성화

4. 수동 활성화가 필요하면 설정 창 열기

> 📖 **개념 설명: 접근성 서비스**
> 
> 원래는 시각/청각 장애인을 돕기 위한 안드로이드 기능이지만, Droidrun은 이 기능을 활용하여 **사용자 대신 화면을 읽고(스크린 리딩), 버튼을 클릭하며(터치), 텍스트를 입력**합니다. 
> 
> Droidrun이 기기를 '제어'하기 위해 필수적인 핵심 권한입니다.

</Tab>
<Tab title="ping">

### Portal 연결 테스트

```bash
# 기본 통신 테스트
droidrun ping

# TCP 모드 테스트
droidrun ping --tcp

# 특정 기기
droidrun ping --device 192.168.1.100:5555
```

**성공 출력:**
```
Portal is installed and accessible. You're good to go!
```

</Tab>
<Tab title="connect">

### TCP/IP를 통해 기기 연결

```bash
droidrun connect 192.168.1.100:5555
```

**사전 준비 사항:**

```bash
# 무선 디버깅 활성화 (Android 11 이상)
# 설정 > 개발자 옵션 > 무선 디버깅

# 또는 USB를 통해:
adb tcpip 5555
adb shell ip route | awk '{print $9}'  # IP 주소 확인
droidrun connect <IP>:5555
```

</Tab>
<Tab title="disconnect">

### 기기 연결 끊기

```bash
droidrun disconnect 192.168.1.100:5555
```

</Tab>
<Tab title="macro">
### 자동화 시퀀스 기록 및 재생

> 📖 **개념 설명: 매크로**
> 
> LLM 에이전트가 "7시 알람 설정"을 수행하며 기록한 '실행 경로(Trajectory)'를 저장해 두었다가, 나중에 LLM의 개입 없이 **그대로 다시 실행(Replay)**하는 기능입니다. 
> 
> 반복적인 작업을 빠르고 안정적으로 자동화할 때 유용합니다.
#### `droidrun macro list`
저장된 실행 경로(trajectory)를 나열합니다.

```bash
# 기본 디렉토리
droidrun macro list

# 사용자 정의 디렉토리
droidrun macro list /path/to/trajectories
```

**출력 예시:**

```
Found 3 trajectory(s):

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ 폴더 (Folder)    ┃ 설명 (Description)        ┃ 동작 수 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ open-settings    │ Opens settings app        │ 3       │
│ enable-dark-mode │ Navigate to display...    │ 8       │
└──────────────────┴───────────────────────────┴─────────┘
```

---

#### `droidrun macro replay`
기록된 매크로를 재생합니다.
```bash
# 기본 재생
droidrun macro replay trajectories/open-settings

# 사용자 정의 기기 및 타이밍
droidrun macro replay trajectories/login-flow \
  --device emulator-5554 \
  --delay 0.5

# 특정 단계부터 시작
droidrun macro replay trajectories/checkout \
  --start-from 5 \
  --max-steps 10

# 실행 없이 미리보기
droidrun macro replay trajectories/test --dry-run
```

**플래그:**

| 플래그 | 설명 | 기본값 |
|--------|------|--------|
| `--device`, `-d` | 기기 시리얼 | 자동 감지 |
| `--delay`, `-t` | 동작 사이의 시간 (초) | 1.0 |
| `--start-from`, `-s` | 시작 단계 (1부터 시작) | 1 |
| `--max-steps`, `-m` | 최대 실행 단계 수 | 전체 |
| `--dry-run` | 미리보기만 실행 | false |
> 📖 **개념 설명: Dry-run**
> 
> '마른 실행'이라는 뜻으로, 실제로는 아무것도 실행하거나 변경하지 않고, **"만약 실행한다면 이런 일들이 일어날 것입니다"**라고 로그만 보여주는 '시뮬레이션' 또는 '미리보기' 모드입니다.

---

#### 실행 경로 기록하기
```bash
# 행동(action) 레벨로 기록 (가장 상세함)
droidrun "오전 7시 알람 생성" --save-trajectory action

# 단계(step) 레벨로 기록
droidrun "연락처 내보내기" --save-trajectory step
```

**실행 경로 구조:**

```
trajectories/2025-10-16_14-30-45/
├── macro.json       # 동작 시퀀스
├── step_0.png       # 스크린샷
├── step_1.png
└── ...
```

</Tab>
</Tabs>

---

## 설정

### 우선 순위

1. **CLI 플래그** (가장 높음)

2. **설정 파일** (`config.yaml`)

3. **기본값** (가장 낮음)

---

### 자주 쓰이는 패턴

<CodeGroup>

```bash 기본 사용
droidrun "다크 모드 켜줘" \
  --provider GoogleGenAI \
  --model models/gemini-2.5-flash
```

```bash 디버깅 모드
droidrun "공항 가는 차 예약해줘" \
  --debug \
  --reasoning \
  --vision \
  --save-trajectory action
```

```bash 비전 비활성화
droidrun "알람 설정해줘" \
  --provider GoogleGenAI \
  --model models/gemini-2.5-flash \
  --no-vision
```

```bash 다중 기기 실행
for device in $(adb devices | awk 'NR>1 {print $1}'); do
  droidrun "알림 지워줘" --device $device
done
```

</CodeGroup>

---

## 문제 해결

<AccordionGroup>

<Accordion title="기기를 찾을 수 없음">

```bash
# ADB 확인
adb devices

# '승인되지 않음' 상태: 기기에서 팝업 승인

# 목록에 없음: 다른 USB 포트/케이블 시도

# ADB 재시작
adb kill-server && adb start-server


# 재설치
droidrun setup

# 접근성 수동 활성화
adb shell settings put secure enabled_accessibility_services \
  com.droidrun.portal/.DroidrunAccessibilityService
```
</Accordion>

<Accordion title="LLM 제공사 오류">

```bash
# 제공사 설치
uv pip install 'droidrun[google,openai,anthropic]'

# API 키 확인
echo $GOOGLE_API_KEY

# 누락된 경우 설정
export GOOGLE_API_KEY=your-key

# 디버그 모드 활성화
droidrun "작업" --debug

# 계획(reasoning) 모드 시도
droidrun "다단계 작업" --reasoning
```
</Accordion>
<Accordion title="TCP 연결 실패">

```bash
# TCP 모드 활성화 (먼저 USB 연결)
adb tcpip 5555

# 기기 IP 확인
adb shell ip route | awk '{print $9}'

# 연결
droidrun connect <IP>:5555

# 확인
droidrun ping --tcp
```

</Accordion>
</AccordionGroup>

---

## 환경 변수

> 📖 **개념 설명: 환경 변수**
> 
> `export GOOGLE_API_KEY=...`처럼 터미널에 설정하는 변수입니다. 
> 
> 코드나 설정 파일에 민감한 정보(API 키 등)를 직접 저장하는 대신, 운영체제(OS)가 이 값을 '기억'하게 하는 방식입니다. 이렇게 하면 코드를 공유할 때 민감한 키가 노출되는 것을 방지할 수 있습니다.
| 변수 | 설명 | 기본값 |
|------|------|--------|
| `GOOGLE_API_KEY` | Google Gemini API 키 | 없음 |
| `OPENAI_API_KEY` | OpenAI API 키 | 없음 |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | 없음 |
| `DEEPSEEK_API_KEY` | DeepSeek API 키 | 없음 |
| `DROIDRUN_CONFIG` | 설정 파일 경로 | `config.yaml` |

---

### 변수 설정하기

<CodeGroup>

```bash Linux/Mac
export GOOGLE_API_KEY=your-key
```

```powershell Windows
$env:GOOGLE_API_KEY="your-key"
```

```bash 영구 설정 (Linux/Mac)
echo 'export GOOGLE_API_KEY=your-key' >> ~/.bashrc
source ~/.bashrc
```

</CodeGroup>

---

## 다음 단계

- [설정 가이드](/sdk/configuration) - 동작 방식 사용자 정의
- [기기 설정](/guides/device-setup) - 상세 설정 안내
- [에이전트 아키텍처](/concepts/architecture) - 작동 원리
- [사용자 정의 도구](/features/custom-tools) - 기능 확장