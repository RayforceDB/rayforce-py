import pytest
import numpy as np
from raypy.types import scalar, container
from raypy.math.operations import add


class TestMathOperations:
    """Tests for the mathematical operations in raypy.math.operations."""

    def test_add_scalar_integers(self):
        """Test adding two scalar integers."""
        a = scalar.i64(5)
        b = scalar.i64(10)
        result = add(a, b)

        assert isinstance(result, scalar.i64)
        assert result.value == 15

    def test_add_scalar_floats(self):
        """Test adding two scalar floats."""
        a = scalar.f64(3.5)
        b = scalar.f64(2.5)
        result = add(a, b)

        assert isinstance(result, scalar.f64)
        assert result.value == 6.0

    def test_add_mixed_scalar_types(self):
        """Test adding int and float scalar types."""
        a = scalar.i64(5)
        b = scalar.f64(2.5)
        result = add(a, b)

        # Результат должен быть типа f64 при смешанных операциях
        assert isinstance(result, scalar.f64)
        assert result.value == 7.5

    def test_add_integer_vectors(self):
        """Test adding two integer vectors."""
        # Создаем векторы с нужным типом и длиной
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

        result_list = result.to_list()
        assert len(result_list) == 3
        assert result_list[0].value == 5
        assert result_list[1].value == 7
        assert result_list[2].value == 9

    def test_add_float_vectors(self):
        """Test adding two float vectors."""
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

        result_list = result.to_list()
        assert len(result_list) == 3
        assert result_list[0].value == 2.0
        assert result_list[1].value == 4.0
        assert result_list[2].value == 6.0

    def test_add_mixed_vector_types(self):
        """Test adding integer and float vectors."""
        a = container.Vector(scalar.i64, 3)
        a[0] = scalar.i64(1)
        a[1] = scalar.i64(2)
        a[2] = scalar.i64(3)

        b = container.Vector(scalar.f64, 3)
        b[0] = scalar.f64(0.5)
        b[1] = scalar.f64(1.5)
        b[2] = scalar.f64(2.5)

        result = add(a, b)

        # Результат должен быть типа Vector[f64] при смешанных операциях
        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.f64

        result_list = result.to_list()
        assert len(result_list) == 3
        assert result_list[0].value == 1.5
        assert result_list[1].value == 3.5
        assert result_list[2].value == 5.5

    def test_add_scalar_and_vector(self):
        """Test adding a scalar to a vector (scalar broadcast)."""
        a = scalar.i64(5)

        b = container.Vector(scalar.i64, 3)
        b[0] = scalar.i64(1)
        b[1] = scalar.i64(2)
        b[2] = scalar.i64(3)

        result = add(a, b)

        assert isinstance(result, container.Vector)
        assert result.class_type == scalar.i64

        result_list = result.to_list()
        assert len(result_list) == 3
        assert result_list[0].value == 6
        assert result_list[1].value == 7
        assert result_list[2].value == 8

    def test_error_unsupported_scalar_type(self):
        """Test that adding unsupported scalar types raises an error."""
        a = scalar.Symbol("test")
        b = scalar.i64(5)

        with pytest.raises(ValueError, match="Argument has to be of type i64 or f64"):
            add(a, b)

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

        with pytest.raises(ValueError, match="Vector has to be of type i64 or f64"):
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

        # Ожидаем какое-то исключение при попытке сложения векторов разной длины
        # API может генерировать различные исключения в зависимости от версии Python или raypy
        with pytest.raises((TypeError, ValueError)):
            add(a, b)
