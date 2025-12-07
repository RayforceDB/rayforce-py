class KDBConnectionAlreadyClosedError(Exception):
    """Raises when attemting to utilise closed KDB connection"""


class PDDataFrameConversionError(Exception):
    """Raised when Pandas DataFrame conversion fails"""


class PLDataFrameConversionError(Exception):
    """Raised when Polars DataFrame conversion fails"""
