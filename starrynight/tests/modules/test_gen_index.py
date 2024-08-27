"""Test Generate index module."""

from pathlib import Path
from cloudpathlib import AnyPath

from starrynight.modules.gen_index.pipe import create_pipe_gen_inv


def test_generate_pipe():
    pipe = create_pipe_gen_inv(AnyPath("s3://random/path"), AnyPath("s3://random/out"))
    print(pipe.node_list)
