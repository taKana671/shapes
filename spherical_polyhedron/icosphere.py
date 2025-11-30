from panda3d.core import Point3

from .spherical_polyhedron import SphericalPolyhedron


class Icosphere(SphericalPolyhedron):
    """Create a sphere model from icosahedron.
        Arges:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of sphere; greater than 0.
    """

    def __init__(self, max_depth=4, scale=2):
        super().__init__(20, max_depth, scale)

    def generate_triangles(self):
        pts = [
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

        for face in faces:
            tri = [Point3(*pts[i]) for i in face]

            for divided_tri in self.subdivide(tri):
                yield divided_tri