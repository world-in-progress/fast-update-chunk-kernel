# fast-update-chunk-kernel
A multiprocessing python framework for updating and merging images.

## Our Philosophy

If you are greedy, make things as **FAST** as you can.

If you are lazy, delay **UPDATES** as long as you can.

If you are poor, subdivide **CHUNKS** as much as you can.

If you are narrow, do not expose your **KERNEL** to the world.

## Dependencies
- Python >= 3.12
- rasterio >= 1.4.3
- requests >= 2.32.3
- rio-tiler >= 7.7.2
- shapely >= 2.1.1

## How to use
Use `uv`:
```bash
uv run main.py 
    --minio-endpoint <MINIO_ENDPOINT> \
    --workspace-dir <WORKSPACE_DIR> \
    --description-path <DESCRIPTION_PATH> \
    --work-units <WORK_UNITS>
```

Use `python`:
```bash
python main.py \
    --minio-endpoint <MINIO_ENDPOINT> \
    --workspace-dir <WORKSPACE_DIR> \
    --description-path <DESCRIPTION_PATH> \
    --work-units <WORK_UNITS>
```

## How to check progress rate

```python
from fast_update_chunk_kernel import check_progress

progress = check_progress('<WORKSPACE_DIR>')
print(f"Progress: {progress * 100:.2f}%")
```
