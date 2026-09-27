# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Ardışık ve bileşik afin dönüşüm ---
import numpy as np
from agbook import apply_affine_map, compose_affine_maps

points = np.array([[0., 0.], [2., 1.], [-1., 3.], [4., -2.]])
A1 = np.array([[1., 0.6], [0., 1.]])
b1 = np.array([2., -1.])
A2 = np.array([[1.8, 0.], [0., 0.5]])
b2 = np.array([-3., 4.])

sequential = apply_affine_map(apply_affine_map(points, A1, b1), A2, b2)
combined = compose_affine_maps(A2, b2, A1, b1)
direct = apply_affine_map(points, combined.matrix, combined.translation)

residual = np.max(np.abs(direct - sequential))
det_residual = abs(combined.determinant - np.linalg.det(A2)*np.linalg.det(A1))
print(residual, det_residual)
assert residual < 1e-12
assert det_residual < 1e-12

# --- 2. Alan ölçeği ve tekil çökme ---
import numpy as np
from agbook import apply_affine_map, polygon_signed_area

polygon = np.array([[0., 0.], [4., 0.], [3., 2.], [0., 1.]])
A = np.array([[1.5, 0.75], [0., -2.]])
image = apply_affine_map(polygon, A, [10., -8.])
ratio = polygon_signed_area(image) / polygon_signed_area(polygon)
print("oran:", ratio, "det:", np.linalg.det(A))
assert abs(ratio - np.linalg.det(A)) < 1e-12

singular = np.array([[1., 0.6], [0.5, 0.3]])
collapsed = apply_affine_map(polygon, singular, [0., 0.])
print("tekil_alan:", polygon_signed_area(collapsed))
assert abs(polygon_signed_area(collapsed)) < 1e-12

# --- 3. Kartezyen--kutupsal gidiş dönüş ---
import numpy as np
from agbook import cartesian_to_polar, polar_to_cartesian

points = np.array([
    [2., 3.], [-4., 5.], [-6., -1.5], [7., -2.], [0., 0.]
])
polar = cartesian_to_polar(points)
recovered = polar_to_cartesian(polar)
residual = np.max(np.abs(recovered - points))
print("artik:", residual)
print("orijin_kutupsal:", polar[-1])
assert residual < 1e-12
assert np.array_equal(polar[-1], [0., 0.])

# --- 4. Determinant, rank, koşul ve açık hata ---
import numpy as np
import pytest
from agbook import inverse_affine_map

matrices = {
    "iyi": np.array([[1.2, 0.1], [0.0, 0.9]]),
    "kotu": np.diag([1.0, 1.0e-10]),
    "tekil": np.array([[1.0, 2.0], [2.0, 4.0]]),
}
for name, A in matrices.items():
    print(name, np.linalg.det(A), np.linalg.matrix_rank(A), np.linalg.cond(A))

with pytest.raises(ValueError, match="tekildir"):
    inverse_affine_map(matrices["tekil"], [0.0, 0.0])
