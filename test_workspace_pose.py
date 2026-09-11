from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time


HOME_ANGLES = [
    0.17,
    -0.7,
    -0.96,
    -91.05,
    0.52,
    -39.02
]

TOOL_ORIENTATION = [
    179.83,
    -2.63,
    -52.13
]

HOME_SPEED = 15
MOVE_SPEED = 10
GRIPPER_SPEED = 40

TEST_POINTS = [
    [167.0, -29.2, 180.4],
    [167.0, 20.8, 180.4],
    [167.0, -79.2, 180.4],
    [187.0, -29.2, 180.4],
    [117.0, -29.2, 180.4],
]


def move_home(mc):
    print("Moving to HOME...")
    mc.send_angles(
        HOME_ANGLES,
        HOME_SPEED
    )
    time.sleep(5)


def open_gripper(mc):
    mc.set_gripper_state(
        0,
        GRIPPER_SPEED
    )
    time.sleep(1.5)


def make_pose(point):
    x, y, z = point
    rx, ry, rz = TOOL_ORIENTATION

    return [
        x,
        y,
        z,
        rx,
        ry,
        rz
    ]


def main():
    mc = MyCobot280(
        PI_PORT,
        PI_BAUD
    )

    time.sleep(0.5)

    move_home(mc)
    open_gripper(mc)

    print()
    print("Workspace pose test")
    print("The robot will move only at safe height.")
    print()

    for index, point in enumerate(
        TEST_POINTS,
        start=1
    ):
        pose = make_pose(point)

        print(
            f"Point {index}: "
            f"X={point[0]}, "
            f"Y={point[1]}, "
            f"Z={point[2]}"
        )

        input(
            "Press Enter to move, "
            "or Ctrl+C to stop..."
        )

        mc.sync_send_coords(
            pose,
            MOVE_SPEED,
            0
        )

        time.sleep(1)

    input(
        "Press Enter to return HOME..."
    )

    move_home(mc)

    print("Test completed.")


if __name__ == "__main__":
    main()