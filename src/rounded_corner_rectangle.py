import array
from types import SimpleNamespace
import math

from panda3d.core import Vec2, Vec3, Point3

from .box import Box

from .rounded_box import BoxEdgeCylinder


class RoundedCornerBox(Box):
    """Create a geom node of capsule prism.
        Args:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_h (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box.
            rounded_left (bool): if True, left side is rounded.
            rounded_right (bool): if True, right side is rounded.
            open_top(bool): used only when thickness is 0; if True, no top side.
            open_bottom(bool): used only when thickness is 0; if True, no bottom side.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, width=4.0, depth=3.0, height=2.0, segs_w=4, segs_d=4, segs_z=4, thickness=0,
                 open_top=False, open_bottom=False, open_back=True, open_front=True,
                 open_left=False, open_right=False, invert=False, corner_radius=1,
                 rounded_f_left=True, rounded_f_right=True, rounded_b_left=True, rounded_b_right=True):
        super().__init__(
            width=width,
            depth=depth - corner_radius * 2,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_back=open_back,
            open_front=open_front,
            open_left=open_left,
            open_right=open_right,
            open_top=open_top,
            open_bottom=open_bottom
        )

        self.cn_radius = corner_radius
        self.rf_left = rounded_f_left
        self.rf_right = rounded_f_right
        self.rb_left = rounded_b_left
        self.rb_right = rounded_b_right

    def create_rect(self, vertex_cnt, vdata_values, prim_indices, width, center, open_faces):
        rect = RoundedCornerBox(
            width=width,
            depth=self.cn_radius,
            height=self.height,
            segs_w=3,
            segs_d=3,
            segs_z=self.segs_z,
            thickness=0,
            **open_faces,
            corner_radius=0,
            rounded_f_left=False,
            rounded_f_right=False,
            rounded_b_left=False,
            rounded_b_right=False,
        )

        rect.define_variables()
        rect.center = center + self.center
        vertex_cnt = rect.create_sides(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_corner(self, vertex_cnt, vdata_values, prim_indices, center, start_angle):
        self.r_edge = BoxEdgeCylinder(
            center=center,
            start_angle_deg=start_angle,
            radius=self.cn_radius,
            inner_radius=0,
            height=self.height,
            segs_c=20,
            segs_a=self.segs_z,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=270,
            invert=self.invert
        )

        vertex_cnt = self.r_edge.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_front(self, vertex_cnt, vdata_values, prim_indices):
        # Create two corners of the front side.
        center = Point3(0, self.depth / 2, -self.height / 2)

        if self.rf_left:
            center.x = -self.width / 2 + self.cn_radius
            angle = 180
            vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, center, angle)

        if self.rf_right:
            center.x = self.width / 2 - self.cn_radius
            angle = 90
            vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, center, angle)

        # Create a rectangle between the two corners of the front side.
        width = self.width - (self.rf_left + self.rf_right) * self.cn_radius
        x = (self.cn_radius * self.rf_left - self.cn_radius * self.rf_right) * 0.5
        y = (self.depth + self.cn_radius) / 2
        center = Point3(x, y, 0) + self.center
        open_faces = dict(open_left=self.rf_left, open_right=self.rf_right, open_front=False)
        vertex_cnt = self.create_rect(vertex_cnt, vdata_values, prim_indices, width, center, open_faces)

        return vertex_cnt

    def create_back(self, vertex_cnt, vdata_values, prim_indices):
        # Create two corners of the back side.
        center = Point3(0, -self.depth / 2, -self.height / 2)

        if self.rb_left:
            center.x = -self.width / 2 + self.cn_radius
            angle = 270
            vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, center, angle)

        if self.rb_right:
            center.x = self.width / 2 - self.cn_radius
            angle = 0
            vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, center, angle)

        # Create a rectangle between the two corners of the back side.
        width = self.width - (self.rb_left + self.rb_right) * self.cn_radius
        x = (self.cn_radius * self.rb_left - self.cn_radius * self.rb_right) * 0.5
        y = -(self.depth + self.cn_radius) / 2
        center = Point3(x, y, 0) + self.center
        open_faces = dict(open_left=self.rb_left, open_right=self.rb_right, open_back=False)
        vertex_cnt = self.create_rect(vertex_cnt, vdata_values, prim_indices, width, center, open_faces)

        return vertex_cnt

    def define_variables(self):
        # Variables for the box.
        super().define_variables()
        # Variables for the left and right cylinders.
        self.c_radius = self.depth / 2.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d

    def create_side(self, index_offset, vdata_values, prim_indices, direction, is_front,
                    vertex, normal, name, index, offset, segs):
        vertex_cnt = 0

        for i in range(segs.axis_2 + 1):
            b = i / segs.axis_2
            vertex[index.axis_2] = (-.5 + b) * self.dims[index.axis_2] + offset.axis_2

            for j in range(segs.axis_1 + 1):
                a = j / segs.axis_1
                vertex[index.axis_1] = (-.5 + a) * self.dims[index.axis_1] + offset.axis_1

                if is_front:
                    u = -b * direction + (1 if direction > 0 else 0)
                    v = a
                else:
                    u = a * direction + (1 if direction < 0 else 0)
                    v = b

                # vert = vertex + self.center
                # vdata_values.extend([*vert, *self.color, *normal, *(u, v)])
                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        self.define_vertex_order(index_offset, prim_indices, direction, segs.axis_1, segs.axis_2)

        return vertex_cnt

    # def create_sides(self, vdata_values, prim_indices):
    def create_sides(self, vertex_cnt, vdata_values, prim_indices):
        # vertex_cnt = 0

        for plane in ('xyz', 'zxy', 'yzx'):
            plane_id = plane[:2]
            is_front = plane_id == 'zx'
            name, index, offset, segments = self.get_plane_details(plane)

            for direction in (-1, 1):
                normal = Vec3()
                normal[index.axis_3] = direction * (-1 if self.invert else 1)
                vertex = Point3()
                vertex[index.axis_3] = .5 * self.dims[index.axis_3] * direction + offset.axis_3
                side_id = f"{'-' if direction == -1 else ''}{plane_id}"

                if self.open_sides[side_id]:
                    if self.thickness > 0:
                        vertex_cnt += self.create_thick_side(vertex_cnt, vdata_values, prim_indices, direction, is_front,
                                                             vertex, normal, name, index, offset, segments)
                else:
                    vertex_cnt += self.create_side(vertex_cnt, vdata_values, prim_indices, direction, is_front,
                                                   vertex, normal, name, index, offset, segments)

        return vertex_cnt

    def get_geom_node(self):
        self.define_variables()

        if self.thickness > 0:
            self.define_inner_details()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)

        if self.cn_radius > 0:
            vertex_cnt = self.create_front(vertex_cnt, vdata_values, prim_indices)
            vertex_cnt = self.create_back(vertex_cnt, vdata_values, prim_indices)

        # if self.thickness > 0:
        #     maker = RoundedBox(
        #         width=self.inner_dims['x'],
        #         depth=self.inner_dims['y'],
        #         height=self.inner_dims['z'],
        #         segs_w=self.segs_w,
        #         segs_d=self.segs_d,
        #         segs_z=self.segs_z,
        #         thickness=0,
        #         rounded_left=self.rounded_left,
        #         rounded_right=self.rounded_right,
        #         open_top=True,
        #         open_bottom=True,
        #         invert=not self.invert
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



        # box1 = RoundedCornerBox(width=2.0, depth=0.5, height=2.0, segs_w=2, segs_d=2, segs_z=4, thickness=0,
        #                         open_front=False, open_left=True, open_right=True, open_back=True)
        # box1.define_variables()
        # # box1.center = Point3(0, 0.375, 0)
        # box1.center = Point3(0, 0.625, 0) # radius of cylinder / 4 + rect width / 2 
        # vertex_cnt = box1.create_sides(vertex_cnt, vdata_values, prim_indices)

        # vertex_cnt = self.create_left(vertex_cnt, vdata_values, prim_indices)
        # vertex_cnt = self.create_right(vertex_cnt, vdata_values, prim_indices)

        
        # box2 = RoundedCornerBox(width=1.0, depth=0.5, height=2.0, segs_w=1, segs_d=1, segs_z=4, thickness=0,
        #                         open_front=True, open_left=True, open_right=True, open_back=False)
        # box2.define_variables()
        # box2.center = Point3(0, -0.375, 0)
        # vertex_cnt = box2.create_sides(vertex_cnt, vdata_values, prim_indices)
        