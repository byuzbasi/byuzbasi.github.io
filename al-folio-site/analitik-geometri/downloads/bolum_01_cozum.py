# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. H1 ve H2'nin yeniden hesaplanması ---
import numpy as np
from agbook import displacement, euclidean_distance, midpoint

a2, b2 = np.array([-3., 2.]), np.array([5., -4.])
a3, b3 = np.array([2., -1., 4.]), np.array([-2., 5., 0.])

computed = np.r_[displacement(a2, b2),
                 euclidean_distance(a2, b2),
                 midpoint(a3, b3),
                 euclidean_distance(a3, b3)]
expected = np.array([8., -6., 10., 0., 2., 2., 2*np.sqrt(17.)])
print(computed)
print(np.max(np.abs(computed - expected)))

# --- 2. 361 dönme matrisinin ortogonallik taraması ---
import numpy as np
from agbook import rotation_matrix_2d

residuals = []
for degree in range(361):
    q = rotation_matrix_2d(np.deg2rad(degree))
    residuals.append(np.linalg.norm(q.T @ q - np.eye(2)))

index = int(np.argmax(residuals))
print(index, f"{residuals[index]:.3e}")
print(max(residuals) < 1e-12)

# --- 3. Dört çıpayla gürültülü konum hesabı ---
import numpy as np
from agbook import trilaterate_linear

anchors = np.array([[0., 0.], [10., 0.],
                    [0., 8.], [10., 8.]])
truth = np.array([4., 3.])
rng = np.random.default_rng(20260907)
ranges = np.linalg.norm(anchors - truth, axis=1)
ranges += rng.normal(0., 0.02, size=4)
fit = trilaterate_linear(anchors, ranges)

print(fit.point)
print(fit.rank)
print(f"{fit.residual_norm:.6f}")
print(f"{np.linalg.norm(fit.point-truth):.6f}")

# --- 4. Rank ile koşulluluğun ayrılması ---
import numpy as np
from agbook import trilaterate_linear

target = np.array([0.5, 1.0])
collinear = np.array([[0., 0.], [1., 0.], [2., 0.]])
near = np.array([[0., 0.], [1., 0.], [2., 1e-8]])

try:
    trilaterate_linear(collinear,
                       np.linalg.norm(collinear-target, axis=1))
except ValueError as error:
    print(type(error).__name__)

ranges = np.linalg.norm(near-target, axis=1)
fit1 = trilaterate_linear(near, ranges)
ranges[-1] += 1e-10
fit2 = trilaterate_linear(near, ranges)
print(fit1.singular_values)
print(np.linalg.norm(fit2.point-fit1.point))
