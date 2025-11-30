import numpy as np
import array

from ..create_geometry import ProceduralGeometry


class TriangleGenerator(ProceduralGeometry):

    def __init__(self, max_depth):
        super().__init__()
        self.max_depth = max_depth

    def calc_midpoints(self, tri):
        """Generates the midpoints of the three sides of a triangle.
            Args:
                tri (list): list of Vec3; having 3 elements.
        """
        for p1, p2 in zip(tri, tri[1:] + tri[:1]):
            yield (p1 + p2) / 2

    def subdivide(self, tri, depth=0):
        if depth == self.max_depth:
            yield tri
        else:
            midpoints = [p for p in self.calc_midpoints(tri)]

            for i, vert in enumerate(tri):
                ii = n if (n := i - 1) >= 0 else len(midpoints) - 1
                divided = [vert, midpoints[i], midpoints[ii]]
                yield from self.subdivide(divided, depth + 1)

            yield from self.subdivide(midpoints, depth + 1)


class SphericalPolyhedron(TriangleGenerator):
    """Create a sphere model from polyhedron.
        Arges:
            faces (int): the number of faces of the polyhedron.
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of sphere; greater than 0.
    """

    def __init__(self, faces, max_depth, scale):
        super().__init__(max_depth)
        self.scale = scale
        self.faces = faces

    def calc_uv(self, normal):
        # abs(normal.y): to prevent jagged vertical lines appear on the texture.
        u = 0.5 + (np.arctan2(normal.x, abs(normal.y))) / (2 * np.pi)
        v = 0.5 + np.arcsin(normal.z) / np.pi

        return (u, v)

    def create_spehre(self, vdata_values, prim_indices):
        """Subdivide a triangle and normalize the vertex position vectors.
        """
        for i, tri in enumerate(self.generate_triangles()):
            for vert in tri:
                normal = vert.normalized()
                vertex = normal * self.scale
                uv = self.calc_uv(normal)

                vdata_values.extend(vertex)               # vertex
                vdata_values.extend(self.color)           # color
                vdata_values.extend(normal)               # normal
                vdata_values.extend(uv)                   # uv

            indices = (idx := i * 3, idx + 1, idx + 2)
            prim_indices.extend(indices)

    def get_geom_node(self):
        vertex_cnt = 4 ** self.max_depth * self.faces * 3
        type_code = 'H' if vertex_cnt <= 65535 else 'I'
        vdata_values = array.array('f', [])
        prim_indices = array.array(type_code, [])

        self.create_spehre(vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt,
            vdata_values,
            prim_indices,
            self.__class__.__name__.lower()
        )

        return geom_node