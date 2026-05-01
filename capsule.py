import array

from panda3d.core import Point3

from .create_geometry import ProceduralGeometry
from .cylinder import BasicCylinder
from .sphere import CapsuleHemisphere


class Capsule(BasicCylinder, ProceduralGeometry):
    """A class to creates a capsule.

       Args:
            radius (float): the radius of the capsule; must be greater than 0; default is 1.
            inner_radius (float):
                the inner radius of the capsule.
                0 <= inner_radius <= radius; default is 0.
            height (float):
                length of the capsule mantle.
                capsule total height is this height + radius * 2.
                must be greater than 0; default is 1.
            segs_c (int): subdivisions of the mantle along a circular cross-section; mininum is 3; default is 40.
            segs_a (int): subdivisions of the mantle along the axis of rotation; minimum is 1 ; default is 2.
            ring_slice_deg (float):
                the angle of the pie slice removed from the capsule, in degrees.
                0 <= ring_slice_deg <= 360; default is 0.
            top_hemisphere (bool): True, a top hemisphere is created; default is True.
            bottom_hemisphere (bool): True, a bottom hemisphere is created; default is True.
            slice_caps_radial (int): subdivisions of both slice caps, along the radius; minimum is 0; default is 2.
            slice_caps_axial (int): subdivisions of both slice caps, along the axis of rotation; minimum is 0; default is 2.
            invert (bool): whether or not the geometry should be rendered inside-out; default is False.
    """

    def __init__(self, radius=1., inner_radius=0., height=1., segs_c=40, segs_a=2, ring_slice_deg=0, slice_caps_radial=2,
                 slice_caps_axial=2, top_hemisphere=True, bottom_hemisphere=True, invert=False):
        self.radius = radius
        self.inner_radius = inner_radius
        self.height = height
        self.segs_c = segs_c
        self.segs_a = segs_a

        segs_cap = 2 if radius - inner_radius <= 4 else int(radius / 2)
        self.segs_tc = 0 if top_hemisphere else segs_cap
        self.segs_bc = 0 if bottom_hemisphere else segs_cap
        self.ring_slice_deg = ring_slice_deg
        self.segs_sc_r = slice_caps_radial
        self.segs_sc_a = slice_caps_axial
        self.invert = invert

        self.top_hemisphere = top_hemisphere
        self.bottom_hemisphere = bottom_hemisphere

        self.color = (1, 1, 1, 1)
        self.slice_caps = [True, False]

    def create_hemisphere(self, vertex_cnt, vdata_values, prim_indices,
                          center, bottom_clip=-1, top_clip=1):
        hemi = CapsuleHemisphere(
            center=center,
            radius=self.radius,
            inner_radius=self.inner_radius,
            segs_h=self.segs_c,
            segs_v=int(self.segs_c / 2),
            slice_deg=self.ring_slice_deg,
            segs_slice_caps=self.segs_sc_r,
            top_clip=top_clip,
            bottom_clip=bottom_clip,
            invert=self.invert
        )

        cnt, index_offset = hemi.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += cnt
        vertex_cnt += hemi.create_mantle_quads(index_offset, vdata_values, prim_indices)
        vertex_cnt += hemi.create_top(vertex_cnt, vdata_values, prim_indices)

        if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
            vertex_cnt += hemi.create_slice_cap(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_bottom(self, vertex_cnt, vdata_values, prim_indices):
        if self.bottom_hemisphere:
            center = Point3(0, 0, 0)
            vertex_cnt = self.create_hemisphere(
                vertex_cnt, vdata_values, prim_indices, center, top_clip=0
            )

        return vertex_cnt

    def create_mantle(self, vertex_cnt, vdata_values, prim_indices):
        vertex_cnt = self.create_cylinder(vertex_cnt, vdata_values, prim_indices)

        if self.ring_slice_deg and self.segs_sc_r and self.segs_sc_a:
            vertex_cnt += self.create_slice_cap_quads(vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def create_top(self, vertex_cnt, vdata_values, prim_indices):
        if self.top_hemisphere:
            center = Point3(0, 0, self.height)
            vertex_cnt = self.create_hemisphere(
                vertex_cnt, vdata_values, prim_indices, center, bottom_clip=0
            )

        return vertex_cnt

    def get_geom_node(self):
        self.define_variables()

        # Create an outer capusule.
        vdata_values = array.array('f', [])
        prim_indices = array.array('H', [])
        vertex_cnt = 0

        vertex_cnt = self.create_bottom(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_mantle(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt = self.create_top(vertex_cnt, vdata_values, prim_indices)

        # Create an inner capsule to connect to the outer one.
        if self.inner_radius:
            maker = Capsule(
                radius=self.inner_radius,
                inner_radius=0,
                height=self.height,
                segs_c=self.segs_c,
                segs_a=self.segs_a,
                top_hemisphere=self.top_hemisphere,
                bottom_hemisphere=self.bottom_hemisphere,
                ring_slice_deg=self.ring_slice_deg,
                slice_caps_radial=0,
                slice_caps_axial=0,
                invert=not self.invert
            )

            maker.segs_tc = 0
            maker.segs_bc = 0

            geom_node = maker.get_geom_node()
            self.add(geom_node, vdata_values, vertex_cnt, prim_indices)
            return geom_node

        # Create the capsule geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, self.__class__.__name__.lower())
        return geom_node