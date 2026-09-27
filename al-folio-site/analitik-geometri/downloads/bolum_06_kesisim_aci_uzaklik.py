"""Bölüm 6 laboratuvarı: iki ölçme ekseninin ilişkisi ve dikme ayağı.

Model düzlemsel ve sentetiktir. Bütün koordinatlar metre, açı çıktısı
derecedir. Yeryüzü eğriliği, projeksiyon ve ölçüm belirsizliği içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    line_angle,
    line_from_points,
    line_intersection_diagnostics,
    line_pencil_member,
    line_residuals,
    parallel_line_through_point,
    perpendicular_line_through_point,
    project_point_to_line,
)


def main() -> None:
    first_a = np.array([100.0, 200.0])  # metre
    first_b = np.array([500.0, 400.0])  # metre
    second_a = np.array([100.0, 500.0])  # metre
    second_b = np.array([500.0, 100.0])  # metre
    control = np.array([420.0, 320.0])  # metre

    first_line = line_from_points(first_a, first_b)
    second_line = line_from_points(second_a, second_b)
    relation = line_intersection_diagnostics(
        first_line,
        second_line,
        angular_tolerance=1.0e-12,
        absolute_tolerance=0.001,
        relative_tolerance=0.0,
        reference_scale=1000.0,
    )
    if relation.point is None:
        raise RuntimeError("Sentetik eksenlerin tek kesişim vermesi bekleniyordu.")

    projection = project_point_to_line(first_line, control)
    parallel = parallel_line_through_point(first_line, control)
    perpendicular = perpendicular_line_through_point(first_line, control)
    pencil = line_pencil_member(
        first_line,
        second_line,
        2.0,
        -1.0,
        angular_tolerance=1.0e-12,
    )
    intersection_residuals = line_residuals(
        np.array([1.0, 0.0, -relation.point[0]]),
        relation.point[None, :],
    )
    pencil_residual = line_residuals(pencil, relation.point[None, :])

    near_loose = line_intersection_diagnostics(
        [0.0, 1.0, 0.0],
        [1.0e-8, 1.0, -1.0],
        angular_tolerance=1.0e-7,
        absolute_tolerance=0.001,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )
    near_strict = line_intersection_diagnostics(
        [0.0, 1.0, 0.0],
        [1.0e-8, 1.0, -1.0],
        angular_tolerance=1.0e-10,
        absolute_tolerance=0.001,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )

    signature_values = np.concatenate(
        [first_line, second_line, relation.point, projection.foot, parallel, perpendicular]
    )
    print("birim: m")
    print("birinci_eksen:", np.round(first_line, 12))
    print("ikinci_eksen:", np.round(second_line, 12))
    print("iliski:", relation.relation)
    print("kesisim:", np.round(relation.point, 12))
    print("kesisim_artiklari:", np.format_float_scientific(np.max(np.abs(relation.residuals)), precision=3))
    print("kontrol_artigi:", np.format_float_scientific(np.max(np.abs(intersection_residuals)), precision=3))
    print("kucuk_aci_derece:", f"{np.degrees(line_angle(first_line, second_line)):.6f}")
    print("normal_matrisi_kosul_sayisi:", f"{relation.condition_number:.6f}")
    print("dikme_ayagi:", np.round(projection.foot, 12))
    print("isaretli_uzaklik_m:", f"{projection.signed_distance:.6f}")
    print("uzaklik_m:", f"{projection.distance:.6f}")
    print("ayak_denklem_artigi:", np.format_float_scientific(abs(projection.foot_residual), precision=3))
    print("ayak_diklik_artigi:", np.format_float_scientific(abs(projection.orthogonality_residual), precision=3))
    print("paralel_dogru:", np.round(parallel, 12))
    print("dik_dogru:", np.round(perpendicular, 12))
    print("demet_ortak_nokta_artigi:", np.format_float_scientific(abs(pencil_residual[0]), precision=3))
    print("yakin_paralel_gevsek_karar:", near_loose.relation)
    print("yakin_paralel_siki_karar:", near_strict.relation)
    print("yakin_paralel_kosul_sayisi:", f"{near_strict.condition_number:.6e}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
