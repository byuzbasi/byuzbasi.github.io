# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 6 laboratuvarı: ilişki, açı ve dikme ayağı ---
import numpy as np
from agbook import (
    line_angle,
    line_from_points,
    line_intersection_diagnostics,
    line_pencil_member,
    parallel_line_through_point,
    perpendicular_line_through_point,
    project_point_to_line,
)

A = np.array([100.0, 200.0])  # metre
B = np.array([500.0, 400.0])
C = np.array([100.0, 500.0])
D = np.array([500.0, 100.0])
P = np.array([420.0, 320.0])

first = line_from_points(A, B)
second = line_from_points(C, D)
relation = line_intersection_diagnostics(
    first,
    second,
    angular_tolerance=1.0e-12,
    absolute_tolerance=0.001,
    relative_tolerance=0.0,
    reference_scale=1000.0,
)
projection = project_point_to_line(first, P)
parallel = parallel_line_through_point(first, P)
perpendicular = perpendicular_line_through_point(first, P)
pencil = line_pencil_member(
    first, second, 2.0, -1.0,
    angular_tolerance=1.0e-12,
)

print("iliski:", relation.relation)
print("kesisim:", np.round(relation.point, 12))
print("kucuk_aci_derece:", f"{np.degrees(line_angle(first, second)):.6f}")
print("kosul_sayisi:", f"{relation.condition_number:.6f}")
print("dikme_ayagi:", np.round(projection.foot, 12))
print("uzaklik_m:", f"{projection.distance:.6f}")
print("ayak_artiklari:", projection.foot_residual,
      projection.orthogonality_residual)
print("paralel_dogru:", np.round(parallel, 12))
print("dik_dogru:", np.round(perpendicular, 12))
