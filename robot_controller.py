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

HOME_SPEED = 15
MOVE_SPEED = 15
VERTICAL_SPEED = 10
GRIPPER_SPEED = 40


class RobotController:
    def __init__(self):
        self.mc = MyCobot280(
            PI_PORT,
            PI_BAUD
        )

        time.sleep(0.5)

    def move_home(self):
        print("Moving to HOME...")

        self.mc.send_angles(
            HOME_ANGLES,
            HOME_SPEED
        )

        time.sleep(5)

        print("HOME reached.")

    def move_to(
        self,
        coords,
        speed,
        mode,
        name
    ):
        print(f"Moving to {name}...")
        print(f"Target: {coords}")

        self.mc.sync_send_coords(
            coords,
            speed,
            mode
        )

        time.sleep(0.5)

        print(f"{name} reached.")

    def open_gripper(self):
        print("Opening gripper...")

        self.mc.set_gripper_state(
            0,
            GRIPPER_SPEED
        )

        time.sleep(1.5)

    def close_gripper(self):
        print("Closing gripper...")

        self.mc.set_gripper_state(
            1,
            GRIPPER_SPEED
        )

        time.sleep(2)

    def emergency_stop(self):
        print("EMERGENCY STOP")

        self.mc.stop()


def main():
    robot = RobotController()

    print("RobotController test")
    print("1. Move HOME")
    print("2. Emergency Stop")

    command = input("Select command: ")

    if command == "1":
        robot.move_home()

    elif command == "2":
        robot.emergency_stop()

    else:
        print("Invalid command.")


if __name__ == "__main__":
    main()