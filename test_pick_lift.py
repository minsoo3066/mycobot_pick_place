from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time
import math

PICK_A = [ 167.0, -29.2, 110.4, 179.83, -2.83, -52.13 ]

SAFE_HEIGHT = 70.0

def main():
	mc = MyCobot280(PI_PORT, PI_BAUD)
	time.sleep(0.5)

	current = mc.get_coords()

	print(f"Current coords : {current}")
	print(f"Pick A         : {PICK_A}")

	if not current:
		print("Failed to read robot coordinates")
		return

	# check only XYZ position
	distance = math.sqrt(
		(current[0] - PICK_A[0]) ** 2 +
		(current[1] - PICK_A[1]) ** 2 +
		(current[2] - PICK_A[2]) ** 2 
	)

	print(f"Distance from Pick A : {distance:.1f} mm")

	# Do not move if the robot is far from the recorded point

	if distance > 30.0:
		print("Robot is too far from Pick A.")
		print("Movement aborted.")
		return

	pick_above = PICK_A.copy()
	pick_above[2] += SAFE_HEIGHT

	print(f"Target coords : {pick_above}")
	print()
	print("The robot will move straight upward by 70 mm.")
	input("Press Enter to continue...")

	mc.sync_send_coords(
		pick_above,
		15,
		1
	)

	print("Lift completed.")

	time.sleep(0.5)

	current = mc.get_coords()
	print(f"Current coords : {current}")

if __name__ == "__main__":
	main()
