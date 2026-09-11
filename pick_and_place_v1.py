from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time

HOME_ANGLES = [ 0.17, -0.7, -0.96, -91.05, 0.52, -39.02 ]

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

PICK_A = [ 167.0, -29.2, 110.4, 179.83, -2.63, -52.13 ]

PLACE_B = [ -102.9, -138.5, 121.7, -176.63, -4.62, -142.87 ]

SAFE_HEIGHT = 70.0

PICK_A_ABOVE = PICK_A.copy()
PICK_A_ABOVE[2] += SAFE_HEIGHT

PLACE_B_ABOVE = PLACE_B.copy()
PLACE_B_ABOVE[2] += SAFE_HEIGHT

HOME_SPEED = 15
MOVE_SPEED = 15
VERTICAL_SPEED = 10
GRIPPER_SPEED = 40

def move_home(mc):
	print("Moving to HOME...")

	mc.send_angles(
		HOME_ANGLES,
		HOME_SPEED
	)

	time.sleep(5)

	print("HOME reached.")

def move_to(mc, coords, speed, mode, name):
	print(f"Moving to {name}...")
	print(f"Target : {coords}")

	mc.sync_send_coords(
		coords,
		speed,
		mode
	)

	time.sleep(0.5)

	print(f"{name} reached.")

def open_gripper(mc):
	print("Opening gripper...")

	mc.set_gripper_state(
		0,
		GRIPPER_SPEED
	)

	time.sleep(1.5)

def close_gripper(mc):
	print("Closing gripper...")

	mc.set_gripper_state(
		1,
		GRIPPER_SPEED
	)

	time.sleep(2)

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

"""
def pick_and_place(mc):

	# 1. Start from HOME
	move_home(mc)

	# 2. Open gripper
	open_gripper(mc)

	# 3. Move above Pick A
	move_to(
		mc,
		PICK_A_ABOVE,
		MOVE_SPEED,
		0,
		"Pick A above"
	)

	# 4. Move straight down
	move_to(
		mc,
		PICK_A,
		VERTICAL_SPEED,
		1,
		"Pick A"
	)

	# 5. Grab object
	close_gripper(mc)

	# 6. Lift object
	move_to(
		mc,
		PICK_A_ABOVE,
		VERTICAL_SPEED,
		1,
		"Pick A Above"
	)

	# 7. Move to HOME while holding the object
	move_home(mc)


	# 8. Move above Place B
	move_to(
		mc,
		PLACE_B_ABOVE,
		MOVE_SPEED,
		0,
		"Place B above"
	)

	# 9. Move straight down
	move_to(
		mc,
		PLACE_B,
		VERTICAL_SPEED,
		1,
		"Place B"
	)

	# 10. Release object
	open_gripper(mc)

	# 11. Move straight up
	move_to(
		mc,
		PLACE_B_ABOVE,
		VERTICAL_SPEED,
		1,
		"Place B above"
	)

	# 12. Return HOME
	move_home(mc)

	print()
	print("Pick and place completed.")
"""
def pick_and_place(
    mc,
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

    move_home(mc)
    open_gripper(mc)

    move_to(
        mc,
        pick_above,
        MOVE_SPEED,
        0,
        "Pick above"
    )

    move_to(
        mc,
        pick_pose,
        VERTICAL_SPEED,
        1,
        "Pick"
    )

    close_gripper(mc)

    move_to(
        mc,
        pick_above,
        VERTICAL_SPEED,
        1,
        "Pick above"
    )

    move_home(mc)

    move_to(
        mc,
        place_above,
        MOVE_SPEED,
        0,
        "Place above"
    )

    move_to(
        mc,
        place_pose,
        VERTICAL_SPEED,
        1,
        "Place"
    )

    open_gripper(mc)

    move_to(
        mc,
        place_above,
        VERTICAL_SPEED,
        1,
        "Place above"
    )

    move_home(mc)

    print()
    print("Pick and place completed.")


def main():
	mc = MyCobot280(
		PI_PORT,
		PI_BAUD
	)

	time.sleep(0.5)

	print("=== Pick and Place ===")
	print(f"Pick  : {PICK_A}")
	print(f"Place : {PLACE_B}")
	print()

	input("Press Enter ro start...")

	pick_and_place(mc)

if __name__ == "__main__":
	main()
