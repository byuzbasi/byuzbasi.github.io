# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Hiperbol üyelik artıkları ---
import numpy as np
from agbook import (
    hyperbola_algebraic_residuals,
    hyperbola_focal_difference_residuals,
    hyperbola_frame_from_center_axes,
    hyperbola_points,
)

frame = hyperbola_frame_from_center_axes([0., 0.], [1., 0.], 3., 4.)
t = np.linspace(-2., 2., 17)
points = np.vstack([
    hyperbola_points([0., 0.], [1., 0.], 3., 4., t, branch=-1),
    hyperbola_points([0., 0.], [1., 0.], 3., 4., t, branch=1),
])
r_alg = hyperbola_algebraic_residuals(
    points, frame.center, frame.transverse_direction, 3., 4.
)
r_diff = hyperbola_focal_difference_residuals(
    points, frame.first_focus, frame.second_focus, 3.
)
print(np.max(np.abs(r_alg)), np.max(np.abs(r_diff)))
assert np.max(np.abs(r_alg)) < 2e-14
assert np.max(np.abs(r_diff)) < 4e-14
