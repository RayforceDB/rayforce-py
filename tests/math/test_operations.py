import pytest
import datetime as dt
from raypy.types import scalar, container
from raypy.math.operations import add, sub, mul, div, fdiv, mod, sum, avg, med, dev
import math


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

        # i32 vector
        c_vec = container.Vector(scalar.i32, 3)
        c_vec[0] = scalar.i32(10)
        c_vec[1] = scalar.i32(20)
        c_vec[2] = scalar.i32(30)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            sub(c_vec, b_vec)

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


class TestMulOperation:
    """Tests for the mul operation in raypy.math.operations."""

    def test_mul_i64_scalars(self):
        """Test multiplying two i64 scalars."""
        a = scalar.i64(5)
        b = scalar.i64(10)
        result = mul(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 50

    def test_mul_f64_scalars(self):
        """Test multiplying two f64 scalars."""
        a = scalar.f64(3.5)
        b = scalar.f64(2.0)
        result = mul(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 7.0

    def test_mul_mixed_scalars(self):
        """Test multiplying i64 and f64 scalars."""
        a = scalar.i64(5)
        b = scalar.f64(2.5)
        result = mul(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 12.5

    def test_mul_i64_vectors(self):
        """Test multiplying two i64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)
        b[2] = scalar.i64(6)

        result = mul(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [4, 10, 18]

    def test_mul_f64_vectors(self):
        """Test multiplying two f64 vectors (element-wise)."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(1.5)
        a[1] = scalar.f64(2.5)
        a[2] = scalar.f64(3.5)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = mul(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [0.75, 3.75, 8.75]

    def test_mul_mixed_vectors(self):
        """Test multiplying i64 and f64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = mul(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [0.5, 3.0, 7.5]

    def test_mul_scalar_to_vector(self):
        """Test multiplying a scalar with a vector (scalar broadcast)."""
        # i64 скаляр * i64 вектор
        a = scalar.i64(2)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        result = mul(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [2, 4, 6]

        # f64 скаляр * f64 вектор
        a2 = scalar.f64(2.0)
        b2 = container.Vector(scalar.f64, 3)
        b2[0] = scalar.f64(0.5)
        b2[1] = scalar.f64(1.0)
        b2[2] = scalar.f64(1.5)

        result2 = mul(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [1.0, 2.0, 3.0]

    def test_mul_mixed_scalar_to_vector(self):
        """Test multiplying mixed scalar types to vectors."""
        # i64 скаляр * f64 вектор
        a = scalar.i64(2)
        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = mul(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1.0, 3.0, 5.0]

    def test_error_unsupported_scalar_type(self):
        """Test that multiplying unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            mul(a, b)

    def test_error_timestamp_not_supported(self):
        """Test that multiplying with Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        b = scalar.i64(5)

        with pytest.raises(
            ValueError, match="Timestamp type is not supported for multiplication"
        ):
            mul(timestamp, b)

        c = scalar.f64(2.5)
        with pytest.raises(
            ValueError, match="Timestamp type is not supported for multiplication"
        ):
            mul(c, timestamp)

    def test_error_i16_i32_not_supported(self):
        """Test that multiplying i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(5)
        b = scalar.i64(10)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            mul(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            mul(c, b)

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
            mul(a_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that multiplying unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            mul(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that multiplying vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(4)
        b[1] = scalar.i64(5)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            mul(a, b)


class TestDivOperation:
    """Tests for the div operation in raypy.math.operations."""

    def test_div_i64_scalars(self):
        """Test dividing two i64 scalars."""
        a = scalar.i64(10)
        b = scalar.i64(2)
        result = div(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 5

        # Integer division truncation
        c = scalar.i64(5)
        d = scalar.i64(2)
        result = div(c, d)

        assert isinstance(result, scalar.i64)
        assert result.value == 2  # 5 / 2 = 2.5, но результат округляется до 2

    def test_div_f64_scalars(self):
        """Test dividing two f64 scalars."""
        a = scalar.f64(10.0)
        b = scalar.f64(2.0)
        result = div(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 5.0

        # В rayforce при делении f64 округляется до целого числа
        c = scalar.f64(5.0)
        d = scalar.f64(2.0)
        result = div(c, d)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.0  # Целочисленное деление: 5.0 // 2.0 = 2.0

    def test_div_mixed_scalars(self):
        """Test dividing i64 and f64 scalars."""
        # i64 / f64 - результат остается i64
        a = scalar.i64(10)
        b = scalar.f64(2.0)
        result = div(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 5

        # f64 / i64 - результат остается f64
        c = scalar.f64(5.0)
        d = scalar.i64(2)
        result = div(c, d)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.0  # div() выполняет целочисленное деление

    def test_div_i64_vectors(self):
        """Test dividing two i64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(3)
        b[2] = scalar.i64(4)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 5, 5]  # 10/2, 15/3, 20/4

    def test_div_f64_vectors(self):
        """Test dividing two f64 vectors (element-wise)."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(10.0)
        a[1] = scalar.f64(15.0)
        a[2] = scalar.f64(20.0)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(2.0)
        b[1] = scalar.f64(3.0)
        b[2] = scalar.f64(4.0)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 5.0, 5.0]  # 10/2, 15/3, 20/4

    def test_div_mixed_vectors(self):
        """Test dividing i64 and f64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(2.0)
        b[1] = scalar.f64(3.0)
        b[2] = scalar.f64(4.0)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64  # Тип не меняется, остается i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 5, 5]  # 10/2, 15/3, 20/4

    def test_div_vector_by_scalar(self):
        """Test dividing a vector by a scalar (scalar broadcast)."""
        # i64 вектор / i64 скаляр
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = scalar.i64(2)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 10, 15]  # 10/2, 20/2, 30/2

        # f64 вектор / f64 скаляр
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(20.0)
        a2[2] = scalar.f64(30.0)

        b2 = scalar.f64(2.0)

        result2 = div(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

    def test_div_mixed_vector_by_scalar(self):
        """Test dividing mixed scalar types to vectors."""
        # i64 вектор / f64 скаляр
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = scalar.f64(2.0)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64  # Тип не меняется, остается i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5, 10, 15]  # 10/2, 20/2, 30/2

        # f64 вектор / i64 скаляр
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(20.0)
        a2[2] = scalar.f64(30.0)

        b2 = scalar.i64(2)

        result2 = div(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

    def test_div_scalar_by_vector(self):
        """Test scalar divided by vector (element-wise)."""
        a = scalar.i64(30)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(3)
        b[2] = scalar.i64(5)

        result = div(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [15, 10, 6]  # 30/2, 30/3, 30/5

    def test_integer_division_truncation(self):
        """Test that integer division behaves like Python's // operator."""
        # Integer division truncation
        a = scalar.i64(5)
        b = scalar.i64(2)
        result = div(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 2  # 5 // 2 = 2

        # Negative integer division
        c = scalar.i64(-5)
        d = scalar.i64(2)
        result2 = div(c, d)

        assert isinstance(result2, scalar.i64)
        # В Python -5 // 2 = -3 (округление вниз)
        assert result2.value == -3  # -5 // 2 = -3 (округление вниз в Python)

        # Vector integer division truncation
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(5)
        vec_a[1] = scalar.i64(7)
        vec_a[2] = scalar.i64(9)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(2)
        vec_b[1] = scalar.i64(3)
        vec_b[2] = scalar.i64(4)

        result3 = div(vec_a, vec_b)

        assert isinstance(result3, container.Vector)
        assert result3.class_type == scalar.i64

        result_values = [item.value for item in result3.to_list()]
        assert result_values == [
            2,
            2,
            2,
        ]  # 5//2=2, 7//3=2, 9//4=2 (целочисленное деление)

    def test_error_division_by_zero(self):
        """Test that division by zero raises an error."""
        a = scalar.i64(10)
        b = scalar.i64(0)

        with pytest.raises(ValueError, match="Division by zero"):
            div(a, b)

        c = scalar.f64(10.0)
        d = scalar.f64(0.0)

        with pytest.raises(ValueError, match="Division by zero"):
            div(c, d)

        # Vector with zero element
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(10)
        vec_a[1] = scalar.i64(20)
        vec_a[2] = scalar.i64(30)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(2)
        vec_b[1] = scalar.i64(0)  # Zero element
        vec_b[2] = scalar.i64(5)

        with pytest.raises(ValueError, match="Division by zero in vector"):
            div(vec_a, vec_b)

    def test_error_unsupported_scalar_type(self):
        """Test that dividing unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            div(a, b)

    def test_error_timestamp_not_supported(self):
        """Test that dividing with Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        b = scalar.i64(5)

        with pytest.raises(
            ValueError, match="Timestamp type is not supported for division"
        ):
            div(timestamp, b)

        c = scalar.f64(2.5)
        with pytest.raises(
            ValueError, match="Timestamp type is not supported for division"
        ):
            div(c, timestamp)

    def test_error_i16_i32_not_supported(self):
        """Test that dividing i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(10)
        b = scalar.i64(2)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            div(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            div(c, b)

        # i16 vector
        a_vec = container.Vector(scalar.i16, 3)
        a_vec[0] = scalar.i16(10)
        a_vec[1] = scalar.i16(20)
        a_vec[2] = scalar.i16(30)

        b_vec = container.Vector(scalar.i64, 3)
        b_vec[0] = scalar.i64(2)
        b_vec[1] = scalar.i64(4)
        b_vec[2] = scalar.i64(6)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            div(a_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that dividing unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            div(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that dividing vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(4)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            div(a, b)


class TestFdivOperation:
    """Tests for the fdiv operation in raypy.math.operations."""

    def test_fdiv_i64_scalars(self):
        """Test float-dividing two i64 scalars."""
        a = scalar.i64(10)
        b = scalar.i64(2)
        result = fdiv(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 5.0

        # Float division with fraction
        c = scalar.i64(5)
        d = scalar.i64(2)
        result = fdiv(c, d)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.5  # 5 / 2 = 2.5

    def test_fdiv_f64_scalars(self):
        """Test float-dividing two f64 scalars."""
        a = scalar.f64(10.0)
        b = scalar.f64(2.0)
        result = fdiv(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 5.0

        # With fraction in result
        c = scalar.f64(5.0)
        d = scalar.f64(2.0)
        result = fdiv(c, d)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.5  # 5.0 / 2.0 = 2.5

    def test_fdiv_mixed_scalars(self):
        """Test float-dividing i64 and f64 scalars."""
        # i64 / f64
        a = scalar.i64(10)
        b = scalar.f64(2.0)
        result = fdiv(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 5.0

        # f64 / i64
        c = scalar.f64(5.0)
        d = scalar.i64(2)
        result = fdiv(c, d)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.5  # fdiv() выполняет деление с плавающей точкой

    def test_fdiv_i64_vectors(self):
        """Test float-dividing two i64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(3)
        b[2] = scalar.i64(4)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 5.0, 5.0]  # 10/2, 15/3, 20/4

    def test_fdiv_f64_vectors(self):
        """Test float-dividing two f64 vectors (element-wise)."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(10.0)
        a[1] = scalar.f64(15.0)
        a[2] = scalar.f64(20.0)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(2.0)
        b[1] = scalar.f64(3.0)
        b[2] = scalar.f64(4.0)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 5.0, 5.0]  # 10/2, 15/3, 20/4

    def test_fdiv_mixed_vectors(self):
        """Test float-dividing i64 and f64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(15)
        a[2] = scalar.i64(20)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(2.0)
        b[1] = scalar.f64(3.0)
        b[2] = scalar.f64(4.0)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 5.0, 5.0]  # 10/2, 15/3, 20/4

    def test_fdiv_vector_by_scalar(self):
        """Test float-dividing a vector by a scalar (scalar broadcast)."""
        # i64 вектор / i64 скаляр
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = scalar.i64(2)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

        # f64 вектор / f64 скаляр
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(20.0)
        a2[2] = scalar.f64(30.0)

        b2 = scalar.f64(2.0)

        result2 = fdiv(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

    def test_fdiv_mixed_vector_by_scalar(self):
        """Test float-dividing mixed vector types by scalars."""
        # i64 вектор / f64 скаляр
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = scalar.f64(2.0)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

        # f64 вектор / i64 скаляр
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(20.0)
        a2[2] = scalar.f64(30.0)

        b2 = scalar.i64(2)

        result2 = fdiv(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [5.0, 10.0, 15.0]  # 10/2, 20/2, 30/2

    def test_fdiv_scalar_by_vector(self):
        """Test float-dividing scalar by vector (element-wise)."""
        a = scalar.i64(30)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(3)
        b[2] = scalar.i64(5)

        result = fdiv(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [15.0, 10.0, 6.0]  # 30/2, 30/3, 30/5

    def test_fdiv_fractions(self):
        """Test that fdiv correctly handles fractional results."""
        # Integer division with fraction
        a = scalar.i64(5)
        b = scalar.i64(2)
        result = fdiv(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.5  # 5 / 2 = 2.5

        # Negative integer division
        c = scalar.i64(-5)
        d = scalar.i64(2)
        result2 = fdiv(c, d)

        assert isinstance(result2, scalar.f64)
        assert result2.value == -2.5  # -5 / 2 = -2.5

        # Vector fraction division
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(5)
        vec_a[1] = scalar.i64(7)
        vec_a[2] = scalar.i64(9)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(2)
        vec_b[1] = scalar.i64(3)
        vec_b[2] = scalar.i64(4)

        result3 = fdiv(vec_a, vec_b)

        assert isinstance(result3, container.Vector)
        assert result3.class_type == scalar.f64

        result_values = [item.value for item in result3.to_list()]
        assert result_values == [
            2.5,
            2.3333333333333335,
            2.25,
        ]  # 5/2=2.5, 7/3≈2.33, 9/4=2.25

    def test_error_division_by_zero(self):
        """Test that float division by zero raises an error."""
        a = scalar.i64(10)
        b = scalar.i64(0)

        with pytest.raises(ValueError, match="Division by zero"):
            fdiv(a, b)

        c = scalar.f64(10.0)
        d = scalar.f64(0.0)

        with pytest.raises(ValueError, match="Division by zero"):
            fdiv(c, d)

        # Vector with zero element
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(10)
        vec_a[1] = scalar.i64(20)
        vec_a[2] = scalar.i64(30)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(2)
        vec_b[1] = scalar.i64(0)  # Zero element
        vec_b[2] = scalar.i64(5)

        with pytest.raises(ValueError, match="Division by zero in vector"):
            fdiv(vec_a, vec_b)

    def test_error_unsupported_scalar_type(self):
        """Test that float-dividing unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            fdiv(a, b)

    def test_error_timestamp_not_supported(self):
        """Test that float-dividing with Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        b = scalar.i64(5)

        with pytest.raises(
            ValueError, match="Timestamp type is not supported for division"
        ):
            fdiv(timestamp, b)

        c = scalar.f64(2.5)
        with pytest.raises(
            ValueError, match="Timestamp type is not supported for division"
        ):
            fdiv(c, timestamp)

    def test_error_i16_i32_not_supported(self):
        """Test that float-dividing i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(10)
        b = scalar.i64(2)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            fdiv(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            fdiv(c, b)

        # i16 vector
        a_vec = container.Vector(scalar.i16, 3)
        a_vec[0] = scalar.i16(10)
        a_vec[1] = scalar.i16(20)
        a_vec[2] = scalar.i16(30)

        b_vec = container.Vector(scalar.i64, 3)
        b_vec[0] = scalar.i64(2)
        b_vec[1] = scalar.i64(4)
        b_vec[2] = scalar.i64(6)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            fdiv(a_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that float-dividing unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            fdiv(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that float-dividing vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(4)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            fdiv(a, b)


class TestModOperation:
    """Tests for the mod operation in raypy.math.operations."""

    def test_mod_i64_scalars(self):
        """Test modulo operation on two i64 scalars."""
        a = scalar.i64(10)
        b = scalar.i64(3)
        result = mod(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 1  # 10 % 3 = 1

        # Negative modulo behaves like Python's modulo
        # In Python: -7 % 3 = 2 (always returns positive result for positive divisor)
        c = scalar.i64(-7)
        d = scalar.i64(3)
        result2 = mod(c, d)

        assert isinstance(result2, scalar.i64)
        assert result2.value == 2  # Python behavior: -7 % 3 = 2

    def test_mod_f64_scalars(self):
        """Test modulo operation on two f64 scalars."""
        a = scalar.f64(10.0)
        b = scalar.f64(3.0)
        result = mod(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 1.0  # 10.0 % 3.0 = 1.0

        # Negative modulo with f64 follows Python's behavior
        c = scalar.f64(-7.0)
        d = scalar.f64(3.0)
        result2 = mod(c, d)

        assert isinstance(result2, scalar.f64)
        assert result2.value == 2.0  # Python behavior: -7.0 % 3.0 = 2.0

    def test_mod_mixed_scalars(self):
        """Test modulo operation with i64 and f64 scalars."""
        # i64 % f64
        a = scalar.i64(10)
        b = scalar.f64(3.0)
        result = mod(a, b)

        # Result is converted to f64 when mixing with f64
        assert isinstance(result, scalar.f64)
        assert result.value == 1.0

        # f64 % i64
        c = scalar.f64(10.0)
        d = scalar.i64(3)
        result2 = mod(c, d)

        assert isinstance(result2, scalar.f64)
        assert result2.value == 1.0

    def test_mod_i64_vectors(self):
        """Test modulo operation on two i64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(11)
        a[2] = scalar.i64(12)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(3)
        b[1] = scalar.i64(4)
        b[2] = scalar.i64(5)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1, 3, 2]  # 10%3=1, 11%4=3, 12%5=2

    def test_mod_f64_vectors(self):
        """Test modulo operation on two f64 vectors (element-wise)."""
        a = container.Vector(scalar.f64, 3)
        a[0] = scalar.f64(10.0)
        a[1] = scalar.f64(11.0)
        a[2] = scalar.f64(12.0)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(3.0)
        b[1] = scalar.f64(4.0)
        b[2] = scalar.f64(5.0)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [
            1.0,
            3.0,
            2.0,
        ]  # 10.0%3.0=1.0, 11.0%4.0=3.0, 12.0%5.0=2.0

    def test_mod_mixed_vectors(self):
        """Test modulo operation on i64 and f64 vectors (element-wise)."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(11)
        a[2] = scalar.i64(12)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(3.0)
        b[1] = scalar.f64(4.0)
        b[2] = scalar.f64(5.0)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        # When mixing i64 and f64, result is converted to f64
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1.0, 3.0, 2.0]  # 10%3=1, 11%4=3, 12%5=2

    def test_mod_vector_by_scalar(self):
        """Test modulo operation of a vector by a scalar (scalar broadcast)."""
        # i64 vector % i64 scalar
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(11)
        a[2] = scalar.i64(12)

        b = scalar.i64(3)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1, 2, 0]  # 10%3=1, 11%3=2, 12%3=0

        # f64 vector % f64 scalar
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(11.0)
        a2[2] = scalar.f64(12.0)

        b2 = scalar.f64(3.0)

        result2 = mod(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [
            1.0,
            2.0,
            0.0,
        ]  # 10.0%3.0=1.0, 11.0%3.0=2.0, 12.0%3.0=0.0

    def test_mod_mixed_vector_by_scalar(self):
        """Test modulo operation with mixed vector and scalar types."""
        # i64 vector % f64 scalar
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(11)
        a[2] = scalar.i64(12)

        b = scalar.f64(3.0)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        # When mixing i64 and f64, result is converted to f64
        assert result.class_type == scalar.f64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1.0, 2.0, 0.0]  # 10%3=1, 11%3=2, 12%3=0

        # f64 vector % i64 scalar
        a2 = container.Vector(scalar.f64, 3)
        a2[0] = scalar.f64(10.0)
        a2[1] = scalar.f64(11.0)
        a2[2] = scalar.f64(12.0)

        b2 = scalar.i64(3)

        result2 = mod(a2, b2)

        assert isinstance(result2, container.Vector)
        assert result2.class_type == scalar.f64

        result_values2 = [item.value for item in result2.to_list()]
        assert result_values2 == [1.0, 2.0, 0.0]  # 10.0%3=1.0, 11.0%3=2.0, 12.0%3=0.0

    def test_mod_scalar_by_vector(self):
        """Test scalar modulo vector (element-wise)."""
        a = scalar.i64(10)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(3)
        b[1] = scalar.i64(4)
        b[2] = scalar.i64(5)

        result = mod(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_values = [item.value for item in result.to_list()]
        assert result_values == [1, 2, 0]  # 10%3=1, 10%4=2, 10%5=0

    def test_negative_modulo(self):
        """Test that modulo operation handles negative numbers like Python's modulo."""
        # In Python: -7 % 3 = 2 (always returns positive result for positive divisor)

        # Testing with negative dividend
        a = scalar.i64(-7)
        b = scalar.i64(3)
        result = mod(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 2  # Python behavior: -7 % 3 = 2

        # Testing with negative divisor
        c = scalar.i64(7)
        d = scalar.i64(-3)
        result2 = mod(c, d)

        assert isinstance(result2, scalar.i64)
        assert result2.value == -2  # Python behavior: 7 % -3 = -2

        # Testing with both negative
        e = scalar.i64(-7)
        f = scalar.i64(-3)
        result3 = mod(e, f)

        assert isinstance(result3, scalar.i64)
        assert result3.value == -1  # Python behavior: -7 % -3 = -1

        # Vector negative modulo
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(-7)
        vec_a[1] = scalar.i64(-9)
        vec_a[2] = scalar.i64(-11)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(3)
        vec_b[1] = scalar.i64(4)
        vec_b[2] = scalar.i64(5)

        result4 = mod(vec_a, vec_b)

        assert isinstance(result4, container.Vector)
        assert result4.class_type == scalar.i64

        result_values = [item.value for item in result4.to_list()]
        assert result_values == [2, 3, 4]  # Python behavior: -7%3=2, -9%4=3, -11%5=4

    def test_error_division_by_zero(self):
        """Test that modulo by zero raises an error."""
        a = scalar.i64(10)
        b = scalar.i64(0)

        with pytest.raises(ValueError, match="Division by zero"):
            mod(a, b)

        c = scalar.f64(10.0)
        d = scalar.f64(0.0)

        with pytest.raises(ValueError, match="Division by zero"):
            mod(c, d)

        # Vector with zero element
        vec_a = container.Vector(scalar.i64, 3)
        vec_a[0] = scalar.i64(10)
        vec_a[1] = scalar.i64(20)
        vec_a[2] = scalar.i64(30)

        vec_b = container.Vector(scalar.i64, 3)
        vec_b[0] = scalar.i64(3)
        vec_b[1] = scalar.i64(0)  # Zero element
        vec_b[2] = scalar.i64(5)

        with pytest.raises(ValueError, match="Division by zero in vector"):
            mod(vec_a, vec_b)

    def test_error_unsupported_scalar_type(self):
        """Test that modulo with unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError):
            mod(a, b)

    def test_error_timestamp_not_supported(self):
        """Test that modulo with Timestamp raises an error."""
        timestamp = scalar.Timestamp(dt.datetime.now())
        b = scalar.i64(5)

        with pytest.raises(
            ValueError, match="Timestamp type is not supported for modulo"
        ):
            mod(timestamp, b)

        c = scalar.f64(2.5)
        with pytest.raises(
            ValueError, match="Timestamp type is not supported for modulo"
        ):
            mod(c, timestamp)

    def test_error_i16_i32_not_supported(self):
        """Test that modulo with i16 and i32 raises an error."""
        # i16 scalar
        a = scalar.i16(10)
        b = scalar.i64(3)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            mod(a, b)

        # i32 scalar
        c = scalar.i32(15)

        with pytest.raises(ValueError, match="Types i16 and i32 are not supported"):
            mod(c, b)

        # i16 vector
        a_vec = container.Vector(scalar.i16, 3)
        a_vec[0] = scalar.i16(10)
        a_vec[1] = scalar.i16(20)
        a_vec[2] = scalar.i16(30)

        b_vec = container.Vector(scalar.i64, 3)
        b_vec[0] = scalar.i64(3)
        b_vec[1] = scalar.i64(4)
        b_vec[2] = scalar.i64(6)

        with pytest.raises(
            ValueError, match="Vector types i16 and i32 are not supported"
        ):
            mod(a_vec, b_vec)

    def test_error_unsupported_vector_type(self):
        """Test that modulo with unsupported vector element types raises an error."""
        a = container.Vector(scalar.Symbol, 3)
        a[0] = scalar.Symbol("a")
        a[1] = scalar.Symbol("b")
        a[2] = scalar.Symbol("c")

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        with pytest.raises(ValueError):
            mod(a, b)

    def test_error_mismatched_vector_lengths(self):
        """Test that modulo with vectors of different lengths raises an error."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(10)
        a[1] = scalar.i64(20)
        a[2] = scalar.i64(30)

        b = container.Vector(scalar.i64, 2)
        b[0] = scalar.i64(3)
        b[1] = scalar.i64(4)

        with pytest.raises(ValueError, match="Vectors must be of same length"):
            mod(a, b)


class TestSumOperation:
    """Tests for the sum operation in raypy.math.operations."""

    def test_sum_scalar(self):
        """Test summing scalar values (which simply returns the input)."""
        # i64 scalar
        a = scalar.i64(42)
        result = sum(a)

        assert isinstance(result, scalar.i64)
        assert result.value == 42

        # f64 scalar
        b = scalar.f64(3.14)
        result = sum(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.14

    def test_sum_i64_vector(self):
        """Test summing i64 vector elements."""
        # Create vector [1, 2, 3, 4, 5]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)
        a[3] = scalar.i64(4)
        a[4] = scalar.i64(5)

        result = sum(a)

        assert isinstance(result, scalar.i64)
        assert result.value == 15  # 1 + 2 + 3 + 4 + 5 = 15

        # Test empty vector
        empty = container.Vector(scalar.i64, 0)
        result = sum(empty)

        assert isinstance(result, scalar.i64)
        assert result.value == 0

    def test_sum_f64_vector(self):
        """Test summing f64 vector elements."""
        # Create vector [1.5, 2.5, 3.5, 4.5, 5.5]
        a = container.Vector(scalar.f64, 5)
        a[0] = scalar.f64(1.5)
        a[1] = scalar.f64(2.5)
        a[2] = scalar.f64(3.5)
        a[3] = scalar.f64(4.5)
        a[4] = scalar.f64(5.5)

        result = sum(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 17.5  # 1.5 + 2.5 + 3.5 + 4.5 + 5.5 = 17.5

        # Test empty vector
        empty = container.Vector(scalar.f64, 0)
        result = sum(empty)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0

    def test_sum_negative_values(self):
        """Test summing with negative values."""
        # Create vector [5, -3, 2, -8, 4]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(5)
        a[1] = scalar.i64(-3)
        a[2] = scalar.i64(2)
        a[3] = scalar.i64(-8)
        a[4] = scalar.i64(4)

        result = sum(a)

        assert isinstance(result, scalar.i64)
        assert result.value == 0  # 5 - 3 + 2 - 8 + 4 = 0

    def test_error_unsupported_type(self):
        """Test that providing an unsupported type raises an error."""
        # Symbol scalar
        sym = scalar.Symbol("test")
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            sum(sym)

        # Timestamp scalar
        ts = scalar.Timestamp(dt.datetime.now())
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            sum(ts)

    def test_error_unsupported_vector_type(self):
        """Test that unsupported vector types raise an error."""
        # Create symbol vector
        sym_vec = container.Vector(scalar.Symbol, 3)
        sym_vec[0] = scalar.Symbol("a")
        sym_vec[1] = scalar.Symbol("b")
        sym_vec[2] = scalar.Symbol("c")

        with pytest.raises(ValueError, match="Vector must be of type i64 or f64"):
            sum(sym_vec)

        # Create timestamp vector
        now = dt.datetime.now()
        ts_vec = container.Vector(scalar.Timestamp, 3)
        ts_vec[0] = scalar.Timestamp(now)
        ts_vec[1] = scalar.Timestamp(now + dt.timedelta(seconds=1))
        ts_vec[2] = scalar.Timestamp(now + dt.timedelta(seconds=2))

        with pytest.raises(ValueError, match="Vector must be of type i64 or f64"):
            sum(ts_vec)


class TestAvgOperation:
    """Tests for the avg operation in raypy.math.operations."""

    def test_avg_scalar(self):
        """Test averaging scalar values (converts to f64)."""
        # i64 scalar
        a = scalar.i64(42)
        result = avg(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 42.0

        # f64 scalar
        b = scalar.f64(3.14)
        result = avg(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.14

    def test_avg_i64_vector(self):
        """Test averaging i64 vector elements."""
        # Create vector [1, 2, 3, 4, 5]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)
        a[3] = scalar.i64(4)
        a[4] = scalar.i64(5)

        result = avg(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.0  # (1 + 2 + 3 + 4 + 5) / 5 = 3.0

        # Test empty vector
        empty = container.Vector(scalar.i64, 0)
        result = avg(empty)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0

    def test_avg_f64_vector(self):
        """Test averaging f64 vector elements."""
        # F64 vectors are not supported by the core implementation
        # Create scalar f64 since vectors are not supported
        a = scalar.f64(3.5)
        result = avg(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.5

    def test_error_unsupported_vector_type(self):
        """Test that unsupported vector types raise an error."""
        # Create symbol vector
        sym_vec = container.Vector(scalar.Symbol, 3)
        sym_vec[0] = scalar.Symbol("a")
        sym_vec[1] = scalar.Symbol("b")
        sym_vec[2] = scalar.Symbol("c")

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            avg(sym_vec)

        # Create f64 vector
        f64_vec = container.Vector(scalar.f64, 3)
        f64_vec[0] = scalar.f64(1.5)
        f64_vec[1] = scalar.f64(2.5)
        f64_vec[2] = scalar.f64(3.5)

        with pytest.raises(ValueError, match="F64 vectors are not supported"):
            avg(f64_vec)

        # Create timestamp vector
        now = dt.datetime.now()
        ts_vec = container.Vector(scalar.Timestamp, 3)
        ts_vec[0] = scalar.Timestamp(now)
        ts_vec[1] = scalar.Timestamp(now + dt.timedelta(seconds=1))
        ts_vec[2] = scalar.Timestamp(now + dt.timedelta(seconds=2))

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            avg(ts_vec)

    def test_avg_negative_values(self):
        """Test averaging with negative values."""
        # Create vector [5, -3, 2, -8, 4]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(5)
        a[1] = scalar.i64(-3)
        a[2] = scalar.i64(2)
        a[3] = scalar.i64(-8)
        a[4] = scalar.i64(4)

        result = avg(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0  # (5 - 3 + 2 - 8 + 4) / 5 = 0.0

    def test_error_unsupported_type(self):
        """Test that providing an unsupported type raises an error."""
        # Symbol scalar
        sym = scalar.Symbol("test")
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            avg(sym)

        # Timestamp scalar
        ts = scalar.Timestamp(dt.datetime.now())
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            avg(ts)

    def test_avg_single_element_vector(self):
        """Test averaging a vector with a single element."""
        # Create vector with single i64 element
        a = container.Vector(scalar.i64, 1)
        a[0] = scalar.i64(42)

        result = avg(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 42.0


class TestMedOperation:
    """Tests for the med operation in raypy.math.operations."""

    def test_med_scalar(self):
        """Test median of scalar values (converts to f64)."""
        # i64 scalar
        a = scalar.i64(42)
        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 42.0

        # f64 scalar
        b = scalar.f64(3.14)
        result = med(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.14

    def test_med_i64_vector_odd(self):
        """Test median of i64 vector with odd length."""
        # Create vector [1, 2, 3, 4, 5]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)
        a[3] = scalar.i64(4)
        a[4] = scalar.i64(5)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.0  # Middle value of [1, 2, 3, 4, 5] is 3

        # Test with unsorted vector [5, 3, 1, 4, 2]
        b = container.Vector(scalar.i64, 5)
        b[0] = scalar.i64(5)
        b[1] = scalar.i64(3)
        b[2] = scalar.i64(1)
        b[3] = scalar.i64(4)
        b[4] = scalar.i64(2)

        result = med(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.0  # Middle value of sorted [1, 2, 3, 4, 5] is 3

    def test_med_i64_vector_even(self):
        """Test median of i64 vector with even length."""
        # Create vector [1, 2, 3, 4, 5, 6]
        a = container.Vector(scalar.i64, 6)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)
        a[3] = scalar.i64(4)
        a[4] = scalar.i64(5)
        a[5] = scalar.i64(6)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.5  # Average of 3 and 4 is 3.5

        # Test with unsorted vector [6, 4, 2, 5, 3, 1]
        b = container.Vector(scalar.i64, 6)
        b[0] = scalar.i64(6)
        b[1] = scalar.i64(4)
        b[2] = scalar.i64(2)
        b[3] = scalar.i64(5)
        b[4] = scalar.i64(3)
        b[5] = scalar.i64(1)

        result = med(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.5  # Average of 3 and 4 is 3.5

    @pytest.mark.skip(reason="F64 vectors are not supported for the median operation")
    def test_med_f64_vector_odd(self):
        """Test median of f64 vector with odd length."""
        # Create vector [1.5, 2.5, 3.5, 4.5, 5.5]
        a = container.Vector(scalar.f64, 5)
        a[0] = scalar.f64(1.5)
        a[1] = scalar.f64(2.5)
        a[2] = scalar.f64(3.5)
        a[3] = scalar.f64(4.5)
        a[4] = scalar.f64(5.5)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 3.5  # Middle value is 3.5

    @pytest.mark.skip(reason="F64 vectors are not supported for the median operation")
    def test_med_f64_vector_even(self):
        """Test median of f64 vector with even length."""
        # Create vector [1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
        a = container.Vector(scalar.f64, 6)
        a[0] = scalar.f64(1.5)
        a[1] = scalar.f64(2.5)
        a[2] = scalar.f64(3.5)
        a[3] = scalar.f64(4.5)
        a[4] = scalar.f64(5.5)
        a[5] = scalar.f64(6.5)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 4.0  # Average of 3.5 and 4.5 is 4.0

    def test_med_negative_values(self):
        """Test median with negative values."""
        # Create vector [5, -3, 2, -8, 4]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(5)
        a[1] = scalar.i64(-3)
        a[2] = scalar.i64(2)
        a[3] = scalar.i64(-8)
        a[4] = scalar.i64(4)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 2.0  # Sorted: [-8, -3, 2, 4, 5], middle is 2

    def test_med_empty_vector(self):
        """Test median of an empty vector."""
        # Empty i64 vector
        empty_i64 = container.Vector(scalar.i64, 0)
        result = med(empty_i64)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0

    def test_error_unsupported_type(self):
        """Test that providing an unsupported type raises an error."""
        # Symbol scalar
        sym = scalar.Symbol("test")
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            med(sym)

        # Timestamp scalar
        ts = scalar.Timestamp(dt.datetime.now())
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            med(ts)

    def test_error_unsupported_vector_type(self):
        """Test that unsupported vector types raise an error."""
        # Create symbol vector
        sym_vec = container.Vector(scalar.Symbol, 3)
        sym_vec[0] = scalar.Symbol("a")
        sym_vec[1] = scalar.Symbol("b")
        sym_vec[2] = scalar.Symbol("c")

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            med(sym_vec)

        # Create f64 vector
        f64_vec = container.Vector(scalar.f64, 3)
        f64_vec[0] = scalar.f64(1.5)
        f64_vec[1] = scalar.f64(2.5)
        f64_vec[2] = scalar.f64(3.5)

        with pytest.raises(ValueError, match="F64 vectors are not supported"):
            med(f64_vec)

        # Create timestamp vector
        now = dt.datetime.now()
        ts_vec = container.Vector(scalar.Timestamp, 3)
        ts_vec[0] = scalar.Timestamp(now)
        ts_vec[1] = scalar.Timestamp(now + dt.timedelta(seconds=1))
        ts_vec[2] = scalar.Timestamp(now + dt.timedelta(seconds=2))

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            med(ts_vec)

    def test_med_single_element_vector(self):
        """Test median of a vector with a single element."""
        # Create vector with single i64 element
        a = container.Vector(scalar.i64, 1)
        a[0] = scalar.i64(42)

        result = med(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 42.0


class TestDevOperation:
    """Tests for the dev operation in raypy.math.operations."""

    def test_dev_scalar(self):
        """Test standard deviation of scalar values (converts to f64)."""
        # i64 scalar
        a = scalar.i64(42)
        result = dev(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0  # Single value has std dev of 0

        # f64 scalar
        b = scalar.f64(3.14)
        result = dev(b)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0  # Single value has std dev of 0

    def test_dev_i64_vector(self):
        """Test standard deviation of i64 vector elements."""
        # Create vector [1, 2, 3, 4, 5]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)
        a[3] = scalar.i64(4)
        a[4] = scalar.i64(5)

        result = dev(a)

        assert isinstance(result, scalar.f64)
        assert round(result.value, 6) == 1.414214  # std dev of [1, 2, 3, 4, 5] is √2

        # Test with different values [2, 4, 4, 4, 5, 5, 7, 9]
        b = container.Vector(scalar.i64, 8)
        b[0] = scalar.i64(2)
        b[1] = scalar.i64(4)
        b[2] = scalar.i64(4)
        b[3] = scalar.i64(4)
        b[4] = scalar.i64(5)
        b[5] = scalar.i64(5)
        b[6] = scalar.i64(7)
        b[7] = scalar.i64(9)

        result = dev(b)

        assert isinstance(result, scalar.f64)
        assert round(result.value, 6) == 2.0  # std dev of [2, 4, 4, 4, 5, 5, 7, 9] is 2

    def test_dev_empty_vector(self):
        """Test standard deviation of an empty vector."""
        # Empty i64 vector
        empty_i64 = container.Vector(scalar.i64, 0)
        result = dev(empty_i64)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0 or math.isnan(
            result.value
        )  # NaN or 0.0 are both acceptable

    def test_error_unsupported_vector_type(self):
        """Test that unsupported vector types raise an error."""
        # Create symbol vector
        sym_vec = container.Vector(scalar.Symbol, 3)
        sym_vec[0] = scalar.Symbol("a")
        sym_vec[1] = scalar.Symbol("b")
        sym_vec[2] = scalar.Symbol("c")

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            dev(sym_vec)

        # Create f64 vector
        f64_vec = container.Vector(scalar.f64, 3)
        f64_vec[0] = scalar.f64(1.5)
        f64_vec[1] = scalar.f64(2.5)
        f64_vec[2] = scalar.f64(3.5)

        with pytest.raises(ValueError, match="F64 vectors are not supported"):
            dev(f64_vec)

        # Create timestamp vector
        now = dt.datetime.now()
        ts_vec = container.Vector(scalar.Timestamp, 3)
        ts_vec[0] = scalar.Timestamp(now)
        ts_vec[1] = scalar.Timestamp(now + dt.timedelta(seconds=1))
        ts_vec[2] = scalar.Timestamp(now + dt.timedelta(seconds=2))

        with pytest.raises(ValueError, match="Vector must be of type i64"):
            dev(ts_vec)

    def test_dev_negative_values(self):
        """Test standard deviation with negative values."""
        # Create vector [5, -3, 2, -8, 4]
        a = container.Vector(scalar.i64, 5)
        a[0] = scalar.i64(5)
        a[1] = scalar.i64(-3)
        a[2] = scalar.i64(2)
        a[3] = scalar.i64(-8)
        a[4] = scalar.i64(4)

        result = dev(a)

        assert isinstance(result, scalar.f64)
        assert round(result.value, 6) == 4.857983  # std dev of [5, -3, 2, -8, 4]

    def test_error_unsupported_type(self):
        """Test that providing an unsupported type raises an error."""
        # Symbol scalar
        sym = scalar.Symbol("test")
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            dev(sym)

        # Timestamp scalar
        ts = scalar.Timestamp(dt.datetime.now())
        with pytest.raises(
            ValueError, match="Input must be a scalar or vector of type i64 or f64"
        ):
            dev(ts)

    def test_dev_single_element_vector(self):
        """Test standard deviation of a vector with a single element."""
        # Create vector with single i64 element
        a = container.Vector(scalar.i64, 1)
        a[0] = scalar.i64(42)

        result = dev(a)

        assert isinstance(result, scalar.f64)
        assert result.value == 0.0  # Single element vector has std dev of 0
