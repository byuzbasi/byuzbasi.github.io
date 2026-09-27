"""Bölüm 4 laboratuvarı: CAD delik merkezi ölçümlerini denetleme."""

from __future__ import annotations

from importlib.metadata import version

import numpy as np
from sympy import Matrix, Rational

from agbook import (
    canonical_array_sha256,
    geometric_close,
    pairwise_distances,
    point_set_tolerance_diagnostics,
)


SEED = 20260907


def main() -> None:
    # Bütün koordinatlar, şartname sınırı ve belirsizlik milimetredir.
    nominal = np.array(
        [[0.0, 0.0], [80.0, 0.0], [80.0, 50.0], [0.0, 50.0], [40.0, 25.0]]
    )
    observed = np.array(
        [[0.02, -0.01], [80.08, 0.04], [80.15, 50.04], [-0.04, 50.02], [40.095, 25.0]]
    )
    diagnostics = point_set_tolerance_diagnostics(
        nominal,
        observed,
        specification_limit=0.10,
        measurement_uncertainty=0.02,
    )

    nominal_distances = pairwise_distances(nominal)
    observed_distances = pairwise_distances(observed)
    distance_matrix_residual = float(np.max(np.abs(observed_distances - nominal_distances)))

    numeric_centroid = np.mean(nominal, axis=0)
    exact_centroid = Matrix(
        [
            sum(Rational(str(value)) for value in nominal[:, axis]) / nominal.shape[0]
            for axis in range(nominal.shape[1])
        ]
    )
    centroid_check = geometric_close(
        numeric_centroid,
        np.array(exact_centroid, dtype=float).reshape(2),
        absolute_tolerance=1.0e-12,
        relative_tolerance=1.0e-12,
        reference_scale=80.0,
    )

    generator_a = np.random.Generator(np.random.PCG64(SEED))
    generator_b = np.random.Generator(np.random.PCG64(SEED))
    seeded_a = generator_a.normal(0.0, 0.01, size=(2, 2))
    seeded_b = generator_b.normal(0.0, 0.01, size=(2, 2))

    combined_hash = canonical_array_sha256(np.vstack([nominal, observed]))
    print("birim: mm")
    print(f"nominal_shape: {nominal.shape}")
    print(f"observed_shape: {observed.shape}")
    print("nokta_hatalari_mm:", np.round(diagnostics.point_errors, 6))
    print("nokta_siniflari:", diagnostics.point_classifications)
    print(f"genel_sinif: {diagnostics.overall_classification}")
    print(f"en_buyuk_hata_mm: {diagnostics.worst_error:.6f}")
    print(f"en_buyuk_hata_indisi: {diagnostics.worst_index}")
    print(f"uzaklik_matrisi_artigi_mm: {distance_matrix_residual:.6f}")
    print(f"kesin_merkez: {tuple(exact_centroid)}")
    print(f"merkez_yakin: {centroid_check.close}")
    print(f"tohum: {SEED}")
    print("bit_uretici: PCG64")
    print(f"tohumlu_tekrar_artigi: {np.max(np.abs(seeded_a - seeded_b)):.3e}")
    print(f"girdi_sha256: {combined_hash}")
    print(f"numpy_surumu: {version('numpy')}")
    print(f"sympy_surumu: {version('sympy')}")


if __name__ == "__main__":
    main()
