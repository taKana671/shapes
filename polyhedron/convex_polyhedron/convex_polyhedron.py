import math

import numpy as np

from ..polyhedron import Polyhedron


class PolyhedralVertexData:
    """A mixin class for calculating the UV coordinates
       and the normal of a convex polyhedron
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
            normal = self.cross(v1 - v0, v2 - v0)
            normals.append(normal)

        normals = np.array(normals)
        avg_normal = np.mean(normals, axis=0)

        if (norm := math.hypot(*avg_normal)) == 0:
            return avg_normal

        if np.dot(avg_normal, v0) < 0:
            avg_normal = -avg_normal

        return avg_normal / norm

    def cross(self, a, b):
        # Using numpy.cross caused performance issues, so use the Python implementation
        # of cross instead (It is because numpy.cross is used on a small numpy.ndarray with shape=(3, ) ?).
        return np.array([
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ])

    def calc_triangle_area(self, p0, p1, p2):
        v1 = p1 - p0
        v2 = p2 - p0

        c = self.cross(v1, v2)
        area = (c[0] ** 2 + c[1] ** 2 + c[2] ** 2) ** 0.5

        return area

    def calc_outward_normal(self, vertices, polyhedron_center, average=True):
        """To calculate the outward normals of a convex polyhedron.
            Args:
                vertices (numpy.ndarray): Vertices of a 3D polygon, which is each face of a polyhedron.
                polyhedron_center (numpy.ndarray): the center of the polyhedron.
                average (bool):
                    if True, the normal is calculated using `calc_average_normal`;
                    if False, the normal is calculated using the first three vertices in the vertex array.
        """
        v0 = vertices[0]

        if average:
            normal = self.calc_average_normal(vertices)
        else:
            v1, v2 = vertices[1:3]
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = self.cross(edge1, edge2)

            if (norm := math.hypot(*normal)) > 1e-9:
                normal /= norm

        face_to_center = v0 - polyhedron_center

        # Flip if pointing inward.
        if np.dot(normal, face_to_center) < 0:
            normal = -normal

        return normal

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
        tangent = self.cross(normal, vec)
        tangent /= math.hypot(*tangent)

        # Calculation of the bitangent vector.
        bitangent = self.cross(normal, tangent)
        bitangent /= math.hypot(*bitangent)

        # Project vertex onto a 2D plane (tangent, bitangent)
        u = np.dot(vertex, tangent)
        v = np.dot(vertex, bitangent)

        return u, v


class ConvexPolyhedron(PolyhedralVertexData, Polyhedron):
    """A class that provides common methods for generating 3D convex polyhedron.
    """

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