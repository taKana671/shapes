import array
import math

from panda3d.core import Vec3, Point3, Vec2, Quat

from .create_geometry import ProceduralGeometry


class Cone(ProceduralGeometry):

    def __init__(self, height=2, segs_c=40, segs_a=2, bottom_cap=2, top_cap=2, slice_deg=0,
                 bottom_radius=1, top_radius=0, bottom_inner_radius=0, top_inner_radius=0,
                 slice_caps_radial=2, slice_cap_axial=2, invert=True):
        super().__init__()

        self.bottom_center = Point3(0, 0, 0)
        self.top_center = Point3(0, 0, height)

        self.segs_c = segs_c
        self.segs_a = segs_a
        self.segs_bc = bottom_cap
        self.segs_tc = top_cap
        self.slice_deg = slice_deg

        self.bottom_radius = bottom_radius
        self.top_radius = top_radius
        self.bottom_inner_radius = bottom_inner_radius
        self.top_inner_radius = top_inner_radius

        self.segs_sc_r = slice_caps_radial
        self.segs_sc_a = slice_cap_axial

        self.bottom_thickness = self.bottom_radius - self.bottom_inner_radius
        self.top_thickness = self.top_radius - self.top_inner_radius
        self.delta_radius = self.top_radius - self.bottom_radius
        self.height = (self.top_center - self.bottom_center).length()
        self.slice_rad = math.pi * self.slice_deg / 180
        self.delta_rad = math.pi * ((360. - self.slice_deg) / 180.) / self.segs_c

        self.color = (1, 1, 1, 1)
        self.invert = invert

    def create_bottom_cap_triangles(self, vdata_values, prim_indices):
        normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)
        direction = -1. if self.invert else 1.
        vertex_cnt = 0

        if not self.bottom_inner_radius:
            # the bottom cap triangle vertices
            uv = Vec2(.5, .5)
            vertex = Point3(0, 0, 0)

            vdata_values.extend([*vertex, *self.color, *normal, *uv])
            vertex_cnt += 1

            radius = self.bottom_radius / self.segs_bc

            for i in range(self.segs_c + 1):
                angle = self.delta_rad * i + (0. if self.invert else self.slice_rad)
                c = math.cos(angle)
                s = math.sin(angle) * direction
                vertex = Point3(radius * c, radius * s, 0)

                u = .5 + .5 * c / self.segs_bc
                v = .5 + .5 * s * -1 * direction / self.segs_bc
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            # the vertex order of the bottom cap triangles
            for i in range(1, self.segs_c + 1):
                prim_indices.extend((0, i + 1, i))

        return vertex_cnt

    def create_bottom_cap_quads(self, vdata_values, prim_indices):
        normal = Vec3(0., 0., 1.) if self.invert else Vec3(0., 0., -1.)
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        if self.segs_bc:
            n = 0 if self.bottom_inner_radius else 1

            for i in range(n, self.segs_bc + 1 - n):
                radius = self.bottom_inner_radius + self.bottom_thickness * (i + n) / self.segs_bc

                for j in range(self.segs_c + 1):
                    angle = self.delta_rad * j + (0 if self.invert else self.slice_rad)
                    c = math.cos(angle)
                    s = math.sin(angle) * direction
                    vertex = Point3(radius * c, radius * s, 0)

                    r = radius / self.bottom_radius
                    u = .5 + .5 * c * r
                    v = .5 + .5 * s * -direction * r
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

            index_offset = (self.segs_c + 1) if self.bottom_inner_radius else 1
            n = 0 if self.bottom_inner_radius else 1

            for i in range(n, self.segs_bc):
                for j in range(self.segs_c):
                    vi1 = index_offset + i * (self.segs_c + 1) + j
                    vi2 = vi1 - self.segs_c - 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

            return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        direction = -1. if self.invert else 1.
        vertex_cnt = 0

        for i in range(self.segs_a + 1):
            radius = self.bottom_radius + self.delta_radius * i / self.segs_a

            print('radius', radius)
            z = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_rad * j + (0. if self.invert else self.slice_rad)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle) * direction
                vertex = Point3(x, y, z)


                # to prevent the normal from being (0, 0, 0)
                _radius = self.bottom_radius + self.delta_radius * i / (self.segs_a + 1)
                normal = Vec3(x, y, -_radius * self.delta_radius / self.height).normalized()
                
                # normal = Vec3(x, y, -radius * self.delta_radius / self.height).normalized()
                normal *= direction
                # print(vertex, normal)
                u = j / self.segs_c
                uv = Vec2(u, v)
                
                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

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

    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices):
        normal = Vec3(0., 0., -1.) if self.invert else Vec3(0., 0., 1.)
        direction = -1. if self.invert else 1.
        vertex_cnt = 0

        if not self.top_inner_radius:
            uv = Vec2(.5, .5)
            vertex = Point3(0, 0, self.height)
            vdata_values.extend([*vertex, *self.color, *normal, *uv])
            vertex_cnt += 1

            radius = self.top_radius / self.segs_tc

            for i in range(self.segs_c + 1):
                angle = self.delta_rad * i + (0. if self.invert else self.slice_rad)
                c = math.cos(angle)
                s = math.sin(angle) * direction
                vertex = Point3(radius * c, radius * s, self.height)

                u = .5 + .5 * c / self.segs_tc
                v = .5 + .5 * s * direction / self.segs_tc
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

            # the vertex order of the bottom cap triangles
            for i in range(index_offset + 1, index_offset + self.segs_c + 1):
                prim_indices.extend((index_offset, i, i + 1))

        return vertex_cnt

    def create_top_cap_quads(self, index_offset, vdata_values, prim_indices):
        normal = Vec3(0., 0., -1.) if self.invert else Vec3(0., 0., 1.)
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        if self.top_thickness:
            n = 0 if self.top_inner_radius else 1

            for i in range(n, self.segs_tc + 1 - n):
                radius = self.top_inner_radius + self.top_thickness * (i + n) / self.segs_tc

                for j in range(self.segs_c + 1):
                    angle = self.delta_rad * j + (0 if self.invert else self.slice_rad)
                    c = math.cos(angle)
                    s = math.sin(angle) * direction
                    vertex = Point3(radius * c, radius * s, self.height)

                    r = radius / self.top_radius
                    u = .5 + .5 * c * r
                    v = .5 + .5 * s * direction * r
                    uv = Vec2(u, v)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

            index_offset += (self.segs_c + 1) if self.top_inner_radius else 1
            n = 0 if self.top_inner_radius else 1

            for i in range(n, self.segs_tc):
                for j in range(self.segs_c):
                    vi1 = index_offset + i * (self.segs_c + 1) + j
                    vi2 = vi1 - self.segs_c - 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    prim_indices.extend([*(vi1, vi3, vi2), *(vi1, vi4, vi3)])

        return vertex_cnt

    def create_slice_cap(self, index_offset, vdata_values, prim_indices):
        max_radius = max(self.bottom_radius, self.top_radius)
        delta_inner_radius = self.top_inner_radius - self.bottom_inner_radius
        direction = -1. if self.invert else 1.
        vertex_cnt = 0

        for is_start in (True, False):
            # index_offset + vertex_cnt

            if is_start:
                normal = Vec3(0, direction, 0)
            else:
                angle = self.delta_rad * self.segs_c
                c = math.cos(angle)
                s = -math.sin(angle)
                normal = Vec3(s, -c, 0.) * direction

            for i in range(self.segs_sc_a + 1):
                f = i / self.segs_sc_a
                radius = self.bottom_radius + self.delta_radius * f
                inner_radius = self.bottom_inner_radius + delta_inner_radius * f
                z = self.height * f

                # v = f
                for j in range(self.segs_sc_r + 1):
                    r = inner_radius + (radius - inner_radius) * j / self.segs_sc_r

                    vertex = Point3(r, 0., z) if is_start else Point3(r * c, r * s, z)

                    coef = .5 if is_start else -.5
                    u = .5 + coef * r / max_radius * -1 * direction
                    uv = Vec2(u, f)

                    vdata_values.extend([*vertex, *self.color, *normal, *uv])
                    vertex_cnt += 1

            for i in range(self.segs_sc_a):
                for j in range(self.segs_sc_r):
                    vi1 = index_offset + j
                    vi2 = vi1 + self.segs_sc_r + 1
                    vi3 = vi1 + 1
                    vi4 = vi2 + 1

                    if is_start:
                        prim_indices.extend((vi1, vi3, vi2) if self.invert else (vi1, vi2, vi3))
                        prim_indices.extend((vi2, vi3, vi4) if self.invert else (vi2, vi4, vi3))
                    else:
                        prim_indices.extend((vi1, vi2, vi3) if self.invert else (vi1, vi3, vi2))
                        prim_indices.extend((vi2, vi4, vi3) if self.invert else (vi2, vi3, vi4))
                index_offset += self.segs_sc_r + 1
            index_offset += self.segs_sc_r + 1

        return vertex_cnt



    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_bottom_cap_triangles(vdata_values, prim_indices)
        vertex_cnt += self.create_bottom_cap_quads(vdata_values, prim_indices)

        vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)
        sub_total = vertex_cnt
        vertex_cnt += self.create_top_cap_triangles(sub_total, vdata_values, prim_indices)
        vertex_cnt += self.create_top_cap_quads(sub_total, vdata_values, prim_indices)

        if self.segs_sc_r and self.segs_sc_a and self.slice_deg:  #???
            vertex_cnt += self.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'cone')

        if self.bottom_inner_radius or self.top_inner_radius:
            self.bottom_radius = self.bottom_inner_radius
            self.top_radius = self.top_inner_radius
            self.delta_radius = self.top_radius - self.bottom_radius
            # ↑の変数を変えてしまうと、Coneインスタンスから2つ以上の同じconeモデルが作れなくなってしまう。
            # create_mantle_quadsメソッド内で何とかすること（torusも同じ）
            vdata_values = array.array('f', [])
            prim_indices = array.array('H', [])
            vertex_cnt = 0

            vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)

        return geom_node