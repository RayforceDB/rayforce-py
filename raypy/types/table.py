import typing as t
from raypy import _rayforce as r
from raypy.core.ffi import FFI
from raypy.types.base import Container
from raypy.types import exceptions
from raypy import utils


class Table(Container):
    type_code = r.TYPE_TABLE

    def __init__(
        self,
        columns: list[str] | None = None,
        values: list | None = None,
        *,
        ptr: r.RayObject | None = None,
    ) -> None:
        if ptr is not None:
            self.ptr = ptr
            self._validate_ptr(ptr)

        elif columns is not None and values is not None:
            if not all([isinstance(i, str) for i in columns]):
                raise exceptions.RayInitException("Table columns have to be strings")
            if len(columns) != len(values):
                raise exceptions.RayInitException("Keys and values lists must have the same length")

            from raypy.types import Vector, Symbol, List, I64, F64, B8
            table_columns = Vector(type_code=Symbol.type_code, length=len(columns))
            for idx, column in enumerate(columns):
                table_columns[idx] = column

            # Convert each column to a Vector instead of keeping as List
            table_values = List([])
            for column_data in values:
                # Auto-detect type and create appropriate Vector
                if not column_data:
                    # Empty column - use generic list
                    table_values.append([])
                elif all(isinstance(x, str) for x in column_data):
                    # String column -> Vector of Symbols
                    vec = Vector(type_code=Symbol.type_code, items=column_data)
                    table_values.append(vec)
                elif all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in column_data):
                    # Numeric column -> detect if int or float
                    if all(isinstance(x, int) for x in column_data):
                        vec = Vector(type_code=I64.type_code, items=column_data)
                    else:
                        vec = Vector(type_code=F64.type_code, items=column_data)
                    table_values.append(vec)
                elif all(isinstance(x, bool) for x in column_data):
                    # Boolean column
                    vec = Vector(type_code=B8.type_code, items=column_data)
                    table_values.append(vec)
                else:
                    # Mixed types or complex types - keep as List
                    table_values.append(column_data)

            self.ptr = FFI.init_table(columns=table_columns.ptr, values=table_values.ptr)
        else:
            raise exceptions.RayInitException("Provide columns and values for table initialisation")

    # TODO: Implement
    @classmethod
    def _create_from_value(*args, **kwargs) -> t.Any:
        pass

    def __iter__(*args, **kwargs) -> t.Any:
        pass

    def __len__(*args, **kwargs) -> t.Any:
        pass

    def to_python(*args, **kwargs) -> t.Any:
        pass

    def columns(self) -> t.Any:
        return utils.ray_to_python(FFI.get_table_keys(self.ptr))

    def values(self) -> t.Any:
        return utils.ray_to_python(FFI.get_table_values(self.ptr))

    def __str__(self) -> str:
        return FFI.repr_table(self.ptr)

    def __repr__(self) -> str:
        return f"Table[{self.columns()}]"

    def __eq__(self, eq: t.Any) -> bool:
        if isinstance(eq, Table):
            return eq.columns() == self.columns() and eq.values() == self.values()
        return False
