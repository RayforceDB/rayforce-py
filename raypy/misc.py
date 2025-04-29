from . import rayforce

# Flag to track if Rayforce has been initialized
_rayforce_initialized = False


def initialize():
    """
    Initialize the Rayforce runtime.
    """
    global _rayforce_initialized
    if not _rayforce_initialized:
        rayforce.ray_init()
        _rayforce_initialized = True
    return _rayforce_initialized
