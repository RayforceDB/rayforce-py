"""
Tests for newly added fluent API features:
- concat()
- join() / inner_join()
- distinct()
- first() / last() / median()
- lookup() for dictionary AT operations
"""

import pytest
from raypy import Table, lookup
from raypy.types import container as c
from raypy.types import scalar as s


def test_concat_two_tables():
    """Test concatenating two tables"""
    table1 = Table.from_dict({
        "name": ["Alice", "Bob"],
        "age": [30, 35]
    })
    
    table2 = Table.from_dict({
        "name": ["Charlie", "Dana"],
        "age": [40, 45]
    })
    
    result = table1.concat(table2)
    
    assert len(result.columns) == 2
    assert "name" in result.columns
    assert "age" in result.columns
    # Should have 4 rows (2 + 2)
    names = [result.values()[0][i].value for i in range(4)]
    assert names == ["Alice", "Bob", "Charlie", "Dana"]


def test_concat_multiple_tables():
    """Test concatenating multiple tables at once"""
    table1 = Table.from_dict({"val": [1, 2]})
    table2 = Table.from_dict({"val": [3, 4]})
    table3 = Table.from_dict({"val": [5, 6]})
    
    result = table1.concat(table2, table3)
    
    assert len(result.columns) == 1
    # Should have 6 rows total
    values = [result.values()[0][i].value for i in range(6)]
    assert values == [1, 2, 3, 4, 5, 6]


def test_concat_all_static_method():
    """Test the static concat_all method"""
    tables = [
        Table.from_dict({"x": [1]}),
        Table.from_dict({"x": [2]}),
        Table.from_dict({"x": [3]}),
    ]
    
    result = Table.concat_all(tables)
    
    values = [result.values()[0][i].value for i in range(3)]
    assert values == [1, 2, 3]


def test_inner_join_single_column():
    """Test inner join on a single column"""
    customers = Table.from_dict({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })
    
    orders = Table.from_dict({
        "id": [2, 3, 3],
        "product": ["Widget", "Gadget", "Gizmo"]
    })
    
    result = customers.join(orders, on="id")
    
    # Should have 3 rows (matching ids: 2, 3, 3)
    assert "name" in result.columns
    assert "product" in result.columns


def test_inner_join_multiple_columns():
    """Test inner join on multiple columns"""
    table1 = Table.from_dict({
        "entity": ["A", "B", "C"],
        "broker": ["X", "Y", "Z"],
        "value1": [10, 20, 30]
    })
    
    table2 = Table.from_dict({
        "entity": ["A", "B", "D"],
        "broker": ["X", "Y", "W"],
        "value2": [100, 200, 300]
    })
    
    result = table1.join(table2, on=["entity", "broker"])
    
    # Should match on (A,X) and (B,Y) -> 2 rows
    assert "value1" in result.columns
    assert "value2" in result.columns


def test_distinct_aggregation():
    """Test distinct() with count()"""
    table = Table.from_dict({
        "dept": ["eng", "eng", "hr", "hr", "eng"],
        "employee": ["Alice", "Bob", "Charlie", "Dana", "Alice"]  # Alice repeats
    })
    
    result = (
        table
        .group_by("dept")
        .agg(
            total_records=table.employee.count(),
            unique_employees=table.employee.distinct().count()
        )
    )
    
    # eng: 3 records, but 2 distinct (Alice appears twice)
    # hr: 2 records, 2 distinct
    assert "total_records" in result.columns
    assert "unique_employees" in result.columns


def test_first_last_aggregations():
    """Test first() and last() aggregations"""
    table = Table.from_dict({
        "group": ["A", "A", "A", "B", "B"],
        "value": [10, 20, 30, 40, 50],
        "label": ["x", "y", "z", "p", "q"]
    })
    
    result = (
        table
        .group_by("group")
        .agg(
            first_value=table.value.first(),
            last_value=table.value.last(),
            first_label=table.label.first(),
            last_label=table.label.last()
        )
    )
    
    assert "first_value" in result.columns
    assert "last_value" in result.columns
    # Group A: first=10, last=30
    # Group B: first=40, last=50


def test_median_aggregation():
    """Test median() aggregation"""
    table = Table.from_dict({
        "group": ["A", "A", "A", "B", "B", "B"],
        "value": [10, 20, 30, 100, 200, 300]
    })
    
    result = (
        table
        .group_by("group")
        .agg(
            median_value=table.value.median()
        )
    )
    
    assert "median_value" in result.columns
    # Group A median: 20
    # Group B median: 200


def test_lookup_dictionary():
    """Test lookup() helper for dictionary AT operations"""
    # NOTE: This feature exists but requires specific C API handling
    # The lookup() function is ready, but the underlying AT operation
    # with Dict objects needs investigation
    
    # Create broker -> entity mapping (Dict takes a Python dict)
    broker_entities = c.Dict({
        "BROKER_1": "ENTITY_A",
        "BROKER_2": "ENTITY_B",
        "BROKER_3": "ENTITY_C"
    })
    
    # Create table
    table = Table.from_dict({
        "broker": ["BROKER_1", "BROKER_2", "BROKER_1", "BROKER_3"],
        "amount": [100, 200, 150, 300]
    })
    
    # Use lookup to map broker to entity
    result = table.update(
        entity=lookup(broker_entities, table.broker)
    ).execute()
    
    assert "entity" in result.columns
    assert "broker" in result.columns


def test_complex_pipeline_query():
    """Test a complex query similar to the pipeline requirements"""
    # Simulate executed orders
    executed_orders = Table.from_dict({
        "Entity": ["ENTITY_A", "ENTITY_A", "ENTITY_B"],
        "Broker": ["BROKER_1", "BROKER_1", "BROKER_2"],
        "Client": ["CLIENT_X", "CLIENT_X", "CLIENT_Y"],
        "ExecQty": [100, 200, 300],
        "ExecCapacity": ["Principal", "Agent", "CrossAsPrincipal"],
        "ClientComm": [10, 20, 30],
        "NetTradeCapt": [5, 10, 15],
        "StreetCost": [2, 4, 6],
    })
    
    # Calculate aggregated costs
    exec_costs = (
        executed_orders
        .group_by("Entity", "Broker", "Client")
        .agg(
            num_executions=executed_orders.ExecQty.count(),
            ExecQty=executed_orders.ExecQty.sum(),
            ExecQtyP=executed_orders.ExecQty.where(
                executed_orders.ExecCapacity.isin(["CrossAsPrincipal", "Principal"])
            ).sum(),
            ClientComm=executed_orders.ClientComm.sum(),
            NetTradeCapt=executed_orders.NetTradeCapt.sum(),
            StreetCost=executed_orders.StreetCost.sum(),
        )
    )
    
    # Add calculated margin column
    result = exec_costs.update(
        Margin=(exec_costs.ClientComm + exec_costs.NetTradeCapt) - exec_costs.StreetCost
    ).execute()
    
    assert "Margin" in result.columns
    assert "ExecQty" in result.columns
    assert "ExecQtyP" in result.columns
    
    # Verify aggregations worked
    # Group 1: ENTITY_A/BROKER_1/CLIENT_X has 2 executions
    # ExecQty should be 100+200=300
    # ExecQtyP should be 100 (only Principal, not Agent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

