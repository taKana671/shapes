from functools import reduce

from panda3d.core import Point3

from .spherical_polyhedron import SphericalPolyhedron


class Cubesphere(SphericalPolyhedron):
    """A class to create a sphere from cube.

        Args:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of sphere; greater than 0.
    """

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
                tri = [p1, p2, center]
                yield tri

    def get_geom_node(self):
        faces = 6 * 4
        return self.create_polyhedron_geom_node(faces)