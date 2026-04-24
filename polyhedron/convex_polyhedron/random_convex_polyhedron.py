import numpy as np

from .convex_polyhedron import ConvexPolyhedron


class RandomConvexPolyhedron(ConvexPolyhedron):
    """A class to create a random convex polyhedron.

        Args:
            polygons (list): A list of numpy.ndarray; vertex coordinates of a polyhedron.
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the scale of the polyhedron; greater than 0.
    """

    def __init__(self, polygons, max_depth=4, scale=2.):
        super().__init__(max_depth, scale)
        self.polygons = polygons
        self.normal = np.zeros(3)
        self.polyhedron_org_center = np.mean(np.concatenate(self.polygons), axis=0)

    def generate_triangles(self):
        for vertices in self.polygons:
            shifted_vertices = vertices - self.polyhedron_org_center
            center = np.mean(shifted_vertices, axis=0)
            self.normal = self.calc_average_normal(shifted_vertices)

            for i, v in enumerate(shifted_vertices):
                next_v = shifted_vertices[(i + 1) % len(shifted_vertices)]
                tri = [center, v, next_v]
                yield tri

    def get_geom_node(self):
        faces = sum(len(face) for face in self.polygons)
        return self.create_polyhedron_geom_node(faces)
