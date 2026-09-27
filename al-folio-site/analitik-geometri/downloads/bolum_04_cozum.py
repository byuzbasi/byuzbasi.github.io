# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Satır farkı ve bütün ikili farklar ---
import numpy as np

p = np.array([[0., 0.], [1., 0.], [1., 2.], [0., 2.]])
q = np.array([[0.1, 0.], [1.1, 0.], [1., 2.1], [0., 2.1]])

rowwise = q - p
pairwise = q[:, None, :] - p[None, :, :]
print(p.shape, q.shape)
print(rowwise.shape)
print(pairwise.shape)

# --- 2. Büyük ofsette kesin ve binary64 fark ---
import numpy as np
from sympy import Matrix, sqrt

s = 10**16
float_a = np.array([s, s], dtype=float)
float_b = np.array([s + 1, s + 1], dtype=float)
exact_a = Matrix([s, s])
exact_b = Matrix([s + 1, s + 1])

print("numpy_fark:", float_b - float_a)
print("numpy_uzaklik:", np.linalg.norm(float_b - float_a))
print("sympy_fark:", exact_b - exact_a)
print("sympy_uzaklik:", sqrt((exact_b-exact_a).dot(exact_b-exact_a)))

# --- 3. Birimle birlikte ölçeklenen yakınlık ---
from agbook import geometric_close

metres = geometric_close(
    [0., 0.], [0.001, 0.],
    absolute_tolerance=0.0005,
    relative_tolerance=0.001,
    reference_scale=1.,
)
millimetres = geometric_close(
    [0., 0.], [1., 0.],
    absolute_tolerance=0.5,
    relative_tolerance=0.001,
    reference_scale=1000.,
)
print(metres.distance, metres.threshold, metres.close)
print(millimetres.distance, millimetres.threshold, millimetres.close)

try:
    geometric_close(
        [0., 0.], [1., 0.],
        absolute_tolerance=-1.,
        relative_tolerance=0.,
        reference_scale=1.,
    )
except ValueError as error:
    print(type(error).__name__)

# --- 4. Tohum, çağrı, sürüm ve girdi özeti ---
from importlib.metadata import version

import numpy as np
from agbook import canonical_array_sha256

seed = 20260907
rng_a = np.random.Generator(np.random.PCG64(seed))
rng_b = np.random.Generator(np.random.PCG64(seed))
a = rng_a.normal(0., 0.01, size=(2, 2))
b = rng_b.normal(0., 0.01, size=(2, 2))

print("bit_generator: PCG64")
print("seed:", seed)
print("call: normal(0, 0.01, size=(2, 2))")
print("shape:", a.shape)
print(f"tekrar_artigi: {np.max(np.abs(a-b)):.1e}")
print("numpy:", version("numpy"))
print("sha256:", canonical_array_sha256(np.vstack([a, b])))
