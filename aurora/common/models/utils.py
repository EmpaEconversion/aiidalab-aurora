from __future__ import annotations

import pandas as pd
from pandas.io.formats.style import Styler
from pydantic import BaseModel, ValidationError


def get_valid(raw_data: list[dict], schema: BaseModel) -> list[BaseModel]:
    """Validate list of data against the given schema.

    Parameters
    ----------
    `raw_data` : `List[dict]`
        The raw list of data to be validated.
    `schema` : `BaseModel`
        The schema against which the raw list of data is validated.

    Returns
    -------
    `List[BaseModel]`
        The validated list of schema-modeled data.
    """
    valid_data = []
    for data in raw_data:
        if valid := validate(data, schema):
            valid_data.append(valid)
    return valid_data


def validate(data: dict, schema: BaseModel) -> BaseModel | None:
    """Validate data dictionary against the given schema.

    If invalid, notify client and discard.

    Parameters
    ----------
    `data` : `dict`
        The raw data.
    `schema` : `BaseModel`
        The schema against which the raw data is validated.

    Returns
    -------
    `Optional[BaseModel]`
        The validated data as an instance of the schema model.
    """
    try:
        return schema.validate(data)
    except ValidationError as err:
        # TODO log, don't print
        print("Failed to validate the following data:", end="\n\n")
        print(data, end="\n\n")
        print(err, end="\n\n")
        return None


def to_pd_query(query_dict: dict) -> str | None:
    """Return a query dictionary as a `pandas` query.

    Convert a dictionary of query conditions to a string of
    "and"-separated `pd.DataFrame`-compatible conditions.

    NOTE: `df.query("tuple()")` returns the full table.

    Parameters
    ----------
    `query_dict` : `dict`
        A dictionary of query conditions.

    Returns
    -------
    `Optional[str]`
        An "and"-separated string representation of the query
        required for querying a `pd.DataFrame` object.

    Example
    -------
    >>> to_pd_query({"batch": "12345", "specs.manufacturer": "BIG-MAP"})
    >>> "(`batch` == "12345") and (`specs.manufacturer` == "BIG-MAP")"
    """

    query_args: list[str] = []

    if from_ := query_dict.pop("from", None):
        query_args.append(
            f"(`metadata.creation_datetime` >= \"{pd.to_datetime(from_)}\")")
    if to := query_dict.pop("to", None):
        query_args.append(
            f"(`metadata.creation_datetime` <= \"{pd.to_datetime(to)}\")")

    processed = quote_query_strings(query_dict)
    query_args.extend(f"(`{k}` == {v})" for k, v in processed.items())
    return " and ".join(query_args)


def quote_query_strings(query_dict: dict) -> dict:
    """Enforce quotes on string queries.

    Parameters
    ----------
    `query_dict` : `dict`
        Dictionary containing query key|value pairs.

    Returns
    -------
    `dict`
        The processed dictionary, with strings wrapped in quotes.
    """
    return {
        k: [cast(v_) for v_ in v] if isinstance(v, list) else cast(v)
        for k, v in query_dict.items() if v is not None
    }


def cast(v: int | float | str) -> int | float | str:
    """Return `int|float` as is; surround in quotes if `str`.

    Parameters
    ----------
    `v` : `Union[int, float, str]`
        The value to cast.

    Returns
    -------
    `Union[int, float, str]`
        The casted value.
    """
    return f"'{v}'" if isinstance(v, str) else v


def style(df: pd.DataFrame) -> Styler:
    """Apply dataframe styles.

    Styling:
    - Move `id` column to front
    - Rename columns
    - Set column width
    - Center column contents
    - Hide index column

    Parameters
    ----------
    `df` : `pd.DataFrame`
        The dataframe to be styled.

    Returns
    -------
    `Styler`
        The styled dataframe object.
    """

    awu = df.iloc[0]["specs.composition.anode.weight.units"]
    cwu = df.iloc[0]["specs.composition.cathode.weight.units"]
    cu = df.iloc[0]["specs.capacity.units"]

    RENAMING_MAP = {
        "metadata.name": "Sample",
        "metadata.creation_process": "Creation Process",
        "specs.composition.anode.weight.total": f"An. Tot. Mass ({awu})",
        "specs.composition.anode.weight.net": f"An. Net Mass ({awu})",
        "specs.composition.cathode.weight.total": f"Cat. Tot. Mass ({cwu})",
        "specs.composition.cathode.weight.net": f"Cat. Net Mass ({cwu})",
        "specs.capacity.nominal": f"C Nominal ({cu})",
        "specs.capacity.actual": f"C Recipe ({cu})",
    }

    STYLES = [
        dict(
            selector="th, td",
            props=[
                ("text-align", "center"),
                ("width", "100vw"),
            ],
        ),
        dict(
            selector="th:nth-child(-n+2), td:nth-child(-n+2)",
            props=[
                ("width", "60vw"),
            ],
        ),
        dict(
            selector="th:nth-child(3), td:nth-child(3)",
            props=[
                ("width", "180vw"),
            ],
        ),
    ]

    df = df[RENAMING_MAP.keys()]
    df = df.rename(columns=RENAMING_MAP)
    df.reset_index(inplace=True)

    return df.style \
        .set_table_styles(STYLES) \
        .format(precision=4) \
        .hide(axis="index")
