import array

from panda3d.core import Point3
from panda3d.core import Vec3

from .create_geometry import ProceduralGeometry


class Plane(ProceduralGeometry):
    """Create a plane geom node.
        Arges:
            width (int): dimension along the x-axis; more than zero
            depth (int): dimension along the y-axis; more than zero
            segs_w (int) the number of subdivisions in width; positive integer
            segs_d (int) the number of subdivisions in depth; positive integer
    """

    def __init__(self, width=1, depth=1, segs_w=2, segs_d=2):
        super().__init__()
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
            vertex_cnt, vdata_values, prim_indices, 'plane')

        return geom_node
