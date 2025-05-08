import pytest
import datetime as dt
from raypy.types import scalar, container
from raypy.math.operations import add


class TestAddOperation:
    """Tests for the add operation in raypy.math.operations."""

    def test_add_i64_scalars(self):
        """Test adding two i64 scalars."""
        a = scalar.i64(5)
        b = scalar.i64(10)
        result = add(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 15

    def test_add_f64_scalars(self):
        """Test adding two f64 scalars."""
        a = scalar.f64(3.5)
        b = scalar.f64(2.5)
        result = add(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 6.0

    def test_add_mixed_scalars(self):
        """Test adding i64 and f64 scalars."""
        a = scalar.i64(5)
        b = scalar.f64(2.5)
        result = add(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 7.5

    def test_add_i64_vectors(self):
        """Test adding two i64 vectors."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)
        b[2] = scalar.i64(6)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 7, 9]

    def test_add_f64_vectors(self):
        """Test adding two f64 vectors."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(1.5)
        a[1] = scalar.f64(2.5)
        a[2] = scalar.f64(3.5)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [2.0, 4.0, 6.0]

    def test_add_mixed_vectors(self):
        """Test adding i64 and f64 vectors."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1.5, 3.5, 5.5]

    def test_add_scalar_to_vector(self):
        """Test adding a scalar to a vector (scalar broadcast)."""
        # i64 скаляр + i64 вектор
        a = scalar.i64(5)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [6, 7, 8]

        # f64 скаляр + f64 вектор
        a2 = scalar.f64(1.5)
        b2 = container.Vector(scalar.f64, 3)
        b2[0] = scalar.f64(0.5)
        b2[1] = scalar.f64(1.0)
        b2[2] = scalar.f64(1.5)

        result2 = add(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [2.0, 2.5, 3.0]

    def test_add_mixed_scalar_to_vector(self):
        """Test adding mixed scalar types to vectors."""
        # i64 скаляр + f64 вектор
        a = scalar.i64(10)
        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [10.5, 11.5, 12.5]

    def test_add_timestamp_and_i64(self):
        """Test adding i64 to Timestamp."""
        # Создаем временную метку
        now = dt.datetime.now()
        timestamp = scalar.Timestamp(now)

        # Добавляем i64 (миллисекунды)
        delta = scalar.i64(1000)
        result = add(timestamp, delta)

        assert isinstance(result, scalar.Timestamp)
        # Результат должен быть на 1 секунду позже
        expected = now + dt.timedelta(milliseconds=1000)
        assert abs((result.value - expected).total_seconds()) < 0.001

        # Добавляем Timestamp к i64
        result2 = add(delta, timestamp)

        assert isinstance(result2, scalar.Timestamp)
        assert abs((result2.value - expected).total_seconds()) < 0.001

    def test_add_i64_to_timestamp_vector(self):
        """Test adding i64 to Vector[Timestamp]."""
        now = dt.datetime.now()
        one_second = dt.timedelta(seconds=1)

        ts_vector = container.Vector(scalar.Timestamp, 3)
        ts_vector[0] = scalar.Timestamp(now)
        ts_vector[1] = scalar.Timestamp(now + one_second)
        ts_vector[2] = scalar.Timestamp(now + 2 * one_second)

        # Добавляем i64 (миллисекунды)
        delta = scalar.i64(500)
        result = add(ts_vector, delta)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.Timestamp

        expected_times = [
            now + dt.timedelta(milliseconds=500),
            now + one_second + dt.timedelta(milliseconds=500),
            now + 2 * one_second + dt.timedelta(milliseconds=500),
        ]

        result_times = [item.value for item in result.to_list()]

        for actual, expected in zip(result_times, expected_times):
            assert abs((actual - expected).total_seconds()) < 0.001

        # Добавляем i64 к вектору Timestamp (обратный порядок)
        result2 = add(delta, ts_vector)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.Timestamp

        result_times2 = [item.value for item in result2.to_list()]

        for actual, expected in zip(result_times2, expected_times):
            assert abs((actual - expected).total_seconds()) < 0.001

    def test_error_unsupported_scalar_type(self):
        """Test that adding unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            add(a, b)

    def test_error_i16_i32_not_supported(self):
        """Test that adding i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(5)
        b = scalar.i64(10)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            add(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            add(c, b)

        # i16 vector
        a_vec = container.Vector(scalar.i16, 3)
        a_vec[0] = scalar.i16(1)
        a_vec[1] = scalar.i16(2)
        a_vec[2] = scalar.i16(3)

        b_vec = container.Vector(scalar.i64, 3)
        b_vec[0] = scalar.i64(4)
        b_vec[1] = scalar.i64(5)
        b_vec[2] = scalar.i64(6)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            add(a_vec, b_vec)

        # i32 vector
        c_vec = container.Vector(scalar.i32, 3)
        c_vec[0] = scalar.i32(10)
        c_vec[1] = scalar.i32(20)
        c_vec[2] = scalar.i32(30)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            add(c_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that adding unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            add(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that adding vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            add(a, b)

    def test_error_invalid_timestamp_addition(self):
        """Test that adding invalid types to Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        f = scalar.f64(1.5)

        # Нельзя добавлять float к timestamp
        with pytest.raises(ValueError):
            add(timestamp, f)
