from pymycobot import MyCobot280, PI_PORT, PI_BAUD
import time

def main():
	print("=== myCobot 280-PI connection test===")
	print(f"port : {PI_PORT}")
	print(f"baud : {PI_BAUD}")

	mc = MyCobot280(PI_PORT, PI_BAUD)

	time.sleep(0.5)

	angles = mc.get_angles()
	coords = mc.get_coords()

	print(f"joint angles : {angles}")
	print(f"joint coords : {coords}")

if __name__=="__main__":
	main()
