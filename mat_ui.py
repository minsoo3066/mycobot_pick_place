import math
import tkinter as tk
from tkinter import messagebox

from workspace import WorkspaceConfig
from coordinate_mapper import CoordinateMapper

from robot_controller import RobotController
from robot_worker import RobotWorker
from pick_and_place import pick_and_place


WINDOW_SIZE = 700

MAT_LEFT = 50
MAT_TOP = 50

MAT_PIXEL_WIDTH = 600
MAT_PIXEL_HEIGHT = 600

GRID_SIZE_MM = 50.0

def home_task(
    robot,
    stop_event
):
    if stop_event.is_set():
        return

    robot.move_home()

class MatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("myCobot Pick and Place")

        self.workspace = WorkspaceConfig()

        self.robot = RobotController()

        self.worker = RobotWorker(
            self.robot
        )

        self.mapper = CoordinateMapper(
            workspace=self.workspace,
            canvas_left=MAT_LEFT,
            canvas_top=MAT_TOP,
            canvas_width=MAT_PIXEL_WIDTH,
            canvas_height=MAT_PIXEL_HEIGHT
        )

        self.start_point = None
        self.goal_point = None

        self.select_mode = "START"

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_SIZE,
            height=WINDOW_SIZE,
            bg="white"
        )

        self.canvas.pack()

        self.canvas.bind(
            "<Button-1>",
            self.on_canvas_click
        )

        self.canvas.bind(
            "<Motion>",
            self.on_mouse_move
        )

        self.draw_workspace()

        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        tk.Button(
            control_frame,
            text="Select START",
            command=self.select_start
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            control_frame,
            text="Select GOAL",
            command=self.select_goal
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            control_frame,
            text="Clear",
            command=self.clear_points
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            control_frame,
            text="Execute",
            command=self.execute_route
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            control_frame,
            text="HOME",
            command=self.go_home
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            control_frame,
            text="EMERGENCY STOP",
            command=self.emergency_stop,
            bg="red",
            fg="white"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        self.mode_label = tk.Label(
            root,
            text="Mode: START"
        )
        self.mode_label.pack()

        self.start_label = tk.Label(
            root,
            text="START: Not selected"
        )
        self.start_label.pack()

        self.goal_label = tk.Label(
            root,
            text="GOAL: Not selected"
        )
        self.goal_label.pack()

        self.status_label = tk.Label(
            root,
            text="Click a position on the workspace."
        )
        self.status_label.pack(pady=5)

        self.cursor_label = tk.Label(
            root,
            text="Cursor: X=--- mm, Y=--- mm"
        )
        self.cursor_label.pack(pady=5)

    def draw_workspace(self):
        self.canvas.create_rectangle(
            MAT_LEFT,
            MAT_TOP,
            MAT_LEFT + MAT_PIXEL_WIDTH,
            MAT_TOP + MAT_PIXEL_HEIGHT,
            fill="#222222",
            outline="black",
            width=2
        )

        self.draw_grid()
        self.draw_no_go_zone()
        self.draw_axes()
        self.draw_robot_origin()
        self.draw_direction_labels()

    def draw_grid(self):
        x_start = (
            math.ceil(
                self.workspace.view_x_min
                / GRID_SIZE_MM
            )
            * GRID_SIZE_MM
        )

        x = x_start

        while x <= self.workspace.view_x_max:
            px1, py = self.mapper.robot_to_pixel(
                x,
                self.workspace.view_y_min
            )

            px2, _ = self.mapper.robot_to_pixel(
                x,
                self.workspace.view_y_max
            )

            self.canvas.create_line(
                px1,
                py,
                px2,
                py,
                fill="#555555"
            )

            x += GRID_SIZE_MM

        y_start = (
            math.ceil(
                self.workspace.view_y_min
                / GRID_SIZE_MM
            )
            * GRID_SIZE_MM
        )

        y = y_start

        while y <= self.workspace.view_y_max:
            px, py1 = self.mapper.robot_to_pixel(
                self.workspace.view_x_min,
                y
            )

            _, py2 = self.mapper.robot_to_pixel(
                self.workspace.view_x_max,
                y
            )

            self.canvas.create_line(
                px,
                py1,
                px,
                py2,
                fill="#555555"
            )

            y += GRID_SIZE_MM

    def draw_no_go_zone(self):

        half_depth = (
            self.workspace.robot_base_depth_mm / 2.0
        )

        half_width = (
            self.workspace.robot_base_width_mm / 2.0
        )

        top_left_x = half_depth
        top_left_y = half_width

        bottom_right_x = -half_depth
        bottom_right_y = -half_width

        px1, py1 = self.mapper.robot_to_pixel(
            top_left_x,
            top_left_y
        )

        px2, py2 = self.mapper.robot_to_pixel(
            bottom_right_x,
            bottom_right_y
        )

        self.canvas.create_rectangle(
            px1,
            py1,
            px2,
            py2,
            fill="#5a2020",
            outline="red",
            width=2
        )

        center_px, center_py = (
            self.mapper.robot_to_pixel(
                0.0,
                0.0
            )
        )

        self.canvas.create_text(
            center_px,
            center_py - 25,
            text="DANGER",
            fill="red"
        )   

    def draw_axes(self):
        if (
            self.workspace.view_x_min
            <= 0.0
            <= self.workspace.view_x_max
        ):
            px1, py = self.mapper.robot_to_pixel(
                0.0,
                self.workspace.view_y_min
            )

            px2, _ = self.mapper.robot_to_pixel(
                0.0,
                self.workspace.view_y_max
            )

            self.canvas.create_line(
                px1,
                py,
                px2,
                py,
                fill="white",
                width=2
            )

        if (
            self.workspace.view_y_min
            <= 0.0
            <= self.workspace.view_y_max
        ):
            px, py1 = self.mapper.robot_to_pixel(
                self.workspace.view_x_min,
                0.0
            )

            _, py2 = self.mapper.robot_to_pixel(
                self.workspace.view_x_max,
                0.0
            )

            self.canvas.create_line(
                px,
                py1,
                px,
                py2,
                fill="white",
                width=2
            )

    def draw_robot_origin(self):
        if not self.workspace.is_inside_view(
            0.0,
            0.0
        ):
            return

        px, py = self.mapper.robot_to_pixel(
            0.0,
            0.0
        )

        radius = 10

        self.canvas.create_oval(
            px - radius,
            py - radius,
            px + radius,
            py + radius,
            fill="white",
            outline="black"
        )

        self.canvas.create_text(
            px,
            py + 25,
            text="ROBOT",
            fill="white"
        )

    def draw_direction_labels(self):
        center_x = (
            MAT_LEFT
            + MAT_PIXEL_WIDTH / 2
        )

        center_y = (
            MAT_TOP
            + MAT_PIXEL_HEIGHT / 2
        )

        self.canvas.create_text(
            center_x,
            20,
            text="FRONT  X+"
        )

        self.canvas.create_text(
            center_x,
            WINDOW_SIZE - 20,
            text="BACK  X-"
        )

        self.canvas.create_text(
            20,
            center_y,
            text="Y+\nLEFT"
        )

        self.canvas.create_text(
            WINDOW_SIZE - 20,
            center_y,
            text="Y-\nRIGHT"
        )

    def on_canvas_click(self, event):
        result = self.mapper.pixel_to_robot(
            event.x,
            event.y
        )

        if result is None:
            self.status_label.config(
                text="Outside workspace."
            )
            return

        robot_x, robot_y = result

        if not self.workspace.is_valid_position(
            robot_x,
            robot_y
        ):
            self.status_label.config(
                text="Invalid position."
            )
            return

        if self.select_mode == "START":
            self.set_start(
                event.x,
                event.y,
                robot_x,
                robot_y
            )

            self.select_goal()

        else:
            self.set_goal(
                event.x,
                event.y,
                robot_x,
                robot_y
            )

    def set_start(
        self,
        px,
        py,
        robot_x,
        robot_y
    ):
        self.start_point = (
            robot_x,
            robot_y
        )

        self.draw_marker(
            px,
            py,
            "START",
            "start_marker",
            "cyan"
        )

        self.start_label.config(
            text=(
                f"START: "
                f"X={robot_x:.1f} mm, "
                f"Y={robot_y:.1f} mm"
            )
        )

        self.status_label.config(
            text="START selected."
        )

        print(
            f"START: "
            f"X={robot_x:.1f}, "
            f"Y={robot_y:.1f}"
        )

    def set_goal(
        self,
        px,
        py,
        robot_x,
        robot_y
    ):
        self.goal_point = (
            robot_x,
            robot_y
        )

        self.draw_marker(
            px,
            py,
            "GOAL",
            "goal_marker",
            "orange"
        )

        self.goal_label.config(
            text=(
                f"GOAL: "
                f"X={robot_x:.1f} mm, "
                f"Y={robot_y:.1f} mm"
            )
        )

        self.status_label.config(
            text="GOAL selected."
        )

        print(
            f"GOAL: "
            f"X={robot_x:.1f}, "
            f"Y={robot_y:.1f}"
        )

    def draw_marker(
        self,
        px,
        py,
        name,
        tag,
        color
    ):
        self.canvas.delete(tag)

        radius = 7

        self.canvas.create_oval(
            px - radius,
            py - radius,
            px + radius,
            py + radius,
            fill=color,
            outline="white",
            tags=tag
        )

        self.canvas.create_text(
            px,
            py - 15,
            text=name,
            fill=color,
            tags=tag
        )

    def select_start(self):
        self.select_mode = "START"

        self.mode_label.config(
            text="Mode: START"
        )

    def select_goal(self):
        self.select_mode = "GOAL"

        self.mode_label.config(
            text="Mode: GOAL"
        )

    def clear_points(self):
        self.start_point = None
        self.goal_point = None

        self.canvas.delete(
            "start_marker"
        )

        self.canvas.delete(
            "goal_marker"
        )

        self.start_label.config(
            text="START: Not selected"
        )

        self.goal_label.config(
            text="GOAL: Not selected"
        )

        self.status_label.config(
            text="Points cleared."
        )

        self.select_start()

    def on_mouse_move(self, event):
        result = self.mapper.pixel_to_robot(
            event.x,
            event.y
        )

        if result is None:
            self.cursor_label.config(
                text="Cursor: Outside workspace"
            )
            return

        robot_x, robot_y = result

        if self.workspace.is_inside_no_go(
            robot_x,
            robot_y
        ):
            position_state = "DANGER"
        else:
            position_state = "VALID"

        self.cursor_label.config(
            text=(
                f"Cursor: "
                f"X={robot_x:.1f} mm, "
                f"Y={robot_y:.1f} mm "
                f"[{position_state}]"
            )
        )

    """
    def execute_route(self):
        if self.start_point is None:
            self.status_label.config(
                text="START is not selected."
            )
            return

        if self.goal_point is None:
            self.status_label.config(
                text="GOAL is not selected."
            )
            return

        start_x, start_y = self.start_point
        goal_x, goal_y = self.goal_point

        print()
        print("=== Pick and Place Route ===")

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
        print("Route:")
        print("1. HOME")
        print("2. START_ABOVE")
        print("3. START")
        print("4. Close gripper")
        print("5. START_ABOVE")
        print("6. HOME")
        print("7. GOAL_ABOVE")
        print("8. GOAL")
        print("9. Open gripper")
        print("10. GOAL_ABOVE")
        print("11. HOME")
        print()

        self.status_label.config(
            text="Route ready. Check terminal output."
        )
    """


    def execute_route(self):
        if self.start_point is None:
            self.status_label.config(
                text="START is not selected."
            )
            return

        if self.goal_point is None:
            self.status_label.config(
                text="GOAL is not selected."
            )
            return

        if self.worker.is_running:
            self.status_label.config(
                text="Robot is already running."
            )
            return

        start_x, start_y = self.start_point
        goal_x, goal_y = self.goal_point

        print()
        print("=== Pick and Place Request ===")

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

        confirm = messagebox.askyesno(
            "Execute Pick and Place",
            (
                f"START\n"
                f"X={start_x:.1f} mm\n"
                f"Y={start_y:.1f} mm\n\n"
                f"GOAL\n"
                f"X={goal_x:.1f} mm\n"
                f"Y={goal_y:.1f} mm\n\n"
                f"Execute?"
            )
        )

        if not confirm:
            self.status_label.config(
                text="Execution cancelled."
            )
            return

        started = self.worker.start_task(
            pick_and_place,
            start_x,
            start_y,
            goal_x,
            goal_y
        )

        if started:
            self.status_label.config(
                text="Pick and Place running..."
            )

    """
    def go_home(self):
        print()
        print("HOME requested.")

        self.status_label.config(
            text="HOME requested."
        )
    """

    def go_home(self):
        if self.worker.is_running:
            self.status_label.config(
                text=(
                    "Robot is running. "
                    "Stop the current task first."
                )
            )
            return

        started = self.worker.start_task(
            home_task
        )

        if started:
            self.status_label.config(
                text="Moving to HOME..."
            )

    """
    def emergency_stop(self):
        print()
        print("EMERGENCY STOP requested.")

        self.status_label.config(
            text="EMERGENCY STOP"
        )
    """
    def emergency_stop(self):
        self.worker.emergency_stop()

        self.status_label.config(
            text="EMERGENCY STOP"
        )

def main():
    root = tk.Tk()

    MatUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()