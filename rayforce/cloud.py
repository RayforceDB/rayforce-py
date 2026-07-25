"""Client for RayforceDB Cloud instances.

Queries run on an instance reached over WSS through the console, which is the
only transport a tenant gets. The protocol, the transport and paging live in
``librfcloud`` — the shared C client that every binding links — and this module
is the Python face of it. Pages come back already decoded, because the C layer
hands them to the same ``ray_de`` that reads an IPC frame.

    from rayforce.cloud import CloudClient

    with CloudClient(url, token) as client:
        result = client.query("(til 5000)", page_size=1000)
        result.value          # the first page, as Python values
        result.total          # rows/items in the whole result
        list(result.pages())  # every page, fetched on demand

A query is either source text or a query object — the same ones the IPC and
WebSocket clients take, so a `Table.select()` built once runs anywhere.

A result larger than one page stays retained on the instance until the
``Result`` is released, which is what lets it be paged and named. Naming one
with ``bind()`` is how an aggregation runs in the engine over the whole result
rather than over the page in hand.
"""

from __future__ import annotations

import contextlib
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.utils import ray_to_python

# What the instance charges a page against: rows for a table, items otherwise.
PageUnit = t.Literal["rows", "items", ""]


class Page(t.NamedTuple):
    """One page of a result, decoded."""

    value: t.Any
    offset: int
    returned: int
    total: int
    unit: PageUnit


def _serialize(query: t.Any) -> bytes:
    """A query object as the bytes of its serialized tree.

    Routed through the same ``python_to_ipc`` the TCP and WebSocket clients use,
    so what can be sent to an instance is one list rather than one per
    transport, and a query object behaves the same wherever it is sent.
    """
    from rayforce.network import utils as network_utils

    try:
        ptr = network_utils.python_to_ipc(query)
    except errors.RayforceTCPError as exc:
        # python_to_ipc reports in the TCP client's terms; the caller is here.
        raise errors.RayforceValueError(
            f"cloud: cannot send a {type(query).__name__} as a query"
        ) from exc

    serialized = FFI.ser_obj(ptr)
    if FFI.get_obj_type(serialized) == r.TYPE_ERR:
        raise errors.RayforceValueError(
            f"cloud: could not serialize the query: {FFI.get_error_obj(serialized)}"
        )
    return FFI.read_u8_vector(serialized)


def _page(raw: tuple[t.Any, int, int, int, str]) -> Page:
    value, offset, returned, total, unit = raw
    return Page(
        value=ray_to_python(value) if value is not None else None,
        offset=offset,
        returned=returned,
        total=total,
        unit=t.cast("PageUnit", unit),
    )


class Result:
    """A completed query and the pages of its result.

    Holding one holds memory on the instance, so release it — ``CloudClient``
    does that for every result it still owns when it closes.
    """

    def __init__(self, client: CloudClient, job: t.Any, first: Page, page_size: int) -> None:
        self._client = client
        self._job = job
        self._page_size = page_size
        self.first = first
        self._released = False

    @property
    def value(self) -> t.Any:
        """The first page's value."""
        return self.first.value

    @property
    def total(self) -> int:
        """Rows or items in the whole result, which may exceed the first page."""
        return self.first.total

    @property
    def unit(self) -> PageUnit:
        return self.first.unit

    @property
    def complete(self) -> bool:
        """Whether the first page already holds the whole result."""
        return self.first.returned >= self.first.total

    def page(self, offset: int, limit: int | None = None) -> Page:
        """Fetch one page starting at `offset`."""
        self._check_live()
        return _page(
            r.cloud_fetch_page(self._client._handle, self._job, offset, limit or self._page_size)
        )

    def pages(self) -> t.Iterator[Page]:
        """Every page in order, the first one already in hand.

        Stops on a page that returns nothing, so a result that shrinks under it
        ends the walk rather than looping on an offset that never advances.
        """
        yield self.first
        offset = self.first.offset + self.first.returned
        while offset < self.first.total:
            page = self.page(offset)
            if page.returned == 0:
                return
            yield page
            offset = page.offset + page.returned

    def bind(self, name: str) -> str:
        """Name this result on the instance and return its qualified name.

        Only a retained result can be named, and a result that fitted in one
        page is not retained — the caller already holds all of it.
        """
        self._check_live()
        return r.cloud_bind_result(self._client._handle, self._job, name)

    def cancel(self) -> None:
        """Ask the instance to stop the job. Best-effort."""
        self._check_live()
        r.cloud_cancel(self._client._handle, self._job)

    def release(self) -> None:
        """Drop the result on the instance. Idempotent."""
        if self._released:
            return
        self._released = True
        self._client._forget(self)
        r.cloud_job_free(self._client._handle, self._job)

    def _check_live(self) -> None:
        if self._released:
            raise errors.RayforceValueError("cloud: this result has been released")

    def __enter__(self) -> Result:
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()

    def __repr__(self) -> str:
        state = "released" if self._released else f"{self.first.returned}/{self.total}"
        return f"Result({state} {self.unit})"


class CloudClient:
    """A connection to one cloud instance.

    Not thread-safe, and every call blocks — one client per thread, or serialise.
    """

    def __init__(
        self,
        url: str,
        token: str,
        *,
        connect_timeout: int = 0,
        request_timeout: int = 0,
    ) -> None:
        """Connect and authenticate.

        `url` is the console's instance endpoint (``wss://host/api/v1/instances/ws``)
        and `token` an ``rf_`` instance token minted from the console. Timeouts
        are seconds; 0 takes the SDK's defaults.
        """
        # Binary is not optional here: it is the native wire format, and the
        # JSON codec exists for clients that have no decoder. This one does.
        self._handle = r.cloud_connect(url, token, 1, connect_timeout, request_timeout)
        self._closed = False
        self._results: list[Result] = []

    def query(self, query: t.Any, page_size: int = 1000) -> Result:
        """Run a query and wait for its first page.

        `query` is either Rayfall source text or a query object — the same ones
        the IPC and WebSocket clients take: ``Table.select()``, ``insert``,
        ``upsert``, the joins, ``Expression``, ``SQLQuery``. An object is sent
        as the tree it already is rather than rendered back into source, which
        for anything carrying data (an insert's rows, a filter's literals) would
        be both lossy and enormous.
        """
        if self._closed:
            raise errors.RayforceValueError("cloud: this client is closed")

        if isinstance(query, str):
            job, first = r.cloud_submit(self._handle, query, page_size)
        else:
            job, first = r.cloud_submit_expr(self._handle, _serialize(query), page_size)

        result = Result(self, job, _page(first), page_size)
        self._results.append(result)
        return result

    def close(self) -> None:
        """Release every result still held, then close the connection."""
        if self._closed:
            return
        # Release before closing: after the socket goes the instance frees them
        # anyway, but only once it notices, and a caller may reconnect first.
        for result in list(self._results):
            result.release()
        self._closed = True
        r.cloud_close(self._handle)

    def _forget(self, result: Result) -> None:
        if result in self._results:
            self._results.remove(result)

    def __enter__(self) -> CloudClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def __del__(self) -> None:
        # A client that goes out of scope still holds a socket and, on the far
        # side, whatever its results retain. Nothing can be raised from here.
        with contextlib.suppress(Exception):
            self.close()

    def __repr__(self) -> str:
        return f"CloudClient({'closed' if self._closed else 'open'})"
