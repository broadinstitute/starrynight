from python:3.11
add --chmod=755 https://astral.sh/uv/install.sh /install.sh
run /install.sh && rm /install.sh
workdir /usr/src/app
copy ./starrynight ./
run /root/.cargo/bin/uv pip install --system --no-cache ".[dev]"
cmd ["starrynight", "--help"]
