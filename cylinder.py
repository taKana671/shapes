import array
import math

from panda3d.core import Vec3, Point3, Vec2
from panda3d.core import NodePath
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexArrayFormat

from .create_geometry import ProcedualGeometry


class CylinderModel(ProcedualGeometry):

    def __init__(self, radius=10, segs_c=40, height=1, segs_a=2, segs_cap=3):
        self.radius = radius
        self.segs_c = segs_c
        self.height = height
        self.segs_a = segs_a
        self.segs_cap = segs_cap
        self.is_inverted = False

        self.color = (1, 1, 1, 1)
        self.delta_angle = 2 * math.pi / self.segs_c

        geom_node = self.get_geom_node()
        super().__init__(geom_node)

    def create_bottom_cap_triangles(self, vdata_values, prim_indices):
        normal = Vec3(0, 0, -1)
        r = self.radius / self.segs_cap

        # bottom cap center and triangle vertices
        for i in range(self.segs_c):
            if i == 0:
                vertex = Point3(0, 0, 0)
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            angle = self.delta_angle * i
            c = math.cos(angle)
            s = math.sin(angle)
            x = r * c
            y = r * s
            u = 0.5 + c * 0.5 / self.segs_cap
            v = 0.5 - s * 0.5 / self.segs_cap

            vertex = Point3(x, y, 0)
            uv = Vec2(u, v)
            vdata_values.extend([*vertex, *self.color, *normal, *uv])

        # the vertex order of the bottom cap triangles
        for i in range(1, self.segs_c):
            prim_indices.extend((0, i + 1, i))
        prim_indices.extend((0, 1, self.segs_c))

        return self.segs_c + 1

    def create_bottom_cap_quads(self, vdata_values, prim_indices):
        normal = Vec3(0, 0, -1)
        vertex_cnt = 0

        # bottom cap quad vertices
        for i in range(1, self.segs_cap):
            r = self.radius * (i + 1) / self.segs_cap

            for j in range(self.segs_c):
                angle = self.delta_angle * j
                c = math.cos(angle)
                s = math.sin(angle)
                x = r * c
                y = r * s
                u = 0.5 + c * 0.5 * (i + 1) / self.segs_cap
                v = 0.5 - s * 0.5 * (i + 1) / self.segs_cap

                vertex = Point3(x, y, 0.0)
                uv = Vec2(u, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            vertex_cnt += self.segs_c

            # the vertex order of the bottom cap quads
            for k in range(self.segs_c - 1):
                vi1 = 1 + i * self.segs_c + k
                vi2 = vi1 - self.segs_c
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

            vi1 = 1 + i * self.segs_c
            vi2 = vi1 - self.segs_c
            vi3 = vi2 + self.segs_c - 1
            vi4 = vi1 + self.segs_c - 1
            prim_indices.extend([*(vi1, vi3, vi2), *(vi1, vi4, vi3)])

        return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        vertex_count = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a

            for j in range(self.segs_c + 1):
                angle = self.delta_angle * j
                x = self.radius * math.cos(angle)
                y = self.radius * math.sin(angle)
                normal = Vec3(x, y, 0.0).normalized()
                u = j / self.segs_c

                vertex = Point3(x, y, z)
                uv = Vec2(u, v)
                vdata_values.extend([*vertex, *self.color, *normal, *uv])

            vertex_count += self.segs_c + 1

            # the vertex order of the mantle mantle quads
            if i > 0:
                for k in range(self.segs_c):
                    vi1 = index_offset + i * (self.segs_c + 1) + k
                    vi2 = vi1 - self.segs_c - 1
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1

                    prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])
                    prim_indices.extend((vi1, vi3, vi4))

        return vertex_count

    def create_top_cap_quads(self, index_offset, vdata_values, prim_indices):
        normal = Vec3(0, 0, 1)
        vertex_count = 0

        for i in range(self.segs_cap, 0, -1):
            r = self.radius * i / self.segs_cap
            vertex = Point3(0, 0, self.height)

            for j in range(self.segs_c):
                angle = self.delta_angle * j
                c = math.cos(angle)
                s = math.sin(angle)
                vertex.x = r * c
                vertex.y = r * s
                u = 0.5 + c * 0.5 * i / self.segs_cap
                v = 0.5 + s * 0.5 * i / self.segs_cap

                vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])

            vertex_count += self.segs_c

            if i < self.segs_cap:
                for k in range(self.segs_c - 1):
                    vi1 = index_offset + 1 + (self.segs_cap - i) * self.segs_c + k
                    vi2 = vi1 - self.segs_c
                    vi3 = vi2 + 1
                    vi4 = vi1 + 1
                    prim_indices.extend([*(vi1, vi3, vi2), *(vi1, vi4, vi3)])

                vi1 = index_offset + 1 + (self.segs_cap - i) * self.segs_c
                vi2 = vi1 - self.segs_c
                vi3 = vi2 + self.segs_c - 1
                vi4 = vi1 + self.segs_c - 1
                prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

        return vertex_count

    def create_top_cap_triangles(self, index_offset, vdata_values, prim_indices):
        normal = Vec3(0, 0, 1)
        vertex = Point3(0, 0, self.height)
        uv = Vec2(0.5, 0.5)
        vdata_values.extend([*vertex, *self.color, *normal, *uv])

        vertex_count = 1
        index_offset += self.segs_c * (self.segs_cap - 1) + 1

        for i in range(index_offset + 1, index_offset + self.segs_c):
            prim_indices.extend((index_offset + self.segs_c, i - 1, i))
        prim_indices.extend((index_offset + self.segs_c, index_offset, index_offset + self.segs_c - 1))

        return vertex_count

    def get_geom_node(self):
        fmt = self.create_format()
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_bottom_cap_triangles(vdata_values, prim_indices)
        vertex_cnt += self.create_bottom_cap_quads(vdata_values, prim_indices)
        vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)

        offset = vertex_cnt - 1
        vertex_cnt += self.create_top_cap_quads(offset, vdata_values, prim_indices)
        vertex_cnt += self.create_top_cap_triangles(offset, vdata_values, prim_indices)

        nd = self.create_geom_node(fmt, vertex_cnt, vdata_values, prim_indices, 'cylinder')
        return nd
