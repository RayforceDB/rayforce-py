from unittest.mock import patch

from raypy import i64, f64


class TestGarbageCollection:
    @patch("raypy.rayforce.drop_obj")
    def test_garbage_collection(self, mock_drop_obj):
        x = i64(42)
        y = f64(3.14)

        x_obj = x.obj
        y_obj = y.obj

        # Simulate garbage collector
        del x
        del y

        # Check that drop_obj was called for both objects
        assert mock_drop_obj.call_count == 2
        mock_drop_obj.assert_any_call(x_obj)
        mock_drop_obj.assert_any_call(y_obj)
