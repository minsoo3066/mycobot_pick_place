# myCobot 280-Pi Pick & Place

Elephant Robotics **myCobot 280-Pi**에서 `pymycobot`을 사용해 매트 위의 물체를 집고 다른 위치로 옮기는 Pick & Place 동작을 단계별로 실습한 저장소입니다.

현재 단계에서는 카메라 인식보다 먼저 **좌표 기반 Pick & Place 동작을 안정적으로 구현**하는 것을 목표로 합니다. 이후 매트 UI에서 출발점과 도착점을 선택하고, 최종적으로 카메라 기반 물체 인식까지 확장할 예정입니다.

> 아래 좌표와 HOME 자세는 현재 실습 장비의 설치 상태에서 측정한 값입니다. 다른 장비나 설치 자세에서는 그대로 사용하면 안 됩니다.

## 환경

- Robot: Elephant Robotics myCobot 280-Pi
- ROS 2: Galactic
- Robot control: `pymycobot`
- Work mat: 400 mm × 400 mm
- Robot base: 매트 중앙에 배치

## 프로젝트 목표

1. 로봇 현재 상태 확인
2. HOME 자세 정의
3. Pick / Place 좌표 직접 기록
4. 그리퍼 Open / Close 제어
5. 안전 높이를 이용한 수직 접근 및 상승
6. `HOME -> Pick -> HOME -> Place -> HOME` 전체 동작 구현
7. 로봇 X/Y 좌표 방향 확인
8. 매트 UI에서 START / GOAL 선택
9. UI 좌표를 로봇 좌표로 변환
10. 이후 카메라 기반 물체 인식으로 확장

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

HOME에서 측정한 End-Effector 좌표는 다음과 같았습니다.

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

A와 B의 Z 차이는 매트 높이 차이가 아니라 수동으로 위치를 기록하면서 생긴 오차입니다. 현재 B 높이에서도 Place 동작은 정상적으로 확인했습니다.

## 안전 높이

물체에 접근할 때 바로 XY 이동을 하지 않고, Pick/Place 지점 위쪽으로 먼저 이동한 뒤 수직으로 내려갑니다.

```python
SAFE_HEIGHT = 70.0
```

예를 들어 Pick A의 Z가 `110.4 mm`이면:

```text
PICK_A_ABOVE Z = 180.4 mm
```

입니다.

## 이동 모드

`sync_send_coords(coords, speed, mode)`에서 이번 실습에서는 두 가지 모드를 사용했습니다.

- `mode = 0`: angular 이동. HOME과 작업 영역 사이처럼 큰 이동에 사용
- `mode = 1`: linear 이동. 물체 위에서 수직으로 접근하거나 들어 올릴 때 사용

현재 기본 규칙은 다음과 같습니다.

```text
HOME -> A_ABOVE       mode 0
A_ABOVE -> A          mode 1
A -> A_ABOVE          mode 1
A_ABOVE -> HOME       joint HOME movement
HOME -> B_ABOVE       mode 0
B_ABOVE -> B          mode 1
B -> B_ABOVE          mode 1
B_ABOVE -> HOME       joint HOME movement
```

## 전체 Pick & Place 순서

최종적으로 검증한 동작 순서는 다음과 같습니다.

```text
HOME
  ↓
Open Gripper
  ↓
A_ABOVE
  ↓
A
  ↓
Close Gripper
  ↓
A_ABOVE
  ↓
HOME
  ↓
B_ABOVE
  ↓
B
  ↓
Open Gripper
  ↓
B_ABOVE
  ↓
HOME
```

A에서 B로 바로 이동하지 않고 **물체를 잡은 상태에서도 HOME을 경유**하도록 구성했습니다. `move_home()`은 팔의 관절 자세만 변경하며 그리퍼 상태는 변경하지 않기 때문에 물체를 잡은 채 HOME을 거칠 수 있습니다.

## 로봇 XY 좌표 방향 확인

Pick A의 안전 높이에서 X와 Y를 각각 `+20 mm` 이동해 실제 방향을 확인했습니다.

```text
X +20 mm -> 로봇 기준 앞으로 이동
Y +20 mm -> 로봇 기준 왼쪽으로 이동
```

따라서 현재 설치 기준 좌표 방향은 다음과 같습니다.

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

이 방향을 이후 매트 UI의 화면 방향과 그대로 대응시킬 예정입니다.

## 파일 설명

- `robot_state_check.py`: 현재 Joint angle과 Cartesian 좌표 확인
- `robot_controller.py`: 로봇 연결 및 HOME 복귀 기본 클래스 실습
- `point_recorder.py`: Servo를 풀고 수동으로 원하는 지점의 좌표 기록
- `test_pick_lift.py`: Pick A에서 70 mm 수직 상승 테스트
- `test_home_route.py`: Pick A 작업 영역과 HOME 사이 이동 경로 테스트
- `test_pick.py`: 실제 물체 Pick 및 Lift 테스트
- `test_release.py`: Pick A에 물체를 다시 내려놓는 Release 테스트
- `test_place_position.py`: Place B의 수직 상승/하강 테스트
- `test_xy_direction.py`: Robot X/Y 좌표의 실제 방향 확인
- `pick_and_place.py`: 전체 Pick & Place 동작

## 현재 완료 항목

- [x] `pymycobot` 연결 확인
- [x] `get_angles()` 확인
- [x] `get_coords()` 확인
- [x] HOME 자세 정의
- [x] HOME 복귀 동작
- [x] Pick A 좌표 기록
- [x] Place B 좌표 기록
- [x] Cartesian 이동
- [x] Gripper Open / Close
- [x] Pick A 수직 접근
- [x] 물체 집기
- [x] 물체 들어 올리기
- [x] 물체 내려놓기
- [x] HOME 경유 이동
- [x] 전체 `HOME -> A -> HOME -> B -> HOME` 동작
- [x] X/Y 좌표 방향 확인

## 다음 진행

다음 단계는 `mat_ui.py` 구현입니다.

1. 400 × 400 mm 매트를 Tkinter UI로 표현
2. 화면 중앙에 로봇 위치 표시
3. START 지점 선택
4. GOAL 지점 선택
5. UI 좌표를 Robot X/Y 좌표로 변환
6. 실제 로봇을 움직이기 전에 좌표 변환 결과만 검증
7. 접근 불가 영역 / 로봇 베이스 영역 설정
8. 검증 후 `pick_and_place()`와 연결

그 이후에는 ROS 2 Action 구조와 카메라 기반 물체 인식을 단계적으로 추가할 예정입니다.
