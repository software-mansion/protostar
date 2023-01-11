from typing import TYPE_CHECKING

from services.everest.business_logic.state_api import StateProxy
from starkware.starknet.business_logic.fact_state.state import CarriedState
from starkware.starknet.business_logic.state.state import CachedState, StateSyncifier

if TYPE_CHECKING:
    from protostar.starknet.cheaters import Cheaters


def cheaters_of(state: StateProxy) -> "Cheaters":
    """
    Extracts the ``Cheaters`` object from any State structures.

    This function workarounds limitations of the inheritance design of ``State`` classes family,
    preventing us from exposing the `cheaters` field via state interface classes like ``SyncState``.
    """

    if state.__class__.__name__ == "CheatableCachedState":
        return state.cheaters  # type: ignore

    if isinstance(state, CachedState):
        raise TypeError("Protostar should always operate on CheatableCachedState.")

    if isinstance(state, CarriedState):
        state = state.state

        if not state.__class__.__name__ == "CheatableCachedState":
            raise TypeError("Carried state is not carrying CheatableCachedState.")

        return state.cheaters  # type: ignore

    if isinstance(state, StateSyncifier):
        state = state.async_state

        if not state.__class__.__name__ == "CheatableCachedState":
            raise TypeError("State syncifier is not carrying CheatableCachedState.")

        return state.cheaters  # type: ignore

    raise TypeError(f"Unknown State class {state.__class__.__name__}.")
