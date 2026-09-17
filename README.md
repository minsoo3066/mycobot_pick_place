# myCobot 280-Pi Pick & Place

Elephant Robotics **myCobot 280-Pi**에서 `pymycobot`을 사용해 매트 위의 물체를 집고 다른 위치로 옮기는 Pick & Place 프로젝트입니다.

현재는 **400 × 400 mm 작업 매트 UI, HOME 경유 Pick & Place, Preview, Emergency Stop, Worker Thread 구조까지 실제 로봇에서 검증**했으며, 비전 구조는 전면 고정 카메라 방식에서 **그리퍼 장착 Eye-in-Hand 카메라 기반 Visual Servo 방식**으로 변경했습니다.

> 아래 좌표와 자세 값은 현재 실습 장비의 설치 상태에서 측정한 값입니다. 다른 장비나 설치 자세에서는 그대로 사용하면 안 됩니다.

## 환경

- Robot: Elephant Robotics myCobot 280-Pi
- ROS 2: Galactic
- Robot control: `pymycobot`
- UI: Tkinter
- Vision: USB camera + OpenCV
- Work mat: 400 mm × 400 mm
- Project path: `~/mycobot_pick_place`

## 현재 프로젝트 구조

```text
mycobot_pick_place/
├── mat_ui.py
├── workspace.py
├── coordinate_mapper.py
├── robot_controller.py
├── robot_worker.py
├── pick_and_place.py
├── camera_test.py
└── dual_camera_test.py
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

UI 대응:

```text
화면 위     = Robot X+
화면 아래   = Robot X-
화면 왼쪽   = Robot Y+
화면 오른쪽 = Robot Y-
```

## HOME

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

측정된 HOME End-Effector pose:

```text
X  = 77.3
Y  = -63.3
Z  = 303.4
Rx = -178.31
Ry = -1.82
Rz = -50.57
```

HOME 복귀는 Cartesian pose가 아니라 `HOME_ANGLES` 기준으로 수행합니다.

## Pick & Place 작업 높이

```python
MAT_Z = 106.0
SAFE_HEIGHT = 70.0
```

```text
Pick / Place Z = 106 mm
ABOVE Z        = 176 mm
```

Preview와 Execute에서 정상 동작을 확인했습니다.

## End-Effector orientation

현재 Pick & Place에서는 Rx / Ry를 기본 자세로 유지하고, Rz는 작업 위치에 따라 계산하는 구조를 사용합니다.

```python
BASE_RX = -178.31
BASE_RY = -1.82

REFERENCE_X = 167.0
REFERENCE_Y = -29.2
REFERENCE_RZ = -52.13
```

```python
target_angle = math.degrees(math.atan2(y, x))
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

## Mat UI

현재 기능:

- Select START / GOAL
- Preview START / GOAL
- Clear
- Execute
- HOME
- Emergency Stop
- Cursor Robot X/Y 표시
- DANGER 영역 선택 방지

DANGER 영역:

```text
X: -75 ~ +75 mm
Y: -60 ~ +60 mm
```

## RobotWorker / Emergency Stop

로봇 동작 중 UI가 멈추지 않도록 실제 motion은 `robot_worker.py`의 별도 Thread에서 실행합니다.

```text
mc.stop()
→ 현재 motion 정지

stop_event.set()
→ 이후 motion 명령 차단
```

HOME / Preview / Execute도 Worker Thread를 통해 실행합니다.

## USB 카메라 확인

두 USB 카메라 입력을 확인했습니다.

```text
PC CAMERA 1
├── /dev/video0
└── /dev/video1

USB2.0 PC CAMERA
├── /dev/video2
└── /dev/video3
```

두 물리 카메라는 다음 조합으로 동시에 열 수 있었습니다.

```python
camera0 = cv2.VideoCapture(0)
camera1 = cv2.VideoCapture(2)
```

## 2026-09-17 - Camera calibration 실험

### ChArUco intrinsic calibration

Camera intrinsic calibration에 사용한 보드:

```text
Board          = 5 x 7 squares
Dictionary     = DICT_6X6_50
Square length  = 31 mm
Marker length  = 19 mm
OpenCV         = 4.6.0
```

`aruco.calibrateCameraCharuco()`에서 segmentation fault가 발생해 ChArUco detection 결과를 `cv2.calibrateCamera()`에 전달하는 방식으로 우회했고, intrinsic calibration에 성공했습니다.

결과는 다음 파일에 저장했습니다.

```text
camera1_intrinsics.npz
```

### Gripper ArUco

그리퍼에 부착한 기준 마커:

```text
Dictionary = DICT_6X6_50
ID         = 0
Size       = 25 x 25 mm
```

부착 위치:

```text
Gripper bottom
     ↑ 75 mm
ArUco black square bottom
     ↑ 12.5 mm
ArUco center
```

따라서 그리퍼 최하단에서 ArUco 중심까지는 `87.5 mm`입니다.

25 mm 마커 거리 테스트:

```text
Actual(mm)   Raw Zc(mm)
300          700
250          570
200          450
150          325
100          210
70           145
```

현재 장비 기준 경험적 Z 보정식:

```python
corrected_z = 0.41376 * camera_z + 12.83
```

이 값은 현재 카메라 / 해상도 / intrinsic / 25 mm marker 조합에 대한 실측 보정값입니다.

### Camera ↔ Robot calibration 실험

고정 카메라에서 그리퍼 ArUco를 관찰하며 Camera pose와 Robot TCP pose를 대응시키는 실험을 진행했습니다.

캘리브레이션 중에는 Pick & Place와 비슷하게 Z / Rx / Ry / Rz를 고정하고 X/Y만 이동하도록 구성했습니다.

시작 pose 후보:

```text
X = 243
Y = -5
Z = 176
```

로봇 이동 시 카메라 영상이 멈추는 문제는 `robot.move_to()`가 OpenCV loop와 같은 thread에서 blocking되기 때문으로 확인했습니다. 기존 `RobotWorker`를 재사용해 robot motion과 camera loop를 분리하는 방향으로 정리했습니다.

## 비전 구조 변경

로봇팔의 실제 가동 범위를 고려한 결과, **전면을 바라보는 고정 Camera 1을 메인 카메라로 사용하는 계획은 철회**했습니다.

따라서 기존의:

```text
Fixed Camera
→ Camera to Robot global calibration
→ Object global XY
→ Robot move
```

구조는 더 이상 메인 설계로 사용하지 않습니다.

Camera 1에서 수행한 intrinsic / ArUco / 거리 측정 결과는 참고용으로 보존합니다.

## 새 메인 구조: Eye-in-Hand Gripper Camera

Camera 2를 그리퍼에 장착하고 **그리퍼가 바라보는 방향을 보는 메인 카메라**로 사용합니다.

```text
HOME
 ↓
SEARCH POSE
 ↓
Gripper Camera
 ↓
Object Detection
 ↓
Visual Servo X/Y
 ↓
Descend
 ↓
Visual Servo X/Y
 ↓
Pick
 ↓
Lift
 ↓
HOME
 ↓
GOAL
 ↓
Place
```

영상 중심과 물체 중심의 pixel error를 계산합니다.

```python
error_x = object_x - image_center_x
error_y = object_y - image_center_y
```

그 오차를 이용해 작은 X/Y 이동을 반복하고, 한 번에 Pick 높이까지 내려가지 않고 단계적으로 하강하면서 재정렬하는 Visual Servo 구조로 개발할 예정입니다.

## UI 방향

향후 START는 사용자가 직접 좌표로 선택하는 대신 비전이 찾아낸 물체로 대체할 예정입니다.

```text
START = Gripper Camera가 찾은 물체
GOAL  = 사용자가 지정한 위치
```

기존 HOME 경유 Pick & Place 구조는 유지합니다.

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
- [x] Emergency Stop
- [x] Preview START / GOAL
- [x] 매트 작업 Z = 106 mm 적용
- [x] 위치 기반 Rz 계산 구조
- [x] USB 카메라 2대 입력 확인
- [x] ChArUco intrinsic calibration
- [x] 25 mm gripper ArUco 거리 측정
- [x] 고정 Camera 1 방식의 한계 확인
- [x] Eye-in-Hand Camera 2 구조로 설계 변경

## 다음 진행

1. Camera 2를 그리퍼에 고정 장착하고 시야 방향 확인
2. `gripper_camera_test.py` 작성
3. 영상 중앙 crosshair 표시
4. 물체 중심점 검출 및 `dx / dy` pixel error 표시
5. Camera 화면 방향과 Robot X/Y 이동 방향 매핑 확인
6. 작은 incremental X/Y Visual Servo 구현
7. 단계적 Z 하강 + 재정렬 구현
8. Pick → HOME → GOAL → Place 흐름에 연결
9. 이후 ROS 2 Action 구조로 확장
