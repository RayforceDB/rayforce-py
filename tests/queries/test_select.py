from raypy import queries as q
from raypy.types import scalar as s
from raypy.types import container as c


TABLE_KEYS = ["id", "first_name", "last_name", "email", "department", "age"]
TABLE_VALUES = [
    ["001", "002", "003", "004", "005"],  # id
    ["alice", "bob", "charlie", "dana", "eli"],  # first_name
    ["johnson", "smith", "kim", "williams", "nguyen"],  # last_name
    [
        "alice.johnson@example.com",
        "bob.smith@example.com",
        "charlie.kim@example.com",
        "dana.williams@example.com",
        "eli.nguyen@example.com",
    ],  # email
    ["engineering", "marketing", "finance", "hr", "design"],  # department
    [29, 34, 41, 38, 25],  # age
]


def test_select():
    query = q.SelectQuery(
        attributes={
            "first_name": "first_name",
            "age_doubled": "age_doubled",
            "age_doubled_tripled": q.Expression(
                operation=q.QueryOperation.multiply,
                x=3,
                y="age_doubled",
            ),
        },
        select_from=q.SelectQuery(
            attributes={
                "first_name": "first_name",
                "age_doubled": q.Expression(
                    operation=q.QueryOperation.multiply,
                    x=2,
                    y="age",
                ),
            },
            select_from="people",
            where=q.Expression(
                operation=q.QueryOperation.ge,
                x="age",
                y=30,
            ),
        ),
        where=q.Expression(
            operation=q.QueryOperation.ge,
            x="age_doubled",
            y=70,
        ),
    )

    c.Table(columns=TABLE_KEYS, values=TABLE_VALUES, name="people")

    result = q.select(query)
    assert len(result.columns()) == 3

    assert result.columns()[0] == s.Symbol("first_name")
    assert result.columns()[1] == s.Symbol("age_doubled")
    assert result.columns()[2] == s.Symbol("age_doubled_tripled")

    # first_name
    assert result.values()[0][0] == s.Symbol("charlie")
    assert result.values()[0][1] == s.Symbol("dana")

    # age_doubled
    assert result.values()[1][0] == s.i64(82)
    assert result.values()[1][1] == s.i64(76)

    # age_doubled_tripled
    assert result.values()[2][0] == s.i64(246)
    assert result.values()[2][1] == s.i64(228)
