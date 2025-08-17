import array
import math
from types import SimpleNamespace

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from .cylinder import Cylinder
from .sphere import Sphere


class Capsule(Cylinder):
    """Creates a capsule model.
       Args:
            radius (float): the radius of the capsule; must be more than zero.
            inner_radius (float): must be 0 < inner_radius < radius; for example, if radius is 1.0, inner radius is 0.8.
            height (float): length of the capsule mantle; capsule total height is this height + radius * 2
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1.
            ring_slice_deg (int): the angle of the pie slice removed from the capsule, in degrees; must be from 0 to 360.
            top_hemisphere (bool): if True, a top hemisphere is created.
            bottom_hemisphere (bool): if True, a bottom hemisphere is created.
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum = 0.
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum=0.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, radius=1., inner_radius=0., height=1., segs_c=40, segs_a=2, ring_slice_deg=0, slice_caps_radial=2,
                 slice_caps_axial=2, top_hemisphere=True, bottom_hemisphere=True, invert=False):
        segs_cap = 2 if radius - inner_radius <= 4 else int(radius / 2)

        super().__init__(
            radius=radius,
            inner_radius=inner_radius,
            height=height,
            segs_c=segs_c,
            segs_a=segs_a,
            segs_top_cap=0 if top_hemisphere else segs_cap,
            segs_bottom_cap=0 if bottom_hemisphere else segs_cap,
            ring_slice_deg=ring_slice_deg,
            slice_caps_radial=slice_caps_radial,
            slice_caps_axial=slice_caps_axial,
            invert=invert
        )

        self.top_hemisphere = top_hemisphere
        self.bottom_hemisphere = bottom_hemisphere

    def create_hemisphere(self, vertex_cnt, vdata_values, prim_indices,
                          center, bottom_clip=-1, top_clip=1):
        hemi = CapsuleHemisphere(
            center=center,
            radius=self.radius,
            inner_radius=self.inner_radius,
            segs_h=self.segs_c,
            segs_v=int(self.segs_c / 2),
            slice_deg=self.ring_slice_deg,
            segs_slice_caps=self.segs_sc_r,
            top_clip=top_clip,
            bottom_clip=bottom_clip,
            invert=self.invert
        )

        cnt, index_offset = hemi.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += cnt
        vertex_cnt += hemi.create_mantle_quads(index_offset, vdata_values, prim_indices)
        vertex_cnt += hemi.create_top(vertex_cnt, vdata_values, prim_indices)

        if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
            vertex_cnt += hemi.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):
        if self.bottom_hemisphere:
            center = Point3(0, 0, 0)
            vertex_cnt = self.create_hemisphere(
                vertex_cnt, vdata_values, prim_indices, center, top_clip=0
            )

        return vertex_cnt

    def create_mantle(self, vertex_cnt, vdata_values, prim_indices):
        vertex_cnt = self.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
            vertex_cnt += self.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_top(self, vertex_cnt, vdata_values, prim_indices):
        if self.top_hemisphere:
            center = Point3(0, 0, self.height)
            vertex_cnt = self.create_hemisphere(
                vertex_cnt, vdata_values, prim_indices, center, bottom_clip=0
            )

        return vertex_cnt

    def create_slice_caps(self, vertex_cnt, vdata_values, prim_indices):
        if self.bottom_hemisphere:
            vertex_cnt += self.b_hemi.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        vertex_cnt += self.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        if self.top_hemisphere:
            vertex_cnt += self.t_hemi.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def get_geom_node(self):
        self.define_variables()

        # Create an outer capusule.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_mantle(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_top(vertex_cnt, vdata_values, prim_indices)

        # Create an inner capsule to connect to the outer one.
        if self.inner_radius:
            maker = Capsule(
                radius=self.inner_radius,
                inner_radius=0,
                height=self.height,
                segs_c=self.segs_c,
                segs_a=self.segs_a,
                top_hemisphere=self.top_hemisphere,
                bottom_hemisphere=self.bottom_hemisphere,
                ring_slice_deg=self.ring_slice_deg,
                slice_caps_radial=0,
                slice_caps_axial=0,
                invert=not self.invert
            )

            maker.segs_tc = 0
            maker.segs_bc = 0

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the capsule geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'capsule')
        return geom_node


class CapsuleHemisphere(Sphere):

    def __init__(self, center, radius=1., inner_radius=0, segs_h=40, segs_v=20,
                 segs_slice_caps=2, slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        super().__init__(
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

    def create_cap_edge_vertices(self, vdata_values, prim_indices, cap):
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

    def create_bottom(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.bottom_height,
            normal=Vec3(0., 0., -1.),
            pole_vertex=Point3(0, 0, -self.radius) + self.center,
            is_bottom=True
        )
        vertex_cnt = 0

        if self.bottom_clip > -1:
            offset_cnt = self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
            vertex_cnt += self.create_bottom_edge_quads(index_offset, vdata_values, prim_indices)
        else:
            offset_cnt = self.create_cap_pole(vdata_values, cap)
            vertex_cnt += self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)

        return vertex_cnt + offset_cnt, index_offset + offset_cnt

    def create_top(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.top_height,
            normal=Vec3(0., 0., 1.),
            pole_vertex=Point3(0, 0, self.radius) + self.center,
            is_bottom=False
        )
        vertex_cnt = 0

        if self.top_clip < 1.:
            vertex_cnt += self.create_cap_edge_vertices(vdata_values, prim_indices, cap)
            self.create_top_edge_quads(index_offset + vertex_cnt - 1, prim_indices)
        else:
            vertex_cnt += self.create_cap_pole(vdata_values, cap)
            self.create_top_pole_triangles(index_offset + vertex_cnt - 1, prim_indices)

        return vertex_cnt

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