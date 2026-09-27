# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Benzerlik kaydında birim eşdeğişkenliği ---
import numpy as np
import pytest
from agbook import fit_similarity_registration, rotation_matrix_2d

source = np.array([[0., 0.], [3., 0.], [0., 2.], [2., 4.]])
R = rotation_matrix_2d(0.4)
target = 1.2*(source @ R.T) + np.array([7., -3.])
base = fit_similarity_registration(source, target)
scaled = fit_similarity_registration(1000.0 * source, 1000.0 * target)

np.testing.assert_allclose(scaled.rotation, base.rotation, atol=2e-12)
assert scaled.scale == pytest.approx(base.scale, abs=2e-12)
np.testing.assert_allclose(
    scaled.translation, 1000.0 * base.translation, atol=2e-9
)
assert scaled.rms_residual == pytest.approx(
    1000.0 * base.rms_residual, abs=2e-9
)

# --- 2. DLT projektif ölçek ve dejenere taban testi ---
import numpy as np
import pytest
from agbook import project_pinhole, triangulate_point_dlt

centers = np.array([[-1., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
cameras = np.stack([np.c_[np.eye(3), -c] for c in centers])
point = np.array([[0.25, -0.15, 5.]])
images = np.vstack([
    project_pinhole(P, point).image_points[0] for P in cameras
])
base = triangulate_point_dlt(cameras, images)
factors = np.array([3.0, -0.02, 11.0])[:, None, None]
scaled = triangulate_point_dlt(factors * cameras, images)
np.testing.assert_allclose(scaled.point, base.point, atol=2e-10)
np.testing.assert_allclose(
    scaled.reprojected_points, base.reprojected_points, atol=2e-9
)

same = np.stack([cameras[0], cameras[0]])
with pytest.raises(ValueError, match="benzersiz"):
    triangulate_point_dlt(same, images[[0, 0]])

# --- 3. Işın--düzlem sınıflarının parametrik testi ---
import numpy as np
from agbook import ray_plane_intersection

cases = [
    ([0, 0, 2], [0, 0, -1], "intersecting"),
    ([0, 0, 2], [0, 0,  1], "behind"),
    ([0, 0, 2], [1, 0,  0], "parallel"),
    ([0, 0, 0], [1, 0,  0], "coplanar"),
]
for origin, direction, expected in cases:
    o = np.array(origin, dtype=float)
    d = np.array(direction, dtype=float)
    o_copy, d_copy = o.copy(), d.copy()
    result = ray_plane_intersection(o, d, [0, 0, 0], [0, 0, 1])
    assert result.classification == expected
    np.testing.assert_array_equal(o, o_copy)
    np.testing.assert_array_equal(d, d_copy)

# --- 4. Uzay elipsi değişmezlerinin testi ---
import numpy as np
from agbook import orbit_ellipse_frame_3d, orbit_ellipse_points_3d

rng = np.random.default_rng(2414)
F = np.array([1., -2., 3.])
n, proposed_u = rng.normal(size=(2, 3))
rp, ra = 3., 7.
frame = orbit_ellipse_frame_3d(F, proposed_u, n, rp, ra)
E = np.linspace(0.0, 2.0 * np.pi, 257)
points = orbit_ellipse_points_3d(frame, E)

plane = (points - frame.focus) @ frame.plane_normal
focal = (
    np.linalg.norm(points - frame.focus, axis=1)
    + np.linalg.norm(points - frame.second_focus, axis=1)
)
np.testing.assert_allclose(plane, 0.0, atol=2e-10)
np.testing.assert_allclose(focal, 2.0 * frame.semi_major_axis, atol=2e-10)
np.testing.assert_allclose(points[0], frame.periapsis, atol=2e-10)
np.testing.assert_allclose(points[128], frame.apoapsis, atol=2e-10)
