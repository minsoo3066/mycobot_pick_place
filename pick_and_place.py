import threading

from robot_controller import (
    RobotController,
    MOVE_SPEED,
    VERTICAL_SPEED
)


PICK_Z = 110.4
PLACE_Z = 121.7

SAFE_HEIGHT = 70.0


PICK_ORIENTATION = [
    179.83,
    -2.63,
    -52.13
]

PLACE_ORIENTATION = [
    -176.63,
    -4.62,
    -142.87
]


def make_pick_pose(x, y):
    rx, ry, rz = PICK_ORIENTATION

    return [
        x,
        y,
        PICK_Z,
        rx,
        ry,
        rz
    ]


def make_place_pose(x, y):
    rx, ry, rz = PLACE_ORIENTATION

    return [
        x,
        y,
        PLACE_Z,
        rx,
        ry,
        rz
    ]


def should_stop(stop_event):
    if stop_event.is_set():
        print("Task stopped.")
        return True

    return False


def pick_and_place(
    robot,
    stop_event,
    start_x,
    start_y,
    goal_x,
    goal_y
):
    pick_pose = make_pick_pose(
        start_x,
        start_y
    )

    place_pose = make_place_pose(
        goal_x,
        goal_y
    )

    pick_above = pick_pose.copy()
    pick_above[2] += SAFE_HEIGHT

    place_above = place_pose.copy()
    place_above[2] += SAFE_HEIGHT

    print()
    print("=== Pick and Place ===")

    print(
        f"START: "
        f"X={start_x:.1f}, "
        f"Y={start_y:.1f}"
    )

    print(
        f"GOAL : "
        f"X={goal_x:.1f}, "
        f"Y={goal_y:.1f}"
    )

    print()

    # 1. HOME
    robot.move_home()

    if should_stop(stop_event):
        return

    # 2. Open gripper
    robot.open_gripper()

    if should_stop(stop_event):
        return

    # 3. Move to START above
    robot.move_to(
        pick_above,
        MOVE_SPEED,
        0,
        "Pick above"
    )

    if should_stop(stop_event):
        return

    # 4. Move vertically down to START
    robot.move_to(
        pick_pose,
        VERTICAL_SPEED,
        1,
        "Pick"
    )

    if should_stop(stop_event):
        return

    # 5. Pick object
    robot.close_gripper()

    if should_stop(stop_event):
        return

    # 6. Lift vertically
    robot.move_to(
        pick_above,
        VERTICAL_SPEED,
        1,
        "Pick above"
    )

    if should_stop(stop_event):
        return

    # 7. Return HOME while holding object
    robot.move_home()

    if should_stop(stop_event):
        return

    # 8. Move to GOAL above
    robot.move_to(
        place_above,
        MOVE_SPEED,
        0,
        "Place above"
    )

    if should_stop(stop_event):
        return

    # 9. Move vertically down to GOAL
    robot.move_to(
        place_pose,
        VERTICAL_SPEED,
        1,
        "Place"
    )

    if should_stop(stop_event):
        return

    # 10. Release object
    robot.open_gripper()

    if should_stop(stop_event):
        return

    # 11. Lift vertically
    robot.move_to(
        place_above,
        VERTICAL_SPEED,
        1,
        "Place above"
    )

    if should_stop(stop_event):
        return

    # 12. Final HOME
    robot.move_home()

    if should_stop(stop_event):
        return

    print()
    print("Pick and place completed.")


def main():
    robot = RobotController()

    stop_event = threading.Event()

    # Known test positions
    start_x = 167.0
    start_y = -29.2

    goal_x = -102.9
    goal_y = -138.5

    print("=== Pick and Place Test ===")

    print(
        f"START: "
        f"X={start_x}, "
        f"Y={start_y}"
    )

    print(
        f"GOAL : "
        f"X={goal_x}, "
        f"Y={goal_y}"
    )

    print()

    input("Press Enter to start...")

    try:
        pick_and_place(
            robot,
            stop_event,
            start_x,
            start_y,
            goal_x,
            goal_y
        )

    except KeyboardInterrupt:
        print()
        print("Emergency stop requested.")

        stop_event.set()
        robot.emergency_stop()

        print("Robot stopped.")


if __name__ == "__main__":
    main()