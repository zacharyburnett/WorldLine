from typing import Collection, Optional, Tuple


def fill_3D_vector(
    vector: Tuple[float, Optional[float], Optional[float]]
) -> Tuple[float, float, float]:
    if not isinstance(vector, Collection):
        vector = [vector]
    if len(vector) < 3:
        vector = (*vector, *(0 for _ in range(3 - len(vector))))
    return vector
