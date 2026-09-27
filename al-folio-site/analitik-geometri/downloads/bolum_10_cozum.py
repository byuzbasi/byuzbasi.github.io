# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Genel çember sınıfları ve ölçek değişmezliği ---
import numpy as np
from agbook import general_circle_diagnostics

cases = [
    [1., -4., 2., -4.],  # r^2=9
    [1., -4., 2.,  5.],  # r^2=0
    [1., -4., 2.,  7.],  # r^2=-2
]
for coefficients in cases:
    first = general_circle_diagnostics(coefficients)
    second = general_circle_diagnostics(
        -7.0 * np.array(coefficients)
    )
    print(first.locus_type, first.center,
          first.radius_squared)
    print(np.max(np.abs(first.center-second.center)),
          first.radius_squared-second.radius_squared)

# --- 2. Ayrık, teğet ve kesen doğrular ---
from agbook import circle_line_intersections

tol = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=10.0,
)
for line in ([0, 1, -8], [0, 1, -7], [1, 0, -1]):
    out = circle_line_intersections(
        [1, 2], 5, line, **tol
    )
    print(out.relation, out.points.shape,
          out.chord_length)
    print(out.line_residuals, out.radial_residuals)

# --- 3. Temas, diklik ve kutupsal artıkları ---
import numpy as np
from agbook import (
    polar_line_of_point,
    tangent_points_from_point,
)

tol = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
C, r, A = np.zeros(2), 5.0, np.array([13., 0.])
out = tangent_points_from_point(C, r, A, **tol)
polar = polar_line_of_point(C, r, A)
print(out.relation, out.points)
print(out.radial_residuals)
print(out.orthogonality_residuals)
print(out.points @ polar[:2] + polar[2])

inside = tangent_points_from_point(
    C, r, [1., 0.], **tol
)
print(inside.relation, inside.points.shape)

# --- 4. Rijit çerçevede kesişim değişmezliği ---
import numpy as np
from agbook import (
    circle_line_intersections,
    rotation_matrix_2d,
)

tol = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=10.0,
)
C = np.array([1., 2.])
line = np.array([0., 1., -4.])
before = circle_line_intersections(C, 5., line, **tol)

Q = rotation_matrix_2d(np.deg2rad(37.0))
b = np.array([8., -3.])
Cm = Q @ C + b
nm = Q @ line[:2]
linem = np.r_[nm, line[2] - nm @ b]
after = circle_line_intersections(Cm, 5., linem, **tol)

expected = before.points @ Q.T + b
print(before.relation, after.relation)
print(before.center_distance, after.center_distance)
print(before.chord_length, after.chord_length)
print(expected)
print(after.points)
