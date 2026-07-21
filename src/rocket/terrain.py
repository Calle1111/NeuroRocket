class Terrain:
    """
    Stores the terrain geometry and landing pad data.

    The terrain is represented as connected points in world coordinates.
    Each pair of neighboring points forms one terrain segment.

    By project design, each segment is either horizontal, vertical,
    or 45 degrees sloped.   
    """

    def __init__ (self):
        """
        Create the first terrain template.
        """
        self.terrain_points = [
            (0.0, 78.0),
            (4.0, 78.0),
            (8.0, 74.0),
            (12.0, 74.0),
            (16.0, 70.0),
            (20.0, 70.0),
            (24.0, 66.0),
            (28.0, 62.0),
            (32.0, 62.0),
            (36.0, 58.0),
            (40.0, 54.0),
            (44.0, 54.0),
            (48.0, 58.0),
            (52.0, 62.0),
            (56.0, 58.0),
            (60.0, 54.0),
            (64.0, 50.0),
            (68.0, 54.0),
            (72.0, 58.0),
            (76.0, 58.0),
            (80.0, 58.0),
            (84.0, 54.0),
            (88.0, 50.0),
            (92.0, 46.0),
            (96.0, 46.0),
            (100.0, 50.0),
            (104.0, 54.0),
            (108.0, 50.0),
            (112.0, 46.0),
            (116.0, 42.0),
            (120.0, 46.0),
            (124.0, 50.0),
            (128.0, 54.0),
            (132.0, 54.0),
            (136.0, 58.0),
            (140.0, 58.0),
        ]

        self.landing_pad_x_min = 72.0
        self.landing_pad_x_max = 80.0
        self.landing_pad_y = 58.0

    def get_segments(self):
        """
        Return the terrain as line segments where each segment is 
        represented as start_point and end_point: ((x1, y1), (x2, y2))
        """
        segments = []

        for index in range(len(self.terrain_points) - 1):
            start_point = self.terrain_points[index]
            end_point = self.terrain_points[index + 1]
            segments.append((start_point, end_point))

        return segments