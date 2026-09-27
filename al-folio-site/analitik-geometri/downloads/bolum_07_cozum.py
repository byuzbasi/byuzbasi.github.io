# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Dört noktanın yansıma koşullarını sınama ---
import numpy as np
from agbook import canonical_line_coefficients, reflect_across_line

points = np.array([[0., 0.], [2., -1.], [4., 3.], [-2., 5.]])
line = canonical_line_coefficients([2., -1., 3.])
images = reflect_across_line(points, line)
midpoints = 0.5 * (points + images)
tangent = np.array([-line[1], line[0]])

line_residuals = midpoints @ line[:2] + line[2]
perpendicularity = (images - points) @ tangent
print(np.max(np.abs(line_residuals)))
print(np.max(np.abs(perpendicularity)))
assert np.allclose(line_residuals, 0.0, atol=1e-12, rtol=0.0)
assert np.allclose(perpendicularity, 0.0, atol=1e-12, rtol=0.0)

# --- 2. Ardışık ve birleşik rijit hareket ---
import numpy as np
from agbook import (
    compose_rigid_motions, rigid_transform, rotation_matrix_2d,
)

points = np.array([[0., 0.], [2., 1.], [-1., 3.]])
q1, t1 = rotation_matrix_2d(0.4), np.array([2., -1.])
q2, t2 = np.diag([1., -1.]), np.array([-3., 4.])
sequential = rigid_transform(rigid_transform(points, q1, t1), q2, t2)
motion = compose_rigid_motions(q2, t2, q1, t1)
direct = rigid_transform(points, motion.matrix, motion.translation)

print("bilesim_artigi:", np.max(np.abs(direct - sequential)))
print("ortogonallik_artigi:",
      np.linalg.norm(motion.matrix.T @ motion.matrix - np.eye(2)))
print("determinant:", motion.determinant)
assert np.allclose(direct, sequential, atol=1e-12, rtol=0.0)

# --- 3. Çerçeve gidiş-dönüş ve uzaklık denetimi ---
import numpy as np
from agbook import (
    coordinates_from_frame, coordinates_in_frame,
    pairwise_distances, rotation_matrix_2d,
)

local = np.array([[0., 0.], [2., 0.], [2., 3.], [-1., 4.], [5., -2.]])
origin = np.array([100., -40.])
axes = rotation_matrix_2d(np.deg2rad(27.0))
world = coordinates_from_frame(local, origin, axes)
recovered = coordinates_in_frame(world, origin, axes)
roundtrip = np.max(np.abs(recovered - local))
distance = np.max(np.abs(
    pairwise_distances(world) - pairwise_distances(local)
))
print(roundtrip, distance)
assert roundtrip <= 1e-12
assert distance <= 1e-12

# --- 4. Geçersiz eksen ve çerçeve testleri ---
import numpy as np
import pytest
from agbook import coordinates_from_frame, reflection_matrix_2d

with pytest.raises(ValueError, match="Yansıma ekseni"):
    reflection_matrix_2d([0.0, 0.0])

non_orthonormal = np.array([[1.0, 0.4], [0.0, 1.0]])
with pytest.raises(ValueError, match="ortogonal"):
    coordinates_from_frame([2.0, 3.0], [0.0, 0.0], non_orthonormal)
