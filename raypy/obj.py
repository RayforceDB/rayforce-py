import sys

from . import rayforce
import weakref

# Global registry to track all RayforceObjects
_object_registry = weakref.WeakValueDictionary()


class RayforceObject:
    """
    Base class for Rayforce objects that provides automatic reference counting
    and garbage collection for Rayforce objects.

    This class serves as the base for all Rayforce data types in Python,
    similar to the Q object in pykx.
    """

    def __init__(self, obj: rayforce.obj_t | None = None):
        """
        Initialize a new RayforceObject.

        Args:
            obj: An existing rayforce obj_t to wrap, or None to create a new one
        """
        self._obj: rayforce.obj_t = obj
        # Register this object in the global registry
        if obj is not None:
            _object_registry[id(self)] = self

    def __del__(self):
        """
        Clean up Rayforce objects when Python object is garbage collected.
        """
        if hasattr(self, "_obj") and self._obj is not None:
            try:
                rayforce.drop_obj(self._obj)
            except Exception as e:
                print(f"Warning: Error dropping object: {e}", file=sys.stderr)
            finally:
                self._obj = None

    @property
    def obj(self) -> rayforce.obj_t:
        return self._obj

    @property
    def type(self) -> str:
        if self._obj is None:
            return None
        return self._obj.type

    @property
    def refcount(self) -> int:
        if self._obj is None:
            return 0
        return rayforce.rc_obj(self._obj)

    def __repr__(self) -> str:
        """
        String representation of the object.
        """
        # TODO: Investigate type mapping
        return "RayforceObject"
