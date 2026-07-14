import array

from panda3d.core import Point3
from panda3d.core import Vec3

from .create_geometry import ProceduralGeometry


class Plane(ProceduralGeometry):
    """A class to create a plane.

        Args:
            width (float): dimension along the x-axis; greater than 0; default is 2.
            depth (float): dimension along the y-axis; greater than 0; default is 2.
            segs_w (int) the number of subdivisions in width; greater than 0; default is 6.
            segs_d (int) the number of subdivisions in depth; greater than 0; default is 6.
    """

    def __init__(self, width=2, depth=2, segs_w=6, segs_d=6):
        self.color = (1, 1, 1, 1)
        self.width = width
        self.depth = depth
        self.segs_w = segs_w
        self.segs_d = segs_d

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        start_w = self.width * -0.5
        start_d = self.depth * -0.5
        offset_u = -start_w
        offset_v = -start_d
        normal = Vec3(0, 0, 1)

        for i in range(self.segs_w + 1):
            x = start_w + i / self.segs_w * self.width
            u = (x + offset_u) / self.width

            for j in range(self.segs_d + 1):
                y = start_d + j / self.segs_d * self.depth
                v = (y + offset_v) / self.depth

                vdata_values.extend(Point3(x, y, 0))
                vdata_values.extend(self.color)
                vdata_values.extend(normal)
                vdata_values.extend((u, v))

            if i > 0:
                for k in range(self.segs_d):
                    idx = i * (self.segs_d + 1) + k
                    prim_indices.extend((idx, idx - self.segs_d - 1, idx - self.segs_d))
                    prim_indices.extend((idx, idx - self.segs_d, idx + 1))

        vertex_cnt = (self.segs_w + 1) * (self.segs_d + 1)
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, self.__class__.__name__.lower())

        return geom_node


class PlaneForTextureAtlas(ProceduralGeometry):
    """A class to create a plane for texture atlas.

        Args:
            divided_u (float):
                A value indicating how many small images of the same size fit horizontally within a single image.
                If a single image contains 8 (vertical) x 8 (horizontal) small images, then 1/8.
            divided_v (float):
                A value indicating how many small images of the same size fit vertically within a single image.
                If a single image contains 8 (vertical) x 8 (horizontal) small images, then 1/8.
            size (float): image size
    """

    def __init__(self, divided_u, divides_v, size=1):
        self.color = (1, 1, 1, 1)
        self.end_u = divided_u
        self.start_v = 1 - divides_v
        self.size = size

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        half = self.size / 2
        vertices = [
            (-half, 0, half),
            (-half, 0, -half),
            (half, 0, half),
            (half, 0, -half),
        ]

        # order is important
        uvs = [
            (0, 1),
            (0, self.start_v),
            (self.end_u, 1),
            (self.end_u, self.start_v),
        ]

        for i, (vertex, uv) in enumerate(zip(vertices, uvs)):
            vdata_values.extend(vertex)
            vdata_values.extend(self.color)
            vdata_values.extend(Vec3(vertex).normalized())
            vdata_values.extend(uv)

        idx = 2
        prim_indices.extend((idx, idx - 2, idx - 1))
        prim_indices.extend((idx, idx - 1, idx + 1))

        vertex_cnt = len(vertices)
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, self.__class__.__name__.lower())

        return geom_node
