# fast-update-chunk-kernel
A multiprocessing python framework for updating and merging images.

## Our Philosophy

If you are greedy, make things as FAST as you can.

If you are lazy, delay UPDATES as long as you can.

If you are poor, subdivide CHUNKS as much as you can.

If you are narrow, do not expose your KERNEL to the world.

## Dependencies
- Python >= 3.12
- rasterio >= 1.4.3
- requests >= 2.32.3
- rio-tiler >= 7.7.2
- shapely >= 2.1.1

## Installation without uv
```bash
pip install -r requirements.txt
```

## How to use
With `uv`:
```bash
uv run main.py \
    --minio-endpoint <MINIO_ENDPOINT: eg. http://localhost:81192> \
    --workspace-dir <WORKSPACE_DIR: /path/to/workspace> \
    --description-path <DESCRIPTION_PATH: /path/to/request/description.json> \
    --mp-num <MULTIPROCESSING_NUM: default is 4> \
```

With `python`:
```bash
python main.py \
    --minio-endpoint <MINIO_ENDPOINT: eg. http://localhost:81192> \
    --workspace-dir <WORKSPACE_DIR: /path/to/workspace> \
    --description-path <DESCRIPTION_PATH: /path/to/request/description.json> \
    --mp-num <MULTIPROCESSING_NUM: default is 4> \
```

## How to check progress rate

```python
from fast_update_chunk_kernel import check_progress

progress = check_progress('<WORKSPACE_DIR>')
print(f"Progress: {progress * 100:.2f}%")
```
