import array

from panda3d.core import Point3, Point2

from .rounded_box import Sides, RoundedBox


class RoundedCornerBox(RoundedBox):
    """Create a geom node of capsule prism.
        Args:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_z (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box; must be less than corner_radius.
            open_top(bool): used only when thickness is 0; if True, no top side.
            open_bottom(bool): used only when thickness is 0; if True, no bottom side.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
            corner_radius (float): radius of the corner cylinders.
            rounded_f_left(bool): if true, the left corner of the front side is rounded.
            rounded_f_right(bool): if true, the right corner of the front side is rounded.
            rounded_b_left(bool): if true, the left corner of the back side is rounded.
            rounded_b_right(bool): if true, the right corner of the back side is rounded.
    """

    def __init__(self, width=2., depth=2., height=2., segs_w=4, segs_d=4, segs_z=4,
                 thickness=0., open_top=False, open_bottom=False, invert=False, corner_radius=0.5,
                 rounded_f_left=True, rounded_f_right=True, rounded_b_left=True, rounded_b_right=True):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_back=False if corner_radius <= 0 else True,
            open_front=False if corner_radius <= 0 else True,
            open_left=False,
            open_right=False,
            open_top=True if thickness > 0 else open_top,
            open_bottom=True if thickness > 0 else open_bottom
        )

        self.c_radius = corner_radius
        self.rf_left = rounded_f_left
        self.rf_right = rounded_f_right
        self.rb_left = rounded_b_left
        self.rb_right = rounded_b_right

    def create_side_rect(self, vertex_cnt, vdata_values, prim_indices,
                         width, depth, center, open_sides):
        rect = RoundedCornerBox(
            width=width,
            depth=depth,
            height=self.height,
            segs_w=3,
            segs_d=3,
            segs_z=self.segs_z,
            thickness=self.thickness,
            open_top=self.open_top,
            open_bottom=self.open_bottom,
            corner_radius=0,
            rounded_f_left=False,
            rounded_f_right=False,
            rounded_b_left=False,
            rounded_b_right=False,
            invert=self.invert
        )

        for k, v in open_sides.items():
            rect.__dict__[k] = v

        rect.define_variables()
        rect.center = center + self.center
        vertex_cnt = rect.create_sides(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_rounded_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self.height * 0.5)

        match side:
            case Sides.FRONT_LEFT:
                angle = 180
                center.xy = Point2(-self._width, self._depth) * 0.5

            case Sides.BACK_LEFT:
                angle = 270 if not self.invert else 90
                center.xy = Point2(-self._width, -self._depth) * 0.5

            case Sides.BACK_RIGHT:
                angle = 0
                center.xy = Point2(self._width, -self._depth) * 0.5

            case Sides.FRONT_RIGHT:
                angle = 90 if not self.invert else 270
                center.xy = Point2(self._width, self._depth) * 0.5

        vertex_cnt = self.create_vertical_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, self.height, center, angle, 270
        )
        return vertex_cnt

    def create_rect_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3()
        x = (self._width + self.c_radius) * 0.5
        y = (self._depth + self.c_radius) * 0.5

        match side:
            case Sides.FRONT_LEFT:
                center.xy = Point2(-x, y)
                open_sides = dict(open_right=True, open_back=True)

            case Sides.BACK_LEFT:
                center.xy = Point2(-x, -y)
                open_sides = dict(open_right=True, open_front=True)

            case Sides.BACK_RIGHT:
                center.xy = Point2(x, -y)
                open_sides = dict(open_left=True, open_front=True)

            case Sides.FRONT_RIGHT:
                center.xy = Point2(x, y)
                open_sides = dict(open_left=True, open_back=True)

        vertex_cnt = self.create_side_rect(
            vertex_cnt, vdata_values, prim_indices, self.c_radius, self.c_radius, center, open_sides
        )
        return vertex_cnt

    def create_rect_sides(self, vertex_cnt, vdata_values, prim_indices, side):
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

        vertex_cnt = self.create_side_rect(
            vertex_cnt, vdata_values, prim_indices, w, d, center, open_sides
        )
        return vertex_cnt

    def create_corners(self, vertex_cnt, vdata_values, prim_indices):
        li = [
            [Sides.FRONT_LEFT, self.rf_left, Sides.LEFT],
            [Sides.BACK_LEFT, self.rb_left, Sides.BACK],
            [Sides.BACK_RIGHT, self.rb_right, Sides.RIGHT],
            [Sides.FRONT_RIGHT, self.rf_right, Sides.FRONT]
        ]
        # import pdb; pdb.set_trace()
        for corner, is_rounded, side in li:
            # create a rounded or box corner.
            if is_rounded:
                vertex_cnt = self.create_rounded_corners(
                    vertex_cnt, vdata_values, prim_indices, corner)
            else:
                vertex_cnt = self.create_rect_corners(
                    vertex_cnt, vdata_values, prim_indices, corner)

            # create a side box.
            vertex_cnt = self.create_rect_sides(
                vertex_cnt, vdata_values, prim_indices, side)

        return vertex_cnt

    def define_variables(self):
        if self.thickness > 0 and self.c_radius > 0:
            self.thickness = min(self.c_radius, self.thickness)

        # Variables for the box.
        self._depth = self.depth - self.c_radius * 2
        self._width = self.width - self.c_radius * 2
        self.dims = (self.width, self._depth, self.height)

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
                ['z', self.height, self.open_bottom, self.open_top]
            ]
            self.define_inner_details(outer_box_details)

        # Variables for the corner cylinders.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d

    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        # center box
        vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)

        if self.c_radius > 0:
            vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        if self.thickness > 0:
            maker = RoundedCornerBox(
                width=self._width + self.c_inner_radius * 2,
                depth=self._depth + self.c_inner_radius * 2,
                height=self.height,
                segs_w=self.segs_w,
                segs_d=self.segs_d,
                segs_z=self.segs_z,
                thickness=0,
                open_top=True,
                open_bottom=True,
                invert=not self.invert,
                corner_radius=self.c_inner_radius,
                rounded_f_left=self.rf_left,
                rounded_f_right=self.rf_right,
                rounded_b_left=self.rb_left,
                rounded_b_right=self.rb_right
            )

            # Define the inner box center.
            maker.center = self.calc_inner_box_center()

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'box')

        return geom_node