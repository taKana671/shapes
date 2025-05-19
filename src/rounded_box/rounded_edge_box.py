import array

from panda3d.core import Vec3, Point3, Vec2, Point2

from .rounded_box import Sides, RoundedBox
# from .rounded_box import BoxEdgeCylinder



# class RoundedEdgeBox(RoundedCornerBox):

    # def __init__(self, corner_radius=0.5, width=2., depth=2., height=2., segs_w=4, segs_d=4, segs_z=4,
    #              thickness=0., open_top=False, open_bottom=False, invert=False):
    #     super().__init__(
    #         corner_radius=corner_radius,
    #         width=width,
    #         depth=depth,
    #         height=height,
    #         segs_w=segs_w,
    #         segs_d=segs_d,
    #         segs_z=segs_z,
    #         thickness=thickness,
    #         open_top=open_top,
    #         open_bottom=open_bottom,
    #         invert=invert
    #     )

class RoundedEdgeBox(RoundedBox):

    def __init__(self, width=4., depth=4., height=4., segs_w=4, segs_d=4, segs_z=4,
                 thickness=0., open_top=False, open_bottom=False, invert=False, corner_radius=0.5):

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

    def create_side_rect(self, vertex_cnt, vdata_values, prim_indices,
                         width, depth, height, center, open_sides):
        rect = RoundedEdgeBox(
            width=width,
            depth=depth,
            # height=self.height,
            height=height,
            segs_w=3,
            segs_d=3,
            segs_z=self.segs_z,
            thickness=self.thickness,
            # open_top=self.open_top,
            # open_bottom=self.open_bottom,
            corner_radius=0,
            # rounded_f_left=False,
            # rounded_f_right=False,
            # rounded_b_left=False,
            # rounded_b_right=False,
            invert=self.invert
        )

        for k, v in open_sides.items():
            rect.__dict__[k] = v

        rect.define_variables()
        rect.center = center + self.center
        vertex_cnt = rect.create_sides(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):

        # center = Point3(0, 0, -(self.height + self.c_radius) / 2)
        # open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
        # vertex_cnt = self.create_side_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        center = Point3(self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        start_angle = 0
        slice_deg = 270

        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        center = Point3(self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        start_angle = 90
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        center = Point3(-self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        start_angle = 180
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)



        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        start_angle = 270
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=-1., top_clip=0)


        # left
        x_axis = False
        height = self._depth
        start_angle = 270
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )

        # back
        x_axis = True
        height = self._width
        start_angle = 270
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )


        # right
        x_axis = False
        height = self._depth
        start_angle = 180
        slice_deg = 270
        center = Point3(self._width * 0.5, -self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )

        # front
        x_axis = True
        height = self._width
        start_angle = 0
        slice_deg = 270
        center = Point3(-self._width * 0.5, self._depth * 0.5, -self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )


        center = Point3(0, 0, -(self._height + self.c_radius) / 2)
        open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
        vertex_cnt = self.create_side_rect(
            vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        return vertex_cnt

    def create_corner_spheres(self, vertex_cnt, vdata_values, prim_indices, side, bottom=True):
        bottom_clip, top_clip = -1, 1

        if bottom:
            top_clip = 0
            z = -self._height * 0.5
        else:
            bottom_clip = 0
            z = self.height * 0.5

        
    
    
    
    def create_top(self, vertex_cnt, vdata_values, prim_indices):

        # center = Point3(0, 0, -(self.height + self.c_radius) / 2)
        # open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_top=True)
        # vertex_cnt = self.create_side_rect(
        #     vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        center = Point3(self._width * 0.5, -self._depth * 0.5, self._height * 0.5)
        start_angle = 0
        slice_deg = 270

        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=0., top_clip=1)


        center = Point3(self._width * 0.5, self._depth * 0.5, self._height * 0.5)
        start_angle = 90
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=0, top_clip=1)


        center = Point3(-self._width * 0.5, self._depth * 0.5, self._height * 0.5)
        start_angle = 180
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=0, top_clip=1)



        center = Point3(-self._width * 0.5, -self._depth * 0.5, self._height * 0.5)
        start_angle = 270
        slice_deg = 270
        vertex_cnt += self.create_corner_sphere(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg,
            bottom_clip=0, top_clip=1)


        # left
        x_axis = False
        height = self._depth
        start_angle = 0
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )

        # back
        x_axis = True
        height = self._width
        start_angle = 180
        slice_deg = 270
        center = Point3(-self._width * 0.5, -self._depth * 0.5, self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )


        # right
        x_axis = False
        height = self._depth
        start_angle = 90
        slice_deg = 270
        center = Point3(self._width * 0.5, -self._depth * 0.5, self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )

        # front
        x_axis = True
        height = self._width
        start_angle = 90
        slice_deg = 270
        center = Point3(-self._width * 0.5, self._depth * 0.5, self._height * 0.5)
        vertex_cnt = self.create_horizontal_rounded_edge(
            vertex_cnt, vdata_values, prim_indices, height, center, start_angle, slice_deg, x_axis
        )


        center = Point3(0, 0, (self._height + self.c_radius) / 2)
        open_sides = dict(open_left=True, open_right=True, open_front=True, open_back=True, open_bottom=True)
        vertex_cnt = self.create_side_rect(
            vertex_cnt, vdata_values, prim_indices, self._width, self._depth, self.c_radius, center, open_sides)

        return vertex_cnt

    def create_rounded_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self._height * 0.5)

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
            vertex_cnt, vdata_values, prim_indices, self._height, center, angle, 270
        )
        return vertex_cnt


    def create_rect_sides(self, vertex_cnt, vdata_values, prim_indices, side):
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

        # import pdb; pdb.set_trace()
        open_sides = {**open_sides, **common_open_sides}
        vertex_cnt = self.create_side_rect(
            vertex_cnt, vdata_values, prim_indices, w, d, self._height, center, open_sides)
        return vertex_cnt

    def create_corners(self, vertex_cnt, vdata_values, prim_indices):
        li = [
            [Sides.FRONT_LEFT, Sides.LEFT],
            [Sides.BACK_LEFT, Sides.BACK],
            [Sides.BACK_RIGHT, Sides.RIGHT],
            [Sides.FRONT_RIGHT, Sides.FRONT]
        ]
        # import pdb; pdb.set_trace()
        for corner, side in li:
            # create a rounded or box corner.
            # if is_rounded:
            vertex_cnt = self.create_rounded_corners(
                vertex_cnt, vdata_values, prim_indices, corner)
            # else:
            #     vertex_cnt = self.create_rect_corners(
            #         vertex_cnt, vdata_values, prim_indices, corner)

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

        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        # center box
        # vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)

        vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_top(vertex_cnt, vdata_values, prim_indices)
        
        
        
        # if self.c_radius > 0:
        #     vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        # if self.thickness > 0:
        #     maker = RoundedCornerBox(
        #         width=self._width + self.c_inner_radius * 2,
        #         depth=self._depth + self.c_inner_radius * 2,
        #         height=self.height,
        #         segs_w=self.segs_w,
        #         segs_d=self.segs_d,
        #         segs_z=self.segs_z,
        #         thickness=0,
        #         open_top=True,
        #         open_bottom=True,
        #         invert=not self.invert,
        #         corner_radius=self.c_inner_radius,
        #         rounded_f_left=self.rf_left,
        #         rounded_f_right=self.rf_right,
        #         rounded_b_left=self.rb_left,
        #         rounded_b_right=self.rb_right
        #     )

        #     # Define the inner box center.
        #     maker.center = self.calc_inner_box_center()

            # geom_node = maker.get_geom_node()
            # self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            # return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'box')

        return geom_node