import array
import math
from types import SimpleNamespace

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from .create_geometry import ProceduralGeometry


class Sphere(ProceduralGeometry):
    """Create a sphere model.
       Args:
            radius (float): the radius of sphere; more than 0;
            inner_radius (float): the radius of the inner sphere; cannot be negative; must be in [0., radius]
            segs_h(int): subdivisions along horizontal circles; minimum = 3
            segs_v (int): subdivisions along vertical semicircles; minimum = 2
            segs_bottom_cap (int): radial subdivisions of the bottom clipping cap; minimum = 0 (no cap)
            segs_top_cap (int): radial subdivisions of the top clipping cap; minimum = 0 (no cap)
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

    def __init__(self, radius=1., inner_radius=0, segs_h=40, segs_v=40,
                 segs_bottom_cap=2, segs_top_cap=2, segs_slice_caps=2,
                 slice_deg=0, bottom_clip=-1., top_clip=1., invert=False):
        super().__init__()
        self.radius = radius
        self.inner_radius = inner_radius
        self.segs_h = segs_h
        self.segs_v = segs_v
        self.segs_tc = segs_top_cap
        self.segs_bc = segs_bottom_cap
        self.segs_sc = segs_slice_caps
        self.top_clip = top_clip
        self.bottom_clip = bottom_clip
        self.slice_deg = slice_deg
        self.invert = invert

    def get_cap_triangle_vertices(self, vdata_values, cap):
        radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        direction = -1 if self.invert else 1
        normal = cap.normal * -1 if self.invert else cap.normal
        vertex = Point3(0., 0., cap.z)

        uv = Vec2(.5, .5)
        vdata_values.extend([*vertex, *self.color, *normal, *uv])

        r = radius_h / cap.segs
        _delta = 0 if self.invert else self.slice_rad

        # Define the bottom cap triangle vertices.
        for i in range(self.segs_h + 1):
            angle_h = self.delta_angle_h * i + _delta
            c = math.cos(angle_h)
            s = math.sin(angle_h) * direction
            vertex = Point3(r * c, r * s, cap.z)

            _direction = -direction if cap.is_bottom else direction
            u = .5 + .5 * c / cap.segs
            v = .5 + .5 * s * _direction / cap.segs
            uv = Vec2(u, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 2

    def get_cap_quad_vertices(self, vdata_values, cap):
        radius_h = math.sqrt(self.radius ** 2 - cap.z ** 2)
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        normal = cap.normal * -1 if self.invert else cap.normal
        _delta = 0 if self.invert else self.slice_rad

        # Define the bottom cap quad vertices.
        for i in range(1, cap.segs):
            r = radius_h * (i + 1) / cap.segs

            for j in range(self.segs_h + 1):
                angle_h = self.delta_angle_h * j + _delta
                c = math.cos(angle_h)
                s = math.sin(angle_h) * direction
                vertex = Point3(r * c, r * s, cap.z)

                _r = (i + 1) / cap.segs
                _direction = direction * -1 if cap.is_bottom else direction
                u = .5 + .5 * c * _r
                v = .5 + .5 * s * _direction * _r
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            vertex_cnt += self.segs_h + 1

        return vertex_cnt

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
            vertex = Point3(x, y, z)
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
            vertex = Point3(x, y, cap.z)
            normal = Vec3(x, y, cap.z).normalized() * direction
            uv = Vec2(i / self.segs_h, v)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        return self.segs_h + 1

    def create_cap_pole(self, vdata_values, prim_indices, cap):
        normal = cap.normal * -1 if self.invert else cap.normal
        v = 0 if cap.is_bottom else 1

        # Define the pole triangle vertices.
        for i in range(self.segs_h):
            uv = Vec2(i / self.segs_h, v)
            vdata_values.extend([*cap.pole_vertex, *self.color, *normal, *uv])

        return self.segs_h

    def create_bottom_cap_triangles(self, vdata_values, prim_indices, cap):
        # Define the bottom cap triangle vertices.
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap triangles.
        for i in range(1, self.segs_h + 1):
            prim_indices.extend((0, i + 1, i))

        return vertex_cnt

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

    def create_bottom(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0
       
        cap = SimpleNamespace(
            z=self.bottom_height,
            segs=self.segs_bc,
            normal=Vec3(0., 0., -1.),
            pole_vertex=Point3(0, 0, -self.radius),
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
            temp_cnt = self.create_cap_pole(vdata_values, prim_indices, cap)
            vertex_cnt += temp_cnt + self.create_bottom_pole_triangles(index_offset, vdata_values, prim_indices)

        return vertex_cnt, index_offset + temp_cnt

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

    def create_top_pole_triangles(self, index_offset, prim_indices):
        # Define the vertex order of the triangles along the bottom pole.
        for i in range(self.segs_h):
            vi1 = index_offset - i
            vi2 = vi1 - self.segs_h - 1
            vi3 = vi1 - self.segs_h

            prim_indices.extend((vi1, vi2, vi3))

    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices, cap):
        # Define the bottom cap triangle vertices.
        vertex_cnt = self.get_cap_triangle_vertices(vdata_values, cap)

        # Define the vertex order of the bottom cap triangles.
        for i in range(index_offset + 1, index_offset + self.segs_h + 1):
            prim_indices.extend((index_offset, i, i + 1))

        return vertex_cnt

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

    def create_top(self, index_offset, vdata_values, prim_indices):
        cap = SimpleNamespace(
            z=self.top_height,
            segs=self.segs_tc,
            normal=Vec3(0., 0., 1.),
            pole_vertex=Point3(0, 0, self.radius),
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
            vertex_cnt += self.create_cap_pole(vdata_values, prim_indices, cap)
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
        inner_bottom_angle = math.pi - math.acos(np.clip(inner_bottom_height / self.inner_radius, -1.0, 1.0))

        inner_top_height = self.top_height - self.thickness
        inner_top_angle = math.acos(np.clip(inner_top_height / self.inner_radius, -1.0, 1.0))
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

            if c_h is None and s_h is None:
                p = Point3(r, 0., z)
                i_p = Point3(i_r, 0., i_z)
            else:
                p = Point3(r * c_h, r * s_h, z)
                i_p = Point3(i_r * c_h, i_r * s_h, i_z)

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

            if c_h is None and s_h is None:
                p = Point3(r, 0., z)
            else:
                p = Point3(r * c_h, r * s_h, z)

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

                # Define the lower inner central vertex of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0]
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the main inner vertices of the slice cap quads.
                _i = 1 if self.bottom_clip > -1 else 0

                for i in range(self.segs_v + 1):
                    vertex = inner_verts[i + _i]

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.radius * -direction
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper inner central vertex of the slice cap.
                if self.top_clip < 1.:
                    vertex = inner_verts[-1]
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)
                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                index_offset += vertex_cnt
            else:
                self.get_closed_cap_inner_vertices(seg_vecs, inner_verts, c_h, s_h)

                vertex = inner_verts[0]
                v = .5 + .5 * vertex.z / self.radius
                uv = Vec2(.5, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            for i in range(self.segs_sc):
                # will be incremented when self.bottom_clip > -1 and self.top_clip < 1.
                cnt = 0

                # Define the lower central vertices of the slice cap.
                if self.bottom_clip > -1.:
                    vertex = inner_verts[0] + seg_vecs[0] * (i + 1)
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(.5, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1
                    cnt += 1

                # Define the main vertices of the slice cap quads.
                _idx = 1 if self.bottom_clip > -1. else 0

                for j in range(self.segs_v + 1):
                    idx = j + _idx
                    i_v = inner_verts[idx] if self.inner_radius else inner_verts[0]
                    vertex = i_v + seg_vecs[idx] * (i + 1)

                    dividend = .5 + .5 * vertex.x if is_start else .5 - .5 * Vec3(vertex.xy, 0).length()
                    u = dividend / self.radius * -direction
                    v = .5 + .5 * vertex.z / self.radius
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

                # Define the upper central vertices of the slice cap.
                if self.top_clip < 1.:
                    i_v = inner_verts[-1]
                    vertex = i_v + seg_vecs[-1] * (i + 1)
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

    def define_variables(self):
        self.top_height = self.radius * self.top_clip
        self.bottom_height = self.radius * self.bottom_clip

        if self.inner_radius:
            if (self.top_height - self.bottom_height) * 0.5 <= self.radius - self.inner_radius:
                self.inner_radius = 0

        self.thickness = self.radius - self.inner_radius
        self.slice_rad = math.pi * self.slice_deg / 180.
        self.delta_angle_h = math.pi * ((360 - self.slice_deg) / 180) / self.segs_h

        # Use np.clip to prevent ValueError: math domain error raised from math.acos.
        self.bottom_angle = math.pi - math.acos(np.clip(self.bottom_height / self.radius, -1.0, 1.0))
        self.top_angle = math.acos(np.clip(self.top_height / self.radius, -1.0, 1.0))
        self.delta_angle_v = (math.pi - self.bottom_angle - self.top_angle) / self.segs_v

    def get_geom_node(self):
        # Calculate required values to define variables.
        self.define_variables()

        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        # Create an outer sphere.
        vertex_cnt, index_offset = self.create_bottom(0, vdata_values, prim_indices)
        vertex_cnt += self.create_mantle_quads(index_offset, vdata_values, prim_indices)
        vertex_cnt += self.create_top(vertex_cnt, vdata_values, prim_indices)

        if self.segs_sc and self.slice_deg:
            vertex_cnt += self.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        # Create a geom node of the inner sphere to connect it to the outer sphere.
        if self.inner_radius > 0:
            bottom_clip = (self.bottom_height + self.thickness) / self.inner_radius
            top_clip = (self.top_height - self.thickness) / self.inner_radius

            sphere_maker = Sphere(self.inner_radius, 0, self.segs_h, self.segs_v,
                                  self.segs_bc, self.segs_tc, 0,
                                  self.slice_deg, bottom_clip, top_clip, not self.invert)

            geom_node = sphere_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'sphere')
        return geom_node


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

    def load_obj(self):
        vertices = [
            [-0.52573111, -0.72360680, 0.44721360],
            [-0.85065081, 0.27639320, 0.44721360],
            [-0.00000000, 0.89442719, 0.44721360],
            [0.85065081, 0.27639320, 0.44721360],
            [0.52573111, -0.72360680, 0.44721360],
            [0.00000000, -0.89442719, -0.44721360],
            [-0.85065081, -0.27639320, -0.44721360],
            [-0.52573111, 0.72360680, -0.44721360],
            [0.52573111, 0.72360680, -0.44721360],
            [0.85065081, -0.27639320, -0.44721360],
            [0.00000000, 0.00000000, 1.00000000],
            [-0.00000000, 0.00000000, -1.00000000]
        ]

        faces = [
            [0, 1, 6], [0, 6, 5], [0, 5, 4], [0, 4, 10],
            [0, 10, 1], [1, 2, 7], [1, 7, 6], [1, 10, 2],
            [2, 3, 8], [2, 8, 7], [2, 10, 3], [3, 4, 9],
            [3, 9, 8], [3, 10, 4], [4, 5, 9], [5, 6, 11],
            [5, 11, 9], [6, 7, 11], [7, 8, 11], [8, 9, 11]
        ]

        return vertices, faces

    def get_geom_node(self):
        vertices, faces = self.load_obj()
        vertex_cnt = 4 ** self.divnum * 20 * 3
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        start = 0

        for face in faces:
            face_verts = [Vec3(*vertices[n]) for n in face]
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
