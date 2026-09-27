# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Cauchy--Schwarz ve üçgen eşitsizliği taraması ---
import numpy as np
from agbook import inner_product, vector_norm

pairs = [
    (np.array([1., 2.]), np.array([-3., 4.])),
    (np.array([1., 2.]), np.array([0.5, -2.])),
    (np.array([-3., 4.]), np.array([5., 0.])),
]
tolerance = 1e-12
cs = [vector_norm(u)*vector_norm(v) - abs(inner_product(u, v))
      for u, v in pairs]
triangle = [vector_norm(u)+vector_norm(v)-vector_norm(u+v)
            for u, v in pairs]
print(f"min_cs_margin: {min(cs):.6e}")
print(f"min_triangle_margin: {min(triangle):.6e}")
print(min(cs) >= -tolerance and min(triangle) >= -tolerance)

# --- 2. Büyük bileşenlerde norm ve açı ---
import numpy as np
from agbook import angle_between, vector_norm

u = np.array([1e307, 1e307])
v = np.array([1e307, 9.99e306])
with np.errstate(over="ignore"):
    direct = np.sqrt(np.sum(u*u))
safe = vector_norm(u)
theta = angle_between(u, v)
print(direct)
print(f"{safe:.6e}")
print(f"{theta:.9e}")
print(np.isfinite(theta) and 0.0 <= theta <= np.pi)

# --- 3. Hedef ölçeği ve yönü ---
import numpy as np
from agbook import scalar_projection, vector_norm, vector_projection

v = np.array([5., 1.])
u = np.array([2., 1.])
reference = vector_projection(v, u)
for c in (1e8, -3., 1e-8):
    projected = vector_projection(v, c*u)
    difference = vector_norm(projected-reference)
    component = scalar_projection(v, c*u)
    print(f"{c: .1e} {difference:.3e} {component:.6f}")

# --- 4. Sıfır ve uygulama eşiği ---
from agbook import unit_vector

for label, vector, tolerance in (
    ("zero_default", [0., 0.], 0.0),
    ("small_default", [1e-10, 0.], 0.0),
    ("small_threshold", [1e-10, 0.], 1e-9),
):
    try:
        print(label, unit_vector(vector, zero_tolerance=tolerance))
    except ValueError as error:
        print(label, type(error).__name__)
