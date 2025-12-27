import io
import re
import pandas as pd

# Columns your Streamlit app used; we’ll ensure these exist.
EXPECTED_COLS = [
    "DepartmentName", "EquipmentName", "CategoryName", "ResponsibleDepartment",
    "ReasonCode", "StopDateTime", "StartDateTime", "ClosedDateTime",
    "DurationAsHours", "EconomicValue"
]

DATETIME_COLS = ["StopDateTime", "StartDateTime", "ClosedDateTime"]

def _duration_text_to_hours(text: str) -> float:
    """
    Converts strings like '2 d 05 h 30 m', '1 h 10 m', '45 m' to hours.
    Returns 0.0 for unknown formats.
    """
    if pd.isna(text):
        return 0.0
    s = str(text).strip()
    # Pattern for "Xd Yh Zm" with any missing part optional
    m = re.fullmatch(r'(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?', s)
    if m:
        d = int(m.group(1) or 0)
        h = int(m.group(2) or 0)
        mins = int(m.group(3) or 0)
        return d * 24.0 + h + mins / 60.0
    # HH:MM or HH:MM:SS
    try:
        parts = s.split(":")
        if len(parts) == 2:
            h, m_ = map(int, parts)
            return h + m_ / 60.0
        if len(parts) == 3:
            h, m_, _ = map(int, parts)
            return h + m_ / 60.0
    except Exception:
        pass
    return 0.0

def _parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATETIME_COLS:
        if col in df.columns:
            # Handle ISO (with/without Z), and typical Excel text formats
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=False, infer_datetime_format=True)
    return df

def _ensure_expected_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Create missing expected columns with defaults
    defaults = {
        "DepartmentName": "Unknown Department",
        "EquipmentName": "Unknown Equipment",
        "CategoryName": "Uncategorized",
        "ResponsibleDepartment": "Unknown Responsible Dept",
        "ReasonCode": "Unknown",
        "StopDateTime": pd.NaT,
        "StartDateTime": pd.NaT,
        "ClosedDateTime": pd.NaT,
        "DurationAsHours": 0.0,
        "EconomicValue": 0.0,
    }
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = defaults[col]
    # Clean nulls in dimension columns
    for c in ["DepartmentName", "EquipmentName", "CategoryName", "ResponsibleDepartment", "ReasonCode"]:
        df[c] = df[c].fillna(defaults[c]).astype(str)
    # Economic value numeric
    df["EconomicValue"] = pd.to_numeric(df.get("EconomicValue", 0.0), errors="coerce").fillna(0.0)
    return df

def _ensure_duration(df: pd.DataFrame) -> pd.DataFrame:
    """
    If DurationAsHours is missing or zero, try to compute from:
    - Duration text column (common in exports)
    - Or from StartDateTime - StopDateTime when both present
    """
    if "DurationAsHours" not in df.columns:
        df["DurationAsHours"] = 0.0
    df["DurationAsHours"] = pd.to_numeric(df["DurationAsHours"], errors="coerce").fillna(0.0)

    # Convert Duration text if present and hours still zero
    if "Duration" in df.columns:
        needs = df["DurationAsHours"] <= 0
        df.loc[needs, "DurationAsHours"] = df.loc[needs, "Duration"].apply(_duration_text_to_hours)

    # Compute from datetimes where still zero
    if "StopDateTime" in df.columns and "StartDateTime" in df.columns:
        needs = df["DurationAsHours"] <= 0
        mask = needs & df["StopDateTime"].notna() & df["StartDateTime"].notna()
        delta_hours = (df.loc[mask, "StartDateTime"] - df.loc[mask, "StopDateTime"]).dt.total_seconds() / 3600.0
        df.loc[mask, "DurationAsHours"] = delta_hours.clip(lower=0)
    return df

def load_xlsx(file_storage) -> pd.DataFrame:
    """
    Accepts werkzeug FileStorage for an .xlsx file and returns a normalized DataFrame.
    """
    content = file_storage.read()
    df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    df = _parse_datetimes(df)
    df = _ensure_expected_columns(df)
    df = _ensure_duration(df)
    return df