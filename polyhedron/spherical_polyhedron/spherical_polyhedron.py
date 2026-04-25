import numpy as np
from panda3d.core import Point2

from ..polyhedron import Polyhedron


class SphericalPolyhedron(Polyhedron):
    """A class that provides common methods for creating spheres from 3D polyhedrons
    """

    def calc_uv(self, vert):
        u = np.atan2(vert.y, vert.x) / (2.0 * np.pi) + 0.5
        v = np.asin(vert.z) / np.pi + 0.5

        return Point2(u, v)

    def fix_uv(self, uv_a, uv_b, uv_c):
        """recalculate the UV to prevent ziggzagging distortion effects.
            Args:
                uv_a, uv_b, uv_c (panda3d.core.Point2):
                    UV coordinates, calculated by the self.calc_uv, for each vertex of the triangle.
        """
        if uv_b.x - uv_a.x >= 0.5 and uv_a.y != 1:
            uv_b.x -= 1

        if uv_c.x - uv_b.x > 0.5:
            uv_c.x -= 1

        if (uv_a.x > 0.5 and uv_a.x - uv_c.x > 0.5) or \
                (uv_a.x == 1 and uv_c.y == 0):
            uv_a.x -= 1

        if uv_b.x > 0.5 and uv_b.x - uv_a.x > 0.5:
            uv_b.x -= 1

        if uv_a.y == 0 or uv_a.y == 1:
            uv_a.x = (uv_b.x + uv_c.x) / 2

        if uv_b.y == 0 or uv_b.y == 1:
            uv_b.x = (uv_a.x + uv_c.x) / 2

        if uv_c.y == 0 or uv_c.y == 1:
            uv_c.x = (uv_a.x + uv_b.x) / 2

    def create_polyhedron(self, vdata_values, prim_indices):
        """Subdivide a triangle and normalize the vertex position vectors.
        """
        for i, tri in enumerate(self.generate_divided_tri()):
            uvs = [self.calc_uv(vert.normalized()) for vert in tri]
            self.fix_uv(*uvs)

            for vert, uv in zip(tri, uvs):
                normal = vert.normalized()
                vertex = normal * self.scale

                vdata_values.extend(vertex)               # vertex
                vdata_values.extend(self.color)           # color
                vdata_values.extend(normal)               # normal
                vdata_values.extend(uv)                   # uv

            indices = (idx := i * 3, idx + 1, idx + 2)
            prim_indices.extend(indices)