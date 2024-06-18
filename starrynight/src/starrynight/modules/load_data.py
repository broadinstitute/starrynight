"Load data for illum module."

import csv
from pathlib import Path

import polars as pl

from starrynight.index import PCPIndex


def gen_load_data(index_path: Path, out_path: Path) -> None:
    df = pl.read_parquet(index_path)
    # Filter for CP images for pipeline 1
    df_pipe_1 = df.filter(pl.col("is_sbs_image").ne(True), pl.col("is_image").eq(True))
    plate_list = df_pipe_1.select(pl.col("plate_id").unique(maintain_order=True))
    plate_channel_list = (
        df_pipe_1.group_by(pl.col("plate_id"))
        .agg(pl.col("channel_dict").explode().unique(maintain_order=True))[
            "channel_dict"
        ]
        .to_list()
    )
    prefix = "/run/media/ank/datastore_001/asma/projects/"
    for chunk_id, df_batch in enumerate(df_pipe_1.iter_slices(100)):
        for i, plate in enumerate(plate_list.to_dict()["plate_id"].to_list()):
            with out_path.joinpath(
                f"load_data_pipeline1_{plate}_chunk{chunk_id}.csv"
            ).open("w") as f:
                loaddata_writer = csv.writer(
                    f, delimiter=",", quoting=csv.QUOTE_MINIMAL
                )
                metadata_heads = [
                    f"Metadata_{col}" for col in ["Plate", "Series", "Site"]
                ]
                filename_heads = [
                    f"FileName_Orig{col}" for col in plate_channel_list[i]
                ]
                frame_heads = [f"Frame_Orig{col}" for col in plate_channel_list[i]]
                pathname_heads = [
                    f"PathName_Orig{col}" for col in plate_channel_list[i]
                ]
                loaddata_writer.writerow(
                    [*metadata_heads, *filename_heads, *frame_heads, *pathname_heads]
                )
                for index in df_batch.to_dicts():
                    index = PCPIndex(**index)
                    assert index.key is not None
                    loaddata_writer.writerow(
                        [
                            index.plate_id,
                            index.site_id,
                            index.site_id,
                            *[f"{index.filename}" for _ in range(len(filename_heads))],
                            *[str(i) for i in range(len(frame_heads))],
                            *[
                                f"{prefix}{'/'.join(index.key.split('/')[0:-1])}/"
                                for _ in range(len(pathname_heads))
                            ],
                        ]
                    )


if __name__ == "__main__":
    gen_load_data(
        Path(__file__).parent.joinpath("asma_index.parquet"),
        Path().joinpath("load_data"),
    )
