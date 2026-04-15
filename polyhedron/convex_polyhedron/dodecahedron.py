import array
import math

import numpy as np
from panda3d.core import Vec3, Point3, Vec2, Point2


# from ...create_geometry import ProceduralGeometry
# from ..triangle_generator import TriangleGenerator
from .convex_polyhedron import ConvexPolyhedron


class Dodecahedron(ConvexPolyhedron):
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

    # def __init__(self, max_depth=3, scale=2):
    #     super().__init__(max_depth)
    #     self.scale = scale
    #     self.color = (1, 1, 1, 1)

    # def calc_average_normal(self, vertices):
    #     normals = []
    #     v0 = vertices[0]

    #     for i in range(1, len(vertices) - 1):
    #         v1 = vertices[i]
    #         v2 = vertices[i + 1]
    #         normal = np.cross(v1 - v0, v2 - v0)
    #         normals.append(normal)

    #     normals = np.array(normals)
    #     avg_normal = np.mean(normals, axis=0)

    #     if (norm := math.hypot(*avg_normal)) == 0:
    #         return avg_normal

    #     if np.dot(avg_normal, v0) < 0:
    #         avg_normal = -avg_normal

    #     return avg_normal / norm

    def generate_triangles(self):
        pts = [
            [-0.35682209, -0.49112347,  0.79465447],
            [0.35682209, -0.49112347,  0.79465447],
            [0.57735027, -0.79465447,  0.18759247],
            [0.00000000, -0.98224695, -0.18759247],
            [-0.57735027, -0.79465447,  0.18759247],
            [-0.57735027,  0.18759247,  0.79465447],
            [0.57735027,  0.18759247,  0.79465447],
            [0.93417236, -0.30353100, -0.18759247],
            [-0.00000000, -0.60706200, -0.79465447],
            [-0.93417236, -0.30353100, -0.18759247],
            [-0.93417236,  0.30353100,  0.18759247],
            [0.00000000,  0.60706200,  0.79465447],
            [0.93417236,  0.30353100,  0.18759247],
            [0.57735027, -0.18759247, -0.79465447],
            [-0.57735027, -0.18759247, -0.79465447],
            [-0.57735027,  0.79465447, -0.18759247],
            [0.00000000,  0.98224695,  0.18759247],
            [0.57735027,  0.79465447, -0.18759247],
            [0.35682209,  0.49112347, -0.79465447],
            [-0.35682209,  0.49112347, -0.79465447],
        ]

        faces = [
            [0, 1, 6, 11, 5],
            [0, 5, 10, 9, 4],
            [0, 4, 3, 2, 1],
            [1, 2, 7, 12, 6],
            [2, 3, 8, 13, 7],
            [3, 4, 9, 14, 8],
            [5, 11, 16, 15, 10],
            [6, 12, 17, 16, 11],
            [7, 13, 18, 17, 12],
            [8, 14, 19, 18, 13],
            [9, 10, 15, 19, 14],
            [15, 16, 17, 18, 19]
        ]

        for face in faces:
            vertices = np.array([pts[i] for i in face])
            center = np.mean(vertices, axis=0)
            self.normal = self.calc_average_normal(vertices)

            for i, v in enumerate(vertices):
                next_v = vertices[(i + 1) % len(vertices)]
                # import pdb; pdb.set_trace()
                # tri = [Point3(*center), Point3(*v), Point3(*next_v)]
                tri = [center, v, next_v]
                yield tri


        # combined = np.concatenate(self.polyhedron_faces)
        # poly_center = np.mean(combined, axis=0)
        # self.radius = math.hypot(*(combined[0] - poly_center))

        # for vertices in self.polyhedron_faces:
        #     shifted_vertices = vertices - poly_center
        #     center = np.mean(shifted_vertices, axis=0)
        #     self.normal = self.calc_average_normal(shifted_vertices)

        #     for i, v in enumerate(shifted_vertices):
        #         next_v = shifted_vertices[(i + 1) % len(shifted_vertices)]
        #         # import pdb; pdb.set_trace()
        #         # tri = [Point3(*center), Point3(*v), Point3(*next_v)]
        #         tri = [center, v, next_v]
        #         yield tri

    # def project_to_uv(self, vertices, normal):
    #     vertices = np.array(vertices)

    #     vec = np.array([1, 0, 0]) if abs(normal[0]) < 0.9 else np.array([0, 1, 0])
    #     tangent = np.cross(normal, vec)
    #     tangent /= math.hypot(*tangent)
    #     bitangent = np.cross(normal, tangent)
    #     u = np.dot(vertices, tangent)
    #     v = np.dot(vertices, bitangent)
    #     return u, v
    
    # def calc_uv(self, vert):
    #     u = np.atan2(vert[1], vert[0]) / (2.0 * np.pi) + 0.5
    #     v = np.asin(vert[2]) / np.pi + 0.5

    #     return Point2(u, v)

    # def fix_uv(self, uv_a, uv_b, uv_c):
    #     """recalculate the UV to prevent ziggzagging distortion effects.
    #         Args:
    #             uv_a, uv_b, uv_c (panda3d.core.Point2):
    #                 UV coordinates, calculated by the self.calc_uv, for each vertex of the triangle.
    #     """
    #     if uv_b.x - uv_a.x >= 0.5 and uv_a.y != 1:
    #         uv_b.x -= 1

    #     if uv_c.x - uv_b.x > 0.5:
    #         uv_c.x -= 1

    #     if (uv_a.x > 0.5 and uv_a.x - uv_c.x > 0.5) or \
    #             (uv_a.x == 1 and uv_c.y == 0):
    #         uv_a.x -= 1

    #     if uv_b.x > 0.5 and uv_b.x - uv_a.x > 0.5:
    #         uv_b.x -= 1

    #     if uv_a.y == 0 or uv_a.y == 1:
    #         uv_a.x = (uv_b.x + uv_c.x) / 2

    #     if uv_b.y == 0 or uv_b.y == 1:
    #         uv_b.x = (uv_a.x + uv_c.x) / 2

    #     if uv_c.y == 0 or uv_c.y == 1:
    #         uv_c.x = (uv_a.x + uv_b.x) / 2


    # def create_polyhedron(self, vdata_values, prim_indices):
    #     """Subdivide a triangle and normalize the vertex position vectors.
    #     """
    #     for i, tri in enumerate(self.generate_divided_tri()):
    #         # import pdb; pdb.set_trace()
    #         # uvs = [self.calc_uv(self.normalize(vert)) for vert in tri]
    #         # uvs = self.calc_planar_uv(tri)
    #         uvs = [self.project_to_uv(v, self.normal) for v in tri]
    #         # self.fix_uv(*uvs)

    #         for vert, uv in zip(tri, uvs):
    #             vertex = vert * self.scale

    #             vdata_values.extend(vertex)               # vertex
    #             vdata_values.extend(self.color)           # color
    #             vdata_values.extend(self.normal)               # normal
    #             vdata_values.extend(uv)                   # uv

    #         indices = (idx := i * 3, idx + 1, idx + 2)
    #         prim_indices.extend(indices)

    def get_geom_node(self):
        faces = 12 * 5
        return self.create_polyhedron_geom_node(faces)
        # vertex_cnt = 4 ** self.max_depth * faces * 3
        # # type_code = 'H' if vertex_cnt <= 65535 else 'I'
        # vdata_values = array.array('f', [])
        # # prim_indices = array.array(type_code, [])
        # prim_indices = array.array('I', [])

        # self.create_polyhedron(vdata_values, prim_indices)
        # geom_node = self.create_geom_node(
        #     vertex_cnt,
        #     vdata_values,
        #     prim_indices,
        #     self.__class__.__name__.lower()
        # )

        # return geom_node