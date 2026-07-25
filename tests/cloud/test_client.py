"""CloudClient — paging arithmetic, handle lifetime, and error mapping.

Most of this runs without an instance. A connection failure is a real exercise
of the C layer's status-to-exception mapping, and the paging walk is pure
arithmetic over what the instance reported. The tests that genuinely need an
instance are gated on RAYFORCE_CLOUD_URL / RAYFORCE_CLOUD_TOKEN and skip
without them, because a live cloud instance is not something CI has.
"""

from __future__ import annotations

import os

import pytest

from rayforce import Column, Table, errors
from rayforce import _rayforce_c as r
from rayforce.cloud import CloudClient, Page, Result, _serialize

pytestmark = pytest.mark.cloud

LIVE_URL = os.environ.get("RAYFORCE_CLOUD_URL")
LIVE_TOKEN = os.environ.get("RAYFORCE_CLOUD_TOKEN")
requires_instance = pytest.mark.skipif(
    not (LIVE_URL and LIVE_TOKEN),
    reason="set RAYFORCE_CLOUD_URL and RAYFORCE_CLOUD_TOKEN to run against an instance",
)


class FakeClient:
    """A CloudClient stand-in that hands out canned pages."""

    def __init__(self, pages: dict[int, Page]) -> None:
        self._handle = object()
        self._pages = pages
        self.fetched: list[int] = []

    def _forget(self, result: Result) -> None:
        pass


def _result(first: Page, rest: dict[int, Page] | None = None) -> tuple[Result, FakeClient]:
    client = FakeClient(rest or {})
    result = Result(client, object(), first, page_size=first.returned or 1)

    def page(offset: int, limit: int | None = None) -> Page:  # noqa: ARG001 — matches Result.page
        client.fetched.append(offset)
        return client._pages[offset]

    result.page = page  # type: ignore[method-assign]
    return result, client


class TestPaging:
    def test_a_result_that_fits_one_page_is_complete(self) -> None:
        result, client = _result(Page(value=[1, 2], offset=0, returned=2, total=2, unit="items"))

        assert result.complete
        assert [p.returned for p in result.pages()] == [2]
        assert client.fetched == []

    def test_walks_every_page_from_the_one_in_hand(self) -> None:
        first = Page(value=None, offset=0, returned=100, total=250, unit="items")
        result, client = _result(
            first,
            {
                100: Page(value=None, offset=100, returned=100, total=250, unit="items"),
                200: Page(value=None, offset=200, returned=50, total=250, unit="items"),
            },
        )

        assert sum(p.returned for p in result.pages()) == 250
        assert client.fetched == [100, 200]

    def test_a_page_that_returns_nothing_ends_the_walk(self) -> None:
        """A result that shrinks under the walk must not loop on an offset that
        never advances — an empty page is the end, not a reason to retry."""
        first = Page(value=None, offset=0, returned=10, total=1_000, unit="rows")
        result, _ = _result(
            first, {10: Page(value=None, offset=10, returned=0, total=1_000, unit="rows")}
        )

        assert [p.returned for p in result.pages()] == [10]


class TestHandleLifetime:
    def test_a_released_result_refuses_further_use(self) -> None:
        result, _ = _result(Page(value=None, offset=0, returned=1, total=1, unit="items"))
        result._released = True

        with pytest.raises(errors.RayforceValueError, match="released"):
            result.bind("x")

    def test_a_bogus_handle_raises_rather_than_dereferencing_it(self) -> None:
        """Handles cross as capsules precisely so an invented one cannot be
        followed into memory that does not belong to it."""
        with pytest.raises(ValueError, match="not an open client"):
            r.cloud_submit(object(), "(til 10)", 10)

    def test_page_size_must_be_positive(self) -> None:
        with pytest.raises((ValueError, errors.RayforceError)):
            r.cloud_submit(object(), "(til 10)", 0)


class TestQueryObjects:
    """A query object goes to the instance as the tree it already is."""

    def test_serializes_to_the_framed_wire_format(self) -> None:
        """The instance deserializes with ray_de, which validates this header —
        the same bytes an IPC frame carries, not a cloud-specific encoding."""
        expr = _serialize(Table("trades").select().where(Column("px") > 2.0))

        assert expr[0:4] == b"\xfa\xde\xfa\xce"
        assert int.from_bytes(expr[8:16], "little") == len(expr) - 16

    def test_an_insert_carries_its_rows(self) -> None:
        """The case that rules out rendering queries back to source text: the
        data is in the tree, and there is no literal that reproduces it."""
        empty = _serialize(Table("trades").select())
        with_rows = _serialize(Table("trades").insert(s="d", px=9.5, qty=99))

        assert len(with_rows) > len(empty)

    def test_an_unsendable_object_reports_in_cloud_terms(self) -> None:
        # python_to_ipc raises RayforceTCPError; a cloud caller never touched
        # the TCP client and should not be told about it.
        with pytest.raises(errors.RayforceValueError, match="cannot send"):
            _serialize(object())

    def test_source_text_does_not_take_the_expression_path(self, monkeypatch) -> None:
        """Text still goes as text: the instance parses it, and wrapping it in a
        serialized string would change what it means."""
        calls: list[str] = []
        monkeypatch.setattr(
            r,
            "cloud_submit",
            lambda *_: (calls.append("submit"), (object(), (None, 0, 1, 1, "")))[1],
        )
        monkeypatch.setattr(r, "cloud_submit_expr", lambda *_: calls.append("expr"))
        monkeypatch.setattr(r, "cloud_connect", lambda *_: object())

        CloudClient("wss://x/y", "rf_x").query("(til 10)")

        assert calls == ["submit"]


class TestConnectErrors:
    def test_an_unresolvable_host_is_a_transport_error(self) -> None:
        with pytest.raises(errors.RayforceWSError):
            CloudClient("wss://no-such-host.invalid/api/v1/instances/ws", "rf_x")

    def test_a_refused_token_is_not_a_transport_error(self) -> None:
        """A bad credential and a dropped link need different handling — one is
        worth retrying and the other never will be."""
        assert not issubclass(errors.RayforceCloudAuthError, errors.RayforceWSError)


@requires_instance
class TestAgainstAnInstance:
    @pytest.fixture
    def client(self):
        with CloudClient(LIVE_URL, LIVE_TOKEN) as client:  # type: ignore[arg-type]
            yield client

    def test_decodes_a_vector_page(self, client: CloudClient) -> None:
        result = client.query("(til 5000)", page_size=100)

        assert result.total == 5000
        assert result.unit == "items"
        assert len(result.value) == 100
        assert [result.value[i] for i in range(3)] == [0, 1, 2]

    def test_decodes_a_table_with_its_columns(self, client: CloudClient) -> None:
        result = client.query("(table [a b] (list (til 5) (til 5)))")

        assert result.unit == "rows"
        assert result.first.returned == 5

    def test_pages_cover_the_whole_result_exactly_once(self, client: CloudClient) -> None:
        result = client.query("(til 5000)", page_size=100)

        assert sum(page.returned for page in result.pages()) == 5000

    def test_a_bound_result_aggregates_in_the_engine(self, client: CloudClient) -> None:
        """The point of binding: the sum is over all 5000 items, not over the
        100 the caller happens to hold."""
        result = client.query("(til 5000)", page_size=100)
        name = result.bind("py_bind_test")

        assert client.query(f"(sum {name})").value == sum(range(5000))

    def test_a_refused_builtin_surfaces_the_runtimes_reason(self, client: CloudClient) -> None:
        with pytest.raises(errors.RayforceError, match="disabled in the cloud runtime"):
            client.query('(.sys.exec "id")')

    def test_a_rejected_token_raises_an_auth_error(self) -> None:
        with pytest.raises(errors.RayforceCloudAuthError):
            CloudClient(LIVE_URL, "rf_deadbeef")  # type: ignore[arg-type]

    @pytest.fixture
    def trades(self, client: CloudClient) -> Table:
        client.query(
            "(set cloud_test_trades (table [s px qty] "
            "(list ['a 'b 'a 'c] [1.5 2.5 3.5 4.5] (as 'I64 [10 20 30 40]))))"
        )
        return Table("cloud_test_trades")

    def test_runs_a_select_built_from_objects(self, client: CloudClient, trades: Table) -> None:
        result = client.query(trades.select())

        assert result.unit == "rows"
        assert result.first.returned == 4

    def test_runs_a_filter_built_from_objects(self, client: CloudClient, trades: Table) -> None:
        result = client.query(trades.select().where(Column("px") > 2.0))

        assert result.first.returned == 3

    def test_aggregates_in_the_engine(self, client: CloudClient, trades: Table) -> None:
        result = client.query(trades.select(total=Column("qty").sum()).by("s"))

        assert result.first.returned == 3

    def test_an_insert_reaches_the_instance_with_its_data(
        self, client: CloudClient, trades: Table
    ) -> None:
        client.query(trades.insert(s="d", px=9.5, qty=99))

        assert client.query(trades.select()).first.returned == 5
