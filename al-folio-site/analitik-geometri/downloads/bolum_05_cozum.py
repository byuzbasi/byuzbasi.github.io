# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. İki noktadan doğru ve artık ---
import numpy as np
from agbook import line_from_points, line_residuals, parametric_line_points

A = np.array([-1.0, 2.0])
B = np.array([3.0, 4.0])
line = line_from_points(A, B)
t = np.linspace(0.0, 1.0, 5)
points = parametric_line_points(A, B - A, t)
all_points = np.vstack([A, B, points])
residuals = line_residuals(line, all_points)

print(np.round(line, 12))
print(points.shape)
print(f"{np.max(np.abs(residuals)):.3e}")

# --- 2. Ortak ölçeği kaldırmak ---
import numpy as np
from agbook import canonical_line_coefficients

base = np.array([1.0, -2.0, 5.0])
scales = np.array([3.5, -7.0, 1.0e120, -1.0e-120])
canonical = np.vstack([
    canonical_line_coefficients(scale * base)
    for scale in scales
])
print(canonical)
print("en_buyuk_fark:", np.max(np.abs(canonical - canonical[0])))

# --- 3. Yatay, dikey ve geçersiz girdiler ---
from agbook import line_from_point_direction

print(line_from_point_direction([0.0, 4.0], [1.0, 0.0]))
print(line_from_point_direction([-3.0, 0.0], [0.0, 1.0]))

for point, direction in [
    ([0.0, 0.0], [0.0, 0.0]),
    ([0.0, 0.0, 1.0], [1.0, 0.0]),
]:
    try:
        line_from_point_direction(point, direction)
    except ValueError as error:
        print(type(error).__name__, str(error))

# --- 4. Üyelik kararının ölçek değişmezliği ---
import numpy as np
from agbook import line_membership_diagnostics

base = np.array([3.0, 4.0, -5.0])
point = np.array([1.0, 0.49])
for scale in [1.0e-6, 1.0, 1.0e6, -4.0]:
    result = line_membership_diagnostics(
        scale * base,
        point,
        absolute_tolerance=0.01,
        relative_tolerance=0.001,
        reference_scale=10.0,
    )
    print(scale, result.residual, result.threshold, result.on_line)
