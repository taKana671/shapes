import array

from panda3d.core import Point3, Point2

from .rounded_box import Sides, RoundedBox


class MatchSide:

    def __init__(self, side):
        self.side = side

    def __eq__(self, side):
        return side in self.side


class RoundedEdgeBox(RoundedBox):
    """Create a geom node of rounded edge box.
        Args:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_z (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box; must be less than corner_radius.
            corner_radius (float): radius of the corner cylinders.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, width=4., depth=4., height=4., segs_w=4, segs_d=1, segs_z=2,
                 thickness=0.5, corner_radius=1, invert=False):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_top=True if thickness > 0 else False,
            open_bottom=True if thickness > 0 else False
        )
        self.c_radius = corner_radius

    def create_rect(self, vertex_cnt, vdata_values, prim_indices,
                    width, depth, height, center, open_sides):
        rect = RoundedEdgeBox(
            width=width,
            depth=depth,
            height=height,
            segs_w=3,
            segs_d=3,
            segs_z=self.segs_z,
            thickness=0,
            corner_radius=0,
            invert=self.invert
        )

        for k, v in open_sides.items():
            rect.__dict__[k] = v

        rect.define_variables()
        rect.center = center + self.center
        vertex_cnt = rect.create_sides(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_rounded_corner(self, vertex_cnt, vdata_values, prim_indices, side):
        x, y = self._width * 0.5, self._depth * 0.5
        z = self._height * 0.5 * (-1 if Sides.BOTTOM in side else 1)
        center = Point3(0, 0, z)

        match MatchSide(side):

            case Sides.BACK_RIGHT:
                start_angle = 0
                center.xy = Point2(x, -y)

            case Sides.FRONT_RIGHT:
                start_angle = 90 if not self.invert else 270
                center.xy = Point2(x, y)

            case Sides.FRONT_LEFT:
                start_angle = 180
                center.xy = Point2(-x, y)

            case Sides.BACK_LEFT:
                start_angle = 270 if not self.invert else 90
                center.xy = Point2(-x, -y)

        bottom_clip = -1 if Sides.BOTTOM in side else 0
        top_clip = 0 if Sides.BOTTOM in side else 1

        vertex_cnt = self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, 270,
            bottom_clip=bottom_clip, top_clip=top_clip
        )

        return vertex_cnt

    def create_horizontal_rounded_edge(self, vertex_cnt, vdata_values, prim_indices, side):
        z = self._height * 0.5 * (-1 if Sides.BOTTOM in side else 1)
        center = Point3(0, 0, z)
        x, y = self._width * 0.5, self._depth * 0.5
        start_slice_cap = end_slice_cap = False

        match MatchSide(side):

            case Sides.LEFT:
                x_axis = False
                height = self._depth
                center.xy = Point2(-x, -y)

                if Sides.TOP in side:
                    start_angle = 0
                    start_slice_cap = True
                else:
                    start_angle = 270 if not self.invert else 90
                    end_slice_cap = True

            case Sides.BACK:
                x_axis = True
                height = self._width
                center.xy = Point2(-x, -y)

                if Sides.TOP in side:
                    start_angle = 180
                    end_slice_cap = True
                else:
                    start_angle = 270 if not self.invert else 90
                    start_slice_cap = True

            case Sides.RIGHT:
                x_axis = False
                height = self._depth
                center.xy = Point2(x, -y)

                if Sides.TOP in side:
                    start_angle = 90 if not self.invert else 270
                    end_slice_cap = True
                else:
                    start_angle = 180
                    start_slice_cap = True

            case Sides.FRONT:
                x_axis = True
                height = self._width
                center.xy = Point2(-x, y)

                if Sides.TOP in side:
                    start_angle = 90 if not self.invert else 270
                    start_slice_cap = True
                else:
                    start_angle = 0
                    end_slice_cap = True

        vertex_cnt = self.create_horizontal_edge_cylinder(
            vertex_cnt, vdata_values, prim_indices, height, center,
            start_angle, 270, x_axis, start_slice_cap, end_slice_cap
        )

        return vertex_cnt

    def create_vertical_rounded_edge(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self._height * 0.5)
        x, y = self._width * 0.5, self._depth * 0.5

        match side:
            case Sides.FRONT_LEFT:
                start_angle = 180
                center.xy = Point2(-x, y)

            case Sides.BACK_LEFT:
                start_angle = 270 if not self.invert else 90
                center.xy = Point2(-x, -y)

            case Sides.BACK_RIGHT:
                start_angle = 0
                center.xy = Point2(x, -y)

            case Sides.FRONT_RIGHT:
                start_angle = 90 if not self.invert else 270
                center.xy = Point2(x, y)

        vertex_cnt = self.create_vertical_edge_cylinder(
            vertex_cnt, vdata_values, prim_indices,
            self._height, center, start_angle, 270
        )

        return vertex_cnt

    def create_rect_side(self, vertex_cnt, vdata_values, prim_indices, side):
        common_open_sides = dict(open_top=True, open_bottom=True)
        center = Point3()
        x = (self._width + self.c_radius) * 0.5
        y = (self._depth + self.c_radius) * 0.5

        match side:
            case Sides.LEFT:
                center.xy = Point2(-x, 0)
                w, d = self.c_radius, self._depth
                open_sides = dict(open_right=True, open_front=True, open_back=True)

            case Sides.BACK:
                center.xy = Point2(0, -y)
                w, d = self._width, self.c_radius
                open_sides = dict(open_left=True, open_right=True, open_front=True)

            case Sides.RIGHT:
                center.xy = Point2(x, 0)
                w, d = self.c_radius, self._depth
                open_sides = dict(open_left=True, open_front=True, open_back=True)

            case Sides.FRONT:
                center.xy = Point2(0, y)
                w, d = self._width, self.c_radius
                open_sides = dict(open_left=True, open_right=True, open_back=True)

        open_sides = {**open_sides, **common_open_sides}
        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, w, d, self._height, center, open_sides
        )
        return vertex_cnt

    def create_rect_edges(self, vertex_cnt, vdata_values, prim_indices, t_or_b):
        """Args:
                t_or_b (Sides): Sides.TOP or Sides.BOTTOM
        """
        # Create corner spheres.
        if self.c_radius > 0:
            for side in [Sides.BACK_RIGHT, Sides.FRONT_RIGHT, Sides.FRONT_LEFT, Sides.BACK_LEFT]:
                vertex_cnt += self.create_rounded_corner(
                    vertex_cnt, vdata_values, prim_indices, t_or_b | side
                )

        # Create horizontal cylinders.
        for side in [Sides.RIGHT, Sides.FRONT, Sides.LEFT, Sides.BACK]:
            vertex_cnt = self.create_horizontal_rounded_edge(
                vertex_cnt, vdata_values, prim_indices, t_or_b | side
            )

        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):
        vertex_cnt = self.create_rect_edges(vertex_cnt, vdata_values, prim_indices, Sides.BOTTOM)

        if not self.open_bottom:
            center = Point3(0, 0, -(self._height + self.c_radius) / 2)
            open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
            vertex_cnt = self.create_rect(
                vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        return vertex_cnt

    def create_middle(self, vertex_cnt, vdata_values, prim_indices):
        li = [
            [Sides.BACK_RIGHT, Sides.RIGHT],
            [Sides.FRONT_LEFT, Sides.LEFT],
            [Sides.BACK_LEFT, Sides.BACK],
            [Sides.FRONT_RIGHT, Sides.FRONT]
        ]

        for corner, side in li:
            if self.c_radius:
                # create vertical cylinders.
                vertex_cnt = self.create_vertical_rounded_edge(
                    vertex_cnt, vdata_values, prim_indices, corner)

            # create a side boxes.
            vertex_cnt = self.create_rect_side(
                vertex_cnt, vdata_values, prim_indices, side)

        return vertex_cnt

    def create_top(self, vertex_cnt, vdata_values, prim_indices):
        if not self.open_top:
            center = Point3(0, 0, (self._height + self.c_radius) / 2)
            open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_bottom=True)
            vertex_cnt = self.create_rect(
                vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        vertex_cnt = self.create_rect_edges(vertex_cnt, vdata_values, prim_indices, Sides.TOP)
        return vertex_cnt

    def define_variables(self):
        if self.thickness > 0 and self.c_radius > 0:
            self.thickness = min(self.c_radius, self.thickness)

        # Variables for the box.
        self._depth = self.depth - self.c_radius * 2
        self._width = self.width - self.c_radius * 2
        self._height = self.height - self.c_radius * 2

        self.dims = (self._width, self._depth, self._height)
        self.segs = {'x': self.segs_w, 'y': self.segs_d, 'z': self.segs_z}

        self.open_sides = {
            '-yz': self.open_left,
            'yz': self.open_right,
            '-zx': self.open_back,
            'zx': self.open_front,
            '-xy': self.open_bottom,
            'xy': self.open_top
        }

        if self.thickness > 0:
            outer_box_details = [
                ['x', self._width, self.open_left, self.open_right],
                ['y', self._depth, self.open_back, self.open_front],
                ['z', self._height, self.open_bottom, self.open_top]
            ]
            self.define_inner_details(outer_box_details)

        # Variables for the corner cylinders.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        self.c_segs_tc = 0
        self.c_segs_bc = 0

    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt = self.create_top(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_middle(vertex_cnt, vdata_values, prim_indices)

        if self.thickness > 0:
            maker = RoundedEdgeBox(
                width=self._width + self.c_inner_radius * 2,
                depth=self._depth + self.c_inner_radius * 2,
                height=self._height + self.c_inner_radius * 2,
                segs_w=self.segs_w,
                segs_d=self.segs_d,
                segs_z=self.segs_z,
                thickness=0,
                invert=not self.invert,
                corner_radius=self.c_inner_radius,
            )

            maker.open_top = True
            maker.open_bottom = True

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'rounded_edge_box')

        return geom_node