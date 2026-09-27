# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Yedi standart koni--düzlem tanısı ---
from agbook import classify_standard_cone_plane

cases = [
    ("cember", (0.0, 0.0), 2.0),
    ("elips", (0.5, 0.0), 2.0),
    ("parabol", (1.0, 0.0), 2.0),
    ("hiperbol", (1.25, 0.0), 2.0),
    ("nokta", (0.5, 0.0), 0.0),
    ("cakisik", (1.0, 0.0), 0.0),
    ("kesisen", (1.25, 0.0), 0.0),
]
for label, slopes, h in cases:
    out = classify_standard_cone_plane(slopes, h)
    print(label, out.section_type, out.slope_norm,
          out.quadratic_determinant, out.degenerate)

# --- 2. Üç konik türünde artık denetimi ---
import numpy as np
from agbook import focus_directrix_diagnostics

models = [
    ("elips", [[5/3, 0], [-5, 0], [0, 2.5]],
     [0, 0], [1, 0, -5], 0.5),
    ("parabol", [[0, 0], [1, 2], [4, -4]],
     [1, 0], [1, 0, 1], 1.0),
    ("hiperbol", [[4, 0], [4/3, 0], [0, 4]],
     [0, 0], [1, 0, -2], 2.0),
]
for name, points, focus, line, e in models:
    d = focus_directrix_diagnostics(
        np.array(points, float), focus, line, e,
        reference_scale=1.0,
    )
    print(name, d.conic_type,
          d.maximum_absolute_residual,
          d.maximum_scaled_residual)

# --- 3. Doğrultman ölçeği ve geçersiz normal ---
import numpy as np
from agbook import focus_directrix_ratios

points = np.array([[5/3, 0], [-5, 0], [0, 2.5]])
r1 = focus_directrix_ratios(points, [0, 0], [1, 0, -5])
r2 = focus_directrix_ratios(points, [0, 0], [-7, 0, 35])
print(np.max(np.abs(r1-r2)))

try:
    focus_directrix_ratios(points, [0, 0], [0, 0, 1])
except ValueError as error:
    print(type(error).__name__)

# --- 4. Rijit ve anizotropik dönüşüm karşılaştırması ---
import numpy as np
from agbook import focus_directrix_ratios, rotation_matrix_2d

P = np.array([[0., 0.], [1., 2.], [4., 4.]])
F = np.array([1., 0.])
line = np.array([1., 0., 1.])       # x=-1
r0 = focus_directrix_ratios(P, F, line)

Q = rotation_matrix_2d(np.pi/2)
b = np.array([3., -2.])
Pr, Fr = P @ Q.T + b, F @ Q.T + b
n = Q @ line[:2]
liner = np.r_[n, line[2] - n @ b]
rr = focus_directrix_ratios(Pr, Fr, liner)

Pa, Fa = P * [2., 1.], F * [2., 1.]
linea = np.array([1., 0., 2.])      # x'=-2
ra = focus_directrix_ratios(Pa, Fa, linea)
print(np.max(np.abs(rr-r0)))
print(r0)
print(ra)
