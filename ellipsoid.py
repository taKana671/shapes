import array
import math
from types import SimpleNamespace

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from .sphere import Sphere


class Ellipsoid(Sphere):
    """Creates a ellipsoid model.
       Args:
            major_axis (float): the longest diameter; must be more than zero
            minor_axis (float): the shortest diameter; must be more than zero
            thickness (floar): the radial offset of major and minor axes; must be 0 < thickness < minor_axis
            segs_h(int): subdivisions along horizontal circles; minimum = 3
            segs_v (int): subdivisions along vertical semicircles; minimum = 2
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0
            segs_slice_caps (int): radial subdivisions of the slice caps; minimum = 0 (no caps)
            slice_deg (float): the angle of the pie slice removed from the ellipsoid, in degrees; must be in [0., 360.]
            bottom_clip (float):
                relative height of the plane that cuts off a bottom part of the ellipsoid;
                must be in [-1., 1.] range;
                -1. (no clipping)
            top_clip (float):
                relative height of the plane that cuts off a top part of the ellipsoid;
                must be in [bottom_clip, 1.] range;
                1. (no clipping);
            invert (bool): whether or not the geometry should be rendered inside-out; default is False
    """

    def __init__(self, major_axis=2, minor_axis=1, thickness=0, segs_h=40, segs_v=40,
                 segs_top_cap=3, segs_bottom_cap=3, segs_slice_caps=2, slice_deg=0,
                 bottom_clip=-1., top_clip=1., invert=False):
        super().__init__(
            segs_h=segs_h,
            segs_v=segs_v,
            segs_bottom_cap=segs_bottom_cap,
            segs_top_cap=segs_top_cap,
            segs_slice_caps=segs_slice_caps,
            slice_deg=slice_deg,
            bottom_clip=bottom_clip,
            top_clip=top_clip,
            invert=invert
        )
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.thickness = thickness

    def get_cap_axis(self, cap):
        """Helper method to get the length of the major_axis and minor_axis
           of the surface cut horizontally at the top or bottom.
        """
        k = self.major_axis / self.minor_axis
        minor_h = math.sqrt(self.semi_minor_axis ** 2 - cap.z ** 2)
        major_h = minor_h * k
        return major_h, minor_h

    def create_cap_edge_vertices(self, vdata_values, cap):
        """Helper method to define the edge vertices of a bottom or top.
        """
        major_h, _ = self.get_cap_axis(cap)
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad
        v = (math.pi - math.acos(cap.z / self.semi_minor_axis)) / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = major_h * math.cos(angle_h)
            y = major_h * math.sin(angle_h) * direction
            vertex = Point3(x, y, cap.z)

            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)
            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def get_cap_quad_vertices(self, vdata_values, cap):
        """Helper method to define the quad vertices of a bottom or top cap.
        """
        major_h, _ = self.get_cap_axis(cap)
        direction = -1 if self.invert else 1
        vertex_cnt = 0
        normal = cap.normal * -1 if self.invert else cap.normal
        _delta = 0 if self.invert else self.slice_rad

        # Define cap quad vertices.
        for i in range(1, cap.segs):
            rj = major_h * (i + 1) / cap.segs

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction
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
        major_h, _ = self.get_cap_axis(cap)
        direction = -1 if self.invert else 1
        normal = cap.normal * -1 if self.invert else cap.normal

        vertex = Point3(0., 0., cap.z)
        uv = Vec2(.5, .5)
        vdata_values.extend([*vertex, *self.color, *normal, *uv])

        rj = major_h / cap.segs
        _delta = 0 if self.invert else self.slice_rad

        # Define the cap triangle vertices.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            vertex = Point3(rj * c, rj * s, cap.z)

            _direction = -direction if cap.is_bottom else direction
            u = .5 + .5 * c / cap.segs
            v = .5 + .5 * s * _direction / cap.segs
            uv = Vec2(u, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 2

    def get_cap_edge_vertices(self, vdata_values):
        """Helper method to define the triangle vertices along a bottom pole.
        """
        direction = -1 if self.invert else 1
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.semi_minor_axis * -math.cos(angle_v)
        rj = self.semi_major_axis * math.sin(angle_v)

        _delta = 0 if self.invert else self.slice_rad
        v = angle_v / math.pi

        # Define the triangle vertices along the bottom pole.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = rj * math.cos(angle_h)
            y = rj * math.sin(angle_h) * direction
            vertex = Point3(x, y, z)

            normal = vertex.normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_bottom(self, index_offset, vdata_values, prim_indices):
        """Create bottom.
        """
        cap = SimpleNamespace(
            z=self.bottom_height,
            segs=self.segs_bc,
            normal=Vec3(0., 0., -1.),
            pole_vertex=Point3(0, 0, -self.semi_minor_axis),
            is_bottom=True
        )

        vertex_cnt, index_offset = self.define_bottom_cap(
            index_offset, vdata_values, prim_indices, cap)
        return vertex_cnt, index_offset

    def create_top(self, index_offset, vdata_values, prim_indices):
        """Create top.
        """
        cap = SimpleNamespace(
            z=self.top_height,
            segs=self.segs_tc,
            normal=Vec3(0., 0., 1.),
            pole_vertex=Point3(0, 0, self.semi_minor_axis),
            is_bottom=False
        )

        vertex_cnt = self.define_top_cap(
            index_offset, vdata_values, prim_indices, cap)
        return vertex_cnt

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
            rj = self.semi_major_axis * math.sin(angle_v)
            v = angle_v / math.pi

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                x = rj * math.cos(angle_h)
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

            if self.has_inner:
                self.get_thickness_cap_vertices(seg_vecs, inner_verts, c_h, s_h)

                # Define the lower inner central vertex of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0]
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the main inner vertices of the slice cap quads.
                _i = 1 if self.bottom_clip > -1 else 0

                for i in range(self.segs_v + 1):
                    vertex = inner_verts[i + _i]

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.semi_major_axis * -direction
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper inner central vertex of the slice cap.
                if self.top_clip < 1.:
                    vertex = inner_verts[-1]
                    v = .5 + .5 * vertex.z / self.minor_axis
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                index_offset += vertex_cnt
            else:
                self.get_cap_vertices(seg_vecs, inner_verts, c_h, s_h)

                vertex = inner_verts[0]
                v = .5 + .5 * vertex.z / self.semi_minor_axis
                uv = Vec2(.5, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            for i in range(self.segs_sc):
                # will be incremented when self.bottom_clip > -1 and self.top_clip < 1.
                cnt = 0

                # Define the lower central vertices of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0] + seg_vecs[0] * (i + 1)
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the main vertices of the slice cap quads.
                _idx = 1 if self.bottom_clip > -1. else 0

                for j in range(self.segs_v + 1):
                    idx = j + _idx
                    i_v = inner_verts[idx] if self.has_inner else inner_verts[0]
                    vertex = i_v + seg_vecs[idx] * (i + 1)

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.semi_major_axis * -direction
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper central vertices of the slice cap.
                if self.top_clip < 1.:
                    i_v = inner_verts[-1]
                    vertex = i_v + seg_vecs[-1] * (i + 1)
                    v = .5 + .5 * vertex.z / self.semi_minor_axis
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the vertex order of the slice cap triangles.
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
                    n = cnt + (0 if self.has_inner else 1)
                    start = 0 if self.has_inner else 1

                    for j in range(start, self.segs_v + n):
                        vi1 = index_offset + j
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

    def get_thickness_cap_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        """Get the vertices of the sliced surface of a ellipsoid with a double structure
           consisting of an inner and outer ellipsoids.
        """
        inner_bottom_height = self.bottom_height + self.thickness
        inner_bottom_angle = math.pi - math.acos(np.clip(inner_bottom_height / self.semi_inner_minor, -1.0, 1.0))

        inner_top_height = self.top_height - self.thickness
        inner_top_angle = math.acos(np.clip(inner_top_height / self.semi_inner_minor, -1.0, 1.0))
        inner_delta_angle_v = (math.pi - inner_bottom_angle - inner_top_angle) / self.segs_v

        if self.bottom_clip > -1.:
            inner_verts.append(Point3(0., 0., inner_bottom_height))
            seg_vecs.append(Vec3(0., 0., -self.thickness / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            rj = self.semi_major_axis * math.sin(angle_v)
            z = self.semi_minor_axis * c

            i_angle_v = inner_bottom_angle + inner_delta_angle_v * i
            i_c = -math.cos(i_angle_v)
            i_rj = self.semi_inner_major * math.sin(i_angle_v)
            i_z = self.semi_inner_minor * i_c

            if c_h is None and s_h is None:
                p = Point3(rj, 0., z)
                i_p = Point3(i_rj, 0., i_z)
            else:
                p = Point3(rj * c_h, rj * s_h, z)
                i_p = Point3(i_rj * c_h, i_rj * s_h, i_z)

            inner_verts.append(i_p)
            seg_vecs.append((p - i_p) / self.segs_sc)

        if self.top_clip < 1.:
            inner_verts.append(Point3(0, 0, inner_top_height))
            seg_vecs.append(Vec3(0, 0, self.thickness / self.segs_sc))

    def get_cap_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        """Get the vertices of the sliced surface of a ellipsoid.
        """
        z = (self.top_height + self.bottom_height) * .5
        h = (self.top_height - self.bottom_height) * .5

        vertex = Point3(0., 0., z)
        inner_verts.append(vertex)

        if self.bottom_clip > -1.:
            seg_vecs.append(Vec3(0., 0., -h / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            rj = self.semi_major_axis * math.sin(angle_v)
            z = self.semi_minor_axis * c

            if c_h is None and s_h is None:
                p = Point3(rj, 0., z)
            else:
                p = Point3(rj * c_h, rj * s_h, z)

            seg_vecs.append((p - vertex) / self.segs_sc)

        if self.top_clip < 1.:
            seg_vecs.append(Vec3(0., 0., h / self.segs_sc))

    def define_inner_details(self):
        """If an inner ellipsoid can be created, define the necessary variables.
        """
        self.inner_major = None
        self.inner_minor = None
        self.has_inner = False

        if self.thickness > 0:
            if (inner_major := self.major_axis - self.thickness * 2) > 0:
                if (self.top_height - self.bottom_height) * 0.5 > self.major_axis - inner_major > 0:
                    self.inner_major = inner_major

            if (inner_minor := self.minor_axis - self.thickness * 2) > 0:
                self.inner_minor = inner_minor

            if self.inner_major and self.inner_minor:
                self.has_inner = True
                self.semi_inner_major = self.inner_major / 2
                self.semi_inner_minor = self.inner_minor / 2

    def define_variables(self):
        self.semi_minor_axis = self.minor_axis / 2
        self.semi_major_axis = self.major_axis / 2
        self.top_height = self.semi_minor_axis * self.top_clip
        self.bottom_height = self.semi_minor_axis * self.bottom_clip

        self.slice_rad = math.pi * self.slice_deg / 180.
        self.delta_angle_h = math.pi * ((360 - self.slice_deg) / 180) / self.segs_h

        # Use np.clip to prevent math domain error raised from math.acos.
        self.bottom_angle = math.pi - math.acos(np.clip(self.bottom_height / self.semi_minor_axis, -1.0, 1.0))
        self.top_angle = math.acos(np.clip(self.top_height / self.semi_minor_axis, -1.0, 1.0))
        self.delta_angle_v = (math.pi - self.bottom_angle - self.top_angle) / self.segs_v

        self.define_inner_details()

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
            bottom_clip = (self.bottom_height + self.thickness) / self.semi_inner_minor
            top_clip = (self.top_height - self.thickness) / self.semi_inner_minor

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
                invert=not self.invert
            )

            geom_node = ellipsoid_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create a geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'ellipsoid')
        return geom_node