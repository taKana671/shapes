import array
from types import SimpleNamespace

from panda3d.core import Vec3, Point3, Vec2

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

    def __init__(self, width=1.0, depth=1.0, height=1.0, segs_w=2, segs_d=2, segs_h=2,
                 thickness=0, invert=False, open_left=False, open_right=False, open_front=False,
                 open_back=False, open_top=False, open_bottom=False):
        super().__init__()
        self.width = width
        self.depth = depth
        self.height = height
        self.segs_w = segs_w
        self.segs_d = segs_d
        self.segs_h = segs_h
        self.thickness = thickness
        self.open_left = open_left
        self.open_right = open_right
        self.open_top = open_top
        self.open_bottom = open_bottom
        self.open_front = open_front
        self.open_back = open_back

        self.center = Point3(0, 0, 0)
        self.invert = False
        self.color = (1, 1, 1, 1)

    def define_vertex_order(self, index_offset, prim_indices, direction, inner_range, outer_range=1):
        for i in range(outer_range):
            for j in range(inner_range):
                vi1 = index_offset + i * (inner_range + 1) + j
                vi2 = vi1 + 1
                vi3 = vi2 + inner_range
                vi4 = vi3 + 1

                if self.invert:
                    prim_indices.extend((vi1, vi4, vi2) if direction == 1 else (vi1, vi2, vi4))
                    prim_indices.extend((vi1, vi3, vi4) if direction == 1 else (vi1, vi4, vi3))
                else:
                    prim_indices.extend((vi1, vi2, vi4) if direction == 1 else (vi1, vi4, vi2))
                    prim_indices.extend((vi1, vi4, vi3) if direction == 1 else (vi1, vi3, vi4))

    def get_plane_details(self, plane):
        name = SimpleNamespace(**{f'axis_{i + 1}': s for i, s in enumerate(plane)})
        index = SimpleNamespace(**{k: 'xyz'.index(v) for k, v in name.__dict__.items()})
        offset = SimpleNamespace(**{k: self.center[v] for k, v in index.__dict__.items()})
        segs = SimpleNamespace(**{k: self.segs[v] for k, v in name.__dict__.items()})

        return name, index, offset, segs

    def create_side(self, index_offset, vdata_values, prim_indices, plane, direction):
        vertex_cnt = 0
        name, index, offset, segs = self.get_plane_details(plane)
        plane_id = plane[:2]

        normal = Vec3()
        normal[index.axis_3] = direction * (-1 if self.invert else 1)

        vertex = Point3()
        vertex[index.axis_3] = .5 * self.dims[index.axis_3] * direction + offset.axis_3

        for i in range(segs.axis_2 + 1):
            b = i / segs.axis_2
            vertex[index.axis_2] = (-.5 + b) * self.dims[index.axis_2] + offset.axis_2

            for j in range(segs.axis_1 + 1):
                a = j / segs.axis_1
                vertex[index.axis_1] = (-.5 + a) * self.dims[index.axis_1] + offset.axis_1

                if plane_id == 'zx':
                    u = -b * direction + (1 if direction > 0 else 0)
                    uv = Vec2(u, a)
                else:
                    u = a * direction + (1 if direction < 0 else 0)
                    uv = Vec2(u, b)

                vdata_values.extend([*vertex, *self.color, *normal, *uv])
                vertex_cnt += 1

        self.define_vertex_order(index_offset, prim_indices, direction, segs.axis_1, segs.axis_2)
        return vertex_cnt

    def create_thick_side(self, index_offset, vdata_values, prim_indices, direction, plane):
        name, index, offset, segments = self.get_plane_details(plane)
        is_front = plane[:2] == 'zx'
        vertex_cnt = 0

        normal = Vec3()
        normal[index.axis_3] = direction * (-1 if self.invert else 1)

        vertex = Point3()
        vertex[index.axis_3] = .5 * self.dims[index.axis_3] * direction + offset.axis_3

        for sign in ('-', ''):
            thicknesses = []
            c1 = self.inner_corners[sign + name.axis_1]
            c2 = self.inner_corners[sign + name.axis_2]

            if c1 > 0:
                dim1 = self.dims[index.axis_2]
                dim2 = self.inner_dims[name.axis_2]
                thicknesses.append([1, ((dim2, c1, c2), (dim1, 0., 0.))])

            if c2 > 0:
                dim1 = self.dims[index.axis_1]
                dim2 = self.inner_dims[name.axis_1]
                thicknesses.append([2, ((dim1, 0., 0.), (dim2, c2, c1))])

            for primary_idx, t in thicknesses:
                _index_offset = index_offset + vertex_cnt

                if primary_idx == 1:
                    idx_1, idx_2 = index.axis_1, index.axis_2
                    offs_1, offs_2 = offset.axis_1, offset.axis_2
                    segs = segments.axis_2
                else:
                    idx_1, idx_2 = index.axis_2, index.axis_1
                    offs_1, offs_2 = offset.axis_2, offset.axis_1
                    segs = segments.axis_1

                for dim, corner_1, corner_2 in t:
                    if sign == '-':
                        coord = corner_1 - self.dims[idx_1] * .5
                    else:
                        coord = self.dims[idx_1] * .5 - corner_1

                    vertex[idx_1] = coord + offs_1
                    a = coord / self.dims[idx_1] + .5

                    for i in range(segs + 1):
                        if sign == '-':
                            coord = corner_2 - self.dims[idx_2] * .5 + i / segs * dim
                        else:
                            coord = self.dims[idx_2] * .5 - i / segs * dim - corner_2

                        vertex[idx_2] = coord + offs_2
                        b = coord / self.dims[idx_2] + .5

                        if is_front:
                            u = (-b if primary_idx == 1 else -a) * direction + (1 if direction > 0 else 0)
                            v = a if primary_idx == 1 else b
                        else:
                            u = (a if primary_idx == 1 else b) * direction + (1 if direction < 0 else 0)
                            v = b if primary_idx == 1 else a

                        if self.invert:
                            u = 1. - u

                        vdata_values.extend([*vertex, *self.color, *normal, *(u, v)])
                        vertex_cnt += 1

                    self.define_vertex_order(_index_offset, prim_indices, direction, segs)
        return vertex_cnt

    def get_inner_box_details(self, inner_corners, inner_dims):
        li = [
            ['x', self.width, self.open_left, self.open_right],
            ['y', self.depth, self.open_back, self.open_front],
            ['z', self.height, self.open_bottom, self.open_top]
        ]

        for axis, dim, open_side1, open_side2 in li:
            th1 = 0. if open_side1 else min(dim, self.thickness)
            th2 = 0. if open_side2 else min(dim, self.thickness)

            if th1 + th2 > dim:
                th1 = th2 = dim * .5

            inner_corners['-' + axis] = th1
            inner_corners[axis] = th2
            inner_dims[axis] = dim - th1 - th2

    def create_sides(self, vdata_values, prim_indices):
        vertex_cnt = 0
        normal = Vec3()
        vertex = Point3()

        # if self.thickness > 0:
        #     self.inner_corners = {}
        #     self.inner_dims = {}
        #     self.get_inner_box_details(self.inner_corners, self.inner_dims)

        for plane in ('xyz', 'zxy', 'yzx'):
            plane_id = plane[:2]

            for direction in (-1, 1):
                str_direction = '-' if direction == -1 else ''
                side_id = str_direction + plane_id

                if self.open_sides[side_id]:
                    if self.thickness > 0:
                        vertex_cnt += self.create_thick_side(vertex_cnt, vdata_values, prim_indices, direction, plane)
                else:
                    vertex_cnt += self.create_side(vertex_cnt, vdata_values, prim_indices, plane, direction)

        return vertex_cnt

    def get_geom_node(self):
        self.dims = (self.width, self.depth, self.height)
        self.segs = {'x': self.segs_w, 'y': self.segs_d, 'z': self.segs_h}

        self.open_sides = {
            '-yz': self.open_left,
            'yz': self.open_right,
            '-zx': self.open_back,
            'zx': self.open_front,
            '-xy': self.open_bottom,
            'xy': self.open_top
        }

        if self.thickness > 0:
            self.inner_corners = {}
            self.inner_dims = {}
            self.get_inner_box_details(self.inner_corners, self.inner_dims)

        # Create outer cube.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt += self.create_sides(vdata_values, prim_indices)

        if self.thickness > 0:
            width = self.inner_dims['x']
            depth = self.inner_dims['y']
            height = self.inner_dims['z']

            maker = Cube(width, depth, height, self.segs_w, self.segs_d, self.segs_h,
                         0, not self.invert, self.open_left, self.open_right, self.open_front,
                         self.open_back, self.open_top, self.open_bottom)

            # Connect the inner sphere to the outer sphere.
            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # import pdb; pdb.set_trace()
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'box')

        return geom_node


# class Cube(ProceduralGeometry):
#     """Create a geom node of cube or cuboid.
#         Arges:
#             width (float): dimension along the x-axis; more than zero
#             depth (float): dimension along the y-axis; more than zero
#             height (float): dimension along the z-axis; must be more than zero
#             segs_w (int) the number of subdivisions in width; positive integer
#             segs_d (int) the number of subdivisions in depth; positive integer
#             segs_h (int) the number of subdivisions in height; positive integer
#     """

#     def __init__(self, width=1.0, depth=1.0, height=1.0, segs_w=1, segs_d=1, segs_h=1):
#         super().__init__()
#         self.width = width
#         self.depth = depth
#         self.height = height
#         self.segs_w = segs_w
#         self.segs_d = segs_d
#         self.segs_h = segs_h
#         self.color = (1, 1, 1, 1)

#     def get_geom_node(self):
#         vdata_values = array.array('f', [])
#         prim_indices = array.array('H', [])

#         vertex = Point3()
#         segs = (self.segs_w, self.segs_d, self.segs_h)
#         dims = (self.width, self.depth, self.height)
#         segs_u = self.segs_w * 2 + self.segs_d * 2
#         vertex_cnt = 0
#         offset_u = 0

#         # (fixed, outer loop, inner loop, normal, uv)
#         side_idxes = [
#             (2, 0, 1, 1, False),     # top
#             (1, 0, 2, -1, False),    # front
#             (0, 1, 2, 1, False),     # right
#             (1, 0, 2, 1, True),      # back
#             (0, 1, 2, -1, True),     # left
#             (2, 0, 1, -1, False),    # bottom
#         ]

#         for a, (i0, i1, i2, n, reverse) in enumerate(side_idxes):
#             segs1 = segs[i1]
#             segs2 = segs[i2]
#             dim1_start = dims[i1] * -0.5
#             dim2_start = dims[i2] * -0.5

#             normal = Vec3()
#             normal[i0] = n
#             vertex[i0] = dims[i0] * 0.5 * n

#             for j in range(segs1 + 1):
#                 vertex[i1] = dim1_start + j / segs1 * dims[i1]

#                 if i0 == 2:
#                     u = j / segs1
#                 else:
#                     u = (segs1 - j + offset_u) / segs_u if reverse else (j + offset_u) / segs_u

#                 for k in range(segs2 + 1):
#                     vertex[i2] = dim2_start + k / segs2 * dims[i2]
#                     v = k / segs2
#                     vdata_values.extend(vertex)
#                     vdata_values.extend(self.color)
#                     vdata_values.extend(normal)
#                     vdata_values.extend((u, v))
#                 if j > 0:
#                     for k in range(segs2):
#                         idx = vertex_cnt + j * (segs2 + 1) + k
#                         prim_indices.extend((idx, idx - segs2 - 1, idx - segs2))
#                         prim_indices.extend((idx, idx - segs2, idx + 1))

#             vertex_cnt += (segs1 + 1) * (segs2 + 1)
#             offset_u += segs2

#         geom_node = self.create_geom_node(
#             vertex_cnt, vdata_values, prim_indices, 'plane')

#         return geom_node
