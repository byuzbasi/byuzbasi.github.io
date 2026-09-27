# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. On katsayılı sınıfların ortak çarpan testi ---
import numpy as np
from agbook import quadric_diagnostics

cases = {
    "ellipsoid": [1,0,0,1,0,1,0,0,0,-1],
    "hyperboloid_one_sheet": [1,0,0,1,0,-1,0,0,0,-1],
    "hyperboloid_two_sheets": [-1,0,0,-1,0,1,0,0,0,-1],
    "elliptic_cone": [1,0,0,1,0,-1,0,0,0,0],
    "elliptic_paraboloid": [1,0,0,1,0,0,0,0,-1,0],
    "hyperbolic_paraboloid": [1,0,0,-1,0,0,0,0,-1,0],
    "elliptic_cylinder": [1,0,0,1,0,0,0,0,0,-1],
    "hyperbolic_cylinder": [1,0,0,-1,0,0,0,0,0,-1],
    "parabolic_cylinder": [1,0,0,0,0,0,0,-1,0,0],
    "intersecting_planes": [1,0,0,-1,0,0,0,0,0,0],
    "parallel_planes": [1,0,0,0,0,0,0,0,0,-1],
    "double_plane": [1,0,0,0,0,0,0,0,0,0],
    "line": [1,0,0,1,0,0,0,0,0,0],
    "point": [1,0,0,1,0,1,0,0,0,0],
    "plane": [0,0,0,0,0,0,1,0,0,-1],
    "all_space": [0,0,0,0,0,0,0,0,0,0],
    "empty": [1,0,0,1,0,1,0,0,0,1],
}
for factor in (1e-12, -3.0, 1.0, 1e8):
    for expected, coeff in cases.items():
        got = quadric_diagnostics(factor*np.array(coeff)).locus_type
        assert got == expected, (factor, expected, got)

# --- 2. Elipsoidin rijit hareket değişmezliği ---
import numpy as np
from agbook import quadric_diagnostics, transform_quadric

rng = np.random.default_rng(2201)
axes = np.array([6.0, 3.5, 2.0])
local = np.array([1/36,0,0,1/12.25,0,1/4,0,0,0,-1])
for _ in range(20):
    raw = rng.normal(size=(3,3))
    R, _ = np.linalg.qr(raw)
    if np.linalg.det(R) < 0:
        R[:, -1] *= -1
    C = rng.normal(size=3)
    world = transform_quadric(local, R.T, -R.T @ C)
    d = quadric_diagnostics(world, coordinate_scale=10.0)
    assert d.locus_type == "ellipsoid"
    np.testing.assert_allclose(d.center, C, atol=2e-13)
    np.testing.assert_allclose(d.semi_axes, axes, atol=2e-13)

# --- 3. 2B iz ile 3B polinomun eşdeğerliği ---
import numpy as np
from agbook import quadric_matrices, quadric_plane_trace

rng = np.random.default_rng(2202)
coeff = np.array([2,1,-2,3,1,4,-5,2,3,-7], dtype=float)
Q, g, _ = quadric_matrices(coeff)
normals = np.eye(3).tolist() + [[1,1,1]]
for normal in normals:
    n = np.asarray(normal, dtype=float)
    n /= np.linalg.norm(n)
    seed = np.eye(3)[np.argmin(np.abs(n))]
    u = seed - (seed @ n)*n
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    B = np.column_stack((u, v))
    P = 0.7*n
    trace = quadric_plane_trace(coeff, P, B)
    assert trace.orthonormal
    a,b,c,d,e,f = trace.conic_coefficients
    for st in rng.normal(size=(10,2)):
        s,t = st
        value2 = a*s*s + b*s*t + c*t*t + d*s + e*t + f
        X = P + B @ st
        value3 = X @ Q @ X + 2*g @ X + coeff[-1]
        np.testing.assert_allclose(value2, value3, atol=2e-13)

# --- 4. Sınıra yakın elipsoit--silindir ailesi ---
from agbook import quadric_diagnostics

for tolerance in (0.0, 1e-12, 1e-8):
    for k in range(15):
        epsilon = 10.0**(-k)
        coeff = [1,0,0,1,0,epsilon,0,0,0,-1]
        d = quadric_diagnostics(coeff, relative_tolerance=tolerance)
        print(tolerance, k, d.locus_type,
              d.quadratic_rank, d.numerically_ambiguous)
