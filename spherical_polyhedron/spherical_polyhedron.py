import numpy as np

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

    def __init__(self, max_depth, scale):
        super().__init__(max_depth)
        self.scale = scale

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
                vdata_values.extend(normal * self.scale)  # vertex
                vdata_values.extend(self.color)           # color
                vdata_values.extend(normal)               # normal

                uv = self.calc_uv(normal)
                vdata_values.extend(uv)                   # uv

            indices = (idx := i * 3, idx + 1, idx + 2)
            prim_indices.extend(indices)



# class Icosphere(ProceduralGeometry):
#     """Create a sphere model from icosahedron quickly.
#         Arges:
#             divnum (int): the number of divisions of one triangle; cannot be negative.
#             scale (float): the size of sphere; greater than 0.
#     """

#     def __init__(self, divnum=3, scale=1):
#         super().__init__()
#         self.divnum = divnum
#         self.scale = scale
       
#     def calc_midpoints(self, face):
#         """face (list): list of Vec3; having 3 elements like below.
#            [(0, 1), (1, 2), (2, 0)]
#         """
#         for i, pt1 in enumerate(face):
#             j = i + 1 if i < len(face) - 1 else 0
#             pt2 = face[j]
#             mid_pt = (pt1 + pt2) / 2

#             yield mid_pt

#     def subdivide(self, face, divnum=0):
#         if divnum == self.divnum:
#             yield face
#         else:
#             midpoints = [pt for pt in self.calc_midpoints(face)]

#             for i, vertex in enumerate(face):
#                 j = len(face) - 1 if i == 0 else i - 1
#                 face = [vertex, midpoints[i], midpoints[j]]
#                 yield from self.subdivide(face, divnum + 1)
#             yield from self.subdivide(midpoints, divnum + 1)

#     def load_obj(self):
#         vertices = [
#             [-0.52573111, -0.72360680, 0.44721360],
#             [-0.85065081, 0.27639320, 0.44721360],
#             [-0.00000000, 0.89442719, 0.44721360],
#             [0.85065081, 0.27639320, 0.44721360],
#             [0.52573111, -0.72360680, 0.44721360],
#             [0.00000000, -0.89442719, -0.44721360],
#             [-0.85065081, -0.27639320, -0.44721360],
#             [-0.52573111, 0.72360680, -0.44721360],
#             [0.52573111, 0.72360680, -0.44721360],
#             [0.85065081, -0.27639320, -0.44721360],
#             [0.00000000, 0.00000000, 1.00000000],
#             [-0.00000000, 0.00000000, -1.00000000]
#         ]

#         faces = [
#             [0, 1, 6], [0, 6, 5], [0, 5, 4], [0, 4, 10],
#             [0, 10, 1], [1, 2, 7], [1, 7, 6], [1, 10, 2],
#             [2, 3, 8], [2, 8, 7], [2, 10, 3], [3, 4, 9],
#             [3, 9, 8], [3, 10, 4], [4, 5, 9], [5, 6, 11],
#             [5, 11, 9], [6, 7, 11], [7, 8, 11], [8, 9, 11]
#         ]

#         return vertices, faces

#     def get_geom_node(self):
#         vertices, faces = self.load_obj()
#         vertex_cnt = 4 ** self.divnum * 20 * 3
#         vdata_values = array.array('f', [])
#         prim_indices = array.array('H', [])
#         start = 0

#         for face in faces:
#             face_verts = [Vec3(*vertices[n]) * 2 for n in face]
#             for subdiv_face in self.subdivide(face_verts):
#                 for vert in subdiv_face:
#                     normal = vert.normalized()
#                     vdata_values.extend(normal * self.scale)  # vertex
#                     vdata_values.extend(self.color)           # color
#                     vdata_values.extend(normal)               # normal

#                     # abs(normal.y): to prevent jagged vertical lines appear on the texture.
#                     u = 0.5 + (np.arctan2(normal.x, abs(normal.y))) / (2 * np.pi)
#                     v = 0.5 + np.arcsin(normal.z) / np.pi
#                     vdata_values.extend((u, v))

#                 indices = (start, start + 1, start + 2)
#                 prim_indices.extend(indices)
#                 start += 3

#         geom_node = self.create_geom_node(
#             vertex_cnt, vdata_values, prim_indices, 'sphere')

#         return geom_node
