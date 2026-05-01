import math

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from .hemisphere import BasicHemisphere


class CapsuleHemisphere(BasicHemisphere):

    """A class that creates the hemispheres at both ends of the capsule

        Args:
            center (panda3d.core.Point3): the center of a hemisphere
            radius (float): the radius of hemisphere; greater than 0; default is 1.
            inner_radius (float):
                the radius of the inner sphere.
                0 <= inner_radius <= radius; default is 0.
            segs_h(int): subdivisions along horizontal circles; minimum = 3; default is 40.
            segs_v (int): subdivisions along vertical circles; minimum = 2; default is 20.
            segs_slice_caps (int): radial subdivisions of the slice caps; minimum = 0 (no caps); default is 2.
            slice_deg (float):
                the angle of the pie slice removed from the hemisphere, in degrees.
                0 <= slice_deg <= 360; default is 0.
            bottom_clip (float): relative height of the plane that cuts off a bottom part of the hemisphere.
            top_clip (float): relative height of the plane that cuts off a top part of the hemisphere.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, center, radius=1., inner_radius=0, segs_h=40, segs_v=20,
                 segs_slice_caps=2, slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        self.color = (1, 1, 1, 1)
        self.radius = radius
        self.inner_radius = inner_radius
        self.segs_h = segs_h
        self.segs_v = segs_v
        self.segs_sc = segs_slice_caps
        self.top_clip = top_clip
        self.bottom_clip = bottom_clip
        self.slice_deg = slice_deg
        self.invert = invert

        self.center = center
        self.define_variables()

    def get_cap_edge_vertices(self, vdata_values):
        direction = -1 if self.invert else 1
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.radius * -math.cos(angle_v)

        radius_h = self.radius * math.sin(angle_v)
        _delta = 0 if self.invert else self.slice_rad
        v = angle_v / math.pi

        # Define the triangle vertices along the bottom pole.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction

            vertex = Point3(x, y, z) + self.center  # add center.
            normal = Vec3(x, y, z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_cap_edge_vertices(self, vdata_values, cap):
        radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad

        v = (math.pi - math.acos(cap.z / self.radius)) / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            vertex = Point3(x, y, cap.z) + self.center   # add center.
            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        n = self.segs_h + 1
        direction = -1 if self.invert else 1
        _delta = 0 if self.invert else self.slice_rad
        vertex_cnt = 0

        # Define the mantle quad vertices.
        for i in range(1, self.segs_v - 1):
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

    def get_hollow_cap_inner_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        inner_bottom_height = self.bottom_height
        inner_bottom_angle = math.pi - math.acos(np.clip(inner_bottom_height / self.inner_radius, -1.0, 1.0))

        inner_top_height = self.top_height
        inner_top_angle = math.acos(np.clip(inner_top_height / self.inner_radius, -1.0, 1.0))
        inner_delta_angle_v = (math.pi - inner_bottom_angle - inner_top_angle) / self.segs_v

        if self._bottom_clip > -1.:
            inner_verts.append(Point3(0., 0., inner_bottom_height))
            seg_vecs.append(Vec3(0., 0., -self.thickness / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            r = self.radius * math.sin(angle_v)
            z = self.radius * c
            i_angle_v = inner_bottom_angle + inner_delta_angle_v * i
            i_c = -math.cos(i_angle_v)
            i_r = self.inner_radius * math.sin(i_angle_v)
            i_z = self.inner_radius * i_c

            if c_h is None and s_h is None:
                p = Point3(r, 0., z)
                i_p = Point3(i_r, 0., i_z)
            else:
                p = Point3(r * c_h, r * s_h, z)
                i_p = Point3(i_r * c_h, i_r * s_h, i_z)

            inner_verts.append(i_p)
            seg_vecs.append((p - i_p) / self.segs_sc)

        if self._top_clip < 1.:
            inner_verts.append(Point3(0, 0, inner_top_height))
            seg_vecs.append(Vec3(0, 0, self.thickness / self.segs_sc))

    def get_closed_cap_inner_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        z = (self.top_height + self.bottom_height) * .5
        h = (self.top_height - self.bottom_height) * .5
        vertex = Point3(0., 0., z)
        inner_verts.append(vertex)

        if self._bottom_clip > -1.:
            seg_vecs.append(Vec3(0., 0., -h / self.segs_sc))

        for i in range(self.segs_v + 1):
            angle_v = self.bottom_angle + self.delta_angle_v * i
            c = -math.cos(angle_v)
            r = self.radius * math.sin(angle_v)
            z = self.radius * c

            if c_h is None and s_h is None:
                p = Point3(r, 0., z)
            else:
                p = Point3(r * c_h, r * s_h, z)

            seg_vecs.append((p - vertex) / self.segs_sc)

        if self._top_clip < 1.:
            seg_vecs.append(Vec3(0., 0., h / self.segs_sc))

    def create_slice_cap(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        total_vertex_cnt = 0
        _offset = index_offset

        self._bottom_clip = -1 if self.inner_radius > 0 else self.bottom_clip
        self._top_clip = 1 if self.inner_radius > 0 else self.top_clip

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

            if self.inner_radius:
                self.get_hollow_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)

                if self._bottom_clip > -1.:
                    vertex = inner_verts[0] + self.center  # add center.
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the main inner vertices of the slice cap quads.
                _i = 1 if self._bottom_clip > -1 else 0

                for i in range(self.segs_v + 1):
                    vertex = inner_verts[i + _i] + self.center  # add center.
                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.radius * -direction
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper inner central vertex of the slice cap.
                if self._top_clip < 1.:
                    vertex = inner_verts[-1] + self.center  # add center.
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                index_offset += vertex_cnt
            else:
                self.get_closed_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)

                vertex = inner_verts[0] + self.center  # add center
                v = .5 + .5 * vertex.z / self.radius
                uv = Vec2(.5, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            for i in range(self.segs_sc):
                # will be incremented when self.bottom_clip > -1 and self.top_clip < 1.
                cnt = 0

                # Define the lower central vertices of the slice cap.
                if self._bottom_clip > -1.:
                    vertex = inner_verts[0] + seg_vecs[0] * (i + 1) + self.center  # add center.
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the main vertices of the slice cap quads.
                _idx = 1 if self._bottom_clip > -1. else 0

                for j in range(self.segs_v + 1):
                    idx = j + _idx
                    i_v = inner_verts[idx] if self.inner_radius else inner_verts[0]
                    vertex = i_v + seg_vecs[idx] * (i + 1) + self.center  # Add center.

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.radius * -direction
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper central vertices of the slice cap.
                if self._top_clip < 1.:
                    i_v = inner_verts[-1]
                    vertex = i_v + seg_vecs[-1] * (i + 1) + self.center  # Add center.
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the vertex order of the slice cap triangles.
                if i == 0 and not self.inner_radius:
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
                    n = cnt + (0 if self.inner_radius else 1)
                    start = 0 if self.inner_radius else 1

                    for j in range(start, self.segs_v + n):
                        vi1 = index_offset + j
                        vi2 = vi1 - self.segs_v - n - (1 if self.inner_radius else 0)
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