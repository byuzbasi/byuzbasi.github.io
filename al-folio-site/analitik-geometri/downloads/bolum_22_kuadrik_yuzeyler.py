"""Bölüm 22: kuadrik yüzeyler laboratuvarı.

Uygulama, bilinen merkez, yarı eksen ve yönelime sahip sentetik bir üç
eksenli elipsoidi genel ikinci derece katsayılarına dönüştürür; ardından
merkezi, yarı eksenleri ve ana yönleri yalnız bu katsayılardan geri kazanır.
Veriler ölçülmüş değildir. Çalışma bir uyumlama, üretim toleransı veya kabul
modeli içermez.
"""

from __future__ import annotations

import math

import numpy as np

from agbook import (
    canonical_array_sha256,
    quadric_diagnostics,
    quadric_plane_trace,
    quadric_residuals,
    quadric_tangent_plane_diagnostics,
    quadratic_conic_diagnostics,
    transform_quadric,
)


def rotation_xyz(ax: float, ay: float, az: float) -> np.ndarray:
    """Sağ elli ``Rz(az) Ry(ay) Rx(ax)`` dönmesini kurar."""

    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=float)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=float)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=float)
    return rz @ ry @ rx


def world_coefficients(
    canonical_coefficients: np.ndarray,
    rotation: np.ndarray,
    center: np.ndarray,
) -> np.ndarray:
    """``X=center+rotation@Y`` modelini dünya katsayılarına çevirir."""

    return transform_quadric(
        canonical_coefficients,
        rotation.T,
        -rotation.T @ center,
    )


def main() -> None:
    length_unit = "mm"
    center_mm = np.array([120.0, -80.0, 45.0])
    semi_axes_mm = np.array([60.0, 35.0, 20.0])
    rotation = rotation_xyz(
        math.radians(15.0),
        math.radians(-20.0),
        math.radians(35.0),
    )
    canonical_coefficients = np.array(
        [
            1.0 / semi_axes_mm[0] ** 2,
            0.0,
            0.0,
            1.0 / semi_axes_mm[1] ** 2,
            0.0,
            1.0 / semi_axes_mm[2] ** 2,
            0.0,
            0.0,
            0.0,
            -1.0,
        ]
    )
    coefficients_mm = world_coefficients(
        canonical_coefficients,
        rotation,
        center_mm,
    )
    diagnostics_mm = quadric_diagnostics(
        coefficients_mm,
        coordinate_scale=100.0,
    )

    alignment = np.abs(rotation.T @ diagnostics_mm.principal_directions)
    principal_trace_types: list[str] = []
    principal_trace_axes: list[np.ndarray] = []
    for indices in ((0, 1), (0, 2), (1, 2)):
        basis = rotation[:, indices]
        trace = quadric_plane_trace(coefficients_mm, center_mm, basis)
        conic = quadratic_conic_diagnostics(
            trace.conic_coefficients,
            coordinate_scale=100.0,
        )
        principal_trace_types.append(conic.locus_type)
        principal_trace_axes.append(conic.semi_axes)

    surface_point_mm = center_mm + semi_axes_mm[0] * rotation[:, 0]
    tangent = quadric_tangent_plane_diagnostics(
        coefficients_mm,
        surface_point_mm,
        coordinate_scale=100.0,
        gradient_tolerance=1.0e-12,
        residual_tolerance=1.0e-12,
    )

    parameters = np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ]
    )
    surface_points_mm = center_mm + (parameters * semi_axes_mm) @ rotation.T
    residuals_mm = quadric_residuals(
        coefficients_mm,
        surface_points_mm,
        coordinate_scale=100.0,
    )

    motion = rotation_xyz(-0.19, 0.27, -0.41)
    translation_mm = np.array([-35.0, 70.0, 25.0])
    moved_coefficients = transform_quadric(
        coefficients_mm,
        motion.T,
        -motion.T @ translation_mm,
    )
    moved_diagnostics = quadric_diagnostics(
        moved_coefficients,
        coordinate_scale=100.0,
    )

    mm_per_m = 1000.0
    coefficients_m = coefficients_mm * np.array(
        [
            mm_per_m**2,
            mm_per_m**2,
            mm_per_m**2,
            mm_per_m**2,
            mm_per_m**2,
            mm_per_m**2,
            mm_per_m,
            mm_per_m,
            mm_per_m,
            1.0,
        ]
    )
    diagnostics_m = quadric_diagnostics(
        coefficients_m,
        coordinate_scale=0.1,
    )

    assert diagnostics_mm.locus_type == "ellipsoid"
    np.testing.assert_allclose(diagnostics_mm.center, center_mm, atol=3.0e-13)
    np.testing.assert_allclose(diagnostics_mm.semi_axes, semi_axes_mm, atol=3.0e-13)
    np.testing.assert_allclose(alignment, np.eye(3), atol=3.0e-14)
    assert principal_trace_types == ["ellipse", "ellipse", "ellipse"]
    np.testing.assert_allclose(principal_trace_axes[0], [60.0, 35.0])
    np.testing.assert_allclose(principal_trace_axes[1], [60.0, 20.0])
    np.testing.assert_allclose(principal_trace_axes[2], [35.0, 20.0])
    assert tangent.regular
    assert tangent.point_on_surface
    np.testing.assert_allclose(residuals_mm, np.zeros(6), atol=3.0e-15)
    assert moved_diagnostics.locus_type == "ellipsoid"
    np.testing.assert_allclose(moved_diagnostics.semi_axes, semi_axes_mm, atol=4.0e-13)
    np.testing.assert_allclose(
        moved_diagnostics.center,
        motion @ center_mm + translation_mm,
        atol=4.0e-13,
    )
    assert diagnostics_m.locus_type == "ellipsoid"
    np.testing.assert_allclose(diagnostics_m.center, center_mm / mm_per_m, atol=4.0e-16)
    np.testing.assert_allclose(
        diagnostics_m.semi_axes,
        semi_axes_mm / mm_per_m,
        atol=4.0e-16,
    )

    signature_values = np.concatenate(
        [
            center_mm,
            semi_axes_mm,
            rotation.ravel(),
            canonical_coefficients,
            coefficients_mm,
            diagnostics_mm.center,
            diagnostics_mm.semi_axes,
            diagnostics_mm.principal_directions.ravel(),
            np.concatenate(principal_trace_axes),
            surface_point_mm,
            tangent.gradient,
            tangent.plane_coefficients,
            surface_points_mm.ravel(),
            residuals_mm,
            moved_coefficients,
            diagnostics_m.center,
            diagnostics_m.semi_axes,
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_uc_eksenli_elipsoid")
    print("olculmus_veri_mi: False")
    print("uyumlama_yapildi_mi: False")
    print("uretim_toleransi_modeli_mi: False")
    print("merkez_mm:", diagnostics_mm.center)
    print("yari_eksenler_mm:", diagnostics_mm.semi_axes)
    print("sinif:", diagnostics_mm.locus_type)
    print("kuadratik_rank:", diagnostics_mm.quadratic_rank)
    print("atalet:", diagnostics_mm.inertia)
    print("ana_yon_hizalama_mutlak:")
    print(alignment)
    print("asal_iz_turleri:", principal_trace_types)
    print("asal_iz_yari_eksenleri_mm:", principal_trace_axes)
    print("teget_noktasi_mm:", surface_point_mm)
    print("teget_duzlem_katsayilari:", tangent.plane_coefficients)
    print("en_buyuk_normalize_artik:", f"{np.max(np.abs(residuals_mm)):.12e}")
    print("rijit_harekette_sinif_korundu_mu:", moved_diagnostics.locus_type == "ellipsoid")
    print("metrede_yari_eksenler:", diagnostics_m.semi_axes)
    print("goreli_siniflandirma_esigi:", diagnostics_mm.relative_tolerance)
    print("sayisal_belirsizlik_var_mi:", diagnostics_mm.numerically_ambiguous)
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
