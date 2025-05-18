import array
import math
from enum import Flag, auto

from panda3d.core import Vec3, Point3, Vec2, Point2

from .box import Box
from .cylinder import Cylinder


class Sides(Flag):

    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    FRONT = auto()
    BACK = auto()

    FRONT_LEFT = FRONT | LEFT
    FRONT_RIGHT = FRONT | RIGHT
    BACK_LEFT = BACK | LEFT
    BACK_RIGHT = BACK | RIGHT


class RoundedBox(Box):

    def create_sides(self, vertex_cnt, vdata_values, prim_indices):
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
                        if plane_id in ('zx', 'yz'):
                            continue

                        vertex_cnt += self.create_thick_side(
                            vertex_cnt, vdata_values, prim_indices, direction, is_front,
                            vertex, normal, name, index, offset, segments)
                else:
                    vertex_cnt += self.create_side(
                        vertex_cnt, vdata_values, prim_indices, direction, is_front,
                        vertex, normal, name, index, offset, segments)

        return vertex_cnt

    def create_corner(self, vertex_cnt, vdata_values, prim_indices, center, start_angle, slice_deg):
        corner = BoxEdgeCylinder(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=self.height,
            segs_c=20,
            segs_a=self.segs_z,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            invert=self.invert
        )

        vertex_cnt = corner.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt


class CapsulePrism(RoundedBox):

    """Create a geom node of capsule prism.
        Args:
            width (float): dimension along the x-axis; more than zero.
            depth (float): dimension along the y-axis; more than zero.
            height (float): dimension along the z-axis; more than zero.
            segs_w (int): the number of subdivisions in width; more than 1.
            segs_d (int): the number of subdivisions in depth; more than 1.
            segs_z (int): the number of subdivisions in height; more than 1.
            thickness (float): offset of inner box sides; 0 means no inner box.
            rounded_left (bool): if True, left side is rounded.
            rounded_right (bool): if True, right side is rounded.
            open_top(bool): used only when thickness is 0; if True, no top side.
            open_bottom(bool): used only when thickness is 0; if True, no bottom side.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, width=1., depth=1., height=1., segs_w=4, segs_d=4, segs_z=4, thickness=0.,
                 rounded_left=True, rounded_right=True, open_top=False, open_bottom=False, invert=False):
        super().__init__(
            width=width,
            depth=depth,
            height=height,
            segs_w=segs_w,
            segs_d=segs_d,
            segs_z=segs_z,
            thickness=thickness,
            invert=invert,
            open_left=rounded_left,
            open_right=rounded_right,
            open_top=True if thickness > 0 else open_top,
            open_bottom=True if thickness > 0 else open_bottom
        )

        self.rounded_left = rounded_left
        self.rounded_right = rounded_right

    def create_left(self, vertex_cnt, vdata_values, prim_indices):
        if self.rounded_left:
            center = Point3(-self.width / 2, 0, -self.height / 2)
            start_angle = 90 if self.invert else 270
            vertex_cnt = self.create_corner(
                vertex_cnt, vdata_values, prim_indices, center, start_angle, 180
            )

        return vertex_cnt

    def create_right(self, vertex_cnt, vdata_values, prim_indices):
        if self.rounded_right:
            center = Point3(self.width / 2, 0, -self.height / 2)
            start_angle = 270 if self.invert else 90
            vertex_cnt = self.create_corner(
                vertex_cnt, vdata_values, prim_indices, center, start_angle, 180
            )

        return vertex_cnt

    def create_rounded_corners(self, vertex_cnt, vdata_values, prim_indices, side):
        center = Point3(0, 0, -self.height * 0.5)

        match side:

            case Sides.LEFT:
                center.x = -self.width * 0.5
                start_angle = 90 if self.invert else 270

            case Sides.RIGHT:
                center.x = self.width * 0.5
                start_angle = 270 if self.invert else 90

        vertex_cnt = self.create_corner(
            vertex_cnt, vdata_values, prim_indices, center, start_angle, 180
        )
        return vertex_cnt

    def create_corners(self, vertex_cnt, vdata_values, prim_indices):
        if self.rounded_left:
            vertex_cnt = self.create_rounded_corners(
                vertex_cnt, vdata_values, prim_indices, Sides.LEFT)

        if self.rounded_right:
            vertex_cnt = self.create_rounded_corners(
                vertex_cnt, vdata_values, prim_indices, Sides.RIGHT)

        return vertex_cnt

    def define_variables(self):
        # Variables for the box.
        super().define_variables()
        # Variables for the left and right cylinders.
        self.c_radius = self.depth / 2.
        self.c_inner_radius = 0 if self.thickness <= 0 else self.c_radius - self.thickness
        self.c_segs_tc = 0 if self.thickness <= 0 and self.open_top else self.segs_d
        self.c_segs_bc = 0 if self.thickness <= 0 and self.open_bottom else self.segs_d

    def get_geom_node(self):
        self.define_variables()

        # Create outer rounded box.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_sides(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_corners(vertex_cnt, vdata_values, prim_indices)

        if self.thickness > 0:
            maker = CapsulePrism(
                width=self.inner_dims['x'],
                depth=self.inner_dims['y'],
                height=self.inner_dims['z'],
                segs_w=self.segs_w,
                segs_d=self.segs_d,
                segs_z=self.segs_z,
                thickness=0,
                rounded_left=self.rounded_left,
                rounded_right=self.rounded_right,
                open_top=True,
                open_bottom=True,
                invert=not self.invert
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

    # def create_rect(self, vertex_cnt, vdata_values, prim_indices, width, depth, center, open_sides):
    def create_rect(self, vertex_cnt, vdata_values, prim_indices, width, depth, height, center, open_sides):
        rect = RoundedCornerBox(
            width=width,
            depth=depth,
            # height=self.height,
            height=height,
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

        vertex_cnt = self.create_corner(vertex_cnt, vdata_values, prim_indices, center, angle, 270)
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

        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, self.c_radius, self.c_radius, self.height, center, open_sides)
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

        vertex_cnt = self.create_rect(
            vertex_cnt, vdata_values, prim_indices, w, d, self.height, center, open_sides)
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


class BoxEdgeCylinder(Cylinder):
    """Creates a cylinder model.
       Args:
            center (Point3): the center of a cylinder.
            start_angle_deg (int): from which angle to start slicing; by degree.
            radius (float): the radius of the cylinder; must be more than zero
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum = 0
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum=0
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, center, start_angle_deg, radius=1., inner_radius=0., height=1.,
                 segs_c=40, segs_a=2, segs_top_cap=3, segs_bottom_cap=3, ring_slice_deg=0, invert=False):
        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_c=segs_c,
            segs_a=segs_a,
            segs_top_cap=segs_top_cap,
            segs_bottom_cap=segs_bottom_cap,
            ring_slice_deg=ring_slice_deg,
            slice_caps_radial=0,
            slice_caps_axial=0,
            invert=invert
        )

        self.center = center
        self.start_angle_deg = start_angle_deg
        self.start_angle_rad = math.pi * self.start_angle_deg / 180
        self.define_variables()

    def create_cap_triangles(self, vdata_values, bottom=True):
        normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        height = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        r = self.radius / segs_cap
        vertex_cnt = 0

        # cap center and triangle vertices
        for i in range(self.segs_c + 1):
            if i == 0:
                vertex = Point3(0, 0, height) + self.center  # Add center.
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            angle = self.delta_rad * i + (0 if self.invert else self.slice_rad) + self.start_angle_rad  # ******
            c = math.cos(angle)
            s = math.sin(angle) * direction
            vertex = Point3(r * c, r * s, height) + self.center  # Add center.

            u = 0.5 + c * 0.5 / segs_cap
            _direction = -direction if bottom else direction
            v = 0.5 + s * 0.5 * _direction / segs_cap

            vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
            vertex_cnt += 1

        return vertex_cnt

    def create_cap_quad_vertices(self, vdata_values, bottom=True):
        normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        height = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        n = 0 if self.inner_radius else 1
        vertex_cnt = 0

        # cap quad vertices
        for i in range(n, segs_cap + 1 - n):
            r = self.inner_radius + self.thickness * (i + n) / segs_cap

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad) + self.start_angle_rad  # ******
                c = math.cos(angle)
                s = math.sin(angle) * direction
                vertex = Point3(r * c, r * s, height) + self.center  # Add center.

                _r = r / self.radius
                u = 0.5 + c * 0.5 * _r
                _direction = -direction if bottom else direction
                v = 0.5 + s * 0.5 * _direction * _r

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad) + self.start_angle_rad

                x = self.radius * math.cos(angle)
                y = self.radius * math.sin(angle) * direction

                vertex = Point3(x, y, z) + self.center  # Add center.
                normal = Vec3(x, y, 0.0).normalized() * direction

                u = j / self.segs_c
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        # the vertex order of the mantle quads
        n = self.segs_c + 1

        for i in range(1, self.segs_a + 1):
            for j in range(self.segs_c):
                vi1 = index_offset + i * n + j
                vi2 = vi1 - n
                vi3 = vi2 + 1
                vi4 = vi1 + 1

                prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))

        return vertex_cnt