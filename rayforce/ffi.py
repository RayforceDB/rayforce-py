from __future__ import annotations

import atexit
import contextlib
import queue
import sys
import threading
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors

_shutting_down = False


class RuntimeThread:
    def __init__(self) -> None:
        self._command_queue: queue.Queue = queue.Queue()
        self._drop_queue: queue.Queue = queue.Queue()
        self._command_condition = threading.Condition()  # Для мгновенной реакции на команды
        self._thread: threading.Thread | None = None
        self._initialized = threading.Event()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._init_error: Exception | None = None

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return

            if self._init_error is not None:
                raise self._init_error

            self._thread = threading.Thread(target=self._runtime_loop, daemon=True)
            self._thread.start()

            if not self._initialized.wait(timeout=10.0):
                raise errors.RayforceInitError("Failed to initialize runtime in thread")

            if self._init_error is not None:
                raise self._init_error

    def _runtime_loop(self) -> None:
        if hasattr(sys, "getswitchinterval"):
            # Устанавливаем более короткий интервал переключения для лучшей отзывчивости
            sys.setswitchinterval(0.000001)

        try:
            # Инициализируем runtime в этом потоке
            # GIL должен быть захвачен для вызова C функций
            r.init_runtime()
            self._initialized.set()
        except Exception as e:
            self._init_error = e
            self._initialized.set()
            return

        while not self._stop_event.is_set():
            # Сначала обрабатываем команды на удаление (без блокировки)
            try:
                while True:
                    obj_to_drop = self._drop_queue.get_nowait()
                    if obj_to_drop is None:  # Сигнал остановки
                        return
            except queue.Empty:
                pass

            # Используем Condition для мгновенной реакции на команды
            with self._command_condition:
                # Проверяем очередь без блокировки
                try:
                    command = self._command_queue.get_nowait()
                except queue.Empty:
                    # Если очередь пуста, ждем уведомления (мгновенно пробуждается при добавлении команды)
                    self._command_condition.wait(timeout=0.0001)  # Таймаут для проверки stop_event
                    continue
                
                if command is None:  # Сигнал остановки
                    break

                func, args, kwargs, result_container, condition = command

                try:
                    result = func(*args, **kwargs)
                    with condition:
                        result_container[0] = (result, None)
                        condition.notify()
                except KeyboardInterrupt:
                    with condition:
                        result_container[0] = (None, KeyboardInterrupt())  # type: ignore[assignment]
                        condition.notify()
                    raise
                except Exception as e:
                    with condition:
                        result_container[0] = (None, e)
                        condition.notify()

    def schedule_drop(self, obj: r.RayObject) -> None:
        if _shutting_down or not self._initialized.is_set() or self._stop_event.is_set():
            return

        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                return

        with contextlib.suppress(queue.Full, RuntimeError):
            self._drop_queue.put(obj, block=False)

    def execute(self, func: t.Callable, *args, **kwargs) -> t.Any:
        if not self._initialized.is_set():
            self.start()
            if self._init_error is not None:
                raise self._init_error

        # Минимальный overhead: список + Condition (быстрее чем Queue + Event)
        result_container: list[tuple[t.Any, Exception | None] | None] = [None]
        condition = threading.Condition()

        # Отправляем команду и уведомляем runtime поток через Condition
        try:
            self._command_queue.put((func, args, kwargs, result_container, condition), block=False)
            with self._command_condition:
                self._command_condition.notify()  # Мгновенно пробуждаем runtime поток
        except queue.Full:
            raise errors.RayforceInitError("Command queue is full")

        # Ждем результата
        with condition:
            while result_container[0] is None:
                condition.wait(timeout=300.0)
                if result_container[0] is None:
                    raise errors.RayforceInitError("Command execution timed out")

        result, error = result_container[0]
        if error is not None:
            raise error
        return result

    def shutdown(self) -> None:
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                return

            self._stop_event.set()
            with contextlib.suppress(queue.Full):
                self._command_queue.put(None, block=False)

            with contextlib.suppress(queue.Full):
                self._drop_queue.put(None, block=False)

            self._thread.join(timeout=5.0)


_runtime_thread = RuntimeThread()


def _shutdown_runtime():
    try:
        _shutting_down = True
        _runtime_thread._stop_event.set()
        _runtime_thread.shutdown()
    except Exception:
        pass


atexit.register(_shutdown_runtime)


class FFI:
    @staticmethod
    @errors.error_handler
    def init_i16(value: int) -> r.RayObject:
        return _runtime_thread.execute(r.init_i16, value)

    @staticmethod
    @errors.error_handler
    def init_i32(value: int) -> r.RayObject:
        return _runtime_thread.execute(r.init_i32, value)

    @staticmethod
    @errors.error_handler
    def init_i64(value: int) -> r.RayObject:
        return _runtime_thread.execute(r.init_i64, value)

    @staticmethod
    @errors.error_handler
    def init_f64(value: float) -> r.RayObject:
        return _runtime_thread.execute(r.init_f64, value)

    @staticmethod
    @errors.error_handler
    def init_u8(value: int) -> r.RayObject:
        return _runtime_thread.execute(r.init_u8, value)

    @staticmethod
    @errors.error_handler
    def init_b8(value: bool) -> r.RayObject:
        return _runtime_thread.execute(r.init_b8, value)

    @staticmethod
    @errors.error_handler
    def init_c8(value: str) -> r.RayObject:
        return _runtime_thread.execute(r.init_c8, value)

    @staticmethod
    @errors.error_handler
    def init_symbol(value: str) -> r.RayObject:
        return _runtime_thread.execute(r.init_symbol, value)

    @staticmethod
    @errors.error_handler
    def init_date(value: t.Any) -> r.RayObject:
        return _runtime_thread.execute(r.init_date, value)

    @staticmethod
    @errors.error_handler
    def init_time(value: t.Any) -> r.RayObject:
        return _runtime_thread.execute(r.init_time, value)

    @staticmethod
    @errors.error_handler
    def init_timestamp(value: t.Any) -> r.RayObject:
        return _runtime_thread.execute(r.init_timestamp, value)

    @staticmethod
    @errors.error_handler
    def init_guid(value: t.Any) -> r.RayObject:
        return _runtime_thread.execute(r.init_guid, value)

    @staticmethod
    @errors.error_handler
    def init_string(value: str) -> r.RayObject:
        return _runtime_thread.execute(r.init_string, value)

    @staticmethod
    @errors.error_handler
    def read_i16(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.read_i16, obj)

    @staticmethod
    @errors.error_handler
    def read_i32(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.read_i32, obj)

    @staticmethod
    @errors.error_handler
    def read_i64(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.read_i64, obj)

    @staticmethod
    @errors.error_handler
    def read_f64(obj: r.RayObject) -> float:
        return _runtime_thread.execute(r.read_f64, obj)

    @staticmethod
    @errors.error_handler
    def read_u8(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.read_u8, obj)

    @staticmethod
    @errors.error_handler
    def read_b8(obj: r.RayObject) -> bool:
        return _runtime_thread.execute(r.read_b8, obj)

    @staticmethod
    @errors.error_handler
    def read_c8(obj: r.RayObject) -> str:
        return _runtime_thread.execute(r.read_c8, obj)

    @staticmethod
    @errors.error_handler
    def read_symbol(obj: r.RayObject) -> str:
        return _runtime_thread.execute(r.read_symbol, obj)

    @staticmethod
    @errors.error_handler
    def read_date(obj: r.RayObject) -> t.Any:
        return _runtime_thread.execute(r.read_date, obj)

    @staticmethod
    @errors.error_handler
    def read_time(obj: r.RayObject) -> t.Any:
        return _runtime_thread.execute(r.read_time, obj)

    @staticmethod
    @errors.error_handler
    def read_timestamp(obj: r.RayObject) -> t.Any:
        return _runtime_thread.execute(r.read_timestamp, obj)

    @staticmethod
    @errors.error_handler
    def read_guid(obj: r.RayObject) -> t.Any:
        return _runtime_thread.execute(r.read_guid, obj)

    @staticmethod
    @errors.error_handler
    def init_vector(type_code: int, length: int) -> r.RayObject:
        return _runtime_thread.execute(r.init_vector, type_code, length)

    @staticmethod
    @errors.error_handler
    def init_list() -> r.RayObject:
        return _runtime_thread.execute(r.init_list)

    @staticmethod
    @errors.error_handler
    def init_dict(keys: r.RayObject, values: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.init_dict, keys, values)

    @staticmethod
    @errors.error_handler
    def init_table(columns: r.RayObject, values: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.init_table, columns, values)

    @staticmethod
    @errors.error_handler
    def push_obj(iterable: r.RayObject, ptr: r.RayObject) -> None:
        return _runtime_thread.execute(r.push_obj, iterable, ptr)

    @staticmethod
    @errors.error_handler
    def insert_obj(iterable: r.RayObject, idx: int, ptr: r.RayObject) -> None:
        return _runtime_thread.execute(r.insert_obj, iterable, idx, ptr)

    @staticmethod
    @errors.error_handler
    def fill_vector(obj: r.RayObject, fill: list[t.Any]) -> None:
        return _runtime_thread.execute(r.fill_vector, obj, fill)

    @staticmethod
    @errors.error_handler
    def fill_list(obj: r.RayObject, fill: list[t.Any]) -> None:
        return _runtime_thread.execute(r.fill_list, obj, fill)

    @staticmethod
    @errors.error_handler
    def at_idx(iterable: r.RayObject, idx: int) -> r.RayObject:
        return _runtime_thread.execute(r.at_idx, iterable, idx)

    @staticmethod
    @errors.error_handler
    def get_obj_length(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.get_obj_length, obj)

    @staticmethod
    @errors.error_handler
    def get_table_keys(table: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.table_keys, table)

    @staticmethod
    @errors.error_handler
    def get_table_values(table: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.table_values, table)

    @staticmethod
    @errors.error_handler
    def repr_table(table: r.RayObject) -> str:
        return _runtime_thread.execute(r.repr_table, table)

    @staticmethod
    @errors.error_handler
    def dict_get(dict_: r.RayObject, key: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.dict_get, dict_, key)

    @staticmethod
    @errors.error_handler
    def get_dict_keys(dict_: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.dict_keys, dict_)

    @staticmethod
    @errors.error_handler
    def get_dict_values(dict_: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.dict_values, dict_)

    @staticmethod
    @errors.error_handler
    def select(query: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.select, query)

    @staticmethod
    @errors.error_handler
    def update(query: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.update, query)

    @staticmethod
    @errors.error_handler
    def insert(table: r.RayObject, data: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.insert, table, data)

    @staticmethod
    @errors.error_handler
    def upsert(table: r.RayObject, keys: r.RayObject, data: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.upsert, table, keys, data)

    @staticmethod
    @errors.error_handler
    def eval_str(obj: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.eval_str, obj)

    @staticmethod
    def eval_obj(obj: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.eval_obj, obj)

    @staticmethod
    def get_obj_type(obj: r.RayObject) -> int:
        current_thread = threading.current_thread()
        runtime_thread = _runtime_thread._thread
        if runtime_thread is not None and current_thread is runtime_thread:
            # Мы в runtime потоке, вызываем напрямую
            return r.get_obj_type(obj)
        return _runtime_thread.execute(r.get_obj_type, obj)

    @staticmethod
    @errors.error_handler
    def quote(obj: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.quote, obj)

    @staticmethod
    @errors.error_handler
    def rc_obj(obj: r.RayObject) -> int:
        return _runtime_thread.execute(r.rc_obj, obj)

    @staticmethod
    @errors.error_handler
    def binary_set(name: r.RayObject, obj: r.RayObject) -> None:
        return _runtime_thread.execute(r.binary_set, name, obj)

    @staticmethod
    @errors.error_handler
    def env_get_internal_function_by_name(name: str) -> r.RayObject:
        current_thread = threading.current_thread()
        runtime_thread = _runtime_thread._thread
        if runtime_thread is not None and current_thread is runtime_thread:
            return r.env_get_internal_function_by_name(name)
        return _runtime_thread.execute(r.env_get_internal_function_by_name, name)

    @staticmethod
    @errors.error_handler
    def env_get_internal_name_by_function(obj: r.RayObject) -> str:
        return _runtime_thread.execute(r.env_get_internal_name_by_function, obj)

    @staticmethod
    @errors.error_handler
    def set_obj_attrs(obj: r.RayObject, attr: int) -> None:
        return _runtime_thread.execute(r.set_obj_attrs, obj, attr)

    @staticmethod
    @errors.error_handler
    def loadfn_from_file(filename: str, fn_name: str, args_count: int) -> r.RayObject:
        return _runtime_thread.execute(r.loadfn_from_file, filename, fn_name, args_count)

    @staticmethod
    def get_error_obj(error_obj: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.get_error_obj, error_obj)

    @staticmethod
    @errors.error_handler
    def hopen(path: r.RayObject) -> r.RayObject:
        return _runtime_thread.execute(r.hopen, path)

    @staticmethod
    @errors.error_handler
    def hclose(handle: r.RayObject) -> None:
        return _runtime_thread.execute(r.hclose, handle)

    @staticmethod
    @errors.error_handler
    def write(handle: r.RayObject, data: r.RayObject) -> None:
        return _runtime_thread.execute(r.write, handle, data)

    @staticmethod
    @errors.error_handler
    def set_obj(obj: r.RayObject, idx: r.RayObject, value: r.RayObject) -> None:
        return _runtime_thread.execute(r.set_obj, obj, idx, value)

    @staticmethod
    @errors.error_handler
    def init_runtime() -> None:
        _runtime_thread.start()

    @staticmethod
    def schedule_drop(obj: r.RayObject) -> None:
        _runtime_thread.schedule_drop(obj)

    @staticmethod
    def shutdown() -> None:
        _runtime_thread.shutdown()
