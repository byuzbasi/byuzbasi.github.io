# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Kuvvetin işaret, rijit hareket ve ölçek deneyi ---
import numpy as np
from agbook import point_power, rotation_matrix_2d

C = np.array([0., 0.])
r = 3.0
points = np.array([[1., 1.], [0., 3.], [4., 2.]])
before = np.array([point_power(C, r, p) for p in points])

Q = rotation_matrix_2d(np.deg2rad(31.0))
b = np.array([8., -5.])
Cm = Q @ C + b
moved = points @ Q.T + b
after = np.array([point_power(Cm, r, p) for p in moved])

s = 3.0
scaled = np.array([
    point_power(s * C, s * r, s * p) for p in points
])
print(before)
print(np.allclose(after, before))
print(np.allclose(scaled, s**2 * before))

# --- 2. Radikal eksenin beş temel sınıfı ---
import numpy as np
from agbook import point_power, radical_axis_diagnostics

tol = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
cases = {
    "kesisen": ((-2., 0.), 3., (2., 0.), 3.),
    "teget": ((0., 0.), 5., (8., 0.), 3.),
    "ayrik": ((0., 0.), 2., (8., 0.), 2.),
    "ozdes": ((1., 2.), 4., (1., 2.), 4.),
    "esmerkezli_farkli": ((1., 2.), 4., (1., 2.), 3.),
}
for name, (c1, r1, c2, r2) in cases.items():
    out = radical_axis_diagnostics(c1, r1, c2, r2, **tol)
    print(name, out.relation, out.line_coefficients)
    if out.line_coefficients is not None:
        a, b, c = out.line_coefficients
        p = -c * np.array([a, b])
        print(point_power(c1, r1, p)
              - point_power(c2, r2, p))

# --- 3. Radikal merkezde nokta, doğru, düzlem ve boş yer ---
import numpy as np
from agbook import radical_center_diagnostics

tol = dict(
    angular_tolerance=1e-12,
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
datasets = {
    "nokta": (
        [[0., 0.], [8., 0.], [0., 6.]], [5., 3., 4.]
    ),
    "dogru": (
        [[2., 0.], [3., 0.], [4., 0.]], [2., 3., 4.]
    ),
    "duzlem": (
        [[1., 1.], [1., 1.], [1., 1.]], [2., 2., 2.]
    ),
    "bos": (
        [[0., 0.], [0., 0.], [3., 0.]], [2., 1., 2.]
    ),
}
for name, (centers, radii) in datasets.items():
    out = radical_center_diagnostics(centers, radii, **tol)
    print(name, out.relation, out.point,
          out.line_coefficients)

# --- 4. Demette ölçek değişmezliği, nokta ve boş üye ---
import numpy as np
from agbook import circle_pencil_member

tangent_1 = np.array([1., 0., 0., -25.])
tangent_2 = np.array([1., -16., 0., 55.])
point_a = circle_pencil_member(tangent_1, tangent_2, 0.625)
point_b = circle_pencil_member(
    -3. * tangent_1, 7. * tangent_2, 0.625
)
print(point_a.locus_type, point_a.center,
      point_a.radius_squared)
print(np.allclose(point_a.center, point_b.center))

apart_1 = np.array([1., 0., 0., -4.])
apart_2 = np.array([1., -16., 0., 60.])
empty = circle_pencil_member(apart_1, apart_2, 0.5)
print(empty.locus_type, empty.center,
      empty.radius_squared)
