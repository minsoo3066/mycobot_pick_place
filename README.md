# myCobot 280-Pi Pick & Place

Elephant Robotics **myCobot 280-Pi**에서 `pymycobot`을 사용해 매트 위의 물체를 집고 다른 위치로 옮기는 Pick & Place 프로젝트입니다.

현재는 **400 × 400 mm 작업 매트 UI에서 START / GOAL을 선택하고, HOME 경유 Pick & Place를 실제 로봇에 실행하는 단계까지 완료**했습니다. Preview, Emergency Stop, 위치 기반 orientation 보정, USB 카메라 입력까지 확장한 상태입니다.

> 아래 좌표와 자세 값은 현재 실습 장비의 설치 상태에서 측정한 값입니다. 다른 장비나 설치 자세에서는 그대로 사용하면 안 됩니다.

## 환경

- Robot: Elephant Robotics myCobot 280-Pi
- ROS 2: Galactic
- Robot control: `pymycobot`
- UI: Tkinter
- Camera: USB camera + OpenCV
- Work mat: 400 mm × 400 mm
- Robot base: 매트 중앙 배치
- Project path: `~/mycobot_pick_place`

## 현재 프로젝트 구조

```text
mycobot_pick_place/
├── mat_ui.py
│   └── START / GOAL / Preview / Execute / HOME / Emergency Stop
├── workspace.py
│   └── Mat 범위 / DANGER 영역 / 좌표 유효성
├── coordinate_mapper.py
│   └── UI pixel ↔ Robot X,Y
├── robot_controller.py
│   └── pymycobot 실제 제어
├── robot_worker.py
│   └── 별도 Thread / 실행 상태 / stop_event
├── pick_and_place.py
│   └── HOME 경유 Pick & Place / 작업 pose 생성
├── camera_test.py
│   └── USB 카메라 영상 확인
└── dual_camera_test.py
    └── USB 카메라 2대 동시 영상 확인
```

## 로봇 좌표계

```text
                  +X
                FRONT
                  ↑
                  |
        +Y  <-  ROBOT  ->  -Y
        LEFT              RIGHT
                  |
                  ↓
                 -X
                BACK
```

실제 테스트 결과:

```text
X +20 mm -> 로봇 기준 앞으로 이동
Y +20 mm -> 로봇 기준 왼쪽으로 이동
```

UI에서는 다음과 같이 대응합니다.

```text
화면 위     = Robot X+
화면 아래   = Robot X-
화면 왼쪽   = Robot Y+
화면 오른쪽 = Robot Y-
```

## HOME

현재 HOME 자세는 관절 상태를 보기 쉽게 다음과 같이 변경했습니다.

```python
HOME_ANGLES = [
    0,
    0,
    0,
    -86,
    0,
    -40
]
```

새 HOME에서 측정한 End-Effector pose:

```text
X  = 77.3
Y  = -63.3
Z  = 303.4
Rx = -178.31
Ry = -1.82
Rz = -50.57
```

HOME 복귀는 Cartesian pose가 아니라 `HOME_ANGLES`를 기준으로 수행합니다.

## Pick & Place 작업 높이

매트가 평평하므로 Pick / Place의 작업 높이를 하나로 통일했습니다.

```python
MAT_Z = 106.0
SAFE_HEIGHT = 70.0
```

따라서 현재 매트 작업 기준은:

```text
Pick / Place Z = 106 mm
ABOVE Z        = 176 mm
```

Preview와 Execute에서 모두 정상 동작을 확인했습니다.

향후 매트 밖으로 작업 영역을 확장하면 해당 영역은 매트보다 약 10 mm 낮으므로 별도의 작업 Z(약 96 mm)를 적용할 예정입니다.

## End-Effector orientation

현재는 모든 위치에 동일한 orientation을 강제로 적용하지 않고, **Rx / Ry는 기본 자세를 유지하고 Rz는 로봇 원점 기준 작업 위치에 따라 변경**하는 방향으로 구성했습니다.

기준값:

```python
BASE_RX = -178.31
BASE_RY = -1.82

REFERENCE_X = 167.0
REFERENCE_Y = -29.2
REFERENCE_RZ = -52.13
```

작업 위치 `(x, y)`의 방향을:

```python
target_angle = math.degrees(math.atan2(y, x))
```

으로 계산하고, 기준점과의 각도 차이를 `Rz`에 반영합니다.

계산된 `Rz`는 다음 식으로 `-180° ~ +180°` 범위에 정규화합니다.

```python
rz = (rz + 180) % 360 - 180
```

## 전체 Pick & Place 순서

```text
HOME
  ↓
Open Gripper
  ↓
START_ABOVE
  ↓
START
  ↓
Close Gripper
  ↓
START_ABOVE
  ↓
HOME
  ↓
GOAL_ABOVE
  ↓
GOAL
  ↓
Open Gripper
  ↓
GOAL_ABOVE
  ↓
HOME
```

START에서 GOAL로 직접 이동하지 않고 **중간에 반드시 HOME을 경유**합니다.

## 이동 모드

`sync_send_coords(coords, speed, mode)`에서:

- `mode = 0`: angular 이동. HOME과 작업 영역 사이의 큰 이동
- `mode = 1`: linear 이동. 물체 접근 / 상승처럼 직선 이동이 필요한 구간

로봇 동작 사이의 불필요한 대기시간을 줄이기 위해 `time.sleep()` 값도 조정했습니다. `sync_send_coords()`처럼 완료를 기다리는 API 뒤의 추가 대기는 최소화하는 방향으로 정리했습니다.

## Mat UI

Tkinter 기반으로 400 × 400 mm 작업 매트를 표현했습니다.

현재 기능:

- Select START
- Select GOAL
- Preview START
- Preview GOAL
- Clear
- Execute
- HOME
- EMERGENCY STOP
- 선택 좌표 Robot X/Y 표시
- Cursor Robot X/Y 실시간 표시
- DANGER 영역 선택 방지

버튼은 기능별로 두 줄로 분리했습니다.

```text
Select START | Select GOAL | Preview START | Preview GOAL | Clear
Execute | HOME | EMERGENCY STOP
```

## Preview

UI에서 선택한 좌표가 실제 매트의 어느 위치인지 실행 전에 확인하기 위해 Preview 기능을 추가했습니다.

```text
HOME
 ↓
START_ABOVE 또는 GOAL_ABOVE
 ↓
해당 위치에서 정지
```

실제 Pick / Place 높이까지 내려가지 않고 ABOVE 위치까지만 이동합니다. Preview 역시 `RobotWorker`에서 실행하므로 이동 중 UI와 Emergency Stop을 계속 사용할 수 있습니다.

## DANGER 영역

로봇 베이스 실측 크기:

```text
좌우: 120 mm
앞뒤: 150 mm
```

원점 `(0, 0)` 기준 선택 금지 영역:

```text
X: -75 ~ +75 mm
Y: -60 ~ +60 mm
```

UI에서는 `DANGER`로 표시하고 내부 코드에서는 `no_go` 영역으로 관리합니다.

## Worker Thread / Emergency Stop

Tkinter UI가 로봇 동작 중 멈추지 않도록 실제 로봇 작업은 `robot_worker.py`의 별도 Thread에서 실행합니다.

Emergency Stop은 두 동작을 함께 수행합니다.

```text
mc.stop()
→ 현재 motion 정지

stop_event.set()
→ Pick & Place의 이후 명령 차단
```

HOME / Preview / Execute는 Worker Thread에서 실행하고 Emergency Stop은 UI에서 즉시 호출할 수 있도록 구성했습니다.

## 카메라 구조

카메라는 로봇 상단 수직 시점이 아니라 **로봇 하단에서 정면 작업 영역을 바라보도록 설치**되어 있습니다.

따라서 전체 매트를 무조건 하나의 화면으로 가정하지 않고 Camera-visible workspace를 별도로 다루는 방향으로 설계합니다.

```text
Camera
  ↓
Object position / pixel
  ↓
Camera pixel (u, v)
  ↓
Camera → Robot calibration
  ↓
Robot X,Y
  ↓
Preview / Pick & Place
```

카메라 영상의 pixel 좌표계:

```text
(0,0) ─────────→ +u
  |
  |
  ↓
 +v
```

## USB 카메라 연결

OpenCV로 USB 카메라 실시간 영상 출력을 확인했습니다.

```python
camera = cv2.VideoCapture(0)
```

또한 두 USB 카메라를 동시에 연결해 정상 영상을 확인했습니다.

`v4l2-ctl --list-devices` 결과:

```text
PC CAMERA 1
├── /dev/video0
└── /dev/video1

USB2.0 PC CAMERA
├── /dev/video2
└── /dev/video3
```

`/dev/video10~16`은 Raspberry Pi codec / ISP 장치이므로 USB 카메라 입력과 구분합니다.

두 물리 카메라는 다음 조합으로 동시에 열었습니다.

```python
camera0 = cv2.VideoCapture(0)
camera1 = cv2.VideoCapture(2)
```

## Camera → Robot 캘리브레이션 계획

물리적인 기준 마커 여러 개를 계속 배치하는 대신 **동일한 마커 하나를 카메라 시야 안의 여러 Robot X/Y 위치로 옮기면서 데이터**를 수집하기로 했습니다.

각 위치에서:

```text
Robot (X, Y) ↔ Camera (u, v)
```

좌표쌍을 수집합니다.

카메라가 하단 전면 시점이므로 단순한 `1 pixel = n mm` 변환은 원근 오차가 생길 수 있습니다. 따라서 여러 좌표쌍으로 평면 Homography를 계산해 Camera pixel을 Robot X/Y로 변환할 예정입니다.

```text
Camera (u,v)
    ↓
Homography
    ↓
Robot (X,Y)
```

카메라가 고정되어 있으면 계산된 변환 행렬을 저장해 재사용할 수 있습니다.

## 현재 완료 항목

- [x] `pymycobot` 연결
- [x] HOME 자세 정의 / 복귀
- [x] Gripper Open / Close
- [x] HOME 경유 Pick & Place
- [x] Robot X/Y 실제 방향 확인
- [x] 400 × 400 mm Mat UI
- [x] START / GOAL 선택
- [x] UI pixel → Robot X/Y 변환
- [x] Robot base DANGER 영역
- [x] Worker Thread 구조
- [x] Emergency Stop (`mc.stop()` + `stop_event`)
- [x] UI Execute → 실제 Pick & Place
- [x] Preview START / GOAL
- [x] 매트 작업 Z = 106 mm 적용
- [x] 새 HOME 자세 적용 / pose 측정
- [x] 위치 기반 Rz 계산 구조
- [x] Rz `-180° ~ +180°` 정규화
- [x] USB 카메라 1대 OpenCV 입력
- [x] USB 카메라 2대 동시 입력 (`/dev/video0`, `/dev/video2`)

## 다음 진행

1. Pick & Place에 사용할 메인 카메라 선정
2. 동일한 기준 마커를 여러 Robot X/Y 위치에 놓고 `(u,v) ↔ (X,Y)` 데이터 수집
3. Homography 계산 및 저장
4. Camera pixel → Robot X/Y 변환 검증
5. 변환된 좌표를 Preview에 연결해 실제 위치 확인
6. 물체 검출 결과를 Pick 좌표로 연결
7. 이후 ROS 2 Action 구조로 확장
