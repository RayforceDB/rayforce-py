"""Type constants for parametrized testing across all rayforce types."""

from __future__ import annotations

from rayforce.types import Dict, List, String, Table, Vector
from rayforce.types.scalars import (
    B8,
    F64,
    GUID,
    I16,
    I32,
    I64,
    U8,
    Date,
    QuotedSymbol,
    Symbol,
    Time,
    Timestamp,
)

ALL_NUMERIC_TYPES = [I16, I32, I64, F64, U8]
ALL_TEMPORAL_TYPES = [Date, Time, Timestamp]
ALL_SCALAR_TYPES = [B8, *ALL_NUMERIC_TYPES, *ALL_TEMPORAL_TYPES, String, GUID, Symbol, QuotedSymbol]
ALL_CONTAINER_TYPES = [Vector, List, Dict, Table]
