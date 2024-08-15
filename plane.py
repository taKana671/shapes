import array

from panda3d.core import Point3
from panda3d.core import Vec3

from .create_geometry import ProceduralGeometry


class PlaneModel(ProceduralGeometry):
    """Create a plane geom node.
        Arges:
            w (int): width; dimension along the x-axis; cannot be negative
            d (int): depth; dimension along the y-axis; cannot be negative
            segs_w (int) the number of subdivisions in width
            segs_d (int) the number of subdivisions in depth
    """

    def __init__(self, w=256, d=256, segs_w=16, segs_d=16):
        super().__init__()
        self.w = w
        self.d = d
        self.segs_w = segs_w
        self.segs_d = segs_d

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        start_w = self.w * -0.5
        start_d = self.d * -0.5
        offset_u = -start_w
        offset_v = -start_d

        color = (1, 1, 1, 1)
        normal = Vec3(0, 0, 1)

        for i in range(self.segs_w + 1):
            x = start_w + i / self.segs_w * self.w
            u = (x + offset_u) / self.w

            for j in range(self.segs_d + 1):
                y = start_d + j / self.segs_d * self.d
                v = (y + offset_v) / self.d

                vdata_values.extend(Point3(x, y, 0))
                vdata_values.extend(color)
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
