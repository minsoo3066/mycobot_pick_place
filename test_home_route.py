from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time
import math

HOME_ANGLES = [ 0.17, -0.7, -0.96, -91.05, 0.52, -39.02 ]
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

	print(f"Distance            : {distance:.1f} mm")

	if distance > 40.0:
		print("Robot is not near Pick A above")
		print("Movement aborted.")
		return

	print()
	print("Step 1 : Move to HOME")
	input("Press Enter to continue..")

	mc.send_angles(HOME_ANGLES, 15)
	time.sleep(5)

	print("HOME reached.")
	print(f"Current angles : {mc.get_angles()}")
	print(f"Current coords : {mc.get_coords()}")

	print()
	print("Step 2 : Move to Pick A above.")
	input("Press Enter to continue...")

	mc.sync_send_coords(
		PICK_A_ABOVE,
		15,
		0
	)

	print("Pick A above reached.")

	time.sleep(0.5)

	print(f"Current coords : {mc.get_coords()}")

if __name__ == "__main__":
	main()
