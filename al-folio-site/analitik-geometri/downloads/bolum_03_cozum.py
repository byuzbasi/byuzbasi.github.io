# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Alternatiflik ve kesme artıkları ---
import numpy as np
from agbook import determinant_2d

pairs = [
    (np.array([3., -1.]), np.array([2., 4.])),
    (np.array([2.5, 0.8]), np.array([0.6, 2.2])),
    (np.array([-5., 7.]), np.array([3., 1.])),
]
lam = 3.25
residuals = []
for u, v in pairs:
    residuals.append(
        determinant_2d(u, v) + determinant_2d(v, u)
    )
    residuals.append(
        determinant_2d(u, v + lam*u) - determinant_2d(u, v)
    )
print(f"max_mutlak_artik: {max(map(abs, residuals)):.3e}")

# --- 2. Çokgen sırası, kapanış ve öteleme ---
import numpy as np
from agbook import polygon_signed_area

p = np.array([
    [0., 0.], [6., 0.], [7., 3.], [4.5, 5.], [1., 4.]
])
closed = np.vstack([p, p[0]])
shifted = p + np.array([1.0e9, -2.0e9])
for name, vertices in (
    ("ozgun", p),
    ("ters", p[::-1]),
    ("kapali", closed),
    ("otelenmis", shifted),
):
    print(name, f"{polygon_signed_area(vertices):.6f}")

# --- 3. Üç tolerans ve kesin determinant ---
import numpy as np
from sympy import Matrix
from agbook import orientation_diagnostics

points = np.array([
    [0., 0.], [1.0e8, 1.0e8], [2.0e8, 2.0e8 + 1.]
])
for tau in (1.0e-6, 1.0e-8, 1.0e-10):
    result = orientation_diagnostics(
        *points, relative_tolerance=tau
    )
    print(f"{tau:.0e}", result.classification,
          f"{result.normalized_determinant:.6e}")
exact = Matrix([
    [100000000, 100000000],
    [200000000, 200000001],
]).det()
print("kesin", exact)

# --- 4. Taşmayı yakalama ve işaret için ölçekleme ---
import numpy as np
from agbook import determinant_2d

u = np.array([1.0e308, 1.0e308])
v = np.array([1.0e308, -1.0e308])
try:
    determinant_2d(u, v)
except OverflowError as error:
    print("overflow:", type(error).__name__)

scale = 1.0e308
scaled_det = determinant_2d(u/scale, v/scale)
print(f"scaled_determinant: {scaled_det:.1f}")
print("sign:", int(np.sign(scaled_det)))
