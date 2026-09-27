# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Delik merkezlerinde şekil, tolerans ve iz kaydı ---
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
nominal = np.array([
    [0., 0.], [80., 0.], [80., 50.],
    [0., 50.], [40., 25.],
])
observed = np.array([
    [0.02, -0.01], [80.08, 0.04], [80.15, 50.04],
    [-0.04, 50.02], [40.095, 25.],
])
diag = point_set_tolerance_diagnostics(
    nominal,
    observed,
    specification_limit=0.10,
    measurement_uncertainty=0.02,
)

d0 = pairwise_distances(nominal)
d1 = pairwise_distances(observed)
matrix_residual = np.max(np.abs(d1 - d0))

numeric_centroid = np.mean(nominal, axis=0)
exact_centroid = Matrix([
    sum(Rational(str(v)) for v in nominal[:, axis]) / len(nominal)
    for axis in range(2)
])
centroid_check = geometric_close(
    numeric_centroid,
    np.array(exact_centroid, dtype=float).reshape(2),
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=80.,
)

rng_a = np.random.Generator(np.random.PCG64(SEED))
rng_b = np.random.Generator(np.random.PCG64(SEED))
z_a = rng_a.normal(0., 0.01, size=(2, 2))
z_b = rng_b.normal(0., 0.01, size=(2, 2))

print("birim: mm")
print("nominal_shape:", nominal.shape)
print("nokta_hatalari_mm:", np.round(diag.point_errors, 6))
print("nokta_siniflari:", diag.point_classifications)
print("genel_sinif:", diag.overall_classification)
print(f"en_buyuk_hata_mm: {diag.worst_error:.6f}")
print(f"uzaklik_matrisi_artigi_mm: {matrix_residual:.6f}")
print("merkez_yakin:", centroid_check.close)
print(f"tohumlu_tekrar_artigi: {np.max(np.abs(z_a-z_b)):.3e}")
print("girdi_sha256:", canonical_array_sha256(
    np.vstack([nominal, observed])
))
print("numpy_surumu:", version("numpy"))
print("sympy_surumu:", version("sympy"))
