import math
from enum import Flag, auto

from panda3d.core import Vec3, Point3, Vec2

from ..box import Box
from ..cylinder import Cylinder
from ..capsule import CapsuleHemisphere


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

    def create_vertical_edge_cylinder(self, vertex_cnt, vdata_values, prim_indices,
                                      height, center, start_angle, slice_deg):
        corner = VerticalRoundedEdge(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=self.segs_z,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            invert=self.invert
        )

        vertex_cnt = corner.create_cylinder(vertex_cnt, vdata_values, prim_indices)
        return vertex_cnt

    def create_horizontal_edge_cylinder(self, vertex_cnt, vdata_values, prim_indices,
                                        height, center, start_angle, slice_deg, x_axis,
                                        start_slice_cap, end_slice_cap):
        edge = HorizontalRoundedEdge(
            center=center + self.center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            height=height,
            segs_c=20,
            segs_a=self.segs_w if x_axis else self.segs_d,
            segs_top_cap=self.c_segs_tc,
            segs_bottom_cap=self.c_segs_bc,
            ring_slice_deg=slice_deg,
            start_slice_cap=start_slice_cap,
            end_slice_cap=end_slice_cap,
            invert=self.invert,
            x_axis=x_axis
        )

        vertex_cnt = edge.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.thickness:
            vertex_cnt += edge.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_corner_sphere(self, vertex_cnt, vdata_values, prim_indices, center,
                             start_angle, slice_deg, bottom_clip=-1., top_clip=1.):
        corner = QuarteredHemisphereCorner(
            center=center,
            start_angle_deg=start_angle,
            radius=self.c_radius,
            inner_radius=self.c_inner_radius,
            segs_h=20,
            segs_v=20,
            segs_slice_caps=0,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=self.invert
        )

        vertex_cnt = corner.create_quartered_hemisphere(
            vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt


class VerticalRoundedEdge(Cylinder):
    """Creates a vertical box edge cylinder model.
       Args:
            center (Point3): the center of a cylinder
            start_angle_deg (int): from which angle to start slicing; by degree
            radius (float): the radius of the cylinder; must be more than zero
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360
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

    def create_mantle_quad_vertices(self, index_offset, vdata_values, prim_indices):
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

        return vertex_cnt


class HorizontalRoundedEdge(Cylinder):
    """Creates a cylinder model.
       Args:
            center (Point3): the center of a cylinder
            start_angle_deg (int): from which angle to start slicing; by degree
            radius (float): the radius of the cylinder; must be more than zero
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360
            start_slice_cap (bool): if True, a cap is created on the slice start side; default is True
            end_slice_cap (bool): if True, a cap is created on the opposite side of the slice start side; default is True
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
            x_axis (bool): if true, parallel to x-axis; if false, parallel to y-axis
    """

    def __init__(self, center, start_angle_deg, radius=1., inner_radius=0., height=1.,
                 segs_c=40, segs_a=2, segs_top_cap=3, segs_bottom_cap=3, ring_slice_deg=0,
                 start_slice_cap=False, end_slice_cap=False, invert=False, x_axis=True):
        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_c=segs_c,
            segs_a=segs_a,
            segs_top_cap=segs_top_cap,
            segs_bottom_cap=segs_bottom_cap,
            slice_caps_radial=2,
            slice_caps_axial=segs_a,
            ring_slice_deg=ring_slice_deg,
            start_slice_cap=start_slice_cap,
            end_slice_cap=end_slice_cap,
            invert=invert
        )
        # If True, tilt a vertical cylinder, whose bottom center is the point (0, 0, 0),
        # 90 degrees in the x-axis direction, and if not, 90 degrees in the y-axis direction.
        self.x_axis = x_axis
        self.center = center
        self.start_angle_deg = start_angle_deg
        self.define_variables()

    def define_variables(self):
        self.start_angle_rad = math.pi * self.start_angle_deg / 180
        super().define_variables()

    def get_cap_normal(self):
        if self.x_axis:
            normal = Vec3(1, 0, 0) if self.invert else Vec3(-1, 0, 0)
        else:
            normal = Vec3(0, 1, 0) if self.invert else Vec3(0, -1, 0)

        return normal

    def create_cap_triangles(self, vdata_values, bottom=True):
        normal = self.get_cap_normal()
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        val = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        r = self.radius / segs_cap
        vertex_cnt = 0

        # cap center and triangle vertices
        for i in range(self.segs_c + 1):
            if i == 0:
                vertex = Point3(val, 0, 0) if self.x_axis else Point3(0, val, 0) + self.center
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            angle = self.delta_rad * i + (0 if self.invert else self.slice_rad) + self.start_angle_rad
            c = math.cos(angle)
            s = math.sin(angle) * direction

            if self.x_axis:
                vertex = Point3(val, r * s, r * c)
            else:
                vertex = Point3(r * c, val, r * s)

            # Add center to vertex.
            vertex += self.center

            u = 0.5 + c * 0.5 / segs_cap
            _direction = -direction if bottom else direction
            v = 0.5 + s * 0.5 * _direction / segs_cap

            vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
            vertex_cnt += 1

        return vertex_cnt

    def create_cap_quad_vertices(self, vdata_values, bottom=True):
        normal = self.get_cap_normal()
        segs_cap = self.segs_bc if bottom else self.segs_tc

        if not bottom:
            normal *= -1

        val = 0 if bottom else self.height
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

                if self.x_axis:
                    vertex = Point3(val, r * s, r * c)
                else:
                    vertex = Point3(r * c, val, r * s)

                # Add center to vertex.
                vertex += self.center

                _r = r / self.radius
                u = 0.5 + c * 0.5 * _r
                _direction = -direction if bottom else direction
                v = 0.5 + s * 0.5 * _direction * _r

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    def create_mantle_quad_vertices(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            f1 = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0 if self.invert else self.slice_rad) + self.start_angle_rad

                f2 = self.radius * math.cos(angle)
                f3 = self.radius * math.sin(angle) * direction
                vertex = Point3(f1, f2, f3) if self.x_axis else Point3(f3, f1, f2)
                # Add center.
                vertex += self.center

                vec = Vec3(0.0, f2, f3) if self.x_axis else Vec3(f3, 0.0, f2)
                normal = vec.normalized() * direction
                u = j / self.segs_c
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        return vertex_cnt

    def get_slice_cap_angle(self, is_start):
        match self.start_angle_deg:
            case 0:
                deg = 90 if is_start else 180
            case 90:
                deg = 0 if is_start else 90
            case 180:
                deg = 270 if is_start else 0
            case 270:
                deg = 180 if is_start else 270

        delta_rad = math.pi * ((360 - deg) / 180) / self.segs_c
        return delta_rad

    def create_slice_cap_quad_vertices(self, index_offset, vdata_values, prim_indices, is_start):
        vertex_cnt = 0
        direction = -1 if self.invert else 1

        delta_rad = self.get_slice_cap_angle(is_start)
        angle = delta_rad * self.segs_c
        c = math.cos(angle)
        s = -math.sin(angle)
        normal = Vec3()

        if self.x_axis:
            normal.y = -direction if self.center.y > 0 else direction
        else:
            normal.x = -direction if self.center.x > 0 else direction

        for i in range(self.segs_sc_a + 1):
            z = self.height * i / self.segs_sc_a
            v = i / self.segs_sc_a

            for j in range(self.segs_sc_r + 1):
                r = self.inner_radius + (self.radius - self.inner_radius) * j / self.segs_sc_r
                vertex = Point3(z, r * s, r * c) if self.x_axis else Point3(r * c, z, r * s)
                vertex += self.center

                coef = 0.5 if is_start else -0.5
                u = 0.5 + coef * r / self.radius * direction * -1
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        return vertex_cnt


class QuarteredHemisphereCorner(CapsuleHemisphere):

    """Create a sphere model.
       Args:
            center (Point3): the center of a sphere
            start_angle_deg (int): from which angle to start slicing; by degree
            radius (float): the radius of sphere; more than 0
            inner_radius (float): the radius of the inner sphere; cannot be negative; must be in [0., radius]
            segs_h(int): subdivisions along horizontal circles; minimum = 3
            segs_v (int): subdivisions along vertical semicircles; minimum = 2
            segs_slice_caps (int): radial subdivisions of the slice caps; minimum = 0 (no caps)
            slice_deg (float): the angle of the pie slice removed from the sphere, in degrees; must be in [0., 360.]
            bottom_clip (float):
                relative height of the plane that cuts off a bottom part of the sphere;
                must be in [-1., 1.] range;
                -1. (no clipping)
            top_clip (float):
                relative height of the plane that cuts off a top part of the sphere;
                must be in [bottom_clip, 1.] range;
                1. (no clipping);
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, center, start_angle_deg=0, radius=1., inner_radius=0, segs_h=40, segs_v=20,
                 segs_slice_caps=2, slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        super().__init__(
            center=center,
            radius=radius,
            inner_radius=inner_radius,
            segs_h=segs_h,
            segs_v=segs_v,
            segs_slice_caps=segs_slice_caps,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=invert
        )
        self.start_angle_deg = start_angle_deg
        self.start_angle_rad = math.pi * self.start_angle_deg / 180

    def create_quartered_hemisphere(self, vertex_cnt, vdata_values, prim_indices):
        vertex_cnt, offset = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += self.create_mantle_quads(offset, vdata_values, prim_indices)
        vertex_cnt += self.create_top(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def get_cap_edge_vertices(self, vdata_values):
        direction = -1 if self.invert else 1
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.radius * -math.cos(angle_v)

        radius_h = self.radius * math.sin(angle_v)
        _delta = 0 if self.invert else self.slice_rad
        v = angle_v / math.pi

        # Shift the slice start position.
        _delta += self.start_angle_rad

        # Define the triangle vertices along the bottom pole.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            # Shift the center and change the position of the vertex.
            vertex = Point3(x, y, z) + self.center

            normal = Vec3(x, y, z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_cap_edge_vertices(self, vdata_values, prim_indices, cap):
        radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad

        # Shift the slice start position.
        _delta += self.start_angle_rad

        v = (math.pi - math.acos(cap.z / self.radius)) / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            # Shift the center and change the position of the vertex.
            vertex = Point3(x, y, cap.z) + self.center

            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        n = self.segs_h + 1
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad
        # Shift the slice start position.
        _delta += self.start_angle_rad
        vertex_cnt = 0

        # Define the mantle quad vertices.
        # in Sphere, `for i in range(1, self.segs_v - 1):`
        for i in range(1, self.segs_v):
            angle_v = self.bottom_angle + self.delta_angle_v * (i + 1)
            z = self.radius * -math.cos(angle_v)
            radius_h = self.radius * math.sin(angle_v)
            v = angle_v / math.pi

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                x = radius_h * math.cos(angle_h)
                y = radius_h * math.sin(angle_h) * direction

                vertex = Point3(x, y, z)
                normal = vertex.normalized() * direction
                # Center must be added after normalize. Otherwise, the shadows will go wrong.
                vertex = Point3(x, y, z) + self.center

                uv = Vec2(j / self.segs_h, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            if i > 0:
                for j in range(self.segs_h):
                    vi1 = i * n + j + index_offset
                    vi2 = vi1 - n
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1

                    prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                    prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))

        return vertex_cnt