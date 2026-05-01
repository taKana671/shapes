import math

from panda3d.core import Vec3, Point3, Vec2

from ..cylinder import BasicCylinder, CylinderGeometry


class VerticalRoundedEdge(CylinderGeometry):
    """A class to create a vertical cylinder on box edge.

       Args:
            center (Point3): the center of a cylinder.
            start_angle_deg (int): from which angle to start slicing; by degree.
            radius (float): the radius of the cylinder; must be more than zero.
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal.
            height (float): length of the cylinder.
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum = 3.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum = 1.
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0.
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0.
            ring_slice_deg (float): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, center, start_angle_deg, radius=1., inner_radius=0., height=1., segs_c=40,
                 segs_a=2, segs_top_cap=3, segs_bottom_cap=3, ring_slice_deg=0, invert=False):
        self.color = (1, 1, 1, 1)
        self.radius = radius
        self.inner_radius = inner_radius
        self.height = height
        self.segs_c = segs_c
        self.segs_a = segs_a
        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap
        self.ring_slice_deg = ring_slice_deg
        self.invert = invert
        self.center = center
        self.start_angle_deg = start_angle_deg
        self.define_variables()

    def define_variables(self):
        self.start_angle_rad = math.pi * self.start_angle_deg / 180
        self.thickness = self.radius - self.inner_radius
        self.slice_rad = math.pi * self.ring_slice_deg / 180
        self.delta_rad = math.pi * ((360 - self.ring_slice_deg) / 180) / self.segs_c

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

    def create_mantle_quad_vertices(self, vdata_values):
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


class HorizontalRoundedEdge(BasicCylinder):
    """A class to create a horizontal cylinder on box edge.

       Args:
            center (Point3): the center of a cylinder.
            start_angle_deg (int): from which angle to start slicing; by degree.
            radius (float): the radius of the cylinder; must be more than zero.
            inner_radius (float): the radius of the inner cylinder; must be less than radius or equal.
            height (float): length of the cylinder.
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum = 3.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum = 1.
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0.
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0.
            ring_slice_deg (float): the angle of the pie slice removed from the cylinder, in degrees; must be from 0 to 360.
            start_slice_cap (bool): if True, a cap is created on the slice start side; default is True.
            end_slice_cap (bool): if True, a cap is created on the opposite side of the slice start side; default is True.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
            x_axis (bool): if true, parallel to x-axis; if false, parallel to y-axis.
    """

    def __init__(self, center, start_angle_deg, radius=1., inner_radius=0., height=1.,
                 segs_c=40, segs_a=2, segs_top_cap=3, segs_bottom_cap=3, ring_slice_deg=0,
                 start_slice_cap=False, end_slice_cap=False, invert=False, x_axis=True):
        self.color = (1, 1, 1, 1)
        self.radius = radius
        self.inner_radius = inner_radius
        self.height = height
        self.segs_c = segs_c
        self.segs_a = segs_a
        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap
        self.segs_sc_r = segs_a
        self.segs_sc_a = segs_a
        self.ring_slice_deg = ring_slice_deg
        self.start_slice_cap = start_slice_cap
        self.end_slice_cap = end_slice_cap
        self.invert = invert

        # If True, tilt a vertical cylinder, whose bottom center is the point (0, 0, 0),
        # 90 degrees in the x-axis direction, and if not, 90 degrees in the y-axis direction.
        self.x_axis = x_axis
        self.center = center
        self.start_angle_deg = start_angle_deg
        self.define_variables()

    def define_variables(self):
        super().define_variables()
        self.start_angle_rad = math.pi * self.start_angle_deg / 180

        self.slice_caps = []

        if self.start_slice_cap:
            self.slice_caps.append(True)

        if self.end_slice_cap:
            self.slice_caps.append(False)

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

    def create_mantle_quad_vertices(self, vdata_values):
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

    def create_slice_cap_quad_vertices(self, vdata_values, is_start):
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
