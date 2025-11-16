from raypy.queries import select, update, upsert, insert
from raypy.types import queries as q
from raypy.types import operators as p
from raypy.types import scalar as s
from raypy.types import container as c
from raypy import misc

COLUMNS = ["id", "first_name", "last_name", "email", "department", "age"]
VALUES = [
    ["001", "002", "003", "004", "005"],
    ["alice", "bob", "charlie", "dana", "eli"],
    ["johnson", "smith", "kim", "williams", "nguyen"],
    [
        "alice.johnson@example.com",
        "bob.smith@example.com",
        "charlie.kim@example.com",
        "dana.williams@example.com",
        "eli.nguyen@example.com",
    ],
    ["engineering", "marketing", "finance", "hr", "design"],
    [29, 34, 41, 38, 45],
]


def test_select():
    table = c.Table(columns=COLUMNS, values=VALUES)
    misc.set_table_name(table=table, name="people")

    expected_table = c.Table(
        columns=["id", "first_name", "last_name", "age_doubled", "age"],
        values=[
            ["003", "005"],
            ["charlie", "eli"],
            ["kim", "nguyen"],
            c.Vector(type_code=s.I64.type_code, length=2, items=[82, 90]),
            [41, 45],
        ],
    )

    # Select by reference
    query_by_ref = q.SelectQuery(
        select_from=table,
        attributes={
            "id": "id",
            "first_name": "first_name",
            "last_name": "last_name",
            "age_doubled": q.Expression(p.Operation.MULTIPLY, "age", 2),
            "age": "age",
        },
        where=q.Expression(p.Operation.GREATER_EQUAL, "age", 40),
    )

    # Select inplace
    query_inplace = q.SelectQuery(
        select_from="people",
        attributes={
            "id": "id",
            "first_name": "first_name",
            "last_name": "last_name",
            "age_doubled": q.Expression(p.Operation.MULTIPLY, "age", 2),
            "age": "age",
        },
        where=q.Expression(p.Operation.GREATER_EQUAL, "age", 40),
    )

    result_by_ref = select(query_by_ref)
    result_inplace = select(query_inplace)
    assert result_by_ref == result_inplace == expected_table

    # Select from selectable
    expected_table = c.Table(
        columns=[
            "id",
            "first_name",
            "last_name",
            "age_doubled_tripled",
            "age_doubled",
            "age",
        ],
        values=[
            ["003", "005"],
            ["charlie", "eli"],
            ["kim", "nguyen"],
            c.Vector(type_code=s.I64.type_code, length=2, items=[246, 270]),
            c.Vector(type_code=s.I64.type_code, length=2, items=[82, 90]),
            [41, 45],
        ],
    )
    query_from_selectable = q.SelectQuery(
        select_from=q.SelectQuery(
            select_from="people",
            attributes={
                "id": "id",
                "first_name": "first_name",
                "last_name": "last_name",
                "age_doubled": q.Expression(p.Operation.MULTIPLY, "age", 2),
                "age": "age",
            },
            where=q.Expression(p.Operation.GREATER_EQUAL, "age", 40),
        ),
        attributes={
            "id": "id",
            "first_name": "first_name",
            "last_name": "last_name",
            "age_doubled_tripled": q.Expression(p.Operation.MULTIPLY, "age_doubled", 3),
            "age_doubled": "age_doubled",
            "age": "age",
        },
        where=q.Expression(p.Operation.GREATER_EQUAL, "age_doubled", 50),
    )
    result_from_selectable = select(query_from_selectable)
    assert result_from_selectable == expected_table


def test_update():
    table = c.Table(columns=COLUMNS, values=VALUES)
    misc.set_table_name(table=table, name="people")

    expected_table = c.Table(
        columns=["id", "first_name", "last_name", "email", "department", "age"],
        values=[
            ["001", "002", "003", "004", "005"],
            ["alice", "bob", "charlie", "dana", "eli"],
            ["johnson", "smith", "kim", "williams", "nguyen"],
            [
                "alice.johnson@example.com",
                "bob.smith@example.com",
                "charlie.kim@example.com",
                "dana.williams@example.com",
                "eli.nguyen@example.com",
            ],
            ["engineering", "marketing", "finance", "hr", "design"],
            [29, 34, 41, 100, 45],
        ],
    )

    query_by_ref = q.UpdateQuery(
        update_from=table,
        attributes={"age": 100},
        where=q.Expression(p.Operation.EQUALS, "age", 38),
    )
    query_inplace = q.UpdateQuery(
        update_from="people",
        attributes={"age": 100},
        where=q.Expression(p.Operation.EQUALS, "age", 38),
    )

    result_by_ref = update(query_by_ref)
    update(query_inplace)

    assert result_by_ref == expected_table
    assert misc.eval_str("people") == expected_table


def test_upsert():
    table = c.Table(columns=COLUMNS, values=VALUES)
    misc.set_table_name(table=table, name="people")

    expected_table = c.Table(
        columns=["id", "first_name", "last_name", "email", "department", "age"],
        values=[
            ["001", "002", "003", "004", "005", "006"],
            ["alice", "bob", "charlie", "dana", "eli", "karim"],
            ["johnson", "smith", "kim", "williams", "nguyen", "nassar"],
            [
                "alice.johnson@example.com",
                "bob.smith@example.com",
                "charlie.kim@example.com",
                "dana.williams@example.com",
                "eli.nguyen@example.com",
                "karim@lynxtrading.com",
            ],
            ["engineering", "marketing", "finance", "hr", "design", "IT"],
            [29, 34, 41, 38, 45, 23],
        ],
    )

    query_by_ref = q.UpsertQuery(
        upsert_to=table,
        match_by_first=1,
        upsertable={
            "id": ["006"],
            "first_name": ["karim"],
            "last_name": ["nassar"],
            "email": ["karim@lynxtrading.com"],
            "department": ["IT"],
            "age": [23],
        },
    )
    query_inplace = q.UpsertQuery(
        upsert_to="people",
        match_by_first=1,
        upsertable={
            "id": ["006"],
            "first_name": ["karim"],
            "last_name": ["nassar"],
            "email": ["karim@lynxtrading.com"],
            "department": ["IT"],
            "age": [23],
        },
    )

    result_by_ref = upsert(query_by_ref)
    upsert(query_inplace)

    assert result_by_ref == expected_table
    assert misc.eval_str("people") == expected_table


def test_insert():
    table = c.Table(columns=COLUMNS, values=VALUES)
    misc.set_table_name(table=table, name="people")

    expected_table = c.Table(
        columns=["id", "first_name", "last_name", "email", "department", "age"],
        values=[
            ["001", "002", "003", "004", "005", "006"],
            ["alice", "bob", "charlie", "dana", "eli", "karim"],
            ["johnson", "smith", "kim", "williams", "nguyen", "nassar"],
            [
                "alice.johnson@example.com",
                "bob.smith@example.com",
                "charlie.kim@example.com",
                "dana.williams@example.com",
                "eli.nguyen@example.com",
                "karim@lynxtrading.com",
            ],
            ["engineering", "marketing", "finance", "hr", "design", "IT"],
            [29, 34, 41, 38, 45, 23],
        ],
    )

    query_by_ref = q.InsertQuery(
        insert_to=table,
        insertable=["006", "karim", "nassar", "karim@lynxtrading.com", "IT", 23],
    )
    query_inplace = q.InsertQuery(
        insert_to="people",
        insertable=["006", "karim", "nassar", "karim@lynxtrading.com", "IT", 23],
    )

    result_by_ref = insert(query_by_ref)
    insert(query_inplace)

    assert result_by_ref == expected_table
    assert misc.eval_str("people") == expected_table
