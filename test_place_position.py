from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time
import math


PLACE_B = [ -102.9, -138.5, 121.7, -176.63, -4.62, -142.87 ]

SAFE_HEIGHT = 70.0

PLACE_B_ABOVE = PLACE_B.copy()
PLACE_B_ABOVE[2] += SAFE_HEIGHT

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
	print(f"Place B             : {PLACE_B}")
	print(f"Place B above coords : {PLACE_B_ABOVE}")

	distance = xyz_distance(current, PLACE_B)

	print(f"Distance from Place B : {distance:.1f} mm")

	if distance > 40.0:
		print("Robot is not near from Place B")
		print("Movement aborted.")
		return

	print()
	print("Step 1 : Move straight up")
	input("Press Enter to continue..")

	mc.sync_send_coords(
		PLACE_B_ABOVE,
		10,
		1
	)

	time.sleep(0.5)

	print(f"Current coords : {mc.get_coords()}")

	print()
	print("Step 2: Move straight down to Place B.")
	input("PressEnter to continue...")

	mc.sync_send_coords(
		PLACE_B,
		10,
		1
	)

	time.sleep(0.5)

	print(f"Current coords : {mc.get_coords()}")


	print()
	print("Step 3 : Move back up.")
	input("Press Enter to continue...")

	mc.sync_send_coords(
		PLACE_B_ABOVE,
		10,
		1
	)

	print("Place position test completed.")
	print(f"Current coords : {mc.get_coords()}")



if __name__ == "__main__":
	main()
