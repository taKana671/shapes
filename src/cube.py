import array

from panda3d.core import Vec3, Point3

from .create_geometry import ProceduralGeometry


class Cube(ProceduralGeometry):
    """Create a geom node of cube or cuboid.
        Arges:
            width (float): dimension along the x-axis; more than zero
            depth (float): dimension along the y-axis; more than zero
            height (float): dimension along the z-axis; must be more than zero
            segs_w (int) the number of subdivisions in width; positive integer
            segs_d (int) the number of subdivisions in depth; positive integer
            segs_h (int) the number of subdivisions in height; positive integer
    """

    def __init__(self, width=1.0, depth=1.0, height=1.0, segs_w=1, segs_d=1, segs_h=1):
        super().__init__()
        self.width = width
        self.depth = depth
        self.height = height
        self.segs_w = segs_w
        self.segs_d = segs_d
        self.segs_h = segs_h
        self.color = (1, 1, 1, 1)

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])

        vertex = Point3()
        segs = (self.segs_w, self.segs_d, self.segs_h)
        dims = (self.width, self.depth, self.height)
        segs_u = self.segs_w * 2 + self.segs_d * 2
        vertex_cnt = 0
        offset_u = 0

        # (fixed, outer loop, inner loop, normal, uv)
        side_idxes = [
            (2, 0, 1, 1, False),     # top
            (1, 0, 2, -1, False),    # front
            (0, 1, 2, 1, False),     # right
            (1, 0, 2, 1, True),      # back
            (0, 1, 2, -1, True),     # left
            (2, 0, 1, -1, False),    # bottom
        ]

        for a, (i0, i1, i2, n, reverse) in enumerate(side_idxes):
            segs1 = segs[i1]
            segs2 = segs[i2]
            dim1_start = dims[i1] * -0.5
            dim2_start = dims[i2] * -0.5

            normal = Vec3()
            normal[i0] = n
            vertex[i0] = dims[i0] * 0.5 * n

            for j in range(segs1 + 1):
                vertex[i1] = dim1_start + j / segs1 * dims[i1]

                if i0 == 2:
                    u = j / segs1
                else:
                    u = (segs1 - j + offset_u) / segs_u if reverse else (j + offset_u) / segs_u

                for k in range(segs2 + 1):
                    vertex[i2] = dim2_start + k / segs2 * dims[i2]
                    v = k / segs2
                    vdata_values.extend(vertex)
                    vdata_values.extend(self.color)
                    vdata_values.extend(normal)
                    vdata_values.extend((u, v))
                if j > 0:
                    for k in range(segs2):
                        idx = vertex_cnt + j * (segs2 + 1) + k
                        prim_indices.extend((idx, idx - segs2 - 1, idx - segs2))
                        prim_indices.extend((idx, idx - segs2, idx + 1))

            vertex_cnt += (segs1 + 1) * (segs2 + 1)
            offset_u += segs2

        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'plane')

        return geom_node
