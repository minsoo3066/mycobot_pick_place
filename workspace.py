from dataclasses import dataclass


@dataclass
class WorkspaceConfig:
    mat_width_mm: float = 400.0
    mat_depth_mm: float = 400.0

    view_x_min: float = -200.0
    view_x_max: float = 200.0

    view_y_min: float = -200.0
    view_y_max: float = 200.0

    robot_base_width_mm: float = 120.0
    robot_base_depth_mm: float = 150.0

    def is_inside_mat(self, x, y):
        half_depth = self.mat_depth_mm / 2.0
        half_width = self.mat_width_mm / 2.0

        return (
            -half_depth <= x <= half_depth
            and -half_width <= y <= half_width
        )

    def is_inside_view(self, x, y):
        return (
            self.view_x_min <= x <= self.view_x_max
            and self.view_y_min <= y <= self.view_y_max
        )

    def is_inside_no_go(self, x, y):
        half_depth = self.robot_base_depth_mm / 2.0
        half_width = self.robot_base_width_mm / 2.0

        return (
            -half_depth <= x <= half_depth
            and -half_width <= y <= half_width
        )

    def is_valid_position(self, x, y):
        return (
            self.is_inside_mat(x, y)
            and self.is_inside_view(x, y)
            and not self.is_inside_no_go(x, y)
        )