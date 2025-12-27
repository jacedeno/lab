import os
import uuid
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for, send_file, abort
from utils import load_xlsx

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB upload limit
app.secret_key = os.getenv("SECRET_KEY", "dev-key-change-me")

# In-memory data store: dataset_id -> DataFrame
DATASETS: dict[str, pd.DataFrame] = {}

def get_df(ds_id: str) -> pd.DataFrame:
    df = DATASETS.get(ds_id)
    if df is None:
        abort(404, "Dataset not found or expired")
    return df

def options_from_df(df: pd.DataFrame):
    opts = {
        "depts": sorted(df["DepartmentName"].dropna().unique().tolist()),
        "equips": sorted(df["EquipmentName"].dropna().unique().tolist()),
        "resps": sorted(df["ResponsibleDepartment"].dropna().unique().tolist()),
        "cats": sorted(df["CategoryName"].dropna().unique().tolist()),
        "min_date": df["StopDateTime"].min().date() if df["StopDateTime"].notna().any() else None,
        "max_date": df["StopDateTime"].max().date() if df["StopDateTime"].notna().any() else None,
    }
    return opts

def apply_filters(df: pd.DataFrame, args) -> pd.DataFrame:
    df_ = df.copy()

    # Date range
    sd = args.get("start_date")
    ed = args.get("end_date")
    if sd:
        df_ = df_[df_["StopDateTime"].dt.date >= pd.to_datetime(sd).date()]
    if ed:
        df_ = df_[df_["StopDateTime"].dt.date <= pd.to_datetime(ed).date()]

    # Multiselect filters
    def choose(name, col):
        vals = args.getlist(name)
        if not vals or "__ALL__" in vals or (len(vals) == 1 and vals[0] == "__ALL__"):
            return df_[col].dropna().unique().tolist()
        return [v for v in vals if v != "__ALL__"]

    depts = choose("dept", "DepartmentName")
    equips = choose("equip", "EquipmentName")
    resps = choose("resp", "ResponsibleDepartment")
    cats = choose("cat", "CategoryName")

    df_ = df_[
        df_["DepartmentName"].isin(depts)
        & df_["EquipmentName"].isin(equips)
        & df_["ResponsibleDepartment"].isin(resps)
        & df_["CategoryName"].isin(cats)
    ].copy()

    return df_

def make_figures(df: pd.DataFrame):
    figs = {}

    # KPIs
    kpis = {
        "total_stoppages": int(len(df)),
        "total_hours": float(df["DurationAsHours"].sum()),
        "avg_duration": float(df["DurationAsHours"].mean()) if len(df) else 0.0,
        "economic_impact": float(pd.to_numeric(df.get("EconomicValue", 0.0), errors="coerce").fillna(0).sum()),
    }

    # Hours by Department
    g_dept = df.groupby("DepartmentName", as_index=False)["DurationAsHours"].sum().sort_values("DurationAsHours", ascending=False)
    figs["dept_bar"] = px.bar(
        g_dept,
        x="DepartmentName", y="DurationAsHours",
        title="Total Duration by Department",
        labels={"DepartmentName": "Department", "DurationAsHours": "Hours"},
        color="DepartmentName",
    ).to_json()

    # Hours by Category
    figs["cat_pie"] = px.pie(
        df, names="CategoryName", values="DurationAsHours",
        title="Distribution by Category",
        hole=0.35
    ).to_json()

    # Top 10 Equipment by hours
    g_eq = df.groupby("EquipmentName", as_index=False).agg(
        Hours=("DurationAsHours", "sum"),
        Stoppages=("EquipmentName", "count"),
        Econ=("EconomicValue", "sum")
    ).sort_values("Hours", ascending=False).head(10)
    figs["equip_bar"] = px.bar(
        g_eq, x="EquipmentName", y="Hours", text="Stoppages",
        title="Top 10 Equipment by Stoppage Hours",
        labels={"EquipmentName": "Equipment", "Hours": "Hours"},
        color="Hours",
        color_continuous_scale="Blues"
    ).to_json()

    # Top Reasons
    if "ReasonCode" in df.columns:
        g_reason = df.groupby("ReasonCode")["DurationAsHours"].agg(["sum","count"]).reset_index()
        g_reason.columns = ["Reason", "Hours", "Count"]
        g_reason = g_reason.sort_values("Hours", ascending=False).head(10)
        figs["reason_bar"] = px.bar(
            g_reason, x="Reason", y="Hours", text="Count",
            title="Top Reasons by Duration",
            labels={"Reason": "Reason", "Hours": "Hours"}
        ).to_json()

    # Timeline (Gantt-like)
    if "StopDateTime" in df.columns and "StartDateTime" in df.columns:
        tl = df.dropna(subset=["StopDateTime", "StartDateTime"]).copy()
        tl = tl[tl["StartDateTime"] >= tl["StopDateTime"]]
        if not tl.empty:
            figs["timeline"] = px.timeline(
                tl, x_start="StopDateTime", x_end="StartDateTime",
                y="DepartmentName", color="CategoryName",
                title="Stoppages Timeline (by Department)"
            ).to_json()

    return kpis, figs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("index.html", error="Please select an .xlsx file.")
        if not file.filename.lower().endswith(".xlsx"):
            return render_template("index.html", error="Only .xlsx files are supported.")
        try:
            df = load_xlsx(file)
        except Exception as e:
            return render_template("index.html", error=f"Failed to read Excel: {e}")
        ds_id = uuid.uuid4().hex[:12]
        DATASETS[ds_id] = df
        return redirect(url_for("dashboard", ds_id=ds_id))
    return render_template("index.html")

@app.route("/dashboard/<ds_id>")
def dashboard(ds_id):
    from datetime import date
    df = get_df(ds_id)
    opts = options_from_df(df)
    filtered = apply_filters(df, request.args)
    kpis, figs = make_figures(filtered)
    return render_template(
        "dashboard.html",
        ds_id=ds_id,
        opts=opts,
        args=request.args,
        kpis=kpis,
        figs=figs,
        rowcount=len(filtered),
        filtered_data=filtered,
        today=date.today().strftime('%Y-%m-%d'),
    )

@app.route("/download/<ds_id>.csv")
def download_csv(ds_id):
    from io import BytesIO
    df = get_df(ds_id)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    return send_file(
        BytesIO(csv_bytes), mimetype="text/csv",
        as_attachment=True, download_name=f"stoppages_{ds_id}.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)
