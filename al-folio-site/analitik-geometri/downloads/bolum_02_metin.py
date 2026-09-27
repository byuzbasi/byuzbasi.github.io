# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 2'nin yeniden üretilebilir deneyi ---
import numpy as np

from agbook import angle_between, orthogonal_decomposition, vector_norm

air_velocity = np.array([15.0, 2.0])
wind_velocity = np.array([-3.0, 4.0])
route_direction = np.array([4.0, 3.0])
ground_velocity = air_velocity + wind_velocity

decomp = orthogonal_decomposition(ground_velocity, route_direction)
scaled = orthogonal_decomposition(
    ground_velocity, 1.0e8 * route_direction
)

print(f"yer_hizi: {ground_velocity}")
print(f"yer_surati: {vector_norm(ground_velocity):.6f}")
print(f"rota_bileseni: {decomp.scalar_component:.6f}")
print(f"paralel: {decomp.parallel}")
print(f"capraz: {decomp.perpendicular}")
print(f"capraz_surat: {vector_norm(decomp.perpendicular):.6f}")
print(f"rota_acisi_derece: "
      f"{angle_between(ground_velocity, route_direction, degrees=True):.6f}")
print(f"yeniden_kurma_artigi: {decomp.reconstruction_residual:.3e}")
print(f"diklik_artigi: {decomp.orthogonality_residual:.3e}")
print(f"olcek_degismezligi: "
      f"{vector_norm(decomp.parallel-scaled.parallel):.3e}")
