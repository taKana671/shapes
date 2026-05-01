import math

from panda3d.core import Vec3, Point3, Vec2

from .hemisphere import BasicHemisphere


class QuarteredHemisphereCorner(BasicHemisphere):
    """A class to create a hemisphere.

       Args:
            center (Point3): the center of a sphere.
            start_angle_deg (int): from which angle to start slicing; by degree.
            radius (float): the radius of sphere; more than 0.
            inner_radius (float): the radius of the inner sphere; cannot be negative; must be in [0., radius].
            segs_h(int): subdivisions along horizontal circles; minimum = 3.
            segs_v (int): subdivisions along vertical semicircles; minimum = 2.
            segs_slice_caps (int): radial subdivisions of the slice caps; minimum = 0 (no caps).
            slice_deg (float): the angle of the pie slice removed from the sphere, in degrees; must be in [0., 360.].
            bottom_clip (float):
                relative height of the plane that cuts off a bottom part of the sphere.
                must be in [-1., 1.] range.
                -1. (no clipping)
            top_clip (float):
                relative height of the plane that cuts off a top part of the sphere.
                must be in [bottom_clip, 1.] range.
                1. (no clipping);
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, center, start_angle_deg=0, radius=1., inner_radius=0, segs_h=40, segs_v=20,
                 segs_slice_caps=2, slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        self.color = (1, 1, 1, 1)
        self.center = center
        self.radius = radius
        self.inner_radius = inner_radius
        self.segs_h = segs_h
        self.segs_v = segs_v
        self.segs_sc = segs_slice_caps
        self.slice_deg = slice_deg
        self.bottom_clip = bottom_clip
        self.top_clip = top_clip
        self.invert = invert
        self.start_angle_deg = start_angle_deg
        self.define_variables()

    def define_variables(self):
        self.start_angle_rad = math.pi * self.start_angle_deg / 180
        super().define_variables()

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

    def create_cap_edge_vertices(self, vdata_values, cap):
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