# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. TLS için dönme ve ölçek metamorfik testi ---
import numpy as np
from agbook import fit_line_tls

rng = np.random.default_rng(2311)
t = np.linspace(-4, 4, 50)
v = np.array([0.8, 0.6])
n = np.array([-0.6, 0.8])
points = t[:, None]*v + rng.normal(0, 0.04, (50, 1))*n
base = fit_line_tls(points)

for angle in np.linspace(0, 2*np.pi, 20, endpoint=False):
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    moved = 7*(points @ R.T) + np.array([12.0, -5.0])
    got = fit_line_tls(moved)
    assert abs(got.direction @ (R @ base.direction)) > 1-1e-12
    np.testing.assert_allclose(
        got.rms_orthogonal, 7*base.rms_orthogonal, rtol=2e-12
    )

# --- 2. Çember geometrik amacının başlangıcı iyileştirmesi ---
import numpy as np
from agbook import fit_circle_geometric

rng = np.random.default_rng(2312)
theta = np.linspace(0, 2*np.pi, 80, endpoint=False)
radial = 5 + rng.normal(0, 0.12, theta.size)
points = np.array([3.0, -2.0]) + radial[:, None]*np.c_[
    np.cos(theta), np.sin(theta)
]
fit = fit_circle_geometric(points)
assert fit.final_sum_squares <= fit.initial_sum_squares + 1e-12
print(fit.initial_sum_squares, fit.final_sum_squares)

# --- 3. Elips yaylarında nullspace ayrışması ---
import numpy as np
from agbook import fit_conic_implicit

for degrees in (360, 90, 30, 10):
    width = np.deg2rad(degrees)
    theta = np.linspace(-width/2, width/2, 120)
    points = np.c_[4*np.cos(theta), 1.5*np.sin(theta)]
    fit = fit_conic_implicit(points)
    print(
        degrees,
        fit.diagnostics.singular_values,
        fit.diagnostics.nullspace_gap,
        fit.conic_diagnostics.locus_type,
    )

# --- 4. Elipsoid uydurmasının benzerlik testi ---
import numpy as np
from agbook import fit_quadric_implicit

azimuth, polar = np.meshgrid(
    np.linspace(0, 2*np.pi, 24, endpoint=False),
    np.linspace(0.15, np.pi-0.15, 12),
)
points = np.c_[
    5*np.sin(polar.ravel())*np.cos(azimuth.ravel()),
    3*np.sin(polar.ravel())*np.sin(azimuth.ravel()),
    2*np.cos(polar.ravel()),
] + np.array([1., -2., 3.])
base = fit_quadric_implicit(points)
Q, _ = np.linalg.qr(np.random.default_rng(2314).normal(size=(3, 3)))
if np.linalg.det(Q) < 0:
    Q[:, -1] *= -1
t = np.array([7.0, -4.0, 2.0])
moved_points = 1000*(points @ Q.T + t)
moved = fit_quadric_implicit(moved_points)

np.testing.assert_allclose(
    moved.quadric_diagnostics.center,
    1000*(Q @ base.quadric_diagnostics.center + t),
    rtol=2e-10,
)
np.testing.assert_allclose(
    np.sort(moved.quadric_diagnostics.semi_axes),
    1000*np.sort(base.quadric_diagnostics.semi_axes),
    rtol=2e-10,
)
assert moved.quadric_diagnostics.locus_type == \
       base.quadric_diagnostics.locus_type

# --- 5. Tam elipsoid ile dar kutup yamasını karşılaştırma ---
import numpy as np
from agbook import fit_quadric_implicit

rng = np.random.default_rng(2344)
azimuth = np.linspace(0, 2*np.pi, 24, endpoint=False)
noise = rng.normal(0, 0.002, (288, 3))

def sampled_ellipsoid(polar):
    aa, pp = np.meshgrid(azimuth, polar)
    return np.c_[
        5*np.sin(pp.ravel())*np.cos(aa.ravel()),
        3*np.sin(pp.ravel())*np.sin(aa.ravel()),
        2*np.cos(pp.ravel()),
    ] + np.array([1., -2., 3.]) + noise

full_points = sampled_ellipsoid(np.linspace(0.15, np.pi-0.15, 12))
polar_patch_points = sampled_ellipsoid(np.linspace(0.15, 0.35, 12))
full = fit_quadric_implicit(full_points)
patch = fit_quadric_implicit(polar_patch_points)

for name, fit in (("tam", full), ("yama", patch)):
    print(name)
    print("tekil_degerler", fit.diagnostics.singular_values)
    print("rank", fit.diagnostics.effective_rank)
    print("nullspace_boslugu", fit.diagnostics.nullspace_gap)
    print("sinif", fit.quadric_diagnostics.locus_type)
    print("merkez", fit.quadric_diagnostics.center)
    print("yari_eksenler", fit.quadric_diagnostics.semi_axes)
