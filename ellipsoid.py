import array
import math

from types import SimpleNamespace
from panda3d.core import Vec3, Point3, Vec2
import numpy as np

from .create_geometry import ProceduralGeometry

# create_cap_edge_vertices
# create_cap_pole


class Ellipsoid(ProceduralGeometry):
    """Creates a cylinder model.
       Args:
            major_axis (float): the longest diameter; must be more than zero
            minor_axis (float): the shortest diameter; must be more than zero
            thickness (floar): the radial offset of major and minor axes; must be 0 < thickness < minor_axis
            height (float): length of the cylinder
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            ring_slice_deg (int): the angle of the pie slice removed from the ellipse, in degrees; must be from 0 to 360
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum = 0
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum=0
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, major_axis=3, minor_axis=6, thickness=0.5, segs_h=40, segs_v=40,
                 segs_top_cap=3, segs_bottom_cap=3, segs_slice_caps=2, slice_deg=120,
                 bottom_clip=-1., top_clip=1., invert=False):
        super().__init__()
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.thickness = thickness
        self.segs_h = segs_h
        self.segs_v = segs_v
        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap
        self.segs_sc = segs_slice_caps
        self.slice_deg = slice_deg
        self.bottom_clip = bottom_clip
        self.top_clip = top_clip
        self.invert = invert

        # self.ring_slice_deg = ring_slice_deg
        # self.segs_sc_r = slice_caps_radial
        # self.segs_sc_a = slice_caps_axial

    def create_cap_edge_vertices(self, vdata_values, prim_indices, cap):
        """Helper method to define the edge vertices of a bottom or top.
        """
        # radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        k = self.major_axis / self.minor_axis
        minor_h = math.sqrt(self.semi_minor_axis ** 2 - cap.z ** 2)
        major_h = minor_h * k

        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad

        # v = (math.pi - math.acos(cap.z / self.radius)) / math.pi
        v = (math.pi - math.acos(cap.z / self.semi_minor_axis)) / math.pi
        # v = (math.pi - math.acos(cap.z / minor_h)) / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            # x = radius_h * math.cos(angle_h)
            # y = radius_h * math.sin(angle_h) * direction
            x = major_h * math.cos(angle_h)
            # y = minor_h * math.sin(angle_h) * direction
            y = major_h * math.sin(angle_h) * direction



            vertex = Point3(x, y, cap.z)
            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1


    def get_cap_quad_vertices(self, vdata_values, cap):
        """Helper method to define the quad vertices of a bottom or top cap.
        """
        # radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        k = self.major_axis / self.minor_axis
        minor_h = math.sqrt(self.semi_minor_axis ** 2 - cap.z ** 2)
        major_h = minor_h * k
        # major_h = math.sqrt(self.semi_major_axis ** 2 - cap.z ** 2)

        direction = -1 if self.invert else 1
        vertex_cnt = 0

        normal = cap.normal * -1 if self.invert else cap.normal
        _delta = 0 if self.invert else self.slice_rad

        # Define the bottom cap quad vertices.
        for i in range(1, cap.segs):
            rj = major_h * (i + 1) / cap.segs
            # rn = minor_h * (i + 1) / cap.segs

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction
                # vertex = Point3(rj * c, rn * s, cap.z)
                vertex = Point3(rj * c, rj * s, cap.z)

                _r = (i + 1) / cap.segs
                _direction = direction * -1 if cap.is_bottom else direction
                u = .5 + .5 * c * _r
                v = .5 + .5 * s * _direction * _r
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            vertex_cnt += self.segs_h + 1

        return vertex_cnt

    def get_cap_triangle_vertices(self, vdata_values, cap):
        """Helper method to define the triangle vertices of a bottom or top cap.
        """
        # radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        # major_h = math.sqrt(self.semi_major_axis ** 2 - cap.z ** 2)
        # minor_h = math.sqrt(self.semi_minor_axis ** 2 - cap.z ** 2)

        k = self.major_axis / self.minor_axis
        minor_h = math.sqrt(self.semi_minor_axis ** 2 - cap.z ** 2)
        major_h = minor_h * k
        # major_h = math.sqrt(self.semi_major_axis ** 2 - cap.z ** 2)
     

        direction = -1 if self.invert else 1
        normal = cap.normal * -1 if self.invert else cap.normal
        vertex = Point3(0., 0., cap.z)

        uv = Vec2(.5, .5)
        vdata_values.extend([*vertex, *self.color, *normal, *uv])

        # r = radius_h / cap.segs
        rj = major_h / cap.segs
        # rn = minor_h / cap.segs
        _delta = 0 if self.invert else self.slice_rad

        # Define the cap triangle vertices.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            # vertex = Point3(rj * c, rn * s, cap.z)
            vertex = Point3(rj * c, rj * s, cap.z)

            _direction = -direction if cap.is_bottom else direction
            u = .5 + .5 * c / cap.segs
            v = .5 + .5 * s * _direction / cap.segs
            uv = Vec2(u, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 2

    # Same with Sphere
    def create_top_cap_quads(self, index_offset, vdata_values, prim_indices, cap):
        # Define the bottom cap quad vertices.
        vertex_cnt = self.get_cap_quad_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap quads.
        for i in range(1, self.segs_tc):
            for j in range(self.segs_h):
                vi1 = index_offset + j
                vi2 = vi1 - self.segs_h - 1
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend((vi1, vi3, vi2) if self.invert else (vi1, vi4, vi2))
                prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi4, vi3, vi2))
            index_offset += self.segs_h + 1

        return vertex_cnt

    # Same with Sphere
    def create_top_edge_quads(self, index_offset, prim_indices):
        index_offset -= (self.segs_h - 1) + self.segs_h + 2

        # Define the vertex order of the polygon along the top cap.
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + 1
            vi3 = vi2 + self.segs_h
            vi4 = vi3 + 1

            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
            prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi2, vi4, vi3))
    
    # Same with Sphere
    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices, cap):
        # Define the bottom cap triangle vertices.
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap triangles.
        for i in range(index_offset + 1, index_offset + self.segs_h + 1):
            prim_indices.extend((index_offset, i, i + 1))

        return vertex_cnt

    # Same with Sphere
    def create_bottom_edge_quads(self, index_offset, vdata_values, prim_indices):
        # Define the vertices along the bottom cap.
        vertex_cnt = self.get_cap_edge_vertices(vdata_values)

        # Define the vertex order of the polygon along the bottom pole or cap.
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + 1
            vi3 = vi2 + self.segs_h
            vi4 = vi3 + 1

            prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi1, vi2, vi3))
            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi2, vi4, vi3))

        return vertex_cnt

    # Same with Sphere
    def create_bottom_cap_quads(self, index_offset, vdata_values, prim_indices, cap):
        # Define the bottom cap quad vertices.
        vertex_cnt = self.get_cap_quad_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap quads.
        for i in range(1, self.segs_bc):
            for j in range(self.segs_h):
                vi1 = index_offset + j
                vi2 = vi1 - self.segs_h - 1
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))
            index_offset += self.segs_h + 1

        return vertex_cnt
    
    # Same with Sphere
    def create_bottom_cap_triangles(self, vdata_values, prim_indices, cap):
        # Define the bottom cap triangle vertices.
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap triangles.
        for i in range(1, self.segs_h + 1):
            prim_indices.extend((0, i + 1, i))

        return vertex_cnt

    # Same with Sphere
    def create_cap_pole(self, vdata_values, cap):
        normal = cap.normal * -1 if self.invert else cap.normal
        v = 0 if cap.is_bottom else 1

        # Define the pole triangle vertices.
        for i in range(self.segs_h):
            uv = Vec2(i / self.segs_h, v)
            vdata_values.extend([*cap.pole_vertex, *self.color, *normal, *uv])

        return self.segs_h

    # Same with Sphere
    def create_bottom_pole_triangles(self, index_offset, vdata_values, prim_indices):
        # Define the triangle vertices along the bottom pole.
        vertex_cnt = self.get_cap_edge_vertices(vdata_values)

        # Define the vertex order of the triangles along the bottom pole.
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + self.segs_h + 1
            vi3 = vi1 + self.segs_h
            prim_indices.extend((vi1, vi2, vi3))

        return vertex_cnt
    
    # Same with Sphere
    def create_top_pole_triangles(self, index_offset, prim_indices):
        # Define the vertex order of the triangles along the bottom pole.
        for i in range(self.segs_h):
            vi1 = index_offset - i
            vi2 = vi1 - self.segs_h - 1
            vi3 = vi1 - self.segs_h

            prim_indices.extend((vi1, vi2, vi3))

    def get_cap_edge_vertices(self, vdata_values):
        """Helper method to define the triangle vertices along a bottom pole.
        """
        direction = -1 if self.invert else 1
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.semi_minor_axis * -math.cos(angle_v)

        # radius_h = self.radius * math.sin(angle_v)
        rj = self.semi_major_axis * math.sin(angle_v)
        # rn = self.semi_minor_axis * math.sin(angle_v)

        _delta = 0 if self.invert else self.slice_rad
        v = angle_v / math.pi

        # height = 0 if bottom else self.semi_minor_axis

        # Define the triangle vertices along the bottom pole.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = rj * math.cos(angle_h)
            y = rj * math.sin(angle_h) * direction
            # y = rn * math.sin(angle_h) * direction
            vertex = Point3(x, y, z)

            normal = vertex.normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        """Create mantle.
        """
        n = self.segs_h + 1
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad
        vertex_cnt = 0

        # Define the mantle quad vertices.
        for i in range(1, self.segs_v - 1):
            angle_v = self.bottom_angle + self.delta_angle_v * (i + 1)
            z = self.semi_minor_axis * -math.cos(angle_v)

            # radius_h = self.radius * math.sin(angle_v)
            rj = self.semi_major_axis * math.sin(angle_v)
            # rn = self.semi_minor_axis * math.sin(angle_v)

            v = angle_v / math.pi

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                x = rj * math.cos(angle_h)
                # y = rn * math.sin(angle_h) * direction
                y = rj * math.sin(angle_h) * direction
                vertex = Point3(x, y, z)

                normal = vertex.normalized() * direction
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


    def create_bottom(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        cap = SimpleNamespace(
            z=self.bottom_height,
            segs=self.segs_bc,
            normal=Vec3(0., 0., -1.),
            # pole_vertex=Point3(0, 0, -self.radius),
            pole_vertex=Point3(0, 0, -self.semi_minor_axis),
            is_bottom=True
        )

        if self.bottom_clip > -1:
            if self.segs_bc:
                vertex_cnt += self.create_bottom_cap_triangles(vdata_values, prim_indices, cap)
                vertex_cnt += self.create_bottom_cap_quads(vertex_cnt, vdata_values, prim_indices, cap)
                index_offset += vertex_cnt
            temp_cnt = self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
            vertex_cnt += temp_cnt + self.create_bottom_edge_quads(index_offset, vdata_values, prim_indices)
        else:
            temp_cnt = self.create_cap_pole(vdata_values, cap)
            vertex_cnt += temp_cnt + self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)

        return vertex_cnt, index_offset + temp_cnt

    def create_top(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.top_height,
            segs=self.segs_tc,

            normal=Vec3(0., 0., 1.),
            # pole_vertex=Point3(0, 0, self.radius),
            pole_vertex=Point3(0, 0, self.semi_minor_axis),
            is_bottom=False
        )

        vertex_cnt = 0

        if self.top_clip < 1.:
            vertex_cnt += self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
            self.create_top_edge_quads(index_offset + vertex_cnt - 1, prim_indices)

            if self.segs_tc:
                vertex_cnt += self.create_top_cap_triangles(index_offset + vertex_cnt, vdata_values, prim_indices, cap)
                vertex_cnt += self.create_top_cap_quads(index_offset + vertex_cnt, vdata_values, prim_indices, cap)
        else:
            vertex_cnt += self.create_cap_pole(vdata_values, cap)
            self.create_top_pole_triangles(index_offset + vertex_cnt - 1, prim_indices)

        return vertex_cnt
    
    def create_slice_cap(self, index_offset, vdata_values, prim_indices):
        """Create slice caps.
        """
        direction = -1 if self.invert else 1
        total_vertex_cnt = 0
        _offset = index_offset

        for is_start in [True, False]:
            vertex_cnt = 0
            index_offset = _offset + total_vertex_cnt
            seg_vecs = []
            inner_verts = []

            if is_start:
                c_h = s_h = None
                normal = Vec3(0., -1., 0.) if self.invert else Vec3(0., 1., 0.)
            else:
                angle_h = self.delta_angle_h * self.segs_h
                c_h = math.cos(angle_h)
                s_h = -math.sin(angle_h)
                normal = Vec3(s_h, -c_h, 0.) * direction

            # if self.inner_radius:
            if self.has_inner:
                self.get_hollow_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)
                # Define the lower inner central vertex of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0]
                    # v = .5 + .5 * vertex.z / self.radius
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the main inner vertices of the slice cap quads.
                _i = 1 if self.bottom_clip > -1 else 0

                # for i in range(self.segs_v + 1):
                for i in range(self.segs_v + 1):
                    vertex = inner_verts[i + _i]

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    # u = dividend / self.radius * -direction
                    # v = .5 + .5 * vertex.z / self.radius
                    u = dividend / self.semi_major_axis * -direction
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper inner central vertex of the slice cap.
                if self.top_clip < 1.:
                    vertex = inner_verts[-1]
                    # v = .5 + .5 * vertex.z / self.radius
                    v = .5 + .5 * vertex.z / self.minor_axis
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                index_offset += vertex_cnt
            else:
                self.get_closed_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)

                vertex = inner_verts[0]
                # v = .5 + .5 * vertex.z / self.radius
                v = .5 + .5 * vertex.z / self.minor_axis
                uv = Vec2(.5, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            for i in range(self.segs_sc):
                # will be incremented when self.bottom_clip > -1 and self.top_clip < 1.
                cnt = 0

                # Define the lower central vertices of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0] + seg_vecs[0] * (i + 1)
                    # v = .5 + .5 * vertex.z / self.radius
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the main vertices of the slice cap quads.
                _idx = 1 if self.bottom_clip > -1. else 0

                for j in range(self.segs_v + 1):
                    idx = j + _idx
                    # i_v = inner_verts[idx] if self.inner_radius else inner_verts[0]
                    i_v = inner_verts[idx] if self.has_inner else inner_verts[0]
                    vertex = i_v + seg_vecs[idx] * (i + 1)

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    # u = dividend / self.radius * -direction
                    # v = .5 + .5 * vertex.z / self.radius
                    u = dividend / self.semi_major_axis * -direction
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper central vertices of the slice cap.
                if self.top_clip < 1.:
                    i_v = inner_verts[-1]
                    vertex = i_v + seg_vecs[-1] * (i + 1)
                    # v = .5 + .5 * vertex.z / self.radius
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the vertex order of the slice cap triangles.
                # if i == 0 and not self.inner_radius:
                if i == 0 and not self.has_inner:
                    for j in range(self.segs_v + cnt):
                        vi1 = index_offset
                        vi2 = vi1 + j + 1
                        vi3 = vi2 + 1

                        if is_start:
                            prim_indices.extend((vi1, vi2, vi3) if self.invert else (vi1, vi3, vi2))
                        else:
                            prim_indices.extend((vi1, vi3, vi2) if self.invert else (vi1, vi2, vi3))
                # Define the vertex order of the slice cap quads.
                else:
                    # n = cnt + (0 if self.inner_radius else 1)
                    # start = 0 if self.inner_radius else 1
                    n = cnt + (0 if self.has_inner else 1)
                    start = 0 if self.has_inner else 1

                    for j in range(start, self.segs_v + n):
                        vi1 = index_offset + j
                        # vi2 = vi1 - self.segs_v - n - (1 if self.inner_radius else 0)
                        vi2 = vi1 - self.segs_v - n - (1 if self.has_inner else 0)
                        vi3 = vi2 + 1
                        vi4 = vi1 + 1

                        if is_start:
                            prim_indices.extend((vi1, vi4, vi2) if self.invert else (vi1, vi2, vi4))
                            prim_indices.extend((vi2, vi4, vi3) if self.invert else (vi2, vi3, vi4))
                        else:
                            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi4, vi2))
                            prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi2, vi4, vi3))

                index_offset += self.segs_v + cnt + 1
            total_vertex_cnt += vertex_cnt

        return total_vertex_cnt
    
    def get_hollow_cap_inner_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        # inner_bottom_height = self.bottom_height + self.thickness
        inner_bottom_height = self.bottom_height + self.minor_thickness
        inner_bottom_angle = math.pi - math.acos(np.clip(inner_bottom_height / self.semi_inner_minor, -1.0, 1.0))

        # inner_top_height = self.top_height - self.thickness
        inner_top_height = self.top_height - self.minor_thickness
        inner_top_angle = math.acos(np.clip(inner_top_height / self.semi_inner_minor, -1.0, 1.0))
        inner_delta_angle_v = (math.pi - inner_bottom_angle - inner_top_angle) / self.segs_v

        if self.bottom_clip > -1.:
            inner_verts.append(Point3(0., 0., inner_bottom_height))
            # seg_vecs.append(Vec3(0., 0., -self.thickness / self.segs_sc))
            seg_vecs.append(Vec3(0., 0., -self.minor_thickness / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            # r = self.radius * math.sin(angle_v)
            # z = self.radius * c

            rj = self.semi_major_axis * math.sin(angle_v)
            # rn = self.semi_minor_axis * math.sin(angle_v)
            z = self.semi_minor_axis * c

            i_angle_v = inner_bottom_angle + inner_delta_angle_v * i
            i_c = -math.cos(i_angle_v)
            # i_r = self.inner_radius * math.sin(i_angle_v)
            # i_z = self.inner_radius * i_c

            i_rj = self.semi_inner_major * math.sin(i_angle_v)
            # i_rn = self.inner_minor * math.sin(i_angle_v)
            i_z = self.semi_inner_minor * i_c

            if c_h is None and s_h is None:
                # p = Point3(r, 0., z)
                # i_p = Point3(i_r, 0., i_z)
                p = Point3(rj, 0., z)
                i_p = Point3(i_rj, 0., i_z)
            else:
                # p = Point3(r * c_h, r * s_h, z)
                # i_p = Point3(i_r * c_h, i_r * s_h, i_z)
                p = Point3(rj * c_h, rj * s_h, z)
                i_p = Point3(i_rj * c_h, i_rj * s_h, i_z)

            inner_verts.append(i_p)
            seg_vecs.append((p - i_p) / self.segs_sc)

        if self.top_clip < 1.:
            inner_verts.append(Point3(0, 0, inner_top_height))
            # seg_vecs.append(Vec3(0, 0, self.thickness / self.segs_sc))
            seg_vecs.append(Vec3(0, 0, self.minor_thickness / self.segs_sc))

    def get_closed_cap_inner_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        z = (self.top_height + self.bottom_height) * .5
        h = (self.top_height - self.bottom_height) * .5
        vertex = Point3(0., 0., z)
        inner_verts.append(vertex)

        if self.bottom_clip > -1.:
            seg_vecs.append(Vec3(0., 0., -h / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            # r = self.radius * math.sin(angle_v)
            # z = self.radius * c

            rj = self.semi_major_axis * math.sin(angle_v)
            # rn = self.semi_minor_axis * math.sin(angle_v)
            z = self.semi_minor_axis * c

            if c_h is None and s_h is None:
                # p = Point3(r, 0., z)
                p = Point3(rj, 0., z)
            else:
                # p = Point3(r * c_h, r * s_h, z)
                p = Point3(rj * c_h, rj * s_h, z)

            seg_vecs.append((p - vertex) / self.segs_sc)

        if self.top_clip < 1.:
            seg_vecs.append(Vec3(0., 0., h / self.segs_sc))




    def define_variables(self):
        self.semi_minor_axis = self.minor_axis / 2
        self.semi_major_axis = self.major_axis / 2

        self.top_height = self.semi_minor_axis * self.top_clip
        self.bottom_height = self.semi_minor_axis * self.bottom_clip

        self.slice_rad = math.pi * self.slice_deg / 180.
        self.delta_angle_h = math.pi * ((360 - self.slice_deg) / 180) / self.segs_h

        # Use np.clip to prevent ValueError: math domain error raised from math.acos.
        self.bottom_angle = math.pi - math.acos(np.clip(self.bottom_height / self.semi_minor_axis, -1.0, 1.0))
        self.top_angle = math.acos(np.clip(self.top_height / self.semi_minor_axis, -1.0, 1.0))
        self.delta_angle_v = (math.pi - self.bottom_angle - self.top_angle) / self.segs_v


        self.major_thickness = self.thickness if 0 < self.thickness < self.major_axis else self.major_axis
        self.minor_thickness = self.thickness if 0 < self.thickness < self.minor_axis else self.minor_axis

        self.inner_major = self.major_axis - self.major_thickness
        self.inner_minor = self.minor_axis - self.minor_thickness
        self.has_inner = True if self.inner_major and self.inner_minor else False

        if self.has_inner:
            self.semi_inner_major = self.inner_major / 2
            self.semi_inner_minor = self.inner_minor / 2

        print('semi_minor_axis', self.semi_minor_axis, 'semi_major_axis', self.semi_major_axis)
        print('top_height', self.top_height, 'bottom_height', self.bottom_height)
        print('self.slice_rad', self.slice_rad, 'self.delta_angle_h', self.delta_angle_h)
        print('self.bottom_angle', self.bottom_angle, 'self.top_angle', self.top_angle)
        print('self.delta_angle_v', self.delta_angle_v)

        


        # self.slice_rad = math.pi * self.ring_slice_deg / 180
        # self.delta_rad = math.pi * ((360 - self.ring_slice_deg) / 180) / self.segs_c

    def get_geom_node(self):
        self.define_variables()

        # Create an outer ellipsoid.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt, index_offset = self.create_bottom(0, vdata_values, prim_indices)
        vertex_cnt += self.create_mantle_quads(index_offset, vdata_values, prim_indices)
        vertex_cnt += self.create_top(vertex_cnt, vdata_values, prim_indices)

        if self.segs_sc and self.slice_deg:
            vertex_cnt += self.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        # Create a inner ellipsoid geom node to connect it to the outer one.
        if self.has_inner:
            bottom_clip = (self.bottom_height + self.minor_thickness) / self.semi_inner_minor
            top_clip = (self.top_height - self.minor_thickness) / self.semi_inner_minor

            ellipsoid_maker = Ellipsoid(
                major_axis=self.inner_major,
                minor_axis=self.inner_minor,
                thickness=0.,
                segs_h=self.segs_h,
                segs_v=self.segs_v,
                segs_top_cap=self.segs_tc,
                segs_bottom_cap=self.segs_bc,
                segs_slice_caps=0,
                slice_deg=self.slice_deg,
                bottom_clip=bottom_clip,
                top_clip=top_clip,
                # bottom_clip=self.bottom_clip,
                # top_clip=self.top_clip,
                invert=not self.invert
            )

            geom_node = ellipsoid_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create a geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')
        return geom_node