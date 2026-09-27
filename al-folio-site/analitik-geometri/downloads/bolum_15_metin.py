# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Birleşik kutupsal konik tanısı ---
import numpy as np
from agbook import polar_conic_diagnostics

cases = [
    (0.5, np.linspace(-np.pi, np.pi, 41)),
    (1.0, np.linspace(-2.5, 2.5, 41)),
    (2.0, np.linspace(-1.9, 1.9, 41)),
]
for e, theta in cases:
    result = polar_conic_diagnostics(
        [0., 0.], [1., 0.], e, 3., theta
    )
    print(
        e,
        np.min(result.denominators),
        result.maximum_absolute_algebraic_residual,
        result.maximum_absolute_focus_directrix_residual,
    )
    assert np.min(result.denominators) > 0.
    assert result.maximum_absolute_algebraic_residual < 4e-13
    assert result.maximum_absolute_focus_directrix_residual < 5e-14
