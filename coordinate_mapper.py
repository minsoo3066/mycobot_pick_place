class CoordinateMapper:
    def __init__(
        self,
        workspace,
        canvas_left,
        canvas_top,
        canvas_width,
        canvas_height
    ):
        self.workspace = workspace

        self.canvas_left = canvas_left
        self.canvas_top = canvas_top
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def is_inside_canvas(self, px, py):
        return (
            self.canvas_left <= px <= self.canvas_left + self.canvas_width
            and self.canvas_top <= py <= self.canvas_top + self.canvas_height
        )

    def pixel_to_robot(self, px, py):
        if not self.is_inside_canvas(px, py):
            return None

        x_ratio = (
            (py - self.canvas_top)
            / self.canvas_height
        )

        y_ratio = (
            (px - self.canvas_left)
            / self.canvas_width
        )

        x_range = (
            self.workspace.view_x_max
            - self.workspace.view_x_min
        )

        y_range = (
            self.workspace.view_y_max
            - self.workspace.view_y_min
        )

        robot_x = (
            self.workspace.view_x_max
            - x_ratio * x_range
        )

        robot_y = (
            self.workspace.view_y_max
            - y_ratio * y_range
        )

        return robot_x, robot_y

    def robot_to_pixel(self, x, y):
        x_range = (
            self.workspace.view_x_max
            - self.workspace.view_x_min
        )

        y_range = (
            self.workspace.view_y_max
            - self.workspace.view_y_min
        )

        px = (
            self.canvas_left
            + (
                self.workspace.view_y_max - y
            ) / y_range
            * self.canvas_width
        )

        py = (
            self.canvas_top
            + (
                self.workspace.view_x_max - x
            ) / x_range
            * self.canvas_height
        )

        return px, py