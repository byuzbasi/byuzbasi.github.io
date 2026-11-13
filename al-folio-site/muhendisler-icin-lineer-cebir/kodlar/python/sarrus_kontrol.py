"""Tam sayılı 3x3 matrislerde Sarrus hesabı: eğitim ve kesin kontrol.

Çalıştırma: python3 -B python/sarrus_kontrol.py
Kurulum ve dış veri gerekmez. Genel boyutlu sayısal determinant yordamı değildir.
"""

from numbers import Integral
from typing import Sequence


def _integer_matrix3(values: Sequence[Sequence[int]]) -> list[list[int]]:
    if len(values) != 3 or any(len(row) != 3 for row in values):
        raise ValueError("Sarrus requires exactly a 3x3 matrix")
    if any(isinstance(v, bool) or not isinstance(v, Integral)
           for row in values for v in row):
        raise TypeError("this exact teaching routine requires integer entries")
    return [[int(v) for v in row] for row in values]


def sarrus(values: Sequence[Sequence[int]]) -> tuple[int, int, int]:
    """Return (P_plus, P_minus, determinant), exactly for integer entries."""
    a = _integer_matrix3(values)
    positive = (a[0][0] * a[1][1] * a[2][2]
                + a[0][1] * a[1][2] * a[2][0]
                + a[0][2] * a[1][0] * a[2][1])
    negative = (a[0][2] * a[1][1] * a[2][0]
                + a[0][0] * a[1][2] * a[2][1]
                + a[0][1] * a[1][0] * a[2][2])
    return positive, negative, positive - negative


def laplace3(values: Sequence[Sequence[int]]) -> int:
    """Independent first-row cofactor expansion for the same input contract."""
    a = _integer_matrix3(values)
    minors = [a[1][1] * a[2][2] - a[1][2] * a[2][1],
              a[1][0] * a[2][2] - a[1][2] * a[2][0],
              a[1][0] * a[2][1] - a[1][1] * a[2][0]]
    return a[0][0] * minors[0] - a[0][1] * minors[1] + a[0][2] * minors[2]


def parameter_matrix(t: int) -> list[list[int]]:
    if isinstance(t, bool) or not isinstance(t, Integral):
        raise TypeError("t must be an integer in this exact teaching routine")
    return [[int(t), 1, 1], [1, int(t), 1], [1, 1, int(t)]]


def self_check() -> int:
    cases = [([[2, 1, 0], [3, -1, 2], [1, 4, 5]], -39),
             ([[1, 0, 2], [3, 0, 4], [5, 6, 0]], 12),
             ([[1, 2, 0], [0, 3, 4], [0, 0, -2]], -6),
             ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1)]
    cases.extend((parameter_matrix(t), (t - 1) ** 2 * (t + 2))
                 for t in range(-3, 4))
    for a, expected in cases:
        if sarrus(a)[2] != expected or laplace3(a) != expected:
            raise AssertionError("Sarrus/Laplace/expected value disagreement")
    if sarrus(cases[0][0]) != (-8, 31, -39):
        raise AssertionError("the two signed product groups are incorrect")
    invalid = [([[1] * 4 for _ in range(4)], ValueError),
               ([[1, 2, 3], [4, 5], [6, 7, 8]], ValueError),
               ([[1.5, 0, 0], [0, 1, 0], [0, 0, 1]], TypeError)]
    for a, error in invalid:
        try:
            sarrus(a)
        except error:
            continue
        raise AssertionError("invalid input was not rejected")
    return len(cases)


if __name__ == "__main__":
    count = self_check()
    example = [[2, 1, 0], [3, -1, 2], [1, 4, 5]]
    plus, minus, determinant = sarrus(example)
    print(f"P+={plus}; P-={minus}; det(A)={determinant} (boyutsuz)")
    print(f"Kesin kontroller: {count} matris, iki yöntem; 3 ret durumu")
    print("t | det(G(t)) | det=(t-1)^2(t+2)")
    for t in range(-3, 4):
        value = sarrus(parameter_matrix(t))[2]
        print(f"{t:2d} | {value:3d} | {(t - 1) ** 2 * (t + 2):3d}")
