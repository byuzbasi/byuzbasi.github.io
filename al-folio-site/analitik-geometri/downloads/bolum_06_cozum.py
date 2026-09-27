# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Üç doğru ilişkisini sınıflandırma ---
import numpy as np
from agbook import line_intersection_diagnostics

pairs = {
    "kesisen": ([1.0, 1.0, -3.0], [1.0, -1.0, -1.0]),
    "ayri_paralel": ([1.0, 2.0, -3.0], [-2.0, -4.0, 10.0]),
    "cakisan": ([1.0, 2.0, -3.0], [-5.0, -10.0, 15.0]),
}
for name, (first, second) in pairs.items():
    result = line_intersection_diagnostics(
        first, second,
        angular_tolerance=1e-12,
        absolute_tolerance=1e-10,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )
    print(name, result.relation)
    if result.point is not None:
        print(np.round(result.point, 12), result.residuals)

# --- 2. Yakın paralellik tablosu ---
import numpy as np
from agbook import line_angle, line_intersection_diagnostics

for k in (2, 4, 6, 8, 10):
    eps = 10.0 ** (-k)
    second = [eps, 1.0, -1.0]
    result = line_intersection_diagnostics(
        [0.0, 1.0, 0.0], second,
        angular_tolerance=0.0,
        absolute_tolerance=0.0,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )
    print(k, np.degrees(line_angle([0, 1, 0], second)),
          result.condition_number, result.point[0])

# --- 3. Üç doğru için dikme ayağı denetimi ---
import numpy as np
from agbook import project_point_to_line

cases = (
    ([0.0, 1.0, -2.0], [3.0, 5.0]),
    ([1.0, 0.0, 4.0], [2.0, -1.0]),
    ([3.0, 4.0, -5.0], [4.0, 1.0]),
)
for line, point in cases:
    result = project_point_to_line(line, point)
    assert abs(result.foot_residual) < 1e-12
    assert abs(result.orthogonality_residual) < 1e-12
    print(np.round(result.foot, 12), result.distance)

# --- 4. Doğru demetinde ölçek değişmezliği ---
import numpy as np
from agbook import line_pencil_member

first = line_pencil_member(
    [1.0, 0.0, -1.0], [0.0, 1.0, -2.0],
    2.0, -3.0, angular_tolerance=1e-12,
)
second = line_pencil_member(
    [-7.0, 0.0, 7.0], [0.0, 5.0, -10.0],
    -20.0, 30.0, angular_tolerance=1e-12,
)
print(first)
print(second)
print(np.max(np.abs(first - second)))
