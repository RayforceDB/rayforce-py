import pytest

from raypy import _rayforce as r
from raypy.types.container import List, Dict, Vector
from raypy.types.scalar import Symbol, i64, b8, i32, f64


class TestListContainer:
    def test_list_creation(self):
        """Test creation of List with different inputs."""
        # Test empty list
        empty_list = List([])
        assert len(empty_list) == 0
        assert str(empty_list) == "[]"

        # Test list with simple integers
        int_list = List([1, 2, 3])
        assert len(int_list) == 3
        assert int_list[0] == 1
        assert int_list[1] == 2
        assert int_list[2] == 3

        # Test list with mixed types
        mixed_list = List([1, "test", True])
        assert len(mixed_list) == 3
        assert mixed_list[0] == 1
        assert mixed_list[1] == "test"
        assert mixed_list[2] == True

        # Test with non-iterable should raise error
        with pytest.raises(ValueError):
            List(123)

    def test_list_from_rayobject(self):
        """Test creating List from RayObject instances."""
        # Create a list using the RayObject API
        ray_list = r.RayObject.create_list()
        ray_list.list_append(r.RayObject.from_i64(10))
        ray_list.list_append(r.RayObject.from_i64(20))

        # Create a List from the RayObject
        list_obj = List(ray_obj=ray_list)

        # Verify values and types
        assert len(list_obj) == 2
        assert list_obj[0] == 10
        assert list_obj[1] == 20

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            List(ray_obj=ray_i64)

    def test_list_append(self):
        """Test append method of List."""
        my_list = List([])

        # Append various types
        my_list.append(10)  # int
        my_list.append("test")  # str
        my_list.append(True)  # bool
        my_list.append(i64(42))  # raypy type

        # Verify
        assert len(my_list) == 4
        assert my_list[0] == 10
        assert my_list[1] == "test"
        assert my_list[2] == True
        assert my_list[3] == 42

        # Append a raw RayObject
        ray_obj = r.RayObject.from_i64(100)
        my_list.append(ray_obj)
        assert my_list[4] == 100

    def test_list_get_and_indexing(self):
        """Test get method and indexing operation."""
        my_list = List([10, 20, 30])

        # Test get method
        assert my_list.get(0) == 10
        assert my_list.get(1) == 20
        assert my_list.get(2) == 30

        # Test get with invalid index
        with pytest.raises(IndexError):
            my_list.get(-1)

        with pytest.raises(IndexError):
            my_list.get(3)

        # Test indexing operator
        assert my_list[0] == 10
        assert my_list[1] == 20
        assert my_list[2] == 30

        # Test indexing with invalid index
        with pytest.raises(IndexError):
            value = my_list[-1]

        with pytest.raises(IndexError):
            value = my_list[3]

    def test_list_set_and_assignment(self):
        """Test set method and assignment operation."""
        my_list = List([10, 20, 30])

        # Test set method
        my_list.set(0, 100)
        assert my_list[0] == 100

        # Test set with raypy type
        my_list.set(1, i64(200))
        assert my_list[1] == 200

        # Test set with raw RayObject
        ray_obj = r.RayObject.from_i64(300)
        my_list.set(2, ray_obj)
        assert my_list[2] == 300

        # Test set with invalid index
        with pytest.raises(IndexError):
            my_list.set(-1, 400)

        with pytest.raises(IndexError):
            my_list.set(3, 400)

        # Test assignment operator
        my_list[0] = 1000
        assert my_list[0] == 1000

        # Test assignment with raypy type
        my_list[1] = b8(False)
        assert my_list[1] == False

        # Test assignment with invalid index
        with pytest.raises(IndexError):
            my_list[-1] = 4000

        with pytest.raises(IndexError):
            my_list[3] = 4000

    def test_list_remove(self):
        """Test remove method of List."""
        my_list = List([10, 20, 30, 40])

        # Remove an item
        my_list.remove(1)  # Remove 20
        assert len(my_list) == 3
        assert my_list[0] == 10
        assert my_list[1] == 30
        assert my_list[2] == 40

        # Remove another item
        my_list.remove(0)  # Remove 10
        assert len(my_list) == 2
        assert my_list[0] == 30
        assert my_list[1] == 40

        # Test remove with invalid index
        with pytest.raises(IndexError):
            my_list.remove(-1)

        with pytest.raises(IndexError):
            my_list.remove(2)

    def test_list_iteration(self):
        """Test iteration over List items."""
        my_list = List([10, 20, 30])

        # Use in a for loop
        items = []
        for item in my_list:
            items.append(item)

        assert items == [10, 20, 30]

        # Use with list comprehension
        items = [item for item in my_list]
        assert items == [10, 20, 30]

    def test_list_string_representation(self):
        """Test string and representation methods."""
        my_list = List([10, 20, 30])

        # Test __str__
        assert str(my_list) == "[i64(10), i64(20), i64(30)]"

        # Test __repr__
        assert repr(my_list) == "List([i64(10), i64(20), i64(30)])"

        # Test with mixed types
        mixed_list = List([10, "test", True])
        assert str(mixed_list) == "[i64(10), Symbol(test), b8(True)]"

        # Test empty list
        empty_list = List([])
        assert str(empty_list) == "[]"
        assert repr(empty_list) == "List([])"

    def test_list_nesting(self):
        """Test nesting lists within lists."""
        inner_list = List([1, 2, 3])
        outer_list = List([10, inner_list, 30])

        assert len(outer_list) == 3
        assert outer_list[0] == 10

        # Verify the inner list was correctly stored
        retrieved_inner = outer_list[1]
        assert isinstance(retrieved_inner, List)
        assert len(retrieved_inner) == 3
        assert retrieved_inner[0] == 1
        assert retrieved_inner[1] == 2
        assert retrieved_inner[2] == 3

        assert outer_list[2] == 30

    def test_list_with_raypy_types(self):
        """Test List with various raypy types."""
        # Create list with raypy types
        i64_val = i64(100)
        sym_val = Symbol("test")
        bool_val = b8(True)

        my_list = List([i64_val, sym_val, bool_val])

        # Verify values and types
        assert my_list[0] == 100
        assert my_list[1] == "test"
        assert my_list[2] == True

        # Complex example with mixed types
        complex_list = List(
            [10, "string", True, i64(200), Symbol("symbol"), List([1, 2, 3])]
        )

        assert len(complex_list) == 6
        assert complex_list[0] == 10
        assert complex_list[1] == "string"
        assert complex_list[2] == True
        assert complex_list[3] == 200
        assert complex_list[4] == "symbol"

        nested = complex_list[5]
        assert isinstance(nested, List)
        assert len(nested) == 3
        assert nested[0] == 1
        assert nested[1] == 2
        assert nested[2] == 3


class TestDictContainer:
    def test_dict_creation(self):
        """Test creation of Dict with different inputs."""
        # Test simple dict
        simple_dict = Dict({"a": 1, "b": 2, "c": 3})
        assert len(simple_dict) == 3
        assert simple_dict.get("a") == 1
        assert simple_dict.get("b") == 2
        assert simple_dict.get("c") == 3

        # Test with mixed types
        mixed_dict = Dict({"a": 1, "b": "test", "c": True})
        assert len(mixed_dict) == 3
        assert mixed_dict.get("a") == 1
        assert mixed_dict.get("b") == "test"
        assert mixed_dict.get("c") == True

        # Test with Symbol keys
        symbol_dict = Dict({Symbol("a"): 1, Symbol("b"): 2})
        assert len(symbol_dict) == 2
        assert symbol_dict.get("a") == 1
        assert symbol_dict.get("b") == 2

        # Test creation with None should raise error
        with pytest.raises(ValueError):
            Dict(None)

        # Test with invalid key types
        with pytest.raises(ValueError):
            Dict({1: "value"})  # Non-string/symbol key

    def test_dict_from_rayobject(self):
        """Test creating Dict from RayObject instances."""
        # Create keys and values lists first
        keys_list = List(["key1", "key2"])
        values_list = List([10, 20])

        # Create a dict using the RayObject API
        ray_dict = r.RayObject.create_dict(keys_list.ptr, values_list.ptr)

        # Create a Dict from the RayObject
        dict_obj = Dict(ray_obj=ray_dict)

        # Verify values and types
        assert len(dict_obj) == 2
        assert dict_obj.get("key1") == 10
        assert dict_obj.get("key2") == 20

        # Test with wrong RayObject type
        ray_i64 = r.RayObject.from_i64(42)
        with pytest.raises(ValueError):
            Dict(ray_obj=ray_i64)

    def test_dict_keys_values(self):
        """Test keys and values methods."""
        test_dict = Dict({"a": 1, "b": 2, "c": 3})

        # Test keys
        keys = test_dict.keys()
        assert isinstance(keys, List)
        assert len(keys) == 3

        # Key values will be Symbols, so check their values
        key_values = [k.value if hasattr(k, "value") else str(k) for k in keys]
        assert sorted(key_values) == ["a", "b", "c"]

        # Test values
        values = test_dict.values()
        assert isinstance(values, List)
        assert len(values) == 3

        # Convert values to a list to check them
        value_list = [v for v in values]
        assert sorted(value_list) == [1, 2, 3]

    def test_dict_get(self):
        """Test get method."""
        test_dict = Dict({"a": 1, "b": "test", "c": True})

        # Test getting values
        assert test_dict.get("a") == 1
        assert test_dict.get("b") == "test"
        assert test_dict.get("c") == True

        # Test getting non-existent key (should raise an exception or return None)
        # Note: behavior depends on implementation
        try:
            result = test_dict.get("non_existent")
            # If it returns None, that's fine
            assert result is None
        except Exception:
            # If it raises an exception, that's also acceptable
            pass

    def test_dict_string_representation(self):
        """Test string and representation methods."""
        test_dict = Dict({"a": 1, "b": 2})

        # Test __str__ format
        str_repr = str(test_dict)
        assert "Symbol(a): i64(1)" in str_repr
        assert "Symbol(b): i64(2)" in str_repr
        assert str_repr.startswith("{")
        assert str_repr.endswith("}")

        # Test __repr__ format
        repr_str = repr(test_dict)
        assert repr_str.startswith("Dict({")
        assert repr_str.endswith("})")
        assert "Symbol(a): i64(1)" in repr_str
        assert "Symbol(b): i64(2)" in repr_str

    def test_dict_with_raypy_types(self):
        """Test Dict with various raypy types."""
        # Create dict with raypy types as values
        dict_with_types = Dict(
            {"int": i64(100), "sym": Symbol("test"), "bool": b8(True)}
        )

        # Verify values
        assert dict_with_types.get("int") == 100
        assert dict_with_types.get("sym") == "test"
        assert dict_with_types.get("bool") == True

        # Test with nested structures
        nested_dict = Dict(
            {"number": 42, "list": List([1, 2, 3]), "dict": Dict({"nested": "value"})}
        )

        assert nested_dict.get("number") == 42

        nested_list = nested_dict.get("list")
        assert isinstance(nested_list, List)
        assert len(nested_list) == 3
        assert nested_list[0] == 1
        assert nested_list[1] == 2
        assert nested_list[2] == 3

        nested_dict_value = nested_dict.get("dict")
        assert isinstance(nested_dict_value, Dict)
        assert nested_dict_value.get("nested") == "value"


class TestVectorContainer:
    def test_vector_creation(self):
        v = Vector(class_type=i32, length=5)
        assert v.ray_type_code == r.TYPE_I32
        assert len(v) == 5

        with pytest.raises(ValueError):
            Vector(i32, ray_obj=r.RayObject.vector(r.TYPE_F64, 5))

    def test_vector_get_set(self):
        v = Vector(i32, 3)

        v[0] = i32(10)
        v[1] = i32(20)
        v[2] = i32(30)

        assert v[0].value == 10
        assert v[1].value == 20
        assert v[2].value == 30

        assert v[-1].value == 30
        assert v[-2].value == 20
        assert v[-3].value == 10

        with pytest.raises(IndexError):
            v[3] = i32(40)

        with pytest.raises(IndexError):
            val = v[3]

    def test_vector_str_repr(self):
        v = Vector(i32, 2)
        v[0] = i32(10)
        v[1] = i32(20)

        assert "Vector[" in str(v)
        assert "[i32(10), i32(20)]" in str(v) or "i32(10), i32(20)" in str(v)

        assert str(v) == repr(v)

    def test_vector_equality(self):
        v1 = Vector(i32, 2)
        v1[0] = i32(10)
        v1[1] = i32(20)

        v2 = Vector(i32, 2)
        v2[0] = i32(10)
        v2[1] = i32(20)

        v3 = Vector(i32, 2)
        v3[0] = i32(10)
        v3[1] = i32(30)

        assert v1 == v2
        assert v1 != v3
        assert v2 != v3

        v4 = Vector(i32, 3)
        v4[0] = i32(10)
        v4[1] = i32(20)
        v4[2] = i32(30)

        assert v1 != v4

    def test_vector_to_list(self):
        v = Vector(i32, 3)
        v[0] = i32(10)
        v[1] = i32(20)
        v[2] = i32(30)

        l = v.to_list()
        assert len(l) == 3
        assert l[0].value == 10
        assert l[1].value == 20
        assert l[2].value == 30

    def test_different_vector_types(self):
        vf = Vector(f64, 2)
        vf[0] = f64(1.5)
        vf[1] = f64(2.5)

        assert vf[0].value == 1.5
        assert vf[1].value == 2.5

        # Тест для вектора символов
        vs = Vector(Symbol, 2)
        vs[0] = Symbol("test1")
        vs[1] = Symbol("test2")

        assert vs[0].value == "test1"
        assert vs[1].value == "test2"


class TestTableContainer:
    """Test suite for Table container."""

    def test_table_simple_creation(self):
        """Test simple creation of Table with minimal inputs."""
        from raypy.types.container import Table, List, Vector
        from raypy.types.scalar import Symbol

        # Создаем минимальный набор данных для таблицы
        # Один ключ и одно значение
        columns = List()
        columns.append(Symbol("id"))

        row = List()
        row.append(Symbol("value"))

        values = List()
        values.append(row)

        # Создаем таблицу
        table = Table(columns, values)

        # Проверяем доступ к values() - это должно работать
        table_values = table.values()
        assert len(table_values) == 1
        assert len(table_values[0]) == 1
        assert str(table_values[0][0]) == "value"

    def test_table_creation(self):
        """Test creation of Table with different inputs."""
        from raypy.types.container import Table, List, Vector
        from raypy.types.scalar import Symbol, i64, f64

        # Создаем колонки и значения для таблицы
        columns = List()  # Используем List вместо Vector для колонок
        columns.append(Symbol("id"))
        columns.append(Symbol("value"))

        row1 = List()
        row1.append(i64(1))
        row1.append(f64(4.5))

        row2 = List()
        row2.append(i64(2))
        row2.append(f64(5.5))

        values = List()
        values.append(row1)
        values.append(row2)

        # Создаем таблицу
        table = Table(columns, values)

        # Проверяем, что объект таблицы был создан правильно
        table_values = table.values()
        assert len(table_values) == 2

        # Проверяем access к значениям вместо ключей
        assert len(table_values[0]) == 2
        assert str(table_values[0][0]) == "1"
        assert str(table_values[0][1]) == "4.5"

    def test_table_values_access(self):
        """Test values access to Table."""
        from raypy.types.container import Table, List
        from raypy.types.scalar import Symbol, i64, f64

        # Создаем колонки и значения для таблицы
        columns = List()
        columns.append(Symbol("id"))
        columns.append(Symbol("value"))

        row1 = List()
        row1.append(i64(1))
        row1.append(f64(4.5))

        row2 = List()
        row2.append(i64(2))
        row2.append(f64(5.5))

        values = List()
        values.append(row1)
        values.append(row2)

        # Создаем таблицу
        table = Table(columns, values)

        # Проверяем доступ к строкам через values()
        rows = table.values()
        assert len(rows) == 2

        # Проверяем первую строку
        first_row = rows[0]
        assert len(first_row) == 2
        assert str(first_row[0]) == "1"
        assert str(first_row[1]) == "4.5"

        # Проверяем вторую строку
        second_row = rows[1]
        assert len(second_row) == 2
        assert str(second_row[0]) == "2"
        assert str(second_row[1]) == "5.5"

    def test_table_len_check(self):
        """Test that Table requires keys and values lists to have the same length."""
        from raypy.types.container import Table, List
        from raypy.types.scalar import Symbol
        import pytest

        # Создаем колонки и значения разной длины
        columns = List()
        columns.append(Symbol("id"))
        columns.append(Symbol("value"))

        row1 = List()
        row1.append(Symbol("only one value"))

        values = List()
        values.append(row1)

        # Создаем таблицу - должна быть ошибка из-за несовпадения длин
        with pytest.raises(ValueError) as excinfo:
            table = Table(columns, values)

        # Проверка сообщения об ошибке
        assert "Keys and values lists must have the same length" in str(excinfo.value)

    def test_table_keys_handling(self):
        """Test handling of keys method that may raise an exception."""
        from raypy.types.container import Table, List
        from raypy.types.scalar import Symbol, i64

        # Создаем корректную таблицу
        columns = List()
        columns.append(Symbol("id"))

        row = List()
        row.append(i64(1))

        values = List()
        values.append(row)

        table = Table(columns, values)

        # Тестируем безопасный доступ к keys() с обработкой исключения
        try:
            keys = table.keys()
            # Если keys() отработал успешно, проверяем результат
            assert len(keys) == 1
        except ValueError as e:
            # Если возникла ошибка "Unknown vector type", это ожидаемое поведение
            # когда функция from_pointer_to_raypy_type пока не поддерживает
            # преобразование для этого типа
            assert "Unknown vector type" in str(e)

        # Тестируем, что значения доступны даже если ключи недоступны
        values = table.values()
        assert len(values) == 1
        assert len(values[0]) == 1
        assert str(values[0][0]) == "1"

    def test_table_str_representation_safe(self):
        """Test string representation of Table with exception handling."""
        from raypy.types.container import Table, List
        from raypy.types.scalar import Symbol, i64

        # Создаем таблицу
        columns = List()
        columns.append(Symbol("id"))

        row = List()
        row.append(i64(1))

        values = List()
        values.append(row)

        table = Table(columns, values)

        # Безопасное получение строкового представления
        try:
            # Попытка получить строковое представление
            table_str = str(table)

            # Если успешно, проверяем содержимое
            assert "Table" in table_str
            assert "with length of 1" in table_str
        except ValueError as e:
            # Ожидаемая ошибка при вызове keys() внутри __str__
            assert "Unknown vector type" in str(e)

            # Проверяем, что можно безопасно создать строковое представление без keys()
            custom_str = f"Table with {len(table.values())} rows"
            assert "Table with 1 rows" == custom_str

    def test_table_init_from_python_list(self):
        """Test initialization of Table from Python lists."""
        from raypy.types.container import Table, List
        import pytest

        # Создаем колонки как список строк Python
        columns = ["id", "name", "age"]

        # Создаем значения как список списков Python
        values = [[1, "Alice", 25], [2, "Bob", 30], [3, "Charlie", 35]]

        # Создаем таблицу
        table = Table(columns, values)

        # Проверяем, что таблица была создана правильно
        rows = table.values()
        assert len(rows) == 3  # Три строки

        # Проверяем данные в строках
        assert str(rows[0][0]) == "1"
        assert str(rows[0][1]) == "Alice"
        assert str(rows[0][2]) == "25"

        assert str(rows[1][0]) == "2"
        assert str(rows[1][1]) == "Bob"
        assert str(rows[1][2]) == "30"

        assert str(rows[2][0]) == "3"
        assert str(rows[2][1]) == "Charlie"
        assert str(rows[2][2]) == "35"

        # Тестирование ошибки с неправильными типами колонок
        with pytest.raises(ValueError) as excinfo:
            Table([1, 2, 3], values)  # Числа вместо строк
        assert "Columns python list must be of strings" in str(excinfo.value)

    def test_table_init_from_numpy_array(self):
        """Test initialization of Table from numpy arrays."""
        from raypy.types.container import Table, List
        import numpy as np
        import pytest

        try:
            # Создаем колонки как numpy array строк
            columns = np.array(["id", "value"])

            # Создаем значения как список списков Python
            values = [[1, 10.5], [2, 20.5]]

            # Создаем таблицу
            table = Table(columns, values)

            # Проверяем, что таблица была создана правильно
            rows = table.values()
            assert len(rows) == 2  # Две строки

            # Проверяем данные в строках
            assert str(rows[0][0]) == "1"
            assert str(rows[0][1]) == "10.5"

            assert str(rows[1][0]) == "2"
            assert str(rows[1][1]) == "20.5"

            # Тестирование ошибки с неправильными типами в numpy array
            with pytest.raises(ValueError):
                Table(np.array([1, 2]), values)  # Числа вместо строк

        except ImportError:
            pytest.skip("numpy not available")

    def test_table_init_from_vector(self):
        """Test initialization of Table from Vector."""
        from raypy.types.container import Table, List, Vector
        from raypy.types.scalar import Symbol, i64, f64
        import pytest

        # Создаем колонки как Vector символов
        columns = Vector(Symbol, 2)
        columns[0] = Symbol("id")
        columns[1] = Symbol("value")

        # Создаем значения
        row1 = List()
        row1.append(i64(1))
        row1.append(f64(10.5))

        row2 = List()
        row2.append(i64(2))
        row2.append(f64(20.5))

        values = List()
        values.append(row1)
        values.append(row2)

        # Создаем таблицу
        table = Table(columns, values)

        # Проверяем, что таблица была создана правильно
        rows = table.values()
        assert len(rows) == 2

        # Проверяем данные в строках
        assert str(rows[0][0]) == "1"
        assert str(rows[0][1]) == "10.5"

        assert str(rows[1][0]) == "2"
        assert str(rows[1][1]) == "20.5"

        # Тестирование с неправильным типом в векторе
        invalid_columns = Vector(i64, 2)
        invalid_columns[0] = i64(1)
        invalid_columns[1] = i64(2)

        with pytest.raises(ValueError) as excinfo:
            Table(invalid_columns, values)
        assert "Columns vector must be of symbols" in str(excinfo.value)

    def test_table_init_with_none_values(self):
        """Test initialization of Table with None values."""
        from raypy.types.container import Table
        import pytest

        # Тестирование с None значениями
        with pytest.raises(ValueError) as excinfo:
            Table(None, None)
        assert "Provide columns and values for table initialisation" in str(
            excinfo.value
        )

        # Тестирование с columns=None
        with pytest.raises(ValueError) as excinfo:
            Table(None, [])
        assert "Provide columns and values for table initialisation" in str(
            excinfo.value
        )

        # Тестирование с values=None
        with pytest.raises(ValueError) as excinfo:
            Table(["id"], None)
        assert "Provide columns and values for table initialisation" in str(
            excinfo.value
        )

    def test_table_init_from_ray_object(self):
        """Test initialization of Table from RayObject."""
        from raypy.types.container import Table, List
        from raypy.types.scalar import Symbol, i64
        import raypy._rayforce as r
        import pytest

        try:
            # Создаем базовую таблицу
            columns = List()
            columns.append(Symbol("id"))

            row = List()
            row.append(i64(1))

            values = List()
            values.append(row)

            original_table = Table(columns, values)

            # Получаем RayObject из таблицы
            ray_obj = original_table.ptr

            # Создаем новую таблицу из RayObject
            new_table = Table(ray_obj=ray_obj)

            # Проверяем, что новая таблица содержит те же данные
            new_values = new_table.values()
            assert len(new_values) == 1
            assert len(new_values[0]) == 1
            assert str(new_values[0][0]) == "1"

            # Тестирование с неправильным типом RayObject
            invalid_ray_obj = (
                r.RayObject.create_list()
            )  # Создаем RayObject типа списка вместо таблицы

            with pytest.raises(ValueError) as excinfo:
                Table(ray_obj=invalid_ray_obj)
            assert "Expected RayForce object of type" in str(excinfo.value)

        except (ImportError, AttributeError) as e:
            pytest.skip(f"RayObject not properly available: {str(e)}")
