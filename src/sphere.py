import array
import math
import copy
from types import SimpleNamespace

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from .create_geometry import ProceduralGeometry


class Sphere(ProceduralGeometry):
    """Create a sphere model.
       Args:
            radius (int): the radius of sphere;
            segs_s (int): the number of surface subdivisions;
            segs_h(int): subdivisions along horizontal circles (or circle arcs, if sliced); minimum = 3
            bottom_cap (int): radial subdivisions of the bottom clipping cap; 0 (no cap)
    """

    def __init__(self, radius=1., inner_radius=0.8, segs=40, segs_h=40, segs_v=40, bottom_cap=2, top_cap=2, slice_caps=2,
                 slice_deg=120, bottom_clip=-.5, top_clip=1., invert=False):
        super().__init__()
        self.radius = radius
        self.inner_radius = inner_radius
        self.segs = segs
        self.segs_h = segs_h
        self.segs_v = segs_v
        self.segs_bc = bottom_cap
        self.segs_tc = top_cap
        self.segs_sc = slice_caps
        self.bottom_clip = bottom_clip
        self.top_clip = top_clip

        self.slice_deg = slice_deg
        self.invert = invert
        self.color = (1, 1, 1, 1)

    def create_bottom_cap_triangles(self, vdata_values, prim_indices):
        # radius_h = math.sqrt(self.radius ** 2 - self.bottom_height ** 2)
        # n = 0 if self.invert else self.slice_rad
        # direction = -1 if self.invert else 1

        # vertex = Point3(0., 0., self.bottom_height)
        # normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)
        # uv = Vec2(.5, .5)
        # vdata_values.extend([*vertex, *self.color, *normal, *uv])
        # # vertex_cnt += 1

        # # the bottom cap triangle vertices
        # r = radius_h / self.segs_bc

        # for i in range(self.segs_h + 1):
        #     angle_h = self.delta_angle_h * i + n
        #     c = math.cos(angle_h)
        #     s = math.sin(angle_h) * direction
        #     vertex = Point3(r * c, r * s, self.bottom_height)

        #     u = .5 + .5 * c / self.segs_bc
        #     v = .5 + .5 * s * -1 * direction / self.segs_bc
        #     uv = Vec2(u, v)

        #     vdata_values.extend([*vertex, *self.color, *normal, *uv])
        #     # vertex_cnt += 1
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values)

        # the vertex order of the bottom cap triangles
        for i in range(1, self.segs_h + 1):
            prim_indices.extend((0, i + 1, i))

        return vertex_cnt
        # return self.segs_h + 2

    def create_bottom_cap_quads(self, index_offset, vdata_values, prim_indices):
        # radius_h = math.sqrt(self.radius ** 2 - self.bottom_height ** 2)
        # n = 0 if self.invert else self.slice_rad
        # normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)
        # direction = -1 if self.invert else 1
        # vertex_cnt = 0

        # # the bottom cap quad vertices
        # for i in range(1, self.segs_bc):
        #     r = radius_h * (i + 1) / self.segs_bc

        #     for j in range(self.segs_h + 1):
        #         angle_h = self.delta_angle_h * j + n
        #         c = math.cos(angle_h)
        #         s = math.sin(angle_h) * direction
        #         vertex = Point3(r * c, r * s, self.bottom_height)

        #         _r = (i + 1) / self.segs_bc
        #         u = .5 + .5 * c * _r
        #         v = .5 + .5 * s * -1 * direction * _r
        #         uv = Vec2(u, v)

        #         vdata_values.extend([*vertex, *self.color, *normal, *uv])

        #     vertex_cnt += self.segs_h + 1
        vertex_cnt = self.get_cap_quad_vertices(vdata_values)

        # the vertex order of the bottom cap quads
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

    # def create_bottom_edge_vertices(self, vdata_values, prim_indices):
    def create_cap_edge_vertices(self, vdata_values, prim_indices, z):
        # the bottom edge vertices
        # v = (math.pi - math.acos(self.bottom_height / self.radius)) / math.pi
        v = (math.pi - math.acos(z / self.radius)) / math.pi
        # radius_h = math.sqrt(self.radius ** 2 - self.bottom_height ** 2)
        radius_h = math.sqrt(self.radius ** 2 - z ** 2)
        direction = -1 if self.invert else 1
        n = 0 if self.invert else self.slice_rad

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + n
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            # vertex = Point3(x, y, self.bottom_height)
            # normal = Vec3(x, y, self.bottom_height).normalized() * direction
            vertex = Point3(x, y, z)
            normal = Vec3(x, y, z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    # def create_bottom_pole(self, vdata_values, prim_indices):
        # normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.) 
        # vertex = Point3(0., 0., -self.radius)

        # # the bottom pole triangle vertices
        # for i in range(self.segs_h):
        #     uv = Vec2(i / self.segs_h, 0)
        #     vdata_values.extend([*vertex, *self.color, *normal, *uv])

        # return self.segs_h
    def create_cap_pole(self, vdata_values, prim_indices, bottom=True):
        direction = 1 if bottom else -1
        normal = Vec3(0., 0., 1. if self.invert else -1) * direction 
        vertex = Point3(0., 0., -self.radius) * direction
        v = 0 if bottom else 1

        # the bottom pole triangle vertices
        for i in range(self.segs_h):
            uv = Vec2(i / self.segs_h, v)
            # print(vertex)
            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h

    def create_vertices_around(self, vdata_values):
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.radius * -math.cos(angle_v)
        # n = 0 if self.invert else self.slice_rad
        direction = -1 if self.invert else 1
        # normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)

        radius_h = self.radius * math.sin(angle_v)
        v = angle_v / math.pi

        # the triangle vertices along the bottom pole
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + (0 if self.invert else self.slice_rad)
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            vertex = Point3(x, y, z)
            normal = vertex.normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_bottom_pole_triangles(self, index_offset, vdata_values, prim_indices):
        # the triangle vertices along the bottom pole
        vertex_cnt = self.create_vertices_around(vdata_values)

        # the vertex order of the triangles along the bottom pole
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + self.segs_h + 1
            vi3 = vi1 + self.segs_h
            prim_indices.extend((vi1, vi2, vi3))

        return vertex_cnt

    def create_bottom_edge_quads(self, index_offset, vdata_values, prim_indices):
        # the vertices along the bottom cap
        vertex_cnt = self.create_vertices_around(vdata_values)

        # the vertex order of the polygon along the bottom pole or cap
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + 1
            vi3 = vi2 + self.segs_h
            vi4 = vi3 + 1

            prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi1, vi2, vi3))
            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi2, vi4, vi3))

        return vertex_cnt

    def create_bottom(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        index_offset = 0

        if self.bottom_clip > -1:
            if self.segs_bc:  # and -self.radius < z < self.radius: ←バリデーションするので、この条件はいらない。
                vertex_cnt += self.create_bottom_cap_triangles(vdata_values, prim_indices)
                vertex_cnt += self.create_bottom_cap_quads(vertex_cnt, vdata_values, prim_indices)
                index_offset += vertex_cnt
            # temp_cnt = self.create_bottom_edge_vertices(vdata_values, prim_indices)
            temp_cnt = self.create_cap_edge_vertices(vdata_values, prim_indices, self.bottom_height)
            vertex_cnt += temp_cnt + self.create_bottom_edge_quads(index_offset, vdata_values, prim_indices)
        else:
            # temp_cnt = self.create_bottom_pole(vdata_values, prim_indices)
            temp_cnt = self.create_cap_pole(vdata_values, prim_indices)
            vertex_cnt += temp_cnt + self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)
        
        return vertex_cnt, index_offset + temp_cnt

    def create_top(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
        # index_offset -= 1

        if self.top_clip < 1.:
            vertex_cnt += self.create_cap_edge_vertices(vdata_values, prim_indices, self.top_height)
            self.create_top_edge_quads(index_offset + vertex_cnt - 1, prim_indices)

            if self.segs_tc:
                vertex_cnt += self.create_top_cap_triangles(index_offset + vertex_cnt, vdata_values, prim_indices)
                vertex_cnt += self.create_top_cap_quads(index_offset + vertex_cnt, vdata_values, prim_indices)
        else:
            vertex_cnt += self.create_cap_pole(vdata_values, prim_indices, bottom=False)
            self.create_top_pole_triangles(index_offset + vertex_cnt - 1, prim_indices)

        return vertex_cnt

    def create_top_edge_quads(self, index_offset, prim_indices):
        index_offset -= (self.segs_h - 1) + self.segs_h + 2

        # the vertex order of the polygon along the top cap
        for i in range(self.segs_h):
            vi1 = i + index_offset
            vi2 = vi1 + 1
            vi3 = vi2 + self.segs_h
            vi4 = vi3 + 1

            prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
            prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi2, vi4, vi3))

    def create_top_pole_triangles(self, index_offset, prim_indices):
        # the triangle vertices along the bottom pole
        # vertex_cnt = self.create_vertices_around(vdata_values)

        # the vertex order of the triangles along the bottom pole
        for i in range(self.segs_h):
            vi1 = index_offset - i
            vi2 = vi1 - self.segs_h - 1
            vi3 = vi1 - self.segs_h
            # print((vi1, vi2, vi3))
            prim_indices.extend((vi1, vi2, vi3))
    
    def get_cap_triangle_vertices(self, vdata_values, bottom=True):
        z = self.bottom_height if bottom else self.top_height
        radius_h = math.sqrt(self.radius ** 2 - z ** 2)
        segs_cap = self.segs_bc if bottom else self.segs_tc
        
        direction = -1 if self.invert else 1
        normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)

        if not bottom:
            normal *= -1

        vertex = Point3(0., 0., z)
        uv = Vec2(.5, .5)
        vdata_values.extend([*vertex, *self.color, *normal, *uv])

        # the bottom cap triangle vertices
        r = radius_h / segs_cap

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + (0 if self.invert else self.slice_rad)
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            vertex = Point3(r * c, r * s, z)

            _direction = -direction if bottom else direction
            u = .5 + .5 * c / segs_cap
            v = .5 + .5 * s * _direction / segs_cap
            uv = Vec2(u, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 2

    def get_cap_quad_vertices(self, vdata_values, bottom=True):
        z = self.bottom_height if bottom else self.top_height
        radius_h = math.sqrt(self.radius ** 2 - z ** 2)
        segs_cap = self.segs_bc if bottom else self.segs_tc

        direction = -1 if self.invert else 1
        normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)

        if not bottom:
            normal *= -1

        vertex_cnt = 0

        for i in range(1, segs_cap):
            r = radius_h * (i + 1) / segs_cap

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + (0 if self.invert else self.slice_rad)
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction
                vertex = Point3(r * c, r * s, z)

                _r = (i + 1) / segs_cap
                _direction = direction * -1 if bottom else direction
                u = .5 + .5 * c * _r
                v = .5 + .5 * s * _direction * _r
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            vertex_cnt += self.segs_h + 1

        return vertex_cnt
    
    
    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices):
        # the bottom cap triangle vertices
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values, bottom=False)

        # the vertex order of the bottom cap triangles
        for i in range(index_offset + 1, index_offset + self.segs_h + 1):
            prim_indices.extend((index_offset, i, i + 1))

        return vertex_cnt

    def create_top_cap_quads(self, index_offset, vdata_values, prim_indices):
        # the bottom cap quad vertices
        vertex_cnt = self.get_cap_quad_vertices(vdata_values, bottom=False)

        # the vertex order of the bottom cap quads
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

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        n = self.segs_h + 1
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # the mantle quad vertices
        for i in range(1, self.segs_v - 1):
            angle_v = self.bottom_angle + self.delta_angle_v * (i + 1)
            z = self.radius * -math.cos(angle_v)
            radius_h = self.radius * math.sin(angle_v)
            v = angle_v / math.pi

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + (0 if self.invert else self.slice_rad)
                x = radius_h * math.cos(angle_h)
                y = radius_h * math.sin(angle_h) * direction
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

    def get_hollow_cap_inner_vertices(self, seg_vecs, inner_verts, c_h=None, s_h=None):
        inner_bottom_height = self.bottom_height + self.thickness

        # cos range from -1 <= x <= 1; if out of range, ValueError: math domain error occur.

        # np.clip(inner_bottom_height / 0.5, -1.0, 1.0)
        # inner_bottom_angle = math.pi - math.acos(np.clip(inner_bottom_height / self.inner_radius, -1.0, 1.0))
        inner_bottom_angle = math.pi - math.acos(inner_bottom_height / self.inner_radius)
        inner_top_height = self.top_height - self.thickness
        inner_top_angle = math.acos(inner_top_height / self.inner_radius)
        # inner_top_angle = math.pi - math.acos(np.clip(inner_top_height / self.inner_radius, -1.0, 1.0))
        inner_delta_angle_v = (math.pi - inner_bottom_angle - inner_top_angle) / self.segs_v

        if self.bottom_clip > -1.:
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

            if c_h is not None and s_h is not None:
                p = Point3(r * c_h, r * s_h, z)
                i_p = Point3(i_r * c_h, i_r * s_h, i_z)
            else:
                p = Point3(r, 0., z)
                i_p = Point3(i_r, 0., i_z)

            inner_verts.append(i_p)
            seg_vecs.append((p - i_p) / self.segs_sc)

        if self.top_clip < 1.:
            inner_verts.append(Point3(0, 0, inner_top_height))
            seg_vecs.append(Vec3(0, 0, self.thickness / self.segs_sc))

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
            r = self.radius * math.sin(angle_v)
            z = self.radius * c

            if c_h is not None and s_h is not None:
                p = Point3(r * c_h, r * s_h, z)
            else:
                p = Point3(r, 0., z)

            seg_vecs.append((p - vertex) / self.segs_sc)

        if self.top_clip < 1.:
            seg_vecs.append(Vec3(0., 0., h / self.segs_sc))

    def create_slice_cap(self, index_offset, vdata_values, prim_indices):
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

            if self.inner_radius:
                self.get_hollow_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)
            else:
                self.get_closed_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)
                inner_vert = inner_verts[0]

            if self.inner_radius:
                # the lower inner central vertex of the slice cap
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0]
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # the main inner vertices of the slice cap quads
                _i = 1 if self.bottom_clip > -1 else 0

                for i in range(self.segs_v + 1):
                    vertex = inner_verts[i + _i]

                    if is_start:
                        u = .5 + .5 * vertex.x / self.radius * -direction
                    else:
                        u = .5 - .5 * Vec3(vertex.xy, 0).length() / self.radius * -direction

                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # the upper inner central vertex of the slice cap
                if self.top_clip < 1.:
                    vertex = inner_verts[-1]
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                index_offset += vertex_cnt
            else:
                v = .5 + .5 * inner_vert.z / self.radius
                uv = Vec2(.5, v)
                vdata_values.extend([*inner_vert, *self.color, *normal, *uv])
                vertex_cnt += 1

            for i in range(self.segs_sc):
                n = 0

                # the lower central vertices of the slice cap
                if self.bottom_clip > -1.:
                    i_v = inner_verts[0] if self.inner_radius else inner_vert
                    vertex = i_v + seg_vecs[0] * (i + 1)

                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    n += 1

                # the main vertices of the slice cap quads
                for j in range(self.segs_v + 1):
                    idx = j + (1 if self.bottom_clip > -1. else 0)
                    i_v = inner_verts[idx] if self.inner_radius else inner_vert
                    vertex = i_v + seg_vecs[idx] * (i + 1)

                    if is_start:
                        u = .5 + .5 * vertex.x / self.radius * -direction
                    else:
                        u = .5 - .5 * Vec3(vertex.xy, 0).length() / self.radius * -direction

                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # the upper central vertices of the slice cap
                if self.top_clip < 1.:
                    i_v = inner_verts[-1] if self.inner_radius else inner_vert
                    vertex = i_v + seg_vecs[-1] * (i + 1)

                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    n += 1

                # the vertex order of the slice cap triangles
                if i == 0 and not self.inner_radius:
                    for j in range(self.segs_v + n):
                        vi1 = index_offset
                        vi2 = vi1 + j + 1
                        vi3 = vi2 + 1

                        if is_start:
                            prim_indices.extend((vi1, vi2, vi3) if self.invert else (vi1, vi3, vi2))
                        else:
                            prim_indices.extend((vi1, vi3, vi2) if self.invert else (vi1, vi2, vi3))
                # the vertex order of the slice cap quads
                else:
                    n += 0 if self.inner_radius else 1
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

                index_offset += self.segs_v + 1 + n
            total_vertex_cnt += vertex_cnt

        return total_vertex_cnt

    def get_geom_node(self):
        self.bottom_height = self.radius * self.bottom_clip
        self.top_height = self.radius * self.top_clip
        self.slice_rad = math.pi * self.slice_deg / 180.
        self.delta_angle_h = math.pi * ((360 - self.slice_deg) / 180) / self.segs_h
        self.bottom_angle = math.pi - math.acos(self.bottom_height / self.radius)
        self.top_angle = math.acos(self.top_height / self.radius)
        self.delta_angle_v = (math.pi - self.bottom_angle - self.top_angle) / self.segs_v
        self.thickness = self.radius - self.inner_radius

        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt, index_offset = self.create_bottom(0, vdata_values, prim_indices)
        vertex_cnt += self.create_mantle_quads(index_offset, vdata_values, prim_indices)
        vertex_cnt += self.create_top(vertex_cnt, vdata_values, prim_indices)

        if self.segs_sc and self.slice_deg and self.thickness:
            vertex_cnt += self.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')

        # if self.thickness:
        if self.inner_radius:
            self.radius = self.inner_radius
            self.inner_radius = 0

            self.bottom_height = self.radius * self.bottom_clip
            self.top_height = self.radius * self.top_clip
            self.slice_rad = math.pi * self.slice_deg / 180.
            self.delta_angle_h = math.pi * ((360 - self.slice_deg) / 180) / self.segs_h
            self.bottom_angle = math.pi - math.acos(self.bottom_height / self.radius)
            self.top_angle = math.acos(self.top_height / self.radius)
            self.delta_angle_v = (math.pi - self.bottom_angle - self.top_angle) / self.segs_v
            self.thickness = self.radius - self.inner_radius

            vdata_values = array.array('f', [])
            prim_indices = array.array('H', [])

            vertex_cnt, index_offset = self.create_bottom(0, vdata_values, prim_indices)
            vertex_cnt += self.create_mantle_quads(index_offset, vdata_values, prim_indices)
            vertex_cnt += self.create_top(vertex_cnt, vdata_values, prim_indices)

            # Connect the inner sphere to outer sphere.
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)

        return geom_node

    def create_bottom_cap_triangles_old(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        if self.bottom_clip > -1:
            z = self.bottom_height
            radius_h = math.sqrt(self.radius ** 2 - z ** 2)
            n = 0 if self.invert else self.slice_rad
            direction = -1 if self.invert else 1

            if self.segs_bc:  # and -self.radius < z < self.radius: ←バリデーションするので、この条件はいらない。
                # the bottom cap triangle vertices
                vertex = Point3(0., 0., z)
                normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)
                uv = Vec2(.5, .5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

                r = radius_h / self.segs_bc

                for i in range(self.segs_h + 1):
                    angle_h = self.delta_angle_h * i + n
                    c = math.cos(angle_h)
                    s = math.sin(angle_h) * direction
                    vertex = Point3(r * c, r * s, z)

                    u = .5 + .5 * c / self.segs_bc
                    v = .5 + .5 * s * -1 * direction / self.segs_bc
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # the vertex order of the bottom cap triangles
                for i in range(1, self.segs_h + 1):
                    prim_indices.extend((0, i + 1, i))

                # the bottom cap quad vertices
                for i in range(1, self.segs_bc):
                    r = radius_h * (i + 1) / self.segs_bc

                    for j in range(self.segs_h + 1):
                        angle_h = self.delta_angle_h * j + n
                        c = math.cos(angle_h)
                        s = math.sin(angle_h) * direction
                        vertex = Point3(r * c, r * s, z)

                        _r = (i + 1) / self.segs_bc
                        u = .5 + .5 * c * _r
                        v = .5 + .5 * s * -1 * direction * _r
                        uv = Vec2(u, v)

                        vdata_values.extend([*vertex, *self.color, *normal, *uv])
                        vertex_cnt += 1

                # the vertex order of the bottom cap quads
                index_offset += self.segs_h + 2

                for i in range(1, self.segs_bc):
                    for j in range(self.segs_h):
                        vi1 = index_offset + j
                        vi2 = vi1 - self.segs_h - 1
                        vi3 = vi2 + 1
                        vi4 = vi1 + 1
                        prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi1, vi2, vi3))
                        prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi1, vi3, vi4))
                    index_offset += self.segs_h + 1

            # the bottom edge vertices
            v = (math.pi - math.acos(z / self.radius)) / math.pi

            for i in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * i + n
                x = radius_h * math.cos(angle_h)
                y = radius_h * math.sin(angle_h) * direction
                vertex = Point3(x, y, z)
                normal = Vec3(x, y, z).normalized() * direction
                uv = Vec2(i / self.segs_h, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        else:
            # 点だけつくる。model_displayには何もできない
            normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.) 
            vertex = Point3(0., 0., -self.radius)

            for i in range(self.segs_h):
                uv = Vec2(i / self.segs_h, 0)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        
        # the vertices along the bottom pole or cap　　self.bottom_clip == -1の場合は頂点の周りのっ三角形だけ作られる
        # self.bottom_clip > -1の場合はcapの周りに、マントルの一番下の段が作られる。
        angle_v = self.bottom_angle + self.delta_angle_v
        z = self.radius * -math.cos(angle_v)
        n = 0 if self.invert else self.slice_rad
        direction = -1 if self.invert else 1
        normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)

        radius_h = self.radius * math.sin(angle_v)
        v = angle_v / math.pi

        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + n
            x = radius_h * math.cos(angle_h)
            y = radius_h * math.sin(angle_h) * direction
            vertex = Point3(x, y, z)
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])
            vertex_cnt += 1

        # the vertex order of the polygon along the bottom pole or cap
        if self.bottom_clip > -1.:
            for i in range(0, self.segs_h):
                vi1 = i + index_offset
                vi2 = vi1 + 1
                vi3 = vi2 + self.segs_h
                vi4 = vi3 + 1

                prim_indices.extend((vi1, vi4, vi3) if self.invert else (vi1, vi2, vi3))
                prim_indices.extend((vi1, vi2, vi4) if self.invert else (vi2, vi4, vi3))

            index_offset += self.segs_h + 1

        else:
            for i in range(self.segs_h):
                vi1 = i + index_offset
                vi2 = vi1 + self.segs_h + 1
                vi3 = vi1 + self.segs_h
                prim_indices.extend((vi1, vi2, vi3))

            index_offset += self.segs_h

        return vertex_cnt



# class Sphere(ProceduralGeometry):
#     """Create a sphere model.
#        Args:
#             radius (int): the radius of sphere;
#             segs_s (int): the number of surface subdivisions;
#     """

#     def __init__(self, radius=1.5, segs_s=40):
#         super().__init__()
#         self.radius = radius
#         self.segs_s = segs_s
#         self.color = (1, 1, 1, 1)

#     def create_bottom_pole(self, vdata_values, prim_indices):
#         # the bottom pole vertices
#         normal = Vec3(0.0, 0.0, -1.0)
#         vertex = Point3(0.0, 0.0, -self.radius)

#         for i in range(self.segs_s):
#             u = i / self.segs_s
#             vdata_values.extend(vertex)
#             vdata_values.extend(self.color)
#             vdata_values.extend(normal)
#             vdata_values.extend((u, 0.0))

#             # the vertex order of the pole vertices
#             prim_indices.extend((i, i + self.segs_s + 1, i + self.segs_s))

#         return self.segs_s

#     def create_quads(self, index_offset, vdata_values, prim_indices):
#         delta_angle = 2 * math.pi / self.segs_s
#         vertex_cnt = 0

#         # the quad vertices
#         for i in range((self.segs_s - 2) // 2):
#             angle_v = delta_angle * (i + 1)
#             radius_h = self.radius * math.sin(angle_v)
#             z = self.radius * -math.cos(angle_v)
#             v = 2.0 * (i + 1) / self.segs_s

#             for j in range(self.segs_s + 1):
#                 angle = delta_angle * j
#                 c = math.cos(angle)
#                 s = math.sin(angle)
#                 x = radius_h * c
#                 y = radius_h * s
#                 normal = Vec3(x, y, z).normalized()
#                 u = j / self.segs_s

#                 vdata_values.extend((x, y, z))
#                 vdata_values.extend(self.color)
#                 vdata_values.extend(normal)
#                 vdata_values.extend((u, v))

#                 # the vertex order of the quad vertices
#                 if i > 0 and j <= self.segs_s:
#                     px = i * (self.segs_s + 1) + j + index_offset
#                     prim_indices.extend((px, px - self.segs_s - 1, px - self.segs_s))
#                     prim_indices.extend((px, px - self.segs_s, px + 1))

#             vertex_cnt += self.segs_s + 1

#         return vertex_cnt

#     def create_top_pole(self, index_offset, vdata_values, prim_indices):
#         vertex = Point3(0.0, 0.0, self.radius)
#         normal = Vec3(0.0, 0.0, 1.0)

#         # the top pole vertices
#         for i in range(self.segs_s):
#             u = i / self.segs_s
#             vdata_values.extend(vertex)
#             vdata_values.extend(self.color)
#             vdata_values.extend(normal)
#             vdata_values.extend((u, 1.0))

#             # the vertex order of the top pole vertices
#             x = i + index_offset
#             prim_indices.extend((x, x + 1, x + self.segs_s + 1))

#         return self.segs_s

#     def get_geom_node(self):
#         vdata_values = array.array('f', [])
#         prim_indices = array.array('H', [])
#         vertex_cnt = 0

#         # create vertices of the bottom pole, quads, and top pole
#         vertex_cnt += self.create_bottom_pole(vdata_values, prim_indices)
#         vertex_cnt += self.create_quads(vertex_cnt, vdata_values, prim_indices)
#         vertex_cnt += self.create_top_pole(vertex_cnt - self.segs_s - 1, vdata_values, prim_indices)

#         geom_node = self.create_geom_node(
#             vertex_cnt, vdata_values, prim_indices, 'sphere')

#         return geom_node


class QuickSphere(ProceduralGeometry):
    """Create a sphere model from icosahedron quickly.
        Arges:
            divnum (int): the number of divisions of one triangle; cannot be negative;
    """

    def __init__(self, divnum=3):
        super().__init__()
        self.divnum = divnum
        self.color = (1, 1, 1, 1)

    def calc_midpoints(self, face):
        """face (list): list of Vec3; having 3 elements like below.
           [(0, 1), (1, 2), (2, 0)]
        """
        for i, pt1 in enumerate(face):
            j = i + 1 if i < len(face) - 1 else 0
            pt2 = face[j]
            mid_pt = (pt1 + pt2) / 2

            yield mid_pt

    def subdivide(self, face, divnum=0):
        if divnum == self.divnum:
            yield face
        else:
            midpoints = [pt for pt in self.calc_midpoints(face)]

            for i, vertex in enumerate(face):
                j = len(face) - 1 if i == 0 else i - 1
                face = [vertex, midpoints[i], midpoints[j]]
                yield from self.subdivide(face, divnum + 1)
            yield from self.subdivide(midpoints, divnum + 1)

    def load_obj(self, file_path):
        vertices = []
        faces = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                li = [val for val in line.split(' ') if val]

                match li[0]:
                    case 'v':
                        vertices.append(tuple(float(val) for val in li[1:]))

                    case 'f':
                        faces.append(tuple(int(val) - 1 for val in li[1:]))

        return vertices, faces

    def get_geom_node(self):
        vertices, faces = self.load_obj('src/objs/icosahedron.obj')
        vertex_cnt = 4 ** self.divnum * 20 * 3
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        start = 0

        for face in faces:
            face_verts = [Vec3(vertices[n]) for n in face]
            for subdiv_face in self.subdivide(face_verts):
                for vert in subdiv_face:
                    normal = vert.normalized()
                    vdata_values.extend(normal)
                    vdata_values.extend(self.color)
                    vdata_values.extend(normal)
                    vdata_values.extend((0, 0))

                indices = (start, start + 1, start + 2)
                prim_indices.extend(indices)
                start += 3

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')

        return geom_node
