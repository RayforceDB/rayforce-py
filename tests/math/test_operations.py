import pytest
import datetime as dt
from raypy.types import scalar, container
from raypy.math.operations import add, sub


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


class TestSubOperation:
    """Tests for the sub operation in raypy.math.operations."""

    def test_sub_i64_scalars(self):
        """Test subtracting two i64 scalars."""
        a = scalar.i64(15)
        b = scalar.i64(10)
        result = sub(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 5

    def test_sub_f64_scalars(self):
        """Test subtracting two f64 scalars."""
        a = scalar.f64(5.5)
        b = scalar.f64(2.5)
        result = sub(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.0

    def test_sub_mixed_scalars(self):
        """Test subtracting i64 and f64 scalars."""
        a = scalar.i64(5)
        b = scalar.f64(2.5)
        result = sub(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.5

    def test_sub_i64_vectors(self):
        """Test subtracting two i64 vectors."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)
        b[2] = scalar.i64(6)

        result = sub(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [6, 10, 14]

    def test_sub_f64_vectors(self):
        """Test subtracting two f64 vectors."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(3.5)
        a[1] = scalar.f64(4.5)
        a[2] = scalar.f64(5.5)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = sub(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [3.0, 3.0, 3.0]

    def test_sub_mixed_vectors(self):
        """Test subtracting i64 and f64 vectors."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = sub(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [9.5, 13.5, 17.5]

    def test_sub_scalar_from_vector(self):
        """Test subtracting a scalar from a vector."""
        # i64 вектор - i64 скаляр
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = scalar.i64(5)

        result = sub(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 10, 15]

        # f64 вектор - f64 скаляр
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(3.5)
        a2[1] = scalar.f64(4.5)
        a2[2] = scalar.f64(5.5)

        b2 = scalar.f64(1.5)

        result2 = sub(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [2.0, 3.0, 4.0]

    def test_sub_mixed_scalar_from_vector(self):
        """Test subtracting mixed scalar types from vectors."""
        # f64 вектор - i64 скаляр
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(10.5)
        a[1] = scalar.f64(15.5)
        a[2] = scalar.f64(20.5)

        b = scalar.i64(5)

        result = sub(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.5, 10.5, 15.5]

    def test_sub_timestamp_and_i64(self):
        """Test subtracting i64 from Timestamp."""
        # Создаем временную метку
        now = dt.datetime.now()
        timestamp = scalar.Timestamp(now)

        # Вычитаем i64 (миллисекунды)
        delta = scalar.i64(1000)
        result = sub(timestamp, delta)

        assert isinstance(result, scalar.Timestamp)
        # Результат должен быть на 1 секунду раньше
        expected = now - dt.timedelta(milliseconds=1000)
        assert abs((result.value - expected).total_seconds()) < 0.001

    def test_sub_timestamp_from_timestamp(self):
        """Test subtracting Timestamp from Timestamp."""
        # Создаем временные метки
        now = dt.datetime.now()
        timestamp1 = scalar.Timestamp(now)
        timestamp2 = scalar.Timestamp(now - dt.timedelta(seconds=30))

        # Вычитаем timestamp2 из timestamp1, должны получить разницу в миллисекундах (30000)
        result = sub(timestamp1, timestamp2)

        assert isinstance(result, scalar.i64)
        assert (
            29900 <= result.value <= 30100
        )  # Проверяем, что разница примерно 30000 мс

    def test_sub_i64_from_timestamp_vector(self):
        """Test subtracting i64 from Vector[Timestamp]."""
        now = dt.datetime.now()
        one_second = dt.timedelta(seconds=1)

        ts_vector = container.Vector(scalar.Timestamp, 3)
        ts_vector[0] = scalar.Timestamp(now)
        ts_vector[1] = scalar.Timestamp(now + one_second)
        ts_vector[2] = scalar.Timestamp(now + 2 * one_second)

        # Вычитаем i64 (миллисекунды)
        delta = scalar.i64(500)
        result = sub(ts_vector, delta)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.Timestamp

        expected_times = [
            now - dt.timedelta(milliseconds=500),
            now + one_second - dt.timedelta(milliseconds=500),
            now + 2 * one_second - dt.timedelta(milliseconds=500),
        ]

        result_times = [item.value for item in result.to_list()]

        for actual, expected in zip(result_times, expected_times):
            assert abs((actual - expected).total_seconds()) < 0.001

    def test_error_unsupported_scalar_type(self):
        """Test that subtracting unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            sub(a, b)

    def test_error_i16_i32_not_supported(self):
        """Test that subtracting i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(5)
        b = scalar.i64(10)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            sub(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            sub(c, b)

        # i16 vector
        a_vec = container.Vector(scalar.i16, 3)
        a_vec[0] = scalar.i16(10)
        a_vec[1] = scalar.i16(15)
        a_vec[2] = scalar.i16(20)

        b_vec = container.Vector(scalar.i64, 3)
        b_vec[0] = scalar.i64(4)
        b_vec[1] = scalar.i64(5)
        b_vec[2] = scalar.i64(6)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            sub(a_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that subtracting unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            sub(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that subtracting vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            sub(a, b)

    def test_error_invalid_timestamp_subtraction(self):
        """Test that subtracting invalid types from Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        f = scalar.f64(1.5)

        # Нельзя вычитать float из timestamp
        with pytest.raises(ValueError):
            sub(timestamp, f)

    def test_error_subtracting_timestamp_vector(self):
        """Test that subtracting Timestamp vectors raises an error."""
        now = dt.datetime.now()

        ts_vector = container.Vector(scalar.Timestamp, 3)
        ts_vector[0] = scalar.Timestamp(now)
        ts_vector[1] = scalar.Timestamp(now + dt.timedelta(seconds=1))
        ts_vector[2] = scalar.Timestamp(now + dt.timedelta(seconds=2))

        # Нельзя вычитать вектор Timestamp
        with pytest.raises(ValueError, match="Cannot subtract Timestamp vectors"):
            sub(scalar.i64(100), ts_vector)

    def test_error_timestamp_from_non_timestamp(self):
        """Test that subtracting Timestamp from non-Timestamp raises an error."""
        now = dt.datetime.now()
        timestamp = scalar.Timestamp(now)

        # Нельзя вычитать timestamp из i64
        with pytest.raises(
            ValueError, match="Cannot subtract Timestamp from non-Timestamp value"
        ):
            sub(scalar.i64(100), timestamp)
