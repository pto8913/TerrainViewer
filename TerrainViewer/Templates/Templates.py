# --- STL ---
from typing import List, Union

# --- PL ---
import numpy as np

# --- MyL ---


MINIMUM_ELEV = -100
WATER_ELEV = 32768

class Math:
    def clamp(self, Target: Union[int, float], Min: Union[int, float], Max: Union[int, float]) -> Union[int, float]:
        if Target < Min:
            return Min
        if Max < Target:
            return Max 
        return Target

class LoadedItemData:
    def __init__(self):
        super(LoadedItemData, self).__init__()

        self._ItemPath = ""

        self._MinimumElev = 0

        self._GridXSize = 225
        self._GridYSize = 150

        self._Elev = np.full(self._GridXSize * self._GridYSize, 0, dtype = np.float64)
        
    # --------------- ItemPath ---------------
    @property
    def ItemPath(self) -> str:
        return self._ItemPath
    @ItemPath.setter
    def ItemPath(self, In: str) -> None:
        self._ItemPath = In

    # --------------- Grid Size ---------------
    @property
    def GridXSize(self) -> int:
        return self._GridXSize

    @property
    def GridYSize(self) -> int:
        return self._GridYSize

    # --------------- Elev ---------------
    @property
    def MinimumElev(self) -> float:
        return self._MinimumElev
    @MinimumElev.setter
    def MinimumElev(self, In: float) -> None:
        self._MinimumElev = In

    def AddElev(self, Index: int, InValue: float) -> None:
        self._Elev[Index] = InValue
        
    @property
    def Elev(self) -> np.ndarray:
        return self._Elev
    @Elev.setter
    def Elev(self, In: np.ndarray) -> np.ndarray:
        self._Elev = In
    
    def ExchangeMinimumElev(self) -> np.ndarray:
        self._Elev = np.where(self._Elev < self._MinimumElev, self._MinimumElev, self._Elev)
        return self._Elev

    def Reshape(self) -> np.ndarray:
        self._Elev = self._Elev.reshape((self._GridYSize, self._GridXSize))
        return self._Elev