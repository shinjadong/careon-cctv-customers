## 개요

Droidrun은 컴퓨터와 기기를 연결하는 전용 Portal 앱을 통해 기기를 제어합니다.

> 📖 **Portal App이란?**
> 
> **정의**: 컴퓨터와 모바일 기기 사이의 '다리(Bridge)' 역할을 하는 특별한 앱
> 
> **쉬운 비유**: 
> - 통역사처럼 컴퓨터의 명령을 기기가 이해할 수 있는 동작으로 변환
> - 양방향 통신: 명령 전달 + 화면 상태 반환
> 
> **핵심 역할**:
> - 컴퓨터 → 기기: "이 버튼 클릭해" 명령 전달
> - 기기 → 컴퓨터: 현재 화면 정보 전송
> - 실제 터치/입력 동작 수행

<Tabs>
<Tab title="Android 설정">

## 사전 준비사항

<Steps>
<Step title="ADB 설치">

**macOS**: 
```bash
brew install android-platform-tools
```

**Linux**: 
```bash
sudo apt install adb
```

**Windows**: [Android 개발자 사이트](https://developer.android.com/studio/releases/platform-tools)에서 다운로드

**확인**: 
```bash
adb version
```

> 📖 **ADB (Android Debug Bridge)란?**
> 
> **정의**: 컴퓨터와 Android 기기를 연결하는 개발자 도구
> 
> **역할**:
> - USB나 Wi-Fi를 통해 기기와 통신
> - 앱 설치/삭제, 파일 전송, 명령 실행
> - 개발 및 디버깅의 필수 도구
> 
> **쉬운 비유**: 
> - USB 케이블 = 물리적 연결
> - ADB = 그 케이블을 통해 대화하는 '언어'

</Step>

<Step title="USB 디버깅 활성화">

1. **설정** > **휴대전화 정보**로 이동
2. **빌드 번호**를 7번 탭 (개발자 옵션 활성화)
3. **설정** > **개발자 옵션**으로 이동
4. **USB 디버깅** 활성화
5. 기기 연결 후 **항상 허용** 탭

**확인**: 
```bash
adb devices
```

> 📖 **USB 디버깅이란?**
> 
> **정의**: 개발자가 USB를 통해 기기에 명령을 보낼 수 있게 하는 권한
> 
> **왜 필요한가?**
> - 일반 사용자: 파일 전송만 가능
> - 디버깅 활성화: 앱 설치, 화면 제어, 로그 확인 등 가능
> 
> **보안 주의**:
> - 악의적인 프로그램이 기기를 제어할 수 있음
> - 신뢰할 수 있는 컴퓨터에만 허용
> - "항상 허용" 체크는 해당 컴퓨터만 기억

</Step>

<Step title="Portal 앱 설치">

```bash
# 자동 설정 (최신 Portal APK 다운로드)
droidrun setup

# 또는 특정 기기 지정
droidrun setup --device SERIAL_NUMBER
```

**수행 작업**:
- 최신 Portal APK 다운로드
- 모든 권한과 함께 설치
- 접근성 서비스 자동 활성화

> 📖 **Portal APK 설치 과정**
> 
> **1. APK 다운로드**:
> - GitHub에서 최신 버전 자동 다운로드
> - 기기 아키텍처에 맞는 버전 선택 (대부분 arm64-v8a)
> 
> **2. 설치 및 권한**:
> ```bash
> # 내부적으로 실행되는 명령
> adb install -g portal.apk  # -g: 모든 권한 자동 부여
> ```
> 
> **3. 접근성 서비스 활성화**:
> - 화면 읽기, 터치 동작 수행에 필요
> - 자동 활성화 시도, 실패 시 설정 화면 열림

</Step>

<Step title="설정 확인">

```bash
droidrun ping
# 출력: Portal is installed and accessible. You're good to go!
```

> 💡 **ping 명령어 역할**
> 
> **확인 항목**:
> 1. ✓ Portal 앱이 설치되어 있는지
> 2. ✓ 접근성 서비스가 활성화되어 있는지
> 3. ✓ ADB 연결이 정상인지
> 4. ✓ 통신이 가능한지
> 
> **성공 시**: "You're good to go!" 메시지
> **실패 시**: 문제 해결 섹션 참조

</Step>
</Steps>

---

## Portal 앱

Droidrun Portal (`com.droidrun.portal`)이 제공하는 기능:

- **접근성 트리 (Accessibility Tree)** - UI 요소와 속성 추출
- **기기 상태 (Device State)** - 현재 활동, 키보드 표시 여부 추적
- **액션 실행 (Action Execution)** - 탭, 스와이프, 텍스트 입력 등의 동작
- **이중 통신 (Dual Communication)** - TCP (빠름) 또는 Content Provider (대체)

> 📖 **각 기능 상세 설명**
> 
> **1. 접근성 트리 (Accessibility Tree)**:
> ```
> 화면 구조 예시:
> [0] Screen
>   [1] Toolbar
>     [2] Button "뒤로가기"
>     [3] TextView "설정"
>   [4] ScrollView
>     [5] Button "Wi-Fi"
> ```
> - 화면의 모든 UI 요소를 계층 구조로 파악
> - 각 요소의 텍스트, 위치, 클릭 가능 여부 등 정보 제공
> 
> **2. 기기 상태**:
> - 현재 열려있는 앱
> - 키보드가 올라와 있는지
> - 화면 방향 (세로/가로)
> 
> **3. 액션 실행**:
> - 화면 터치 시뮬레이션
> - 텍스트 입력
> - 스와이프/드래그 제스처
> 
> **4. 이중 통신**:
> - **TCP**: 빠름, 포트 포워딩 필요
> - **Content Provider**: 느림, 추가 설정 불필요

<Note>
Portal은 ADB를 통해 로컬에서만 통신합니다. 외부 서버로 데이터가 전송되지 않습니다.
</Note>

> 🔒 **개인정보 보호**
> 
> **로컬 전용 통신**:
> - 모든 통신이 컴퓨터 ↔ 기기 사이에서만 발생
> - 인터넷 연결 불필요 (LLM 호출 제외)
> - 외부 서버에 화면 정보 전송 안 함
> 
> **보안 검증**:
> - 오픈소스: 코드 검증 가능
> - ADB 권한 필요: 신뢰할 수 있는 기기만 연결

---

## 통신 모드

<AccordionGroup>
<Accordion title="TCP 모드 (권장) - 작업별">

**작동 방식:**
- Portal이 기기 포트 8080에서 HTTP 서버 실행
- ADB가 로컬 포트 → 기기 포트 8080으로 포워딩
- Droidrun이 `localhost:PORT`로 HTTP 요청 전송

> 📖 **포트 포워딩이란?**
> 
> **정의**: 컴퓨터의 포트를 기기의 포트로 연결하는 기술
> 
> **쉬운 비유**:
> - 기기의 8080번 문(포트)으로 가려면
> - 컴퓨터의 8080번 통로를 만들어서
> - 그 통로를 통해 기기의 문으로 직접 연결
> 
> **명령어**:
> ```bash
> adb forward tcp:8080 tcp:8080
> # 컴퓨터:8080 → 기기:8080
> ```

**활성화:**

```bash
# CLI
droidrun run "명령어" --tcp

# Python
tools = DeviceConfig(serial="DEVICE_SERIAL", use_tcp=True)
```

**문제 해결:**

```bash
# 포트 포워딩 확인
adb forward --list

# Portal 서버 테스트
adb shell netstat -an | grep 8080

# 모든 포워딩 제거 후 재시도
adb forward --remove-all
droidrun ping --tcp
```

> 💡 **TCP 모드 사용 시나리오**
> 
> **권장하는 경우**:
> - 빠른 응답 속도 필요
> - 많은 명령 연속 실행
> - 안정적인 USB 연결 환경
> 
> **주의사항**:
> - 포트 포워딩 설정 필요
> - USB 연결 끊기면 재설정 필요
> - 방화벽이 포트를 차단할 수 있음

</Accordion>

<Accordion title="Content Provider (대체) - 작업별">

**작동 방식:**
- Portal이 `content://com.droidrun.portal/`에 content provider 노출
- `adb shell`을 통해 명령 전송: `content query --uri ...`
- 쉘 출력에서 JSON 응답 파싱

> 📖 **Content Provider란?**
> 
> **정의**: Android 앱 간 데이터를 공유하는 표준 방식
> 
> **쉬운 비유**:
> - TCP = 직접 전화 통화 (빠름)
> - Content Provider = 우편 (느리지만 확실함)
> 
> **특징**:
> - 설정 불필요 (자동 작동)
> - TCP보다 느림
> - 안정적 (추가 설정 없음)

**사용법:**

```bash
# 기본 모드 (플래그 불필요)
droidrun ping

# Python
tools = DeviceConfig(serial="DEVICE_SERIAL", use_tcp=False)
```

**문제 해결:**

```bash
# content provider 직접 테스트
adb shell content query --uri content://com.droidrun.portal/state

# 출력 예상: Row: 0 result={"data": "{...}"}
```

> 💡 **Content Provider 사용 시나리오**
> 
> **권장하는 경우**:
> - TCP 설정이 어려운 경우
> - 포트 포워딩 문제 발생 시
> - 단순한 명령 몇 개 실행
> 
> **자동 폴백**:
> - TCP 연결 실패 시 자동으로 Content Provider로 전환
> - 사용자 개입 없이 작동

</Accordion>
</AccordionGroup>

---

## 고급 설정

<AccordionGroup>
<Accordion title="무선 디버깅 (Android 11 이상)">

### 설정

<Steps>
<Step title="무선 디버깅 활성화">

1. **설정** > **개발자 옵션** > **무선 디버깅**
2. IP 주소와 포트 확인 (예: `192.168.1.100:37757`)

> 📖 **무선 디버깅이란?**
> 
> **정의**: USB 케이블 없이 Wi-Fi로 ADB 연결
> 
> **장점**:
> - ✓ 케이블 불필요
> - ✓ 이동 중에도 사용 가능
> - ✓ 여러 기기 동시 연결 쉬움
> 
> **단점**:
> - ✗ 초기 페어링 복잡
> - ✗ 같은 Wi-Fi 네트워크 필요
> - ✗ USB보다 느릴 수 있음

</Step>

<Step title="기기 페어링 (최초 1회)">

**QR 코드 방식:**
```bash
adb pair <QR_CODE_STRING>
```

**페어링 코드 방식:**
1. **페어링 코드로 기기 페어링** 탭
2. 페어링 코드와 IP:포트 확인
3. 실행: `adb pair IP:PORT`
4. 페어링 코드 입력

> 💡 **페어링 방식 선택**
> 
> **QR 코드** (추천):
> - 빠름
> - 입력 오류 없음
> - QR 코드 스캐너 필요
> 
> **페어링 코드**:
> - QR 스캐너 없을 때
> - 6자리 코드 수동 입력
> - 1회만 필요

</Step>

<Step title="연결">

```bash
adb connect IP:PORT
droidrun ping --device IP:PORT
```

</Step>
</Steps>

### 일반적인 문제

- **연결 거부** → 같은 Wi-Fi 네트워크 확인 및 방화벽 체크
- **연결 자주 끊김** → 5GHz Wi-Fi 사용 또는 공유기 근처에서 사용
- **IP를 찾을 수 없음** → USB로 연결 후 `adb shell ip addr show wlan0 | grep "inet "` 실행

> 🔧 **문제 해결 상세**
> 
> **1. 연결 거부 (Connection Refused)**:
> ```bash
> # 같은 네트워크 확인
> # 컴퓨터 IP: 192.168.1.10
> # 기기 IP: 192.168.1.100
> # → 앞 3자리 (192.168.1) 동일해야 함
> 
> # 방화벽 확인 (Windows)
> # 제어판 → 방화벽 → 5555, 37757 포트 허용
> ```
> 
> **2. 연결 끊김**:
> - 2.4GHz Wi-Fi: 느리고 불안정
> - 5GHz Wi-Fi: 빠르고 안정적 (권장)
> - 공유기와 거리: 가까울수록 좋음
> 
> **3. IP 찾기**:
> ```bash
> # USB로 먼저 연결
> adb shell ip addr show wlan0 | grep "inet "
> # 출력: inet 192.168.1.100/24
> ```

</Accordion>

<Accordion title="무선 디버깅 (Android 10 이하)">

<Steps>
<Step title="TCP/IP 모드 활성화 (USB 필요)">

```bash
# 먼저 USB로 연결
adb tcpip 5555
```

> 📖 **tcpip 5555 명령어**
> 
> **의미**: 
> - ADB를 TCP/IP 모드로 전환
> - 5555번 포트 사용
> 
> **왜 USB가 먼저 필요한가?**
> - 초기 설정은 물리적 연결 필요
> - 이후에는 무선으로 사용 가능

</Step>

<Step title="기기 IP 찾기">

```bash
adb shell ip addr show wlan0 | grep inet
```

</Step>

<Step title="무선 연결">

```bash
# USB 케이블 분리
adb connect DEVICE_IP:5555
droidrun ping --device DEVICE_IP:5555
```

> 💡 **Android 10 이하 무선 연결 특징**
> 
> **장점**:
> - 페어링 과정 없음 (간단)
> - 한 번만 설정하면 됨
> 
> **단점**:
> - USB 연결 필요 (최초)
> - 보안이 약함 (페어링 없음)
> - 재부팅 시 재설정 필요

</Step>
</Steps>

</Accordion>

<Accordion title="여러 기기 사용">

### 기기 목록

```bash
droidrun devices
# Found 2 connected device(s):
#   • emulator-5554
#   • 192.168.1.100:5555
```

### 특정 기기 지정

```bash
# CLI
droidrun run "명령어" --device emulator-5554

# Python
tools = DeviceConfig(serial="emulator-5554")
agent = DroidAgent(goal="작업", tools=tools)
```

> 📖 **기기 시리얼 번호 형식**
> 
> **에뮬레이터**: `emulator-5554`, `emulator-5556`
> - 5554부터 2씩 증가
> - 여러 에뮬레이터 동시 실행 가능
> 
> **USB 연결**: `ABC123DEF456` (기기 고유 번호)
> - 기기마다 다름
> - 설정 → 휴대전화 정보에서 확인 가능
> 
> **무선 연결**: `192.168.1.100:5555`
> - IP 주소 + 포트 번호
> - 네트워크 변경 시 IP 변경될 수 있음

### 병렬 제어

```python
import asyncio
from droidrun import DeviceConfig, DroidrunConfig, DroidAgent
from adbutils import adb

async def control_device(serial: str, command: str):
    device_config = DeviceConfig(serial=serial)
    config = DroidrunConfig(device=device_config)
    agent = DroidAgent(goal=command, config=config)
    return await agent.run()

async def main():
    devices = adb.list()

    tasks = [
        control_device(devices[0].serial, "설정 열기"),
        control_device(devices[1].serial, "배터리 확인"),
    ]

    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

> 💡 **병렬 제어 활용 시나리오**
> 
> **다중 기기 테스트**:
> ```python
> # 여러 기기에서 동시에 같은 작업 테스트
> devices = ["emulator-5554", "emulator-5556", "192.168.1.100:5555"]
> 
> async def test_all():
>     tasks = [
>         control_device(d, "앱 설치 및 실행 테스트")
>         for d in devices
>     ]
>     results = await asyncio.gather(*tasks)
>     # 모든 기기 결과 한 번에 확인
> ```
> 
> **대규모 자동화**:
> - 여러 계정 테스트
> - 다양한 기기 모델 검증
> - 성능 비교 테스트

</Accordion>
</AccordionGroup>

---

## 문제 해결

<AccordionGroup>
<Accordion title="기기를 찾을 수 없음">

**증상:** `adb devices`가 기기를 표시하지 않거나 `unauthorized` 표시

**해결 방법:**
1. USB 케이블 분리/재연결, 다른 포트 시도
2. USB 디버깅 권한 취소 (개발자 옵션)
3. 재연결 후 "항상 허용" 탭
4. ADB 재시작: `adb kill-server && adb start-server`
5. **Windows**: [Google USB 드라이버](https://developer.android.com/studio/run/win-usb) 설치

> 🔧 **단계별 문제 해결**
> 
> **1단계: 물리적 연결 확인**
> ```bash
> adb devices
> # 빈 목록 → USB 케이블/포트 문제
> # unauthorized → 권한 문제
> ```
> 
> **2단계: 권한 재설정**
> - 설정 → 개발자 옵션 → USB 디버깅 권한 취소
> - USB 디버깅 끄기 → 다시 켜기
> - USB 재연결 → "항상 허용" 체크
> 
> **3단계: ADB 재시작**
> ```bash
> adb kill-server  # ADB 서버 종료
> adb start-server # ADB 서버 시작
> adb devices      # 다시 확인
> ```
> 
> **4단계 (Windows 전용)**:
> - Google USB 드라이버 필요
> - 기기 제조사 드라이버도 가능
> - 장치 관리자에서 드라이버 업데이트

</Accordion>

<Accordion title="Portal이 설치되지 않음">

**증상:** `droidrun ping`이 "Portal is not installed"로 실패

**해결 방법:**
1. 재설치: `droidrun setup`
2. 확인: `adb shell pm list packages | grep droidrun`
3. APK 아키텍처가 기기와 일치하는지 확인 (대부분 arm64-v8a)

> 🔧 **Portal 설치 검증**
> 
> **설치 확인**:
> ```bash
> adb shell pm list packages | grep droidrun
> # 출력: package:com.droidrun.portal
> # → 설치됨
> 
> # 출력 없음 → 설치 안 됨
> ```
> 
> **아키텍처 확인**:
> ```bash
> adb shell getprop ro.product.cpu.abi
> # 출력: arm64-v8a (최신 기기)
> # 출력: armeabi-v7a (구형 기기)
> ```
> 
> **수동 설치**:
> ```bash
> # APK 파일 직접 다운로드
> adb install -g portal-arm64-v8a.apk
> ```

</Accordion>

<Accordion title="접근성 서비스가 활성화되지 않음">

**증상:** `droidrun ping`이 "accessibility service not enabled"로 실패

**해결 방법:**
1. 자동 활성화:
   ```bash
   adb shell settings put secure enabled_accessibility_services \
     com.droidrun.portal/com.droidrun.portal.DroidrunAccessibilityService
   adb shell settings put secure accessibility_enabled 1
   ```
2. 수동: 설정 > 접근성 > Droidrun Portal > 토글 ON
3. 확인:
   ```bash
   adb shell settings get secure enabled_accessibility_services
   # 출력에 포함되어야 함: com.droidrun.portal/...
   ```

> 📖 **접근성 서비스 권한**
> 
> **왜 필요한가?**
> - 화면의 모든 UI 요소 읽기
> - 터치/스와이프 동작 수행
> - 텍스트 입력
> 
> **보안 경고**:
> - Android가 "이 앱이 화면을 볼 수 있습니다" 경고 표시
> - 정상적인 동작 (Droidrun이 화면을 봐야 제어 가능)
> - Portal은 로컬에서만 작동 (인터넷 전송 없음)
> 
> **활성화 확인**:
> ```bash
> adb shell settings get secure enabled_accessibility_services
> # com.droidrun.portal 포함 → 활성화됨
> # 포함 안 됨 → 비활성화됨
> ```

</Accordion>

<Accordion title="텍스트 입력이 작동하지 않음">

**증상:** `input_text()`가 실패하거나 이상한 문자 입력

**해결 방법:**
1. 키보드 자동 활성화 (`AdbTools.__init__()`에서 수행):
   ```bash
   # 확인
   adb shell settings get secure default_input_method
   # 출력: com.droidrun.portal/.DroidrunKeyboardIME
   ```
2. 수동 전환: 스페이스 바 길게 누르기 → "Droidrun Keyboard" 선택
3. 먼저 요소에 포커스: `tools.tap_by_index(5)` 후 `tools.input_text("text")`

> 📖 **Droidrun 키보드 (IME)**
> 
> **IME (Input Method Editor)란?**
> - 텍스트 입력 방식을 제어하는 시스템
> - 한글, 영어, 이모지 등 입력 담당
> 
> **Droidrun 키보드 특징**:
> - 화면에 키보드 표시 없음 (백그라운드 작동)
> - API를 통한 직접 텍스트 입력
> - 특수문자, 유니코드 모두 지원
> 
> **문제 상황**:
> ```python
> # ❌ 잘못된 방법
> tools.input_text("Hello")  # 포커스 없음 → 실패
> 
> # ✅ 올바른 방법
> tools.tap_by_index(5)      # 텍스트 필드 클릭
> tools.input_text("Hello")   # 입력 성공
> ```

</Accordion>

<Accordion title="UI 상태가 비어있음">

**증상:** `get_state()`가 빈 UI 트리 또는 불완전한 트리 반환

**해결 방법:**
1. 접근성 확인: `droidrun ping`
2. 일부 앱은 접근성 서비스를 차단 (WebView, 게임, 커스텀 UI)
3. UI 대기: tap/swipe 후 `time.sleep(1)`
4. Portal 오버레이 활성화하여 감지된 요소 확인

> 💡 **UI 트리가 비는 이유**
> 
> **1. 접근성 차단 앱**:
> - 게임: Unity, Unreal Engine
> - WebView: 브라우저 내장 뷰
> - 금융 앱: 보안상 차단
> - 해결: 대체 방법 없음 (앱 제한)
> 
> **2. UI 로딩 시간**:
> ```python
> tools.tap_by_index(5)
> time.sleep(1)  # UI 로드 대기
> state = tools.get_state()  # 완전한 트리 반환
> ```
> 
> **3. 동적 UI**:
> - 애니메이션 중인 요소
> - 스크롤 중인 리스트
> - 해결: `wait_for_stable_ui` 설정 증가
> 
> **4. Portal 오버레이**:
> - Portal 앱 열기 → 오버레이 활성화
> - 화면에 감지된 요소 표시
> - 디버깅에 유용

</Accordion>
</AccordionGroup>

</Tab>

<Tab title="iOS 설정 (실험적)">

<Warning>
iOS 지원은 현재 **실험적** 단계입니다. Android에 비해 기능이 제한적입니다.
</Warning>

> ⚠️ **iOS 실험적 지원 의미**
> 
> **현재 상태**:
> - 기본 기능 작동 (탭, 스와이프, 스크린샷)
> - 일부 기능 미구현 (뒤로가기, 드래그 등)
> - 안정성 검증 중
> 
> **프로덕션 사용 주의**:
> - 중요한 작업에는 권장하지 않음
> - 기능 변경 가능성 있음
> - 피드백 환영

---

## 사전 준비사항

- Xcode가 설치된 **macOS**
- 개발자 모드가 활성화된 **iOS 기기**
- **iOS Portal 앱** (Android Portal과 별도)

> 📖 **iOS 개발자 모드란?**
> 
> **정의**: iOS 16 이상에서 개발 및 디버깅을 위한 특별 모드
> 
> **활성화 방법**:
> 1. 설정 → 개인정보 보호 및 보안
> 2. 개발자 모드 (맨 아래)
> 3. 토글 ON
> 4. 기기 재시작
> 5. 확인 팝업에서 "켜기" 선택
> 
> **주의사항**:
> - iOS 16 이상 필요
> - 재시작 필요
> - 보안 경고 표시 (정상)

---

## 설정

<Steps>
<Step title="iOS Portal 설치">

iOS Portal 앱은 기기에 수동으로 설치해야 합니다.

<Note>
설치 안내 및 다운로드 링크는 곧 제공될 예정입니다.
</Note>

> 📖 **iOS Portal 수동 설치 이유**
> 
> **Android vs iOS 차이**:
> - **Android**: ADB로 자동 설치 가능
> - **iOS**: Apple 정책상 수동 설치 필요
> 
> **설치 방법 (예정)**:
> 1. TestFlight를 통한 배포
> 2. 또는 Xcode로 직접 빌드
> 3. 또는 Enterprise 인증서로 배포
> 
> **현재 상태**:
> - 설치 방법 준비 중
> - GitHub에서 공지 예정

</Step>

<Step title="기기 IP 확인">

설정 → Wi-Fi → (i) 아이콘에서 iOS 기기의 IP 주소 확인

> 💡 **iOS IP 주소 찾기**
> 
> **단계별 확인**:
> 1. 설정 앱 열기
> 2. Wi-Fi 탭
> 3. 연결된 네트워크 이름 옆 (i) 탭
> 4. "IP 주소" 항목 확인
> 
> **예시**: 192.168.1.100
> 
> **주의사항**:
> - Wi-Fi 연결 필수
> - 컴퓨터와 같은 네트워크
> - DHCP 사용 시 IP 변경될 수 있음

</Step>

<Step title="연결 테스트">

```python
from droidrun import IOSTools

tools = IOSTools(url="http://DEVICE_IP:8080")
result = tools.ping()
print(result)
```

> 📖 **iOS 연결 구조**
> 
> **Android와의 차이**:
> - **Android**: ADB → Portal
> - **iOS**: HTTP 직접 연결 → Portal
> 
> **URL 형식**:
> ```
> http://[기기 IP]:[포트]
> 예: http://192.168.1.100:8080
> ```
> 
> **포트 번호**:
> - 기본값: 8080
> - Portal 앱 설정에서 변경 가능
> - 방화벽에서 허용 필요

</Step>
</Steps>

---

## 아키텍처

iOS Portal은 Android와 다른 아키텍처를 사용합니다:

| 기능 | Android | iOS |
|------|---------|-----|
| 통신 방식 | ADB + TCP/Content Provider | HTTP 서버만 |
| 설정 도구 | `droidrun setup` | 수동 설치 |
| 접근성 | Android Accessibility API | iOS Accessibility API |
| 텍스트 입력 | 커스텀 키보드 IME | 직접 텍스트 입력 |

> 📖 **플랫폼 차이 상세**
> 
> **1. 통신 방식**:
> - **Android**: 
>   - USB 케이블 → ADB → Portal
>   - 복잡하지만 강력함
> - **iOS**: 
>   - Wi-Fi → HTTP → Portal
>   - 간단하지만 제한적
> 
> **2. 설정**:
> - **Android**: 
>   - `droidrun setup` 한 번
>   - 자동화된 설치
> - **iOS**: 
>   - 수동 앱 설치
>   - Apple 정책 제약
> 
> **3. 접근성 API**:
> - **Android**: 
>   - 강력한 접근성 서비스
>   - 모든 UI 요소 접근 가능
> - **iOS**: 
>   - 제한적인 접근성 API
>   - 일부 앱 정보 접근 제한
> 
> **4. 텍스트 입력**:
> - **Android**: 
>   - 커스텀 IME 키보드
>   - 백그라운드 입력
> - **iOS**: 
>   - 직접 입력 API
>   - 포커스 제한

---

## 사용법

### Python API

```python
from droidrun import IOSTools, DroidAgent

# 기기 URL로 iOS 도구 초기화
tools = IOSTools(
    url="http://192.168.1.100:8080",
    bundle_identifiers=["com.example.app"]  # 선택사항
)

# 에이전트 생성
agent = DroidAgent(
    goal="설정 열고 Wi-Fi 확인",
    tools=tools
)

result = await agent.run()
```

> 📖 **bundle_identifiers란?**
> 
> **정의**: iOS 앱의 고유 식별자
> 
> **형식**: `com.회사명.앱명`
> - 예: `com.apple.mobilesafari` (Safari)
> - 예: `com.apple.Preferences` (설정)
> 
> **용도**:
> - 특정 앱만 제어하도록 제한
> - 여러 앱 지정 가능 (리스트)
> 
> **생략 가능**:
> - 지정 안 하면 모든 앱 제어 가능
> - 보안상 특정 앱만 지정 권장

### CLI

```bash
# --ios 플래그 사용
droidrun run "명령어" --ios

# 또는 config.yaml에서 플랫폼 설정:
# device:
#   platform: ios
```

> 💡 **CLI에서 iOS 사용**
> 
> **방법 1: 플래그 사용**:
> ```bash
> droidrun run "설정 열기" --ios
> # 매번 --ios 플래그 필요
> ```
> 
> **방법 2: 설정 파일** (권장):
> ```yaml
> # config.yaml
> device:
>   platform: ios
>   serial: "http://192.168.1.100:8080"
> ```
> ```bash
> droidrun run "설정 열기"
> # 플래그 불필요
> ```

---

## 제한사항

현재 iOS 지원에는 다음과 같은 제한사항이 있습니다:

| 기능 | 상태 | 비고 |
|------|------|------|
| `get_date()` | ❌ | "Not implemented for iOS" 반환 |
| `back()` | ❌ | `NotImplementedError` 발생 |
| `drag()` | ❌ | 미구현, False 반환 |
| `get_apps()` | ⚠️ | 대신 `list_packages()` 사용 |
| `input_text()` | ⚠️ | `index` 및 `clear` 파라미터 없음 |
| `tap()`, `swipe()` | ✅ | 완전 지원 |
| `get_state()` | ✅ | 접근성 트리 반환 |
| `take_screenshot()` | ✅ | 완전 지원 |

> 📖 **제한사항 상세 설명**
> 
> **❌ 미구현 기능**:
> ```python
> # get_date() - 기기 날짜/시간
> date = tools.get_date()
> # 오류: "Not implemented for iOS"
> 
> # back() - 뒤로가기
> tools.back()
> # 오류: NotImplementedError
> 
> # drag() - 드래그 제스처
> tools.drag(100, 100, 200, 200)
> # 반환: False (작동 안 함)
> ```
> 
> **⚠️ 부분 지원 기능**:
> ```python
> # get_apps() - 사용 금지
> # apps = tools.get_apps()  # 작동 안 함
> 
> # 대신 list_packages() 사용
> packages = tools.list_packages()
> 
> # input_text() - 제한적
> tools.input_text("Hello")  # 작동
> # tools.input_text("Hello", index=5)  # 오류: index 미지원
> # tools.input_text("Hello", clear=True)  # 오류: clear 미지원
> ```
> 
> **✅ 완전 지원 기능**:
> ```python
> # 기본 제어 기능
> tools.tap_by_index(5)      # 탭
> tools.swipe(100, 500, 100, 100)  # 스와이프
> state = tools.get_state()  # UI 상태
> screenshot = tools.take_screenshot()  # 스크린샷
> ```
> 
> **대체 방법**:
> - `back()` 없음 → 홈 버튼 좌표로 `tap()` 사용
> - `drag()` 없음 → 긴 `swipe()`로 대체
> - `get_date()` 없음 → 시스템 API 직접 호출

</Tab>
</Tabs>

---

## 다음 단계

- [에이전트 시스템](/concepts/architecture) 학습하기
- [구성 옵션](/sdk/configuration) 살펴보기
- [커스텀 도구](/features/custom-tools) 시도하기
- [구조화된 출력](/features/structured-output) 구현하기

---

## 요약

**기기 설정 핵심 단계**:

**Android**:
1. ✓ ADB 설치 및 USB 디버깅 활성화
2. ✓ `droidrun setup`으로 Portal 설치
3. ✓ `droidrun ping`으로 연결 확인
4. ✓ TCP 모드 권장 (빠름)

**iOS** (실험적):
1. ✓ macOS + Xcode 필요
2. ✓ iOS Portal 수동 설치
3. ✓ Wi-Fi로 HTTP 연결
4. ✓ 일부 기능 제한 있음

**문제 해결 우선순위**:
1. `adb devices`로 연결 확인
2. `droidrun ping`으로 Portal 확인
3. 접근성 서비스 활성화 확인
4. 문제 해결 섹션 참조

**고급 기능**:
- 무선 디버깅 (편리함)
- 여러 기기 병렬 제어 (효율적)
- TCP vs Content Provider (속도 vs 안정성)
