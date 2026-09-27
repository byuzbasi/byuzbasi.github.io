# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Üç konik türünde payda ve artık tanısı ---
import numpy as np
from agbook import polar_conic_diagnostics

cases = {
    "ellipse": (0.5, np.linspace(-np.pi, np.pi, 41)),
    "parabola": (1.0, np.linspace(-2.5, 2.5, 41)),
    "hyperbola": (2.0, np.linspace(-1.9, 1.9, 41)),
}
for name, (e, theta) in cases.items():
    d = polar_conic_diagnostics([0., 0.], [1., 0.], e, 3., theta)
    print(
        name,
        "payda_marji=", np.min(d.denominators),
        "cebirsel=", d.maximum_absolute_algebraic_residual,
        "odak_dogrultman=", d.maximum_absolute_focus_directrix_residual,
    )
    assert np.min(d.denominators) > 0.
    assert d.maximum_absolute_algebraic_residual < 4e-13
    assert d.maximum_absolute_focus_directrix_residual < 5e-14

# --- 2. Kutupsal ve rasyonel elipsin eşleştirilmesi ---
import numpy as np
from agbook import (
    polar_conic_frame,
    polar_conic_points,
    rational_conic_points,
)

F = np.array([1., -2.])
u = np.array([3., 4.])
e, ell = 0.6, 5.
theta = np.deg2rad([-150., -90., -20., 0., 45., 130.])
t = np.tan(theta / 2.)
p_polar = polar_conic_points(F, u, e, ell, theta)
p_rational = rational_conic_points(F, u, e, ell, t)
gap = np.linalg.norm(p_polar - p_rational, axis=1)
assert np.max(gap) < 3e-14

frame = polar_conic_frame(F, u, e, ell)
closed_samples = np.vstack([p_rational, frame.rational_limit_point])
print("en_buyuk_fark:", np.max(gap))
print("t_sonsuz_noktasi:", frame.rational_limit_point)
print("tamamlanmis_boyut:", closed_samples.shape)

# --- 3. Hiperbol dalları ve açık sınır hataları ---
import numpy as np
from agbook import (
    polar_conic_frame,
    polar_conic_points,
    rational_conic_points,
)

e, ell = 2., 3.
alpha = np.arccos(-1. / e)
beta = np.arccos(1. / e)
near = polar_conic_points(
    [0., 0.], [1., 0.], e, ell,
    np.linspace(-alpha + 0.1, alpha - 0.1, 101),
)
far = polar_conic_points(
    [0., 0.], [1., 0.], e, ell,
    np.linspace(-beta + 0.1, beta - 0.1, 101),
    branch="far_side",
)

frame = polar_conic_frame([0., 0.], [1., 0.], e, ell)
tau = frame.rational_singular_parameters[1]
intervals = [
    np.linspace(-4., -tau - 0.1, 80),
    np.linspace(-tau + 0.1, tau - 0.1, 160),
    np.linspace(tau + 0.1, 4., 80),
]
rational_parts = [
    rational_conic_points([0., 0.], [1., 0.], e, ell, values)
    for values in intervals
]
assert near.shape == (101, 2)
assert far.shape == (101, 2)
assert sum(part.shape[0] for part in rational_parts) == 320

bad_calls = [
    lambda: polar_conic_points(
        [0., 0.], [1., 0.], e, ell, np.pi
    ),
    lambda: rational_conic_points(
        [0., 0.], [1., 0.], e, ell, tau,
        denominator_tolerance=1e-14,
    ),
]
for call in bad_calls:
    try:
        call()
    except ValueError as error:
        print(type(error).__name__, str(error))
    else:
        raise AssertionError("Geçersiz girdi sessizce kabul edildi.")

# --- 4. Rijit hareket ve metre--milimetre ölçeği ---
import numpy as np
from agbook import (
    polar_conic_algebraic_residuals,
    polar_conic_frame,
    polar_conic_points,
    rotation_matrix_2d,
)

F = np.array([2., -1.])
u = np.array([3., 4.])
e, ell = 0.7, 5.          # ell metre cinsinde
theta = np.array([-1.2, 0., 0.8])
points_m = polar_conic_points(F, u, e, ell, theta)

Q = rotation_matrix_2d(np.deg2rad(31.))
q = np.array([7., -3.])
moved = polar_conic_points(Q @ F + q, Q @ u, e, ell, theta)
assert np.allclose(moved, points_m @ Q.T + q)

scale = 1000.             # metre -> milimetre
points_mm = polar_conic_points(scale * F, u, e, scale * ell, theta)
assert np.allclose(points_mm, scale * points_m)
frame_m = polar_conic_frame(F, u, e, ell)
frame_mm = polar_conic_frame(scale * F, u, e, scale * ell)
assert frame_mm.eccentricity == frame_m.eccentricity
assert np.isclose(frame_mm.semilatus_rectum, scale * ell)

r_m = polar_conic_algebraic_residuals(points_m, F, u, e, ell)
r_mm = polar_conic_algebraic_residuals(
    points_mm, scale * F, u, e, scale * ell
)
assert np.allclose(r_mm, r_m, atol=3e-15)
