from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time

def record_point(mc, name):
	print()
	print(f"Move the gripper to {name}.")
	input("Press Enter when ready...")

	time.sleep(0.2)

	coords = mc.get_coords()

	print(f"{name} : {coords}")

	return coords

def main():
	mc = MyCobot280(PI_PORT, PI_BAUD)
	time.sleep(0.5)

	print("Opening gripper...")
	mc.set_gripper_state(0, 50)
	time.sleep(1)

	print()
	print("Hold the robot arm.")
	input("Press Enter to release the servos...")

	mc.release_all_servos()

	print()
	print("Servos relesaed.")
	print("Record the four corners of the mat.")

	near_left = record_point(
		mc,
		"NEAR_LEFT"
	)

	near_right = record_point(
		mc,
		"NEAR_RIGHT"
	)

	far_left = record_point(
		mc,
		"FAR_LEFT"
	)

	far_right = record_point(
		mc,
		"FAR_LEFT"
	)

	print()
	print("Hold the robot arm.")
	print("Press Enter to enable the servos...")

	mc.focus_all_servos()

	print()
	print("=== MAT CALIBRATION ===")
	print(f"NEAR_LEFT = {near_left}")
	print(f"NEAR_RIGHT = {near_right}")
	print(f"FAR_LEFT = {far_left}")
	print(f"FAR_RIGHT = {far_right}")

	print()
	print("Calibration recording completed.")

if __name__=="__main__":
	main()
