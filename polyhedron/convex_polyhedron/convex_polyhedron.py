import math

import numpy as np

from ..polyhedron import Polyhedron


class ConvexPolyhedron(Polyhedron):
    """A class that provides common methods for generating 3D convex polyhedron.
        Args:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the size of polyhedron; greater than 0.
    """

    def calc_normal_newell(self, vertices):
        """Calculating the average normal using the Newell method.
            Args:
                vertices (numpy.ndarray): Vertices of a 3D polygon
        """
        normal = np.zeros(3)
        n = len(vertices)

        for i, v_curr in enumerate(vertices):
            v_next = vertices[(i + 1) % n, :]
            normal[0] += (v_curr[1] - v_next[1]) * (v_curr[2] + v_next[2])
            normal[1] += (v_curr[2] - v_next[2]) * (v_curr[0] + v_next[0])
            normal[2] += (v_curr[0] - v_next[0]) * (v_curr[1] + v_next[1])

        if (norm := math.hypot(*normal)) == 0:
            return normal

        return normal / norm

    def calc_average_normal(self, vertices):
        """Divide a 3D polygon into triangles, calculate the average normal,
           and normalize the value.
            Args:
                vertices (numpy.ndarray): Vertices of a 3D polygon
        """
        normals = []
        v0 = vertices[0]

        for i in range(1, len(vertices) - 1):
            v1 = vertices[i]
            v2 = vertices[i + 1]
            normal = np.cross(v1 - v0, v2 - v0)
            normals.append(normal)

        normals = np.array(normals)
        avg_normal = np.mean(normals, axis=0)

        if (norm := math.hypot(*avg_normal)) == 0:
            return avg_normal

        if np.dot(avg_normal, v0) < 0:
            avg_normal = -avg_normal

        return avg_normal / norm

    def project_to_uv(self, vertex, normal):
        """Calculate plane-projected UV coordinates from 3D vertices and face normals.
            Args:
                vertex (numpy.ndarray): Vertex of a triangle
                normal (numpy.ndarray): Normal
        """
        # Determine a vector perpendicular to the normal.
        # If the normal is too close to the x-axis [1,0,0], use the y-axis [0,1,0] (to avoid singularities).
        vec = np.array([1, 0, 0]) if abs(normal[0]) < 0.9 else np.array([0, 1, 0])

        # Calculating the tangent vector.
        tangent = np.cross(normal, vec)
        tangent /= math.hypot(*tangent)

        # Calculation of the bitangent vector.
        bitangent = np.cross(normal, tangent)
        bitangent /= math.hypot(*bitangent)

        # Project vertex onto a 2D plane (tangent, bitangent)
        u = np.dot(vertex, tangent)
        v = np.dot(vertex, bitangent)
        return u, v

    def create_polyhedron(self, vdata_values, prim_indices):
        for i, tri in enumerate(self.generate_divided_tri()):
            for vert in tri:
                uv = self.project_to_uv(vert, self.normal)

                vdata_values.extend(vert * self.scale)    # vertex
                vdata_values.extend(self.color)           # color
                vdata_values.extend(self.normal)          # normal
                vdata_values.extend(uv)                   # uv

            indices = (idx := i * 3, idx + 1, idx + 2)
            prim_indices.extend(indices)