# API which is responsible for Rayforce object operations
# Never use Raypy types here, operate with rayforce types only
import uuid
import datetime as dt
import numpy as np
from typing import Any

from raypy import _rayforce as r

EPOCH_DATE = dt.date(1970, 1, 1)


def init_i16(value: int | float | str) -> r.RayObject:
    try:
        _value = int(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to int type - {value}") from e
    try:
        return getattr(r, "init_i16")(_value)
    except Exception as e:
        raise TypeError(f"Error during i16 type initialisation - {str(e)}") from e


def read_i16(obj: r.RayObject) -> int:
    try:
        return getattr(r, "read_i16")(obj)
    except Exception as e:
        raise ValueError("Unable to get i16 type from RayObject") from e


def init_i32(value: int | float | str) -> r.RayObject:
    try:
        _value = int(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to int type - {value}") from e
    try:
        return getattr(r, "init_i32")(_value)
    except Exception as e:
        raise TypeError(f"Error during i32 type initialisation - {str(e)}") from e


def read_i32(obj: r.RayObject) -> int:
    try:
        return getattr(r, "read_i32")(obj)
    except Exception as e:
        raise ValueError("Unable to get i16 type from RayObject") from e


def init_i64(value: int | float | str) -> r.RayObject:
    try:
        _value = int(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to int type - {value}") from e
    try:
        return getattr(r, "init_i64")(_value)
    except Exception as e:
        raise TypeError(f"Error during i64 type initialisation - {str(e)}") from e


def read_i64(obj: r.RayObject) -> int:
    try:
        return getattr(r, "read_i64")(obj)
    except Exception as e:
        raise ValueError("Unable to get i64 type from RayObject") from e


def init_b8(value: Any) -> r.RayObject:
    try:
        _value = bool(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to bool type - {value}") from e

    try:
        return getattr(r, "init_b8")(_value)
    except Exception as e:
        raise TypeError(f"Error during b8 type initialisation - {str(e)}") from e


def read_b8(obj: r.RayObject) -> bool:
    try:
        return getattr(r, "read_b8")(obj)
    except Exception as e:
        raise ValueError("Unable to get b8 type from RayObject") from e


def init_c8(value: str | int) -> r.RayObject:
    if isinstance(value, str):
        if len(value) == 1:
            # If unicode value of given char is not supported, set it as "A"
            char_value = "A" if ord(value) > 127 else value
        else:
            raise ValueError(
                "Character must be a single character string or an integer (0-126)"
            )
    elif isinstance(value, int):
        if 0 <= value <= 126:
            char_value = chr(value)
        else:
            raise ValueError(
                f"Integer representation of a char should be between 0 and 126. Given - {value}"
            )
    else:
        raise ValueError(
            "Character must be a single character string or an integer (0-126)"
        )

    try:
        return getattr(r, "init_b8")(char_value)
    except Exception as e:
        raise TypeError(f"Error during c8 type initialisation - {str(e)}") from e


def read_c8(obj: r.RayObject) -> str:
    try:
        return getattr(r, "read_c8")(obj)
    except Exception as e:
        raise ValueError("Unable to get c8 type from RayObject") from e


def init_date(value: dt.date | int | str) -> r.RayObject:
    if value is None:
        raise ValueError("Value is required")

    days_since_epoch = 0
    if isinstance(value, int):
        days_since_epoch = value
    elif isinstance(value, dt.date):
        days_since_epoch = (value - EPOCH_DATE).days
    elif isinstance(value, str):
        try:
            date_obj = dt.date.fromisoformat(value)
            days_since_epoch = (date_obj - EPOCH_DATE).days
        except ValueError as e:
            raise ValueError("Date string must be in format YYYY-MM-DD") from e
    else:
        raise TypeError(f"Unable to convert {type(value)} to date")

    try:
        return getattr(r, "init_date")(days_since_epoch)
    except Exception as e:
        raise TypeError(f"Error during date type initialisation - {str(e)}") from e


def read_date(obj: r.RayObject) -> dt.date:
    try:
        days_since_epoch = getattr(r, "read_date")(obj)
    except Exception as e:
        raise ValueError(f"Error during Date type extraction - {str(e)}") from e

    return EPOCH_DATE + dt.timedelta(days=days_since_epoch)


def init_f64(value: int | float) -> r.RayObject:
    try:
        _value = float(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to bool type - {value}") from e

    try:
        return getattr(r, "init_f64")(_value)
    except Exception as e:
        raise TypeError(f"Error during f64 type initialisation - {str(e)}") from e


def read_f64(obj: r.RayObject) -> float:
    try:
        return getattr(r, "init_f64")(obj)
    except Exception as e:
        raise ValueError(f"Error during f8 type extraction - {str(e)}") from e


def init_symbol(value: str) -> r.RayObject:
    try:
        _value = str(value)
    except ValueError as e:
        raise ValueError(f"Unable to convert value to str type - {value}") from e

    try:
        return getattr(r, "init_symbol")(_value)
    except Exception as e:
        raise TypeError(f"Error during symbol type initialisation - {str(e)}") from e


def read_symbol(obj: r.RayObject) -> str:
    try:
        return getattr(r, "read_symbol")(obj)
    except Exception as e:
        raise TypeError(f"Error during symbol type extraction - {str(e)}") from e


def init_time(value: dt.time | int | str) -> r.RayObject:
    if value is None:
        raise ValueError("Value is required")

    ms_since_midnight = 0
    if isinstance(value, int):
        if value < 0 or value > 86399999:  # 24*60*60*1000 - 1
            raise ValueError("Time int value must be in range 0-86399999 milliseconds")
        ms_since_midnight = value
    elif isinstance(value, dt.time):
        ms_since_midnight = (
            value.hour * 3600 + value.minute * 60 + value.second
        ) * 1000 + value.microsecond // 1000
    elif isinstance(value, str):
        try:
            if "." in value:
                # Parse with milliseconds
                time_obj = dt.time.fromisoformat(value)
            else:
                # Parse without milliseconds
                time_obj = dt.time.fromisoformat(value)
            ms_since_midnight = (
                time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
            ) * 1000 + time_obj.microsecond // 1000
        except ValueError as e:
            raise ValueError(
                "Time string must be in format HH:MM:SS or HH:MM:SS.mmm"
            ) from e
    else:
        raise TypeError(f"Unable to convert {type(value)} to Time")

    try:
        return getattr(r, "init_time")(ms_since_midnight)
    except Exception as e:
        raise TypeError(f"Error during time type initialisation - {str(e)}") from e


def read_time(obj: r.RayObject) -> dt.time:
    try:
        ms_since_midnight = getattr(r, "read_time")(obj)
    except Exception as e:
        raise TypeError(f"Error during time type extraction - {str(e)}") from e

    ms = ms_since_midnight
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    milliseconds = ms % 1000
    return dt.time(hours, minutes, seconds, milliseconds * 1000)


def init_timestamp(value: dt.datetime | int | str) -> r.RayObject:
    if value is None:
        raise ValueError("Value is required")
    ms_since_epoch = 0
    if isinstance(value, int):
        ms_since_epoch = value
    elif isinstance(value, dt.datetime):
        ms_since_epoch = int(value.timestamp() * 1000)
    elif isinstance(value, str):  # Parse from string (ISO format)
        try:
            dt_obj = dt.datetime.fromisoformat(value)
            ms_since_epoch = int(dt_obj.timestamp() * 1000)
        except ValueError:
            raise ValueError("Timestamp string must be in ISO format")
    else:
        raise TypeError(f"Unable to convert {type(value)} to Date")

    try:
        return getattr(r, "init_timestamp")(ms_since_epoch)
    except Exception as e:
        raise TypeError(f"Error during timestamp type initialisation - {str(e)}") from e


def read_timestamp(obj: r.RayObject) -> dt.datetime:
    try:
        ms_since_epoch = getattr(r, "read_timestamp")(obj)
    except Exception as e:
        raise TypeError(f"Error during timestamp type extraction - {str(e)}") from e
    ms = ms_since_epoch
    seconds = ms // 1000
    microseconds = (ms % 1000) * 1000
    return dt.datetime.fromtimestamp(seconds).replace(microsecond=microseconds)


def init_u8(value: int) -> r.RayObject:
    if not isinstance(value, int):
        try:
            value = int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Expected value of int-able type, got {type(value)}"
            ) from e

    if value < 0 or value > 255:
        raise ValueError("Unsigned value is out of range (0-255)")

    try:
        return getattr(r, "init_u8")(value)
    except Exception as e:
        raise TypeError(f"Error during u8 type initialisation - {str(e)}") from e


def read_u8(obj: r.RayObject) -> int:
    try:
        return getattr(r, "read_u8")(obj)
    except Exception as e:
        raise TypeError(f"Error during unsigned type extraction - {str(e)}") from e


def init_guid(value: str | uuid.UUID | bytes | bytearray) -> r.RayObject:
    if value is None:
        raise ValueError("Value is required")

    if isinstance(value, uuid.UUID):
        guid_bytes = value.bytes
    elif isinstance(value, str):
        try:
            guid_bytes = uuid.UUID(value).bytes
        except ValueError as e:
            raise ValueError("Invalid GUID string format") from e
    elif isinstance(value, (bytes, bytearray)):
        if len(value) != 16:
            raise ValueError("GUID must be 16 bytes")
        guid_bytes = bytes(value)
    else:
        raise TypeError(f"Unable to convert {type(value)} to GUID")

    try:
        return getattr(r, "init_guid")(guid_bytes)
    except Exception as e:
        raise TypeError(f"Error during GUID type initialisation - {str(e)}") from e


def read_guid(obj: r.RayObject) -> uuid.UUID:
    try:
        raw_bytes = getattr(r, "read_guid")(obj)
    except Exception as e:
        raise TypeError(f"Error during GUID type extraction - {str(e)}") from e

    return uuid.UUID(bytes=raw_bytes)


def init_vector(type_code: int, length: int) -> r.RayObject:
    try:
        return getattr(r, "init_vector")(type_code, length)
    except Exception as e:
        raise TypeError(f"Error during Vector type initialization - {str(e)}") from e


def get_obj_length(value: r.RayObject) -> int:
    try:
        return getattr(r, "get_obj_length")(value)
    except Exception as e:
        raise TypeError(f"Error during getting object length - {str(e)}") from e


def insert_obj(source_obj: r.RayObject, idx: int, value: r.RayObject) -> None:
    try:
        getattr(r, "ins_obj")(source_obj, idx, value)
    except Exception as e:
        raise ValueError("Error during insert object operation") from e


def get_object_at_idx(source_obj: r.RayObject, idx: int) -> r.RayObject:
    try:
        return getattr(r, "at_idx")(source_obj, idx)
    except Exception as e:
        raise ValueError("Error during get object at idx operation") from e


def remove_object_at_idx(source_obj: r.RayObject, idx: int) -> None:
    try:
        return getattr(r, "remove_idx")(source_obj, idx)
    except Exception as e:
        raise ValueError("Error during removing object at idx operation") from e


def push_obj_to_iterable(iterable: r.RayObject, obj: r.RayObject) -> None:
    try:
        getattr(r, "push_obj")(iterable, obj)
    except Exception as e:
        raise ValueError("Error during push object operation") from e


def init_list() -> r.RayObject:
    try:
        return getattr(r, "init_list")()
    except Exception as e:
        raise TypeError(f"Error during List type initialization - {str(e)}") from e


def init_dict(value: dict[str, Any]) -> r.RayObject:
    dict_keys = init_list()
    for item in value.keys():
        if not isinstance(item, str):
            raise ValueError(f"Expected string as dict key, got {type(item)}")
        push_obj_to_iterable(dict_keys, init_symbol(item))

    dict_values = init_list()
    for item in value.values():
        push_obj_to_iterable(dict_values, from_python_to_rayforce_type(item))

    init_dict_from_rf_objects(dict_keys, dict_values)


def init_dict_from_rf_objects(keys: r.RayObject, values: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "init_dict")(keys, values)
    except Exception as e:
        raise TypeError(f"Error during Dict type initialisation - {str(e)}") from e


def get_dict_keys(obj: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "dict_keys")(obj)
    except Exception as e:
        raise ValueError("Error during get dict keys operation") from e


def get_dict_values(obj: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "dict_values")(obj)
    except Exception as e:
        raise ValueError("Error during get dict values operation") from e


def get_dict_value_by_key(obj: r.RayObject, key: Any) -> r.RayObject:
    try:
        return getattr(r, "dict_get")(obj, from_python_to_rayforce_type(key))
    except Exception as e:
        raise ValueError("Error during get dict value by key operation") from e


def init_table(columns: list[str], values: list) -> r.RayObject:
    if (columns is None or values is None) or len(columns) == 0:
        raise ValueError("Provide columns and values for table initialisation")

    # Assert columns vector and values list are having same length
    if len(columns) != len(values):
        raise ValueError("Keys and values lists must have the same length")

    if isinstance(columns, list):
        if not all([isinstance(i, str) for i in columns]):
            raise ValueError("Column elements must be of RF Symbols or Python strings")
        table_columns = init_vector(type_code=-r.TYPE_SYMBOL, length=len(columns))

        for idx, item in enumerate(columns):
            insert_obj(table_columns, idx, from_python_to_rayforce_type(item))

    table_values = init_list()
    for item in values:
        push_obj_to_iterable(table_values, from_python_to_rayforce_type(item))

    try:
        return getattr(r, "init_table")(table_columns, table_values)
    except Exception as e:
        raise TypeError(f"Error during Table type initialisation - {str(e)}") from e


def get_table_keys(obj: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "table_keys")(obj)
    except Exception as e:
        raise ValueError("Error during get table keys operation") from e


def get_table_values(obj: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "table_values")(obj)
    except Exception as e:
        raise ValueError("Error during get table values operation") from e


def is_vector(obj: r.RayObject) -> bool:
    try:
        return getattr(r, "is_vector")(obj)
    except Exception as e:
        raise ValueError("Error during is_vector operation") from e


def get_primitive_function_by_name(name: str) -> r.RayObject:
    try:
        return getattr(r, "env_get_internal_function_by_name")(name)
    except Exception as e:
        raise ValueError(
            "Error during env_get_internal_function_by_name operation"
        ) from e


def get_name_by_primitive_function(obj: r.RayObject) -> str:
    try:
        return getattr(r, "env_get_internal_name_by_function")(obj)
    except Exception as e:
        raise ValueError(
            "Error during env_get_internal_name_by_function operation"
        ) from e


def set_obj_to_env(name: str, obj: r.RayObject) -> None:
    try:
        return getattr(r, "binary_set")(init_symbol(name), obj)
    except Exception as e:
        raise ValueError("Error during binary_set operation") from e


def get_error_message(obj: r.RayObject) -> str:
    try:
        return getattr(r, "get_error_message")(obj)
    except Exception as e:
        raise ValueError("Error during get_error_message operation") from e


def select(obj: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "select")(obj)
    except Exception as e:
        raise ValueError("Error during select operation") from e


def init_lambda(args: r.RayObject, expressions: r.RayObject) -> r.RayObject:
    try:
        return getattr(r, "init_lambda")(args, expressions)
    except Exception as e:
        raise ValueError("Error during lambda initialization") from e


def from_python_to_rayforce_type(value: Any) -> r.RayObject:
    if isinstance(value, r.RayObject):
        return value
    elif hasattr(value, "ptr"):
        return value.ptr
    elif hasattr(value, "primitive"):
        return value.primitive
    elif isinstance(value, str):
        return init_symbol(value)
    elif isinstance(value, int) and not isinstance(value, bool):
        return init_i64(value)
    elif isinstance(value, float):
        return init_f64(value)
    elif isinstance(value, bool):
        return init_b8(value)
    elif isinstance(value, dt.date):
        return init_date(value)
    elif isinstance(value, dt.time):
        return init_time(value)
    elif isinstance(value, dt.datetime):
        return init_timestamp(value)
    elif isinstance(value, uuid.UUID):
        return init_guid(value)
    elif isinstance(value, dict):
        return init_dict(value)
    elif isinstance(value, list):
        ll = init_list()
        for item in value:
            push_obj_to_iterable(ll, from_python_to_rayforce_type(item))
        return ll
    elif isinstance(value, np.ndarray):
        if value.dtype == object:
            raise ValueError("Expected homogeneous numpy array")

        v = init_vector(
            type_code=from_python_to_rayforce_type(value[0].item()).get_obj_type(),
            length=len(value),
        )
        for idx, item in enumerate(value):
            insert_obj(v, idx, from_python_to_rayforce_type(item))
        return v

    raise ValueError(
        f"Python type is not supported for Rayforce type conversion - {type(value)}"
    )
