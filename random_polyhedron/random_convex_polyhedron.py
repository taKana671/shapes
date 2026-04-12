import array
import math

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from ..create_geometry import ProceduralGeometry
from ..cylinder import BasicCylinder


polyhedron_faces = [
    np.array([
        [0.39444913, 1., 0.82813675],
        [0.33434778, 1., 0.72031574],
        [0.40758976, 0.95513772, 0.79719745]
    ]),
    np.array([
        [0.13772716, 1., 0.],
        [0.11089399, 0.97587645, 0.],
        [0.11710056, 1., 0.09077217]
    ]),
    np.array([
        [1., 1., 0.61061996],
        [1., 0.35694058, 0.05879407],
        [0.88551684, 0.23917097, 0.0218984],
        [0.49889851, 0.85842498, 0.76998793],
        [0.49708892, 1., 0.89249134]
    ]),
    np.array([
        [1., 0.35694058, 0.05879407],
        [1., 0.36675212, 0.],
        [0.88017536, 0.23704328, 0.],
        [0.88551684, 0.23917097, 0.0218984]
    ]),
    np.array([
        [0.49889851, 0.85842498, 0.76998793],
        [0.88551684, 0.23917097, 0.0218984],
        [0.88017536, 0.23704328, 0.],
        [0.11089399, 0.97587645, 0.],
        [0.11710056, 1., 0.09077217],
        [0.33434778, 1., 0.72031574],
        [0.40758976, 0.95513772, 0.79719745]
    ]),
    np.array([
        [0.49708892, 1., 0.89249134],
        [0.49889851, 0.85842498, 0.76998793],
        [0.40758976, 0.95513772, 0.79719745],
        [0.39444913, 1., 0.82813675]
    ]),
    np.array([
        [1., 1., 0.],
        [1., 1., 0.61061996],
        [1., 0.35694058, 0.05879407],
        [1., 0.36675212, 0.]
    ]),
    np.array([
        [1., 1., 0.],
        [1., 1., 0.61061996],
        [0.49708892, 1., 0.89249134],
        [0.39444913, 1., 0.82813675],
        [0.33434778, 1., 0.72031574],
        [0.11710056, 1., 0.09077217],
        [0.13772716, 1., 0.]
    ]),
    np.array([
        [0.88017536, 0.23704328, 0.],
        [1., 0.36675212, 0.],
        [1., 1., 0.],
        [0.13772716, 1., 0.],
        [0.11089399, 0.97587645, 0.]
    ])
]

polyhedron_faces2 = [
    np.array([
        [0.39444913, 1., 0.82813675],
        [0.40758976, 0.95513772, 0.79719745],
        [0.34359338, 0., 0.29985625],
        [0., 0., 0.46114527],
        [0., 0.95716483, 0.98964681],
        [0.12366986, 1., 0.95524549]]),
    np.array([
        [0.49889851, 0.85842498, 0.76998793],
        [0.49708892, 1., 0.89249134],
        [0.51146935, 1., 1.],
        [0.63999281, 0., 1.],
        [0.55297095, 0., 0.34942088]]),
    np.array([
        [0.55297095, 0., 0.34942088],
        [0.49889851, 0.85842498, 0.76998793],
        [0.40758976, 0.95513772, 0.79719745],
        [0.34359338, 0., 0.29985625]]),
    np.array([
        [0.49708892, 1., 0.89249134],
        [0.49889851, 0.85842498, 0.76998793],
        [0.40758976, 0.95513772, 0.79719745],
        [0.39444913, 1., 0.82813675]]),
    np.array([
        [0.12366986, 1., 0.95524549],
        [0.27691311, 1., 1.],
        [0., 0.95087602, 1.],
        [0., 0.95716483, 0.98964681]]),
    np.array([
        [0., 0.95716483, 0.98964681],
        [0., 0.95087602, 1.],
        [0., 0., 1.],
        [0., 0., 0.46114527]]),
    np.array([
        [0.63999281, 0., 1.],
        [0.55297095, 0., 0.34942088],
        [0.34359338, 0., 0.29985625],
        [0., 0., 0.46114527],
        [0., 0., 1.]]),
    np.array([
        [0.51146935, 1., 1.],
        [0.49708892, 1., 0.89249134],
        [0.39444913, 1., 0.82813675],
        [0.12366986, 1., 0.95524549],
        [0.27691311, 1., 1.]]),
    np.array([
        [0.63999281, 0., 1.],
        [0.51146935, 1., 1.],
        [0.27691311, 1., 1.],
        [0., 0.95087602, 1.],
        [0., 0., 1.]])
]


class RandomConvexPolygon:

    def __init__(self, vertices, thickness=0., segs_radius=10, segs_a=2, invert=False, open=False):
        self.color = (1, 1, 1, 1)
        self.vertices = vertices
        self.segs_a = segs_a
        self.open = open

        self.segs_radius = segs_radius
        self.invert = invert
        self.segs_c = len(self.vertices)

        self.center = np.mean(self.vertices, axis=0)
        # self.center = sum(self.vertices) / self.segs_c
        self.radius = math.hypot(*(self.vertices[0] - self.center))
        self.thickness = self.radius if not thickness else max(0, min(self.radius, thickness))
        # self.shifted_vertices = [v - self.center for v in self.vertices + self.vertices[:1]]
        self.shifted_vertices = np.vstack([self.vertices, self.vertices[0]])
        # self.normal = self.calc_normal_newell()
        # self.normal = self.calc_normal_cross()
        self.normal = self.calc_average_normal()

        self.inner_radius = self.radius - self.thickness
        self.height = self.thickness

        self.edge_length, self.edge_lengths = self.calc_perimeter()

    def calc_perimeter(self):
        edges = np.diff(self.vertices, axis=0, append=[self.vertices[0]])
        edge_lengths = np.sqrt(np.sum(edges ** 2, axis=1))
        edge_length = np.sum(edge_lengths)
        return edge_length, edge_lengths

    def calc_normal_newell(self):
        normal = np.zeros(3)
        n = len(self.vertices)

        for i, v_curr in enumerate(self.vertices):
            v_next = self.vertices[(i + 1) % n, :]
            normal[0] += (v_curr[1] - v_next[1]) * (v_curr[2] + v_next[2])
            normal[1] += (v_curr[2] - v_next[2]) * (v_curr[0] + v_next[0])
            normal[2] += (v_curr[0] - v_next[0]) * (v_curr[1] + v_next[1])

        if (norm := math.hypot(*normal)) == 0:
            return normal

        return normal / norm

    def normalize(self, vertex):
        norm = math.hypot(*vertex)
        return vertex / norm

    def calc_normal_cross(self):
        normal = np.cross(
            self.vertices[1, :] - self.vertices[0, :],
            self.vertices[2, :] - self.vertices[0, :]
        )

        if (norm := math.hypot(*normal)) == 0:
            return normal

        # Ensure it points away from the centroid
        if np.dot(normal, self.vertices[0]) < 0:
            normal = -normal

        return normal / norm

    def calc_average_normal(self):
        normals = []
        v0 = self.vertices[0]

        for i in range(1, len(self.vertices) - 1):
            v1 = self.vertices[i]
            v2 = self.vertices[i + 1]
            normal = np.cross(v1 - v0, v2 - v0)
            normals.append(normal)

        normals = np.array(normals)
        avg_normal = np.mean(normals, axis=0)

        if (norm := math.hypot(*avg_normal)) == 0:
            return avg_normal

        if np.dot(avg_normal, v0) < 0:
            avg_normal = -avg_normal

        return avg_normal / norm

    def create_triangles(self, vdata_values):
        direction = -1 if self.invert else 1
        r = self.radius / self.segs_radius
        vertex_cnt = 0

        # cap center and triangle vertices
        for i, shifted_vert in enumerate(self.shifted_vertices):
            if i == 0:
                # vertex = Point3(*shifted_vert)
                vertex = Point3(*self.center)
                uv = Vec2(0.5, 0.5)
                vdata_values.extend([*vertex, *self.color, *self.normal, *uv])
                vertex_cnt += 1

            vertex = Point3(*((shifted_vert - self.center) / self.segs_radius + self.center))
            u = 0.5 + vertex.x / r * 0.5 / self.segs_radius
            v = 0.5 + vertex.y / r * 0.5 * direction / self.segs_radius

            # normal = self.normalize(vertex)
            # vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])

            vdata_values.extend([*vertex, *self.color, *self.normal, *(u, v)])
            vertex_cnt += 1

        return vertex_cnt
    
    def create_quad_vertices(self, vdata_values):
        # normal = Vec3(0, 0, 1) if self.invert else Vec3(0, 0, -1)
        # segs_cap = self.segs_bc if bottom else self.segs_tc

        # if not bottom:
        #     normal *= -1

        # height = 0 if bottom else self.height
        direction = -1 if self.invert else 1
        n = 0 if self.inner_radius else 1
        vertex_cnt = 0

        # cap quad vertices
        for i in range(n, self.segs_radius + 1 - n):
            r = self.inner_radius + self.thickness * (i + n) / self.segs_radius

            for shifted_vert in self.shifted_vertices:
                _r = r / self.radius
                # vertex = Point3(*shifted_vert[:2] * _r, height)

                pt = (shifted_vert - self.center) * _r + self.center
                vertex = Point3(*pt)
                # vertex = Point3(*shifted_vert * _r)
                u = 0.5 + vertex.x / r * 0.5 * _r
                # _direction = -direction if bottom else direction
                # v = 0.5 + vertex.y / r * 0.5 * _direction * _r
                v = 0.5 + vertex.y / r * 0.5 * direction * _r

                # normal = self.normalize(vertex)
                # vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                vdata_values.extend([*vertex, *self.color, *self.normal, *(u, v)])
                vertex_cnt += 1

        return vertex_cnt

    def create_face_triangles(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        if not self.inner_radius:
            # bottom cap center and triangle vertices
            vertex_cnt += self.create_triangles(vdata_values)

            # the vertex order of the bottom cap triangles
            for i in range(index_offset + 1, index_offset + self.segs_c + 1):
                prim_indices.extend((index_offset, i + 1, i))

        return vertex_cnt

    def create_face_quads(self, index_offset, vdata_values, prim_indices):
        # bottom cap quad vertices
        vertex_cnt = self.create_quad_vertices(vdata_values)

        # the vertex order of the bottom cap quads
        index_offset += (self.segs_c + 1) if self.inner_radius else 1
        n = 0 if self.inner_radius else 1

        for i in range(n, self.segs_radius):
            for j in range(self.segs_c):
                vi1 = index_offset + i * (self.segs_c + 1) + j
                vi2 = vi1 - self.segs_c - 1
                vi3 = vi2 + 1
                vi4 = vi1 + 1
                prim_indices.extend([*(vi1, vi2, vi3), *(vi1, vi3, vi4)])

        return vertex_cnt

    # def create_polygon(self, vertex_cnt, vdata_values, prim_indices):
    #     if self.segs_radius:
    #         sub_total = vertex_cnt
    #         vertex_cnt += self.create_face_triangles(sub_total, vdata_values, prim_indices)
    #         vertex_cnt += self.create_face_quads(sub_total, vdata_values, prim_indices)

    #     return vertex_cnt

    def create_polygon(self, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        if self.segs_radius:
            vertex_cnt += self.create_face_triangles(index_offset, vdata_values, prim_indices)
            vertex_cnt += self.create_face_quads(index_offset, vdata_values, prim_indices)
        
        # if not self.segs_radius:
        # # if self.open:
        #     vertex_cnt += self.create_mantle_quads(vertex_cnt, vdata_values, prim_indices)


        return vertex_cnt

    def create_mantle_quad_vertices(self, index_offset, vdata_values, prim_indices):
        direction = -1 if self.invert else 1
        vertex_cnt = 0

        # mantle quad vertices
        for i in range(self.segs_a + 1):
            z = self.height * i / self.segs_a
            v = i / self.segs_a
            total_edge_length = 0

            for j, shifted_vert in enumerate(self.shifted_vertices):
                # pt = shifted_vert - (shifted_vert - self.center) * (z / self.radius)
                pt = (shifted_vert - shifted_vert * (self.inner_radius / self.radius)) * (i / self.segs_a)
                pt = shifted_vert * (self.inner_radius / 
                                     self.radius) + pt 
                vertex = Point3(*pt)
                # vertex = Point3(*shifted_vert[:2], z)
                normal = Vec3(vertex.x, vertex.y, 0.0).normalized() * direction

                if j > 0:
                    total_edge_length += self.edge_lengths[j - 1]

                u = total_edge_length / self.edge_length
                uv = Vec2(u, v)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        return vertex_cnt

    def create_mantle_quads(self, index_offset, vdata_values, prim_indices):
        # mantle quad vertices
        vertex_cnt = self.create_mantle_quad_vertices(index_offset, vdata_values, prim_indices)

        # the vertex order of the mantle quads
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


class RandomConvexPolyhedron(ProceduralGeometry):
    """A class to create a prism from 3D vertex coordinates of a polygonal base with height 0.

        Args:
            vertices: (list): a list of numpy.ndarray of double; coordinates of the Voronoi vertices.
            thickness (float):
                radial offset of inner cylinder;
                results in a straight tube with an inner radius equal to radius minus thickness;
                must be in [0., radius] range; default is 0.0.
            height (float): length of the cylinder, greater than 0; default is 1.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1; default is 2.
            segs_top_cap (int): radial subdivisions of the top cap; minimum = 0; default is 3.
            segs_bottom_cap (int): radial subdivisions of the bottom cap; minimum = 0; default is 3.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, vertices=polyhedron_faces2, thickness=0.0, height=1, segs_a=1, segs_radius=10, invert=False, open=False):
        self.polyhedron_faces = vertices
        self.segs_radius = segs_radius
        self.invert = invert
        self.thickness = thickness
        self.height = height
        self.segs_a = segs_a
        self.open = open

    def create_polyhedron(self, vertex_cnt, vdata_values, prim_indices):
        poly_center = np.mean(np.concatenate(self.polyhedron_faces), axis=0)
        self.polygons = []

        # for face in self.polyhedron_faces[4:5]:
        for face in self.polyhedron_faces:
            vertices = face - poly_center
            polygon = RandomConvexPolygon(
                vertices, thickness=self.thickness, segs_radius=self.segs_radius,
                invert=self.invert, open=self.open)
            vertex_cnt += polygon.create_polygon(vertex_cnt, vdata_values, prim_indices)
            self.polygons.append(polygon)

        return vertex_cnt

    def get_geom_node(self):
        # Create an outer cylinder.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0
        vertex_cnt = self.create_polyhedron(vertex_cnt, vdata_values, prim_indices)

        # vertex_cnt = self.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.thickness:
            # import pdb; pdb.set_trace()
            cylinder_maker = RandomConvexPolyhedron(
                # vertices=[f * (v.inner_radius / v.radius) for v, f in zip(self.polygons, self.polyhedron_faces)],
                vertices=[f * 0.8 for v, f in zip(self.polygons, self.polyhedron_faces)],
                thickness=0,
                height=self.height,
                segs_a=self.segs_a,
                segs_radius=2,
                invert=not self.invert,
                open=True
            )

            geom_node = cylinder_maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, self.__class__.__name__.lower())
        return geom_node
