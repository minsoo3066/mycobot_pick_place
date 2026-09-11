# myCobot 280-Pi Pick & Place

Elephant Robotics **myCobot 280-Pi**에서 `pymycobot`을 사용해 매트 위의 물체를 집고 다른 위치로 옮기는 Pick & Place 동작을 단계별로 구현하는 프로젝트입니다.

현재는 **400 × 400 mm 작업 매트 UI에서 START / GOAL을 선택하고, HOME 경유 Pick & Place를 실제 로봇에 실행하는 단계까지 완료**했습니다. 이후 임의 좌표에 적용할 Z / orientation 정책을 정리하고, ROS 2 Action과 카메라 기반 물체 인식으로 확장할 예정입니다.

> 아래 좌표와 HOME 자세는 현재 실습 장비의 설치 상태에서 측정한 값입니다. 다른 장비나 설치 자세에서는 그대로 사용하면 안 됩니다.

## 환경

- Robot: Elephant Robotics myCobot 280-Pi
- ROS 2: Galactic
- Robot control: `pymycobot`
- Work mat: 400 mm × 400 mm
- Robot base: 매트 중앙에 배치
- Project path: `~/mycobot_pick_place`

## 프로젝트 목표

1. HOME / Pick / Place 기본 동작 구현
2. 안전 높이를 이용한 수직 접근 및 상승
3. `HOME -> Pick -> HOME -> Place -> HOME` 경로 구성
4. 매트 UI에서 START / GOAL 선택
5. UI pixel을 Robot X/Y로 변환
6. 로봇 베이스 DANGER 영역 선택 방지
7. HOME / Emergency Stop / Execute UI 연결
8. 이후 임의 좌표와 카메라 기반 입력으로 확장

## 현재까지 검증한 좌표

### HOME

```python
HOME_ANGLES = [
    0.17,
    -0.7,
    -0.96,
    -91.05,
    0.52,
    -39.02
]
```

HOME에서 측정한 End-Effector 좌표:

```python
HOME_COORDS = [
    77.1,
    -62.7,
    296.6,
    178.21,
    2.12,
    -50.84
]
```

HOME 복귀에는 Cartesian 좌표가 아니라 `HOME_ANGLES`를 사용합니다.

### Pick A

```python
PICK_A = [
    167.0,
    -29.2,
    110.4,
    179.83,
    -2.63,
    -52.13
]
```

### Place B

```python
PLACE_B = [
    -102.9,
    -138.5,
    121.7,
    -176.63,
    -4.62,
    -142.87
]
```

A와 B의 Z 차이는 수동 위치 기록 과정에서 생긴 오차입니다. 현재 B 높이에서도 Place 동작은 정상적으로 확인했습니다.

## 안전 높이

```python
SAFE_HEIGHT = 70.0
```

Pick / Place 지점으로 바로 이동하지 않고 먼저 위쪽 안전 높이로 이동한 뒤 수직 접근합니다.

## 이동 모드

`sync_send_coords(coords, speed, mode)`에서:

- `mode = 0`: angular 이동. HOME과 작업 영역 사이의 큰 이동에 사용
- `mode = 1`: linear 이동. 물체 접근 및 상승처럼 직선 이동이 필요한 구간에 사용

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

START에서 GOAL로 직접 이동하지 않고 **중간에 반드시 HOME을 경유**합니다. 현재 프로젝트에서는 이 경로 설계를 주요 안전 전략으로 사용합니다.

## 로봇 XY 좌표 방향

실제 이동 테스트 결과:

```text
X +20 mm -> 로봇 기준 앞으로 이동
Y +20 mm -> 로봇 기준 왼쪽으로 이동
```

따라서 현재 설치 기준 좌표 방향은:

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

UI에서는 다음과 같이 대응합니다.

```text
화면 위     = Robot X+
화면 아래   = Robot X-
화면 왼쪽   = Robot Y+
화면 오른쪽 = Robot Y-
```

## Mat UI

Tkinter 기반으로 400 × 400 mm 작업 매트를 표현했습니다.

현재 기능:

- START 선택
- GOAL 선택
- START 선택 후 자동으로 GOAL 모드 전환
- 선택 좌표 Robot X/Y 표시
- 마우스 Cursor X/Y 실시간 표시
- Clear
- Execute
- HOME
- EMERGENCY STOP

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

UI에서는 `DANGER`로 표시하고, 내부 코드에서는 `no_go` 영역으로 관리합니다.

## 프로젝트 구조

```text
mycobot_pick_place/
│
├── mat_ui.py
│   └── UI / START / GOAL / 버튼 처리
│
├── workspace.py
│   └── Mat 범위 / DANGER 영역 / 좌표 유효성
│
├── coordinate_mapper.py
│   └── UI pixel ↔ Robot X,Y 변환
│
├── robot_controller.py
│   └── pymycobot 실제 제어
│       - move_home()
│       - move_to()
│       - open_gripper()
│       - close_gripper()
│       - emergency_stop()
│
├── robot_worker.py
│   └── Robot task를 별도 Thread에서 실행
│       - 실행 상태 관리
│       - stop_event 관리
│
└── pick_and_place.py
    └── HOME 경유 Pick & Place 동작 순서
```

## Worker Thread와 Emergency Stop

Tkinter UI가 로봇 동작 중 멈추지 않도록 실제 로봇 작업은 `robot_worker.py`의 별도 Thread에서 실행합니다.

설치된 `pymycobot`에서 실제 정지 메서드를 확인했습니다.

```python
def stop(self):
    """Stop moving"""
    return self._mesg(ProtocolCode.STOP)
```

Emergency Stop은 두 가지를 함께 수행합니다.

```text
mc.stop()
→ 현재 motion 정지

stop_event.set()
→ Pick & Place의 이후 명령 실행 차단
```

HOME과 Execute는 Worker Thread에서 실행하고, Emergency Stop 버튼은 UI가 계속 반응하는 상태에서 즉시 호출할 수 있도록 구성했습니다.

## 경로 테스트에서 확인한 점

공통 End-Effector orientation을 유지한 채 여러 점을 이동해보는 실험 중, X- 방향의 한 점에서 그리퍼가 로봇 본체와 충돌한 뒤 더 뒤로 이동하려는 동작이 발생해 즉시 중단했습니다.

이 경험을 바탕으로 모든 좌표를 점 단위로 검증하는 방식보다, **작업점 위로 수직 상승한 뒤 HOME을 거쳐 다음 작업점으로 이동하는 경로를 강제**하는 방향으로 설계를 유지합니다.

## 카메라 확장 고려

현재는 로봇이 매트 중앙에 있지만, 향후 카메라가 전방만 보게 될 가능성을 고려해 **화면 범위와 로봇 좌표계를 분리**했습니다.

```text
UI / Camera
    ↓
Coordinate Mapper
    ↓
Robot X,Y
    ↓
Pick & Place
    ↓
Robot Controller
```

로봇 좌표계는 그대로 유지하고, 카메라 시야가 바뀌면 `workspace`의 표시 / 선택 범위만 변경할 수 있도록 확장할 예정입니다.

## 현재 완료 항목

- [x] `pymycobot` 연결
- [x] `get_angles()` / `get_coords()` 확인
- [x] HOME 자세 정의 및 복귀
- [x] Pick A / Place B 좌표 기록
- [x] Gripper Open / Close
- [x] 수직 Pick / Lift / Release
- [x] `HOME -> Pick -> HOME -> Place -> HOME` 동작
- [x] Robot X/Y 실제 방향 확인
- [x] 400 × 400 mm Mat UI
- [x] START / GOAL 선택
- [x] UI pixel → Robot X/Y 변환
- [x] Cursor 좌표 실시간 표시
- [x] Robot base DANGER 영역
- [x] Execute 확인창
- [x] HOME 버튼 실제 로봇 연결
- [x] Robot Worker Thread 구조
- [x] Emergency Stop 실제 동작 확인
- [x] `mc.stop()` + `stop_event` 적용
- [x] UI Execute → Pick & Place 실제 연결
- [x] UI에서 A → B Pick & Place 성공

## 다음 진행

다음 단계에서는 UI의 임의 좌표를 실제 Pick / Place에 사용할 수 있도록 다음 항목을 정리합니다.

1. 평평한 매트에서 사용할 Pick / Place Z 기준
2. 임의 X/Y에서 사용할 End-Effector orientation 정책
3. 필요 시 workspace를 로봇 전방 또는 Camera visible area로 제한
4. 이후 ROS 2 Action 구조로 확장
5. 카메라 캘리브레이션 및 Camera → Robot 좌표 변환
