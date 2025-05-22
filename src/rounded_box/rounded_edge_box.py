import array

from panda3d.core import Vec3, Point3, Vec2, Point2

from .rounded_box import Sides, RoundedBox
# from .rounded_box import BoxEdgeCylinder


class MatchSide:

    def __init__(self, side):
        self.side = side

    def __eq__(self, side):
        return side in self.side


class RoundedEdgeBox(RoundedBox):

    def __init__(self, width=4., depth=4., height=4., segs_w=1, segs_d=1, segs_z=1,
                 thickness=0.2, open_top=True, open_bottom=False, invert=False, corner_radius=1):

        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_top=True if thickness > 0 else open_top,
            open_bottom=True if thickness > 0 else open_bottom
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
            # thickness=self.thickness,
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
        z = self._height * 0.5 * (-1 if Sides.BOTTOM in side else 1)
        center = Point3(0, 0, z)
        x, y = self._width * 0.5, self._depth * 0.5

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
                # start_angle = 270
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

        match MatchSide(side):

            case Sides.LEFT:
                x_axis = False
                height = self._depth
                # start_angle = 0 if Sides.TOP in side else 270
                if Sides.TOP in side:
                    start_angle = 0
                else:
                    start_angle = 270 if not self.invert else 90
                #  270


                center.xy = Point2(-x, -y)

            case Sides.BACK:
                x_axis = True
                height = self._width
                # start_angle = 180 if Sides.TOP in side else 270

                if Sides.TOP in side:
                    start_angle = 180
                else:
                    start_angle = 270 if not self.invert else 90


                center.xy = Point2(-x, -y)

            case Sides.RIGHT:
                x_axis = False
                height = self._depth
                # start_angle = 90 if Sides.TOP in side else 180
                if Sides.TOP in side:
                    start_angle = 90 if not self.invert else 270
                else:
                    start_angle = 180


                center.xy = Point2(x, -y)

            case Sides.FRONT:
                x_axis = True
                height = self._width
                # start_angle = 90 if Sides.TOP in side else 0

                if Sides.TOP in side:
                    start_angle = 90 if not self.invert else 270
                else:
                    start_angle = 0



                center.xy = Point2(-x, y)

        vertex_cnt = self.create_horizontal_edge_cylinder(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, 270, x_axis
        )
        return vertex_cnt

    def create_vertical_rounded_edge(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self._height * 0.5)

        match side:
            case Sides.FRONT_LEFT:
                start_angle = 180
                center.xy = Point2(-self._width, self._depth) * 0.5

            case Sides.BACK_LEFT:
                start_angle = 270 if not self.invert else 90
                center.xy = Point2(-self._width, -self._depth) * 0.5

            case Sides.BACK_RIGHT:
                start_angle = 0
                center.xy = Point2(self._width, -self._depth) * 0.5

            case Sides.FRONT_RIGHT:
                start_angle = 90 if not self.invert else 270
                center.xy = Point2(self._width, self._depth) * 0.5

        vertex_cnt = self.create_vertical_edge_cylinder(
            vertex_cnt, vdata_values, prim_indices, self._height, center, start_angle, 270
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
        for side in [Sides.BACK_RIGHT, Sides.FRONT_RIGHT, Sides.FRONT_LEFT, Sides.BACK_LEFT]:
            vertex_cnt += self.create_rounded_corner(
                vertex_cnt, vdata_values, prim_indices, t_or_b | side
            )

        for side in [Sides.LEFT, Sides.BACK, Sides.RIGHT, Sides.FRONT]:
            vertex_cnt = self.create_horizontal_rounded_edge(
                vertex_cnt, vdata_values, prim_indices, t_or_b | side
            )

        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):
        # if self.open_bottom:
        #     open_sides = dict(open_bottom=True, open_top=True)
        # else:
        #     open_sides.update(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)

        # z = -(self._height + self.c_radius) * 0.5
        # center = Point3(0, 0, z)
        # vertex_cnt = self.create_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        # vertex_cnt = self.create_rect_edges(vertex_cnt, vdata_values, prim_indices, Sides.BOTTOM)

        # return vertex_cnt

       
        # center = Point3(0, 0, -(self.height - self.thickness) * 0.5)
        # open_sides = dict(open_bottom=True, open_top=True)
        # vertex_cnt = self.create_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.thickness, center, open_sides)


        vertex_cnt = self.create_rect_edges(vertex_cnt, vdata_values, prim_indices, Sides.BOTTOM)

        if not self.open_top:
            center = Point3(0, 0, -(self._height + self.c_radius) / 2)
            open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
            vertex_cnt = self.create_rect(
                vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        return vertex_cnt

    def create_middle(self, vertex_cnt, vdata_values, prim_indices):
        # if self.c_radius > 0:
        li = [
            [Sides.FRONT_LEFT, Sides.LEFT],
            [Sides.BACK_LEFT, Sides.BACK],
            [Sides.BACK_RIGHT, Sides.RIGHT],
            [Sides.FRONT_RIGHT, Sides.FRONT]
        ]

        for corner, side in li:
            # create a rounded or box corner.
            vertex_cnt = self.create_vertical_rounded_edge(
                vertex_cnt, vdata_values, prim_indices, corner)

            # create a side box.
            vertex_cnt = self.create_rect_side(
                vertex_cnt, vdata_values, prim_indices, side)

        return vertex_cnt

        open_sides = dict(open_top=True, open_bottom=True)
        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self._height,
            self.center, open_sides
        )
        return vertex_cnt

    def create_top(self, vertex_cnt, vdata_values, prim_indices):
        # if self.open_top:
        #     open_sides = dict(open_bottom=True, open_top=True)
        # else:
        #     open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_bottom=True)

        # z = (self._height + self.c_radius) / 2
        # center = Point3(0, 0, z)
        # vertex_cnt = self.create_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        # vertex_cnt = self.create_rect_edges(vertex_cnt, vdata_values, prim_indices, Sides.TOP)

        # return vertex_cnt
        # if self.thickness:
        #     center = Point3(0, 0, (self.height / 2 - self.thickness / 2))
        #     open_sides = dict(open_bottom=True, open_top=True)
        #     vertex_cnt = self.create_rect(
        #         vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.thickness, center, open_sides)

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
        self._height = self.height - self.c_radius * 2    # **********************

        self.dims = (self.width, self._depth, self._height)  # **********************
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
                ['z', self._height, self.open_bottom, self.open_top]  # **********************
            ]
            self.define_inner_details(outer_box_details)

        # Variables for the corner cylinders.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        # self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        # self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d
        self.c_segs_tc = 0
        self.c_segs_bc = 0

    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt = self.create_middle(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_top(vertex_cnt, vdata_values, prim_indices)

        # if self.c_radius > 0:
        #     vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        if self.thickness > 0:
            maker = RoundedEdgeBox(
                width=self._width + self.c_inner_radius * 2,
                depth=self._depth + self.c_inner_radius * 2,
                height=self._height + self.c_inner_radius * 2,
                segs_w=self.segs_w,
                segs_d=self.segs_d,
                segs_z=self.segs_z,
                thickness=0,
                open_top=True,
                open_bottom=True,
                invert=not self.invert,
                # corner_radius=self.c_radius
                corner_radius=self.c_inner_radius,
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