import marimo

__generated_with = "0.10.9"
app = marimo.App(width="full")

@app.cell
def _():
    import marimo as mo
    import numpy as np
    import polars as pl
    return mo, np, pl

@app.cell
def _(mo):
    mo.md(r"""# Inspect generated index""")
    return

@app.cell
def _(pl):
    index_path = "/datastore/ip-merck-dev/projects/cpg1234-AMD-screening/workspace/index/index.parquet"
    df = pl.read_parquet(index_path)
    df
    return df, index_path

@app.cell
def _(mo):
    mo.md(
        """
        # SBS metrics
        df["channel_dict"][0]
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
