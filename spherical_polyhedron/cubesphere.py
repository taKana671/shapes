import array
from functools import reduce

from panda3d.core import Point3

from .spherical_polyhedron import SphericalPolyhedron


class Cubesphere(SphericalPolyhedron):
    """Create a sphere model from cube.
        Arges:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of sphere; greater than 0.
    """

    def __init__(self, max_depth=4, scale=2):
        super().__init__(max_depth, scale)

    def generate_triangles(self):
        v = 0.57735027

        pts = [
            [-1, -1, 1],
            [-1, 1, 1],
            [1, 1, 1],
            [1, -1, 1],
            [-1, -1, -1],
            [-1, 1, -1],
            [1, 1, -1],
            [1, -1, -1],
        ]

        faces = [
            [0, 1, 5, 4],
            [0, 4, 7, 3],
            [0, 3, 2, 1],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [4, 5, 6, 7],
        ]

        for face in faces:
            tri = [Point3(*pts[i]) * v for i in face]
            center = reduce(lambda x, y: x + y, tri, Point3()) / 4

            for p1, p2 in zip(tri, tri[1:] + tri[:1]):
                for divided_tri in self.subdivide([p1, p2, center]):
                    yield divided_tri

    def get_geom_node(self):
        vertex_cnt = 4 ** self.max_depth * 6 * 4 * 3
        type_code = 'H' if vertex_cnt <= 65535 else 'I'
        vdata_values = array.array('f', [])
        prim_indices = array.array(type_code, [])

        self.create_spehre(vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'cube_sphere')

        return geom_node
