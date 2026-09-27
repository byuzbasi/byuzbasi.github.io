# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 7: yerel CAD çerçevesinden dünyaya geçiş ---
import numpy as np
from agbook import (
    coordinates_from_frame,
    coordinates_in_frame,
    pairwise_distances,
    polygon_signed_area,
    reflect_across_line,
    rigid_motion_diagnostics,
    rotation_matrix_2d,
)

part_local = np.array([
    [0.0, 0.0], [120.0, 0.0],
    [120.0, 60.0], [0.0, 60.0],
])  # mm
feature_local = np.array([95.0, 45.0])  # mm
origin = np.array([420.0, 180.0])  # mm
axes = rotation_matrix_2d(np.deg2rad(35.0))

part_world = coordinates_from_frame(part_local, origin, axes)
feature_world = coordinates_from_frame(feature_local, origin, axes)
recovered = coordinates_in_frame(part_world, origin, axes)
diagnostics = rigid_motion_diagnostics(part_local, axes, origin)
reflected = reflect_across_line(feature_local, [0.0, 1.0, -30.0])

distance_residual = np.max(np.abs(
    pairwise_distances(part_world) - pairwise_distances(part_local)
))
print("dunya_ozellik:", np.round(feature_world, 8))
print("yansitilmis_yerel_ozellik:", reflected)
print("ortogonallik_artigi:", f"{diagnostics.orthogonality_residual:.3e}")
print("gidis_donus_artigi_mm:", f"{np.max(np.abs(recovered-part_local)):.3e}")
print("uzaklik_artigi_mm:", f"{distance_residual:.3e}")
print("alanlar_mm2:", polygon_signed_area(part_local),
      polygon_signed_area(part_world))
