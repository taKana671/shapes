import array

from .create_geometry import ProceduralPoints


class Particles(ProceduralPoints):
    """A class to generate points.
        Args:
            vertices (list):
                A flat list of vertex coordinates like below. A generator is also acceptable.
                [x0, y0, z0, x1, y1, z1, x2, y2, z2, ...]
    """

    def __init__(self, vertices):
        self.vertices = vertices

    def get_geom_node(self):

        vertex_count = int(len(self.vertices) / 3)
        vdata_values = array.array('f', self.vertices)

        geom_node = self.create_geom_node(
            vertex_count, vdata_values, self.__class__.__name__.lower())
        return geom_node
