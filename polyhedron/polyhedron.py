import array
from abc import abstractmethod

from ..create_geometry import ProceduralGeometry


class TriangleGenerator:

    def calc_midpoints(self, tri):
        """Generates the midpoints of the three sides of a triangle.
            Args:
                tri (list): list of Vec3; having 3 elements.
        """
        for p1, p2 in zip(tri, tri[1:] + tri[:1]):
            yield (p1 + p2) / 2

    def subdivide(self, tri, max_depth, depth=0):
        if depth == max_depth:
            yield tri
        else:
            midpoints = [p for p in self.calc_midpoints(tri)]

            for i, vert in enumerate(tri):
                ii = n if (n := i - 1) >= 0 else len(midpoints) - 1
                divided = [vert, midpoints[i], midpoints[ii]]
                yield from self.subdivide(divided, max_depth, depth + 1)

            yield from self.subdivide(midpoints, max_depth, depth + 1)


class Polyhedron(TriangleGenerator, ProceduralGeometry):
    """An abstract base class for generating 3D polyhedron
        rgs:
            max_depth (int): the number of divisions of one triangle; cannot be negative.
            scale (float): the scale of the polyhedron; greater than 0.
    """

    def __init__(self, max_depth=4, scale=2):
        self.max_depth = max_depth
        self.scale = scale

    @abstractmethod
    def generate_triangles(self):
        """Generate triangle vertices.
        """
        pass

    @abstractmethod
    def create_polyhedron(vdata_values, prim_indices):
        """Define the vertices and vertex order of a polyhedron.
            Args:
                vdata_values (array.array): vertex data
                prim_indices (array.array): vertex indices
        """
        pass

    def generate_divided_tri(self):
        for tri in self.generate_triangles():
            for divided_tri in self.subdivide(tri, self.max_depth):
                yield divided_tri

    def create_polyhedron_geom_node(self, faces):
        vertex_cnt = 4 ** self.max_depth * faces * 3
        type_code = 'H' if vertex_cnt <= 65535 else 'I'
        vdata_values = array.array('f', [])
        prim_indices = array.array(type_code, [])

        self.create_polyhedron(vdata_values, prim_indices)

        geom_node = self.create_geom_node(
            vertex_cnt,
            vdata_values,
            prim_indices,
            self.__class__.__name__.lower()
        )

        return geom_node
