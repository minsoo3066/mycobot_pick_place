from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time

def main():
	mc = MyCobot280(PI_PORT, PI_BAUD)
	time.sleep(0.5)

	# Gripper Open
	print("Opening Gripper...")
	mc.set_gripper_state(0, 50)
	time.sleep(1)

	print("Hold the robot arm and press Enter")
	input()

	# Release all servos
	mc.release_all_servos()

	print("Servos released.")
	print("Move the gripper to the desired point.")
	print("Press Enter when ready")
	input()

	coords = mc.get_coords()
	angles = mc.get_angles()

	print()
	print("== RECORDED POINT ==")
	print(f"Coords : {coords}")
	print(f"Angles : {angles}")

	# Enable all servos again
	mc.focus_all_servos()

	print("Servos enabled.")

if __name__ == "__main__":
	main()
