import numpy as np

from .convex_polyhedron import ConvexPolyhedron


class Dodecahedron(ConvexPolyhedron):
    """A class to create a dodecahedron.

        Args:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of sphere; greater than 0.
    """

    def generate_triangles(self):
        pts = [
            [-0.35682209, -0.49112347, 0.79465447],
            [0.35682209, -0.49112347, 0.79465447],
            [0.57735027, -0.79465447, 0.18759247],
            [0.00000000, -0.98224695, -0.18759247],
            [-0.57735027, -0.79465447, 0.18759247],
            [-0.57735027, 0.18759247, 0.79465447],
            [0.57735027, 0.18759247, 0.79465447],
            [0.93417236, -0.30353100, -0.18759247],
            [-0.00000000, -0.60706200, -0.79465447],
            [-0.93417236, -0.30353100, -0.18759247],
            [-0.93417236, 0.30353100, 0.18759247],
            [0.00000000, 0.60706200, 0.79465447],
            [0.93417236, 0.30353100, 0.18759247],
            [0.57735027, -0.18759247, -0.79465447],
            [-0.57735027, -0.18759247, -0.79465447],
            [-0.57735027, 0.79465447, -0.18759247],
            [0.00000000, 0.98224695, 0.18759247],
            [0.57735027, 0.79465447, -0.18759247],
            [0.35682209, 0.49112347, -0.79465447],
            [-0.35682209, 0.49112347, -0.79465447],
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
                tri = [center, v, next_v]
                yield tri

    def get_geom_node(self):
        faces = 12 * 5
        return self.create_polyhedron_geom_node(faces)