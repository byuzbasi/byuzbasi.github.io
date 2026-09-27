"""Bölüm 23: sayısal kararlılık ve geometrik model uydurma laboratuvarı.

Sabit tohumlu sentetik bir ölçüm plakası üzerinde doğru, çember, elips ve
elipsoid uydurulur. Veriler gerçek ölçüm değildir; bütün uzunluklar mm'dir.
Tek kirletilmiş çember noktası açıkça korunur ve sağlam kayıp yalnız belirtilen
ölçekle etkinleştirilir. Hiçbir gözlem silinmez veya yeniden kodlanmaz.
"""

from __future__ import annotations

import math

import numpy as np

from agbook import (
    canonical_array_sha256,
    fit_circle_geometric,
    fit_ellipse_direct,
    fit_line_tls,
    fit_line_vertical_ols,
    fit_quadric_implicit,
)


def rotation_2d(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]])


def rotation_xyz(ax: float, ay: float, az: float) -> np.ndarray:
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=float)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=float)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=float)
    return rz @ ry @ rx


def main() -> None:
    seed = 2301
    rng = np.random.default_rng(seed)
    length_unit = "mm"

    line_direction = np.array([0.82, 0.5723635208501674])
    line_normal = np.array([-line_direction[1], line_direction[0]])
    line_parameter = np.linspace(-55.0, 55.0, 70)
    line_points = np.array([-25.0, 18.0]) + line_parameter[:, None] * line_direction
    line_points += rng.normal(scale=0.35, size=(line_parameter.size, 1)) * line_normal
    line_tls = fit_line_tls(line_points)
    line_ols = fit_line_vertical_ols(line_points)

    circle_center = np.array([42.0, -28.0])
    circle_radius = 24.0
    circle_theta = np.linspace(0.0, 2.0 * np.pi, 72, endpoint=False)
    circle_radial = circle_radius + rng.normal(scale=0.28, size=circle_theta.size)
    circle_points = circle_center + circle_radial[:, None] * np.column_stack(
        (np.cos(circle_theta), np.sin(circle_theta))
    )
    contaminated_index = 9
    circle_points[contaminated_index] += np.array([11.0, -7.0])
    circle_least_squares = fit_circle_geometric(
        circle_points,
        measurement_sigma=0.28,
    )
    circle_robust = fit_circle_geometric(
        circle_points,
        loss="soft_l1",
        loss_scale=0.6,
    )

    ellipse_center = np.array([-36.0, 31.0])
    ellipse_axes = np.array([30.0, 13.0])
    ellipse_rotation = rotation_2d(math.radians(27.0))
    ellipse_theta = np.linspace(0.0, 2.0 * np.pi, 100, endpoint=False)
    ellipse_local = np.column_stack(
        (ellipse_axes[0] * np.cos(ellipse_theta), ellipse_axes[1] * np.sin(ellipse_theta))
    )
    ellipse_points = ellipse_local @ ellipse_rotation.T + ellipse_center
    ellipse_points += rng.normal(scale=0.18, size=ellipse_points.shape)
    ellipse_fit = fit_ellipse_direct(ellipse_points)

    ellipsoid_center = np.array([18.0, -12.0, 9.0])
    ellipsoid_axes = np.array([21.0, 14.0, 8.0])
    ellipsoid_rotation = rotation_xyz(0.22, -0.31, 0.47)
    azimuth = np.linspace(0.0, 2.0 * np.pi, 18, endpoint=False)
    polar = np.linspace(0.22, np.pi - 0.22, 9)
    aa, pp = np.meshgrid(azimuth, polar)
    ellipsoid_local = np.column_stack(
        (
            ellipsoid_axes[0] * np.sin(pp.ravel()) * np.cos(aa.ravel()),
            ellipsoid_axes[1] * np.sin(pp.ravel()) * np.sin(aa.ravel()),
            ellipsoid_axes[2] * np.cos(pp.ravel()),
        )
    )
    ellipsoid_points = ellipsoid_local @ ellipsoid_rotation.T + ellipsoid_center
    ellipsoid_points += rng.normal(scale=0.12, size=ellipsoid_points.shape)
    quadric_fit = fit_quadric_implicit(ellipsoid_points)

    assert abs(line_tls.direction @ line_direction) > 0.99999
    assert line_tls.rms_orthogonal < 0.45
    assert circle_least_squares.final_sum_squares <= circle_least_squares.initial_sum_squares
    assert np.linalg.norm(circle_robust.center - circle_center) < np.linalg.norm(
        circle_least_squares.center - circle_center
    )
    assert abs(circle_robust.radius - circle_radius) < abs(
        circle_least_squares.radius - circle_radius
    )
    assert ellipse_fit.conic_diagnostics.locus_type == "ellipse"
    assert quadric_fit.quadric_diagnostics.locus_type == "ellipsoid"
    np.testing.assert_allclose(
        ellipse_fit.conic_diagnostics.center,
        ellipse_center,
        atol=0.15,
    )
    np.testing.assert_allclose(
        np.sort(ellipse_fit.conic_diagnostics.semi_axes),
        np.sort(ellipse_axes),
        atol=0.2,
    )
    np.testing.assert_allclose(
        quadric_fit.quadric_diagnostics.center,
        ellipsoid_center,
        atol=0.12,
    )
    np.testing.assert_allclose(
        np.sort(quadric_fit.quadric_diagnostics.semi_axes),
        np.sort(ellipsoid_axes),
        atol=0.15,
    )

    signature_values = np.concatenate(
        (
            line_points.ravel(),
            line_tls.coefficients,
            [line_tls.rms_orthogonal, line_ols.rms_vertical],
            circle_points.ravel(),
            circle_least_squares.center,
            [circle_least_squares.radius, circle_least_squares.rms_geometric],
            circle_robust.center,
            [circle_robust.radius, circle_robust.rms_geometric],
            ellipse_points.ravel(),
            ellipse_fit.coefficients,
            ellipse_fit.conic_diagnostics.center,
            ellipse_fit.conic_diagnostics.semi_axes,
            ellipsoid_points.ravel(),
            quadric_fit.coefficients,
            quadric_fit.quadric_diagnostics.center,
            quadric_fit.quadric_diagnostics.semi_axes,
        )
    )

    print("tohum:", seed)
    print("uzunluk_birimi:", length_unit)
    print("veri: sentetik_olcum_plakasi")
    print("olculmus_veri_mi: False")
    print("eksik_deger_islemi: yok")
    print("gozlem_silindi_mi: False")
    print("dogru_tls_katsayilari:", line_tls.coefficients)
    print("dogru_tls_rms_mm:", f"{line_tls.rms_orthogonal:.9f}")
    print("dogru_ols_dikey_rms_mm:", f"{line_ols.rms_vertical:.9f}")
    print("cember_kirletilmis_indis:", contaminated_index)
    print("cember_ls_merkez_mm:", circle_least_squares.center)
    print("cember_ls_yaricap_mm:", f"{circle_least_squares.radius:.9f}")
    print("cember_ls_standart_hatalar_mm:", circle_least_squares.standard_errors)
    print("cember_robust_merkez_mm:", circle_robust.center)
    print("cember_robust_yaricap_mm:", f"{circle_robust.radius:.9f}")
    print("cember_robust_kayip:", circle_robust.loss)
    print("cember_robust_kayip_olcegi_mm:", circle_robust.loss_scale)
    print("elips_sinifi:", ellipse_fit.conic_diagnostics.locus_type)
    print("elips_merkez_mm:", ellipse_fit.conic_diagnostics.center)
    print("elips_yari_eksenler_mm:", ellipse_fit.conic_diagnostics.semi_axes)
    print("elips_tasarim_ranki:", ellipse_fit.diagnostics.effective_rank)
    print("elips_nullspace_araligi:", ellipse_fit.diagnostics.nullspace_gap)
    print("kuadrik_sinifi:", quadric_fit.quadric_diagnostics.locus_type)
    print("kuadrik_merkez_mm:", quadric_fit.quadric_diagnostics.center)
    print("kuadrik_yari_eksenler_mm:", quadric_fit.quadric_diagnostics.semi_axes)
    print("kuadrik_tasarim_ranki:", quadric_fit.diagnostics.effective_rank)
    print("kuadrik_nullspace_araligi:", quadric_fit.diagnostics.nullspace_gap)
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
