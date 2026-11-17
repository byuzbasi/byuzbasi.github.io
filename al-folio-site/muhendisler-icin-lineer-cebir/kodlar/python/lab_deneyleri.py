"""Kitabın 13 kısa laboratuvarında başlangıç ve değişiklik hesapları."""

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "applications" / "python"))


def sensor_offset(changed):
    from bolum01_model_kurma import affine_output, linear_output, sensor_case

    case = sensor_case()
    offset = np.array(case["offset_v"])
    if changed:
        offset[0] = 0.30
    matrix, state = case["sensitivity_matrix"], case["state_change"]
    linear = linear_output(matrix, state)
    raw = affine_output(matrix, state, offset)
    return {"ilk_ofset_V": float(offset[0]), "ilk_ham_V": float(raw[0]),
            "ilk_duzeltilmis_V": float(linear[0])}


def vector_norm_choice(changed):
    from bolum02_vektor_geometri import vector_norm

    vector = [3, -4, 12]
    order = math.inf if changed else 2
    return {"vektor": vector, "norm": "sonsuz" if changed else "2",
            "norm_degeri": vector_norm(vector, order)}


def transformation_order(changed):
    from bolum03_matris_donusumleri import rotation_matrix_2d, scaling_matrix_2d

    rotation = rotation_matrix_2d(math.pi / 2)
    scale = scaling_matrix_2d(2, 1)
    first, second = (rotation, scale) if changed else (scale, rotation)
    output = second @ (first @ np.array([1.0, 0.0]))
    return {"sira": "donme, olcekleme" if changed else "olcekleme, donme",
            "cikti": output.tolist()}


def determinant_parameter(changed):
    from sarrus_kontrol import laplace3, parameter_matrix, sarrus

    t = -2 if changed else 0
    matrix = parameter_matrix(t)
    return {"t": t, "sarrus": sarrus(matrix)[2], "laplace": laplace3(matrix)}


def material_target(changed):
    from bolum04_lineer_sistemler import solve_report

    matrix = np.array([[1, 1, 1], [2, 5, 8], [6, 2, 1]])
    second_target = 54 if changed else 53
    physical_rhs = np.array([100, second_target, 25])
    solved = solve_report("malzeme_dengesi", matrix, physical_rhs * [1, 10, 10])
    actual = (matrix @ solved["solution"]) / [1, 10, 10]
    return {"hedef_kg_saat": physical_rhs.tolist(), "debi_kg_saat": solved["solution"],
            "denge_artigi_kg_saat": (physical_rhs - actual).tolist()}


def displacement_membership(changed):
    from bolum05_vektor_uzaylari import rigid_plate_modes, span_membership

    displacement = [0.01, 0.02, 0.011 if changed else 0.01, 0.04]
    result = span_membership(rigid_plate_modes(), displacement)
    return {"yer_degistirme_m": displacement, "alt_uzayda": result.in_span,
            "ucuncu_eksi_ilk_bilesen_m": displacement[2] - displacement[0]}


def four_subspaces(changed):
    from bolum06_temel_alt_uzaylar import actuator_sensor_matrix, fundamental_subspaces

    matrix = actuator_sensor_matrix()
    if changed:
        matrix[2, 3] = 2
    result = fundamental_subspaces(matrix)
    return {"a34": float(matrix[2, 3]), "rank": result.rank,
            "sutun_uzayi_boyutu": result.column_space_basis.shape[1],
            "satir_uzayi_boyutu": result.row_space_basis.shape[1],
            "sifir_uzayi_boyutu": result.null_space_basis.shape[1],
            "sol_sifir_uzayi_boyutu": result.left_null_space_basis.shape[1]}


def output_projection(changed):
    from bolum08_ortogonallik_qr import orthogonal_projection

    plane = np.column_stack((np.array([1, 2, 0]) / math.sqrt(5), [0, 0, 1]))
    rhs = [2, 4 if changed else 5, 0]
    result = orthogonal_projection(plane, rhs)
    return {"sag_taraf": rhs, "izdusum": result.projection.tolist(),
            "artik": result.residual.tolist(),
            "goreli_diklik_artigi": result.perpendicularity_residual_inf}


def calibration_check(changed):
    from bolum09_en_kucuk_kareler import load_cell_calibration_case

    result = load_cell_calibration_case()
    observed = result["data"]["check"]["observed_response_millivolt"]
    if changed:
        observed += 0.02
    prediction = result["check_prediction_millivolt"]
    return {"kontrol_gozlemi_mV": observed, "kontrol_ongorusu_mV": prediction,
            "kontrol_artigi_mV": observed - prediction,
            "uyum_kareler_toplami_mV2": result["qr"].residual_sum_squares,
            "katsayilar": result["physical_coefficients"].tolist()}


def conditioning(changed):
    from bolum10_sayisal_dogruluk import solve_with_diagnostics

    epsilon = 1e-8 if changed else 1.0
    matrix = np.diag([1.0, epsilon])
    reference = np.array([1.0, 1.0])
    rhs = matrix @ reference
    delta = np.array([0.0, 1e-8])
    result = solve_with_diagnostics(matrix, rhs + delta)
    return {"epsilon": epsilon, "sag_taraf_perturbasyonu": delta.tolist(),
            "kosul_sayisi_2": result.condition_number, "cozum": result.solution.tolist(),
            "cozum_degisim_normu_2": float(np.linalg.norm(result.solution - reference)),
            "degistirilmis_sistem_artigi_2": result.residual_norm,
            "degistirilmis_sistem_geri_hatasi": result.normwise_backward_error}


def spring_grounding(changed):
    from bolum11_simetri_enerji import grounding_transition_case

    rows = grounding_transition_case()["rows"]
    target = 1.0 if changed else 1000.0
    return next(row for row in rows if row["ground_constant"] == target)


def modal_stiffness(changed):
    from bolum12_ozdeger_modlar import assemble_shear_building, generalized_symmetric_eigh

    first = 16e6 if changed else 8e6
    mass, stiffness = assemble_shear_building([2000, 1500, 1000], [first, 6e6, 4e6])
    result = generalized_symmetric_eigh(stiffness, mass)
    frequencies = result["frequency_classification"]["frequencies_hz"]
    return {"ilk_rijitlik_N_m": first, "dogal_frekans_Hz": list(map(float, frequencies))}


def thermal_rank(changed):
    from bolum13_svd_dusuk_rank import low_rank_approximation, synthetic_thermal_image

    rank = 3 if changed else 2
    result = low_rank_approximation(synthetic_thermal_image(), rank)
    return {"rank": rank, "goreli_frobenius_hatasi": result["relative_frobenius_error"],
            "saklanan_sayi_adedi": result["storage"]["factor_scalar_count"]}


EXPERIMENTS = (sensor_offset, vector_norm_choice, transformation_order,
               determinant_parameter, material_target, displacement_membership,
               four_subspaces, output_projection, calibration_check, conditioning,
               spring_grounding, modal_stiffness, thermal_rank)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bolum", type=int, choices=range(1, len(EXPERIMENTS) + 1))
    parser.add_argument("asama", choices=("ilk", "degistir"))
    args = parser.parse_args()
    result = EXPERIMENTS[args.bolum - 1](args.asama == "degistir")
    print(json.dumps({"bolum": args.bolum, "asama": args.asama, "sonuc": result},
                     ensure_ascii=False, allow_nan=False, indent=2))


if __name__ == "__main__":
    main()
