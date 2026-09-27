"""Bölüm 21: silindir, koni ve dönel yüzeyler laboratuvarı.

Uygulama, milimetre cinsinden tanımlanmış sentetik ve parçalı doğrusal bir
profilin keyfi bir eksen çevresinde tam tur döndürülmesini inceler. Profil iki
silindirik parça ile aradaki bir konik kesik parçadan oluşur. Hesap yalnız yan
yüzey geometrisidir; kapak, et kalınlığı, yuvarlatma, üretim toleransı ve
yapısal yeterlilik modeli içermez.
"""

from __future__ import annotations

import math

import numpy as np

from agbook import (
    axis_frame_3d,
    canonical_array_sha256,
    circular_cone_diagnostics,
    circular_cylinder_diagnostics,
    piecewise_linear_revolution_diagnostics,
    revolution_surface_point_diagnostics,
    surface_of_revolution_points,
)


def main() -> None:
    length_unit = "mm"
    axis_point_mm = np.array([40.0, -25.0, 15.0])
    axis_direction = np.array([2.0, -1.0, 2.0])
    radial_reference = np.array([1.0, 2.0, 0.0])
    axial_mm = np.array([0.0, 30.0, 60.0, 90.0])
    radial_mm = np.array([18.0, 18.0, 12.0, 12.0])
    angles_rad = np.linspace(0.0, 2.0 * math.pi, 73)
    absolute_tolerance_mm = 1.0e-10

    frame = axis_frame_3d(
        axis_point_mm,
        axis_direction,
        radial_reference=radial_reference,
    )
    profile = piecewise_linear_revolution_diagnostics(axial_mm, radial_mm)
    mesh_mm = surface_of_revolution_points(
        axis_point_mm,
        axis_direction,
        axial_mm,
        radial_mm,
        angles_rad,
        radial_reference=radial_reference,
    )

    first_cylinder_point = mesh_mm[0, 11]
    second_cylinder_point = mesh_mm[-1, 29]
    first_cylinder = circular_cylinder_diagnostics(
        axis_point_mm,
        axis_direction,
        18.0,
        first_cylinder_point,
        axial_bounds=(0.0, 30.0),
        absolute_tolerance=absolute_tolerance_mm,
        reference_scale=90.0,
    )
    second_cylinder = circular_cylinder_diagnostics(
        axis_point_mm,
        axis_direction,
        12.0,
        second_cylinder_point,
        axial_bounds=(60.0, 90.0),
        absolute_tolerance=absolute_tolerance_mm,
        reference_scale=90.0,
    )

    frustum_half_angle = math.atan(0.2)
    virtual_apex_mm = axis_point_mm + 120.0 * frame.unit_axis
    frustum_point = mesh_mm[1, 17]
    frustum_cone = circular_cone_diagnostics(
        virtual_apex_mm,
        -frame.unit_axis,
        frustum_half_angle,
        frustum_point,
        nappe="positive",
        absolute_tolerance=absolute_tolerance_mm,
        reference_scale=120.0,
    )

    cylindrical_regular_point = revolution_surface_point_diagnostics(
        axis_point_mm,
        axis_direction,
        axial_coordinate=15.0,
        radial_coordinate=18.0,
        axial_derivative=1.0,
        radial_derivative=0.0,
        angle=0.7,
        radial_reference=radial_reference,
    )
    frustum_regular_point = revolution_surface_point_diagnostics(
        axis_point_mm,
        axis_direction,
        axial_coordinate=45.0,
        radial_coordinate=15.0,
        axial_derivative=1.0,
        radial_derivative=-0.2,
        angle=1.1,
        radial_reference=radial_reference,
    )
    axis_singularity = revolution_surface_point_diagnostics(
        axis_point_mm,
        axis_direction,
        axial_coordinate=0.0,
        radial_coordinate=0.0,
        axial_derivative=1.0,
        radial_derivative=1.0,
        angle=0.0,
        radial_reference=radial_reference,
    )

    rotation = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    translation_mm = np.array([125.0, 60.0, -40.0])
    moved_mesh_mm = surface_of_revolution_points(
        rotation @ axis_point_mm + translation_mm,
        rotation @ axis_direction,
        axial_mm,
        radial_mm,
        angles_rad,
        radial_reference=rotation @ radial_reference,
    )
    expected_moved_mesh_mm = mesh_mm @ rotation.T + translation_mm

    metre_scale = 0.001
    profile_m = piecewise_linear_revolution_diagnostics(
        metre_scale * axial_mm,
        metre_scale * radial_mm,
    )

    expected_slant_lengths_mm = np.array([30.0, 6.0 * math.sqrt(26.0), 30.0])
    expected_areas_mm2 = np.array(
        [
            1080.0 * math.pi,
            180.0 * math.pi * math.sqrt(26.0),
            720.0 * math.pi,
        ]
    )
    expected_total_area_mm2 = 180.0 * math.pi * (10.0 + math.sqrt(26.0))

    assert profile.segment_types == ("cylinder", "frustum", "cylinder")
    np.testing.assert_allclose(profile.slant_lengths, expected_slant_lengths_mm)
    np.testing.assert_allclose(profile.segment_lateral_areas, expected_areas_mm2)
    np.testing.assert_allclose(profile.total_lateral_area, expected_total_area_mm2)
    assert profile.smooth_interior_joins == (False, False)
    assert mesh_mm.shape == (4, 73, 3)
    np.testing.assert_allclose(mesh_mm[:, 0], mesh_mm[:, -1], atol=2.0e-14)
    assert first_cylinder.lateral_surface_member
    assert second_cylinder.lateral_surface_member
    assert frustum_cone.relation == "on_surface"
    assert frustum_cone.allowed_nappe
    assert cylindrical_regular_point.regular
    assert frustum_regular_point.regular
    assert not axis_singularity.regular
    assert axis_singularity.is_axis_point
    np.testing.assert_allclose(moved_mesh_mm, expected_moved_mesh_mm, atol=3.0e-14)
    np.testing.assert_allclose(
        profile_m.total_lateral_area,
        metre_scale**2 * profile.total_lateral_area,
        rtol=3.0e-16,
    )

    signature_values = np.concatenate(
        [
            axis_point_mm,
            axis_direction,
            radial_reference,
            frame.unit_axis,
            frame.radial_u,
            frame.radial_v,
            axial_mm,
            radial_mm,
            angles_rad,
            profile.slant_lengths,
            profile.segment_lateral_areas,
            np.array([profile.total_lateral_area]),
            mesh_mm.ravel(),
            virtual_apex_mm,
            np.array(
                [
                    frustum_half_angle,
                    frustum_cone.implicit_residual,
                    cylindrical_regular_point.area_density,
                    frustum_regular_point.area_density,
                    profile_m.total_lateral_area,
                    absolute_tolerance_mm,
                ]
            ),
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_parcali_dogrusal_donel_yan_yuzey")
    print("olculmus_veri_mi: False")
    print("kapak_var_mi: False")
    print("et_kalinligi_var_mi: False")
    print("yuvarlatma_var_mi: False")
    print("uretim_toleransi_modeli_mi: False")
    print("yapisal_yeterlilik_modeli_mi: False")
    print("eksen_noktasi_mm:", axis_point_mm)
    print("eksen_birim_yonu:", frame.unit_axis)
    print("profil_s_mm:", axial_mm)
    print("profil_rho_mm:", radial_mm)
    print("segment_turleri:", profile.segment_types)
    print("egik_uzunluklar_mm:", profile.slant_lengths)
    print("segment_yan_alanlari_mm2:", profile.segment_lateral_areas)
    print("toplam_yan_alan_mm2:", f"{profile.total_lateral_area:.12f}")
    print("ic_birlesimler_duzgun_mu:", profile.smooth_interior_joins)
    print("ilk_silindir_yuzey_uyesi_mi:", first_cylinder.lateral_surface_member)
    print("ikinci_silindir_yuzey_uyesi_mi:", second_cylinder.lateral_surface_member)
    print("konik_kesik_noktasi_koni_uzerinde_mi:", frustum_cone.relation == "on_surface")
    print("rijit_harekette_ag_korundu_mu:", np.allclose(moved_mesh_mm, expected_moved_mesh_mm))
    print(
        "mm2_den_m2_ye_alan_orani:",
        f"{profile_m.total_lateral_area / profile.total_lateral_area:.12e}",
    )
    print("eksen_noktasi_duzenli_mi:", axis_singularity.regular)
    print("sayisal_siniflandirma_esigi_mm:", f"{absolute_tolerance_mm:.12e}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
