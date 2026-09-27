# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. İki hiperbol kurucusunun eşdeğerliği ---
import numpy as np
from agbook import (
    hyperbola_frame_from_center_axes,
    hyperbola_frame_from_foci,
)

first = hyperbola_frame_from_center_axes([1., -2.], [2., 1.], 4., 3.)
second = hyperbola_frame_from_foci(
    first.first_focus, first.second_focus, first.semi_transverse
)

for name in (
    "center", "first_focus", "second_focus", "transverse_direction",
    "first_directrix", "second_directrix", "first_asymptote",
    "second_asymptote",
):
    assert np.allclose(getattr(first, name), getattr(second, name))
assert np.isclose(first.semi_conjugate, second.semi_conjugate)
assert np.isclose(first.eccentricity, second.eccentricity)
print(first.focal_distance, first.eccentricity)

# --- 2. İki kolda üyelik ve teğet artıkları ---
import numpy as np
from agbook import (
    hyperbola_algebraic_residuals,
    hyperbola_focal_difference_residuals,
    hyperbola_frame_from_center_axes,
    hyperbola_points,
    hyperbola_tangent_line,
)

frame = hyperbola_frame_from_center_axes([0., 0.], [1., 0.], 3., 4.)
t = np.linspace(-1.5, 1.5, 9)
for branch in (-1, 1):
    points = hyperbola_points([0., 0.], [1., 0.], 3., 4., t, branch=branch)
    r_alg = hyperbola_algebraic_residuals(
        points, [0., 0.], [1., 0.], 3., 4.
    )
    r_diff = hyperbola_focal_difference_residuals(
        points, frame.first_focus, frame.second_focus, 3.
    )
    lines = np.vstack([
        hyperbola_tangent_line(
            [0., 0.], [1., 0.], 3., 4., value, branch=branch
        ) for value in t
    ])
    r_tan = np.sum(lines[:, :2] * points, axis=1) + lines[:, 2]
    print(branch, np.max(abs(r_alg)), np.max(abs(r_diff)), np.max(abs(r_tan)))
    assert np.max(abs(r_alg)) < 2e-14
    assert np.max(abs(r_diff)) < 4e-14
    assert np.max(abs(r_tan)) < 2e-14

# --- 3. Asimptot yakınsaması ve rijit hareket ---
import numpy as np
from agbook import (
    hyperbola_diagnostics,
    hyperbola_points,
    rotation_matrix_2d,
)

t = np.array([0., 1., 2., 3.])
before = hyperbola_diagnostics([0., 0.], [1., 0.], 3., 2., t, branch=1)
print(before.nearest_asymptote_distances)
assert np.all(np.diff(before.nearest_asymptote_distances) < 0.)

Q = rotation_matrix_2d(np.deg2rad(37.))
shift = np.array([5., -3.])
after = hyperbola_diagnostics(shift, Q @ np.array([1., 0.]), 3., 2., t, branch=1)
expected = before.points @ Q.T + shift
assert np.allclose(after.points, expected)
assert np.allclose(
    after.signed_focal_differences, before.signed_focal_differences
)

# --- 4. Ölçek değişmezliği ve açık sınır hataları ---
import numpy as np
from agbook import (
    hyperbola_algebraic_residuals,
    hyperbola_focal_difference_residuals,
    hyperbola_frame_from_center_axes,
    hyperbola_points,
)

m = hyperbola_frame_from_center_axes([0., 0.], [1., 0.], 3., 4.)
mm = hyperbola_frame_from_center_axes([0., 0.], [1., 0.], 3000., 4000.)
assert np.isclose(mm.focal_distance, 1000. * m.focal_distance)
assert np.isclose(mm.eccentricity, m.eccentricity)

p = hyperbola_points([0., 0.], [1., 0.], 3., 4., 0.8, branch=1)
p_bad = p + np.array([0.01, -0.02])
r_m = hyperbola_focal_difference_residuals(
    p_bad, m.first_focus, m.second_focus, 3.
)
r_mm = hyperbola_focal_difference_residuals(
    1000. * p_bad, mm.first_focus, mm.second_focus, 3000.
)
assert np.isclose(r_mm, 1000. * r_m)
assert np.isclose(
    hyperbola_algebraic_residuals(p_bad, [0., 0.], [1., 0.], 3., 4.),
    hyperbola_algebraic_residuals(
        1000. * p_bad, [0., 0.], [1., 0.], 3000., 4000.
    ),
)

bad_calls = [
    lambda: hyperbola_frame_from_center_axes([0., 0.], [1., 0.], 0., 4.),
    lambda: hyperbola_points([0., 0.], [1., 0.], 3., 4., 0., branch=0),
    lambda: hyperbola_points([0., 0.], [1., 0.], 3., 4., [], branch=1),
]
for call in bad_calls:
    try:
        call()
    except ValueError as error:
        print(type(error).__name__, str(error))
