"""Bölüm 14: hiperbolik TDOA konum belirleme laboratuvarı.

Model yalnız iki boyutlu, sabit yayılma hızlı, eşzamanlı saatli ve gürültüsüz
bir sistemi temsil eder. Çok yollu yayılım, engeller, kırılma, saat
sürüklenmesi, hız değişimi, sensör belirsizliği ve üç boyutlu konum modele
dahil değildir.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

from agbook import (
    canonical_array_sha256,
    hyperbola_diagnostics,
    hyperbola_frame_from_foci,
    rotation_matrix_2d,
)


def signed_distance_difference(
    point_m: np.ndarray,
    first_receiver_m: np.ndarray,
    second_receiver_m: np.ndarray,
) -> float:
    """İlk ve ikinci alıcıya uzaklıkların işaretli farkını metreyle verir."""

    return float(
        np.linalg.norm(point_m - first_receiver_m)
        - np.linalg.norm(point_m - second_receiver_m)
    )


def tdoa_residuals_m(
    point_m: np.ndarray,
    receivers_m: np.ndarray,
    measured_differences_m: np.ndarray,
) -> np.ndarray:
    """AB ve AC çiftlerinin model-ölçüm uzaklık farkı artıklarını verir."""

    receiver_a_m, receiver_b_m, receiver_c_m = receivers_m
    modeled_m = np.array(
        [
            signed_distance_difference(point_m, receiver_a_m, receiver_b_m),
            signed_distance_difference(point_m, receiver_a_m, receiver_c_m),
        ]
    )
    return modeled_m - measured_differences_m


def tdoa_jacobian(
    point_m: np.ndarray,
    receivers_m: np.ndarray,
    measured_differences_m: np.ndarray | None = None,
) -> np.ndarray:
    """İki uzaklık-fark denkleminin noktaya göre boyutsuz Jacobianını verir."""

    del measured_differences_m
    offsets = point_m - receivers_m
    distances_m = np.linalg.norm(offsets, axis=1)
    if np.any(distances_m == 0.0):
        raise ValueError("Kaynak konumu bir alıcıyla çakışamaz.")
    unit_directions = offsets / distances_m[:, None]
    return np.vstack(
        [
            unit_directions[0] - unit_directions[1],
            unit_directions[0] - unit_directions[2],
        ]
    )


def main() -> None:
    wave_speed_m_s = 343.0
    receivers_m = np.array(
        [
            [-6.0, 0.0],
            [6.0, 0.0],
            [0.0, 8.0],
        ]
    )
    true_source_m = np.array([2.0, 3.0])

    measured_differences_m = np.array(
        [
            signed_distance_difference(true_source_m, receivers_m[0], receivers_m[1]),
            signed_distance_difference(true_source_m, receivers_m[0], receivers_m[2]),
        ]
    )
    measured_tdoa_s = measured_differences_m / wave_speed_m_s

    pair_indices = ((0, 1), (0, 2))
    frames = []
    branches = []
    sample_diagnostics = []
    sample_parameters = np.linspace(-1.5, 1.5, 13)
    for difference_m, (first_index, second_index) in zip(
        measured_differences_m,
        pair_indices,
        strict=True,
    ):
        semi_transverse_m = 0.5 * abs(float(difference_m))
        frame = hyperbola_frame_from_foci(
            receivers_m[first_index],
            receivers_m[second_index],
            semi_transverse_m,
        )
        branch = 1 if difference_m > 0.0 else -1
        frames.append(frame)
        branches.append(branch)
        sample_diagnostics.append(
            hyperbola_diagnostics(
                frame.center,
                frame.transverse_direction,
                frame.semi_transverse,
                frame.semi_conjugate,
                sample_parameters,
                branch=branch,
            )
        )

    initial_guess_m = np.array([1.0, 2.0])
    result = least_squares(
        tdoa_residuals_m,
        initial_guess_m,
        jac=tdoa_jacobian,
        args=(receivers_m, measured_differences_m),
        method="trf",
        xtol=1e-14,
        ftol=1e-14,
        gtol=1e-14,
        max_nfev=100,
    )
    estimated_source_m = result.x
    final_residuals_m = tdoa_residuals_m(
        estimated_source_m,
        receivers_m,
        measured_differences_m,
    )
    position_error_m = float(np.linalg.norm(estimated_source_m - true_source_m))
    jacobian = tdoa_jacobian(estimated_source_m, receivers_m)
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    condition_number = float(singular_values[0] / singular_values[-1])

    assert result.success
    np.testing.assert_allclose(estimated_source_m, true_source_m, atol=2e-13)
    np.testing.assert_allclose(final_residuals_m, 0.0, atol=2e-13)
    assert np.linalg.matrix_rank(jacobian) == 2
    for difference_m, branch, diagnostic in zip(
        measured_differences_m,
        branches,
        sample_diagnostics,
        strict=True,
    ):
        np.testing.assert_allclose(
            diagnostic.signed_focal_differences,
            difference_m,
            atol=3e-14,
        )
        assert diagnostic.branch == branch
        assert diagnostic.maximum_absolute_algebraic_residual < 2e-14
        assert diagnostic.maximum_absolute_focal_difference_residual < 4e-14

    rotation = rotation_matrix_2d(np.deg2rad(29.0))
    translation_m = np.array([11.0, -4.0])
    moved_receivers_m = receivers_m @ rotation.T + translation_m
    moved_source_m = true_source_m @ rotation.T + translation_m
    moved_differences_m = np.array(
        [
            signed_distance_difference(
                moved_source_m,
                moved_receivers_m[first_index],
                moved_receivers_m[second_index],
            )
            for first_index, second_index in pair_indices
        ]
    )
    np.testing.assert_allclose(moved_differences_m, measured_differences_m, atol=3e-15)

    signature_values = np.concatenate(
        [
            np.array([wave_speed_m_s]),
            receivers_m.ravel(),
            true_source_m,
            measured_differences_m,
            measured_tdoa_s,
            initial_guess_m,
            estimated_source_m,
            final_residuals_m,
            jacobian.ravel(),
            singular_values,
            np.array(branches, dtype=float),
            sample_parameters,
            sample_diagnostics[0].points.ravel(),
            sample_diagnostics[1].points.ravel(),
            rotation.ravel(),
            translation_m,
            moved_receivers_m.ravel(),
            moved_source_m,
        ]
    )

    print("uzunluk_birimi: m")
    print("zaman_birimi: s")
    print("model: sentetik_iki_boyutlu_gurultusuz_tdoa")
    print("gercek_konumlandirma_sistemi_mi: False")
    print("yayilma_hizi_m_s:", wave_speed_m_s)
    print("alicilar_m:", receivers_m.tolist())
    print("gercek_kaynak_m:", true_source_m)
    print("olculen_uzaklik_farklari_m:", measured_differences_m)
    print("olculen_tdoa_s:", measured_tdoa_s)
    print("hiperbol_kollari:", branches)
    print("tahmin_edilen_kaynak_m:", estimated_source_m)
    print("konum_hatasi_m:", f"{position_error_m:.3e}")
    print("son_uzaklik_fark_artiklari_m:", final_residuals_m)
    print("jacobian_ranki:", int(np.linalg.matrix_rank(jacobian)))
    print("jacobian_kosul_sayisi:", f"{condition_number:.6f}")
    print(
        "en_buyuk_ornekleme_cebirsel_artigi:",
        f"{max(d.maximum_absolute_algebraic_residual for d in sample_diagnostics):.3e}",
    )
    print(
        "en_buyuk_ornekleme_odak_fark_artigi_m:",
        f"{max(d.maximum_absolute_focal_difference_residual for d in sample_diagnostics):.3e}",
    )
    print("rijit_harekette_olculer_korundu_mu:", bool(np.allclose(moved_differences_m, measured_differences_m)))
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
