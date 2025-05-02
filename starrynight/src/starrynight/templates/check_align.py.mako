import marimo

__generated_with = "0.10.9"
app = marimo.App(width="full")

@app.cell
def _():
    import marimo as mo
    import numpy as np
    import polars as pl
    from cloudpathlib import AnyPath
    import matplotlib.pyplot as plt
    return mo, np, pl, AnyPath, plt

@app.cell
def _(mo):
    mo.md(r"""# Check Alignment""")
    return

@app.cell
def _(pl):
    index_path = ${str(index_path.resolve())}
    index_df = pl.read_parquet(index_path)
    index_df
    return index_df, index_path

@app.cell
def _(mo):
    mo.md(
        """
        # Alignment metrics
        """
    )
    return

@app.cell
def _(df):
    df["channel_dict"][0]
    return

@app.cell
def _(mo):
    mo.md("""## Imaging cycles""")
    return

@app.cell
def _(df, mo):
    _df = mo.sql(
        f"""
        select distinct(cast("cycle_id" as int)) FROM df where "cycle_id" is not null order by cast("cycle_id" as int) asc
        """
    )
    return

if __name__ == "__main__":
    app.run()
