from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time
import math


PICK_A = [ 167.0, -29.2, 110.4, 179.83, -2.63, -52.13 ]

SAFE_HEIGHT = 70.0

PICK_A_ABOVE = PICK_A.copy()
PICK_A_ABOVE[2] += SAFE_HEIGHT

def xyz_distance(a, b):
	return math.sqrt(
		(a[0] - b[0]) ** 2 +
		(a[1] - b[1]) ** 2 +
		(a[2] - b[2]) ** 2
	)

def main():
	mc = MyCobot280(PI_PORT, PI_BAUD)
	time.sleep(0.5)

	current = mc.get_coords()

	if not current:
		print("Failed to read robot coordinates.")
		return

	print(f"Current coords      : {current}")
	print(f"Pick A above coords : {PICK_A_ABOVE}")

	distance = xyz_distance(current, PICK_A_ABOVE)

	print(f"Distance from above : {distance:.1f} mm")

	if distance > 40.0:
		print("Robot is not near Pick A above")
		print("Movement aborted.")
		return

	print()
	print("Step 1 : Move down to Pick A")
	input("Press Enter to continue..")

	mc.sync_send_coords(
		PICK_A,
		10,
		1
	)

	time.sleep(0.5)

	print()
	print("Step 2: Open gripper.")
	input("PressEnter to continue...")

	mc.set_gripper_state(0, 40)
	time.sleep(1.5)

	print()
	print("Step 3 : Move back up.")
	input("Press Enter to continue...")

	mc.sync_send_coords(
		PICK_A_ABOVE,
		10,
		1
	)

	print("Release completed.")

if __name__ == "__main__":
	main()
