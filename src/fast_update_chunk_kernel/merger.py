import json
import logging
import rasterio
from pathlib import Path
import multiprocessing as mp
from rasterio.merge import merge
from rasterio.enums import Resampling
from .work_uint import process
from .schemas import Tile, Scene, GridHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Merger:
    def __init__(self, minio_endpoint: str, workspace_dir: str, description_path: str, workUnits: int):
        self.minio_endpoint = minio_endpoint
        self.workUnits = workUnits
        with open(description_path, 'r') as f:
            self.meta = json.load(f)
        
        # Parse meta
        self.grid_helper = GridHelper(self.meta.get('resolution'))
        self.grids: list[Tile] = [Tile(**grid) for grid in self.meta.get('tiles', [])]
        self.scenes: list[Scene] = [Scene(**scene) for scene in self.meta.get('scenes', [])]
        
        # Make workspace (output path)
        self.workspace_dir = Path(workspace_dir)
        self.grid_output_dir = self.workspace_dir / 'output'
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.grid_output_dir.mkdir(parents=True, exist_ok=True)
        for grid in self.grids:
            grid_dir = self.grid_output_dir / f'{grid.x}_{grid.y}'
            grid_dir.mkdir(parents=True, exist_ok=True)
        
        # Mark grid num in workspace
        with open(self.workspace_dir / f'grid_num_{len(self.grids)}', 'w') as f:
            f.write(f'{len(self.grids)}\n')
            
        # Initialize multiprocessing pool
        self.pool = mp.Pool(processes=self.workUnits)

    def run(self):
        # Use multiprocessing to process each grid
        self._process_grids()
        
        # Merge all grids
        self._merge_grids()

    def _process_grids(self):
        if not self.grids:
            return
        
        tasks = []
        for grid in self.grids:
            task_args = (
                self.minio_endpoint,
                grid,
                self.scenes,
                self.grid_helper,
                str(self.grid_output_dir / f'{grid.x}_{grid.y}')
            )
            tasks.append(task_args)
        
        self.pool.starmap(process, tasks)
    
    def _merge_grids(self):
        if not self.grids:
            return

        files_to_merge = []
        for grid in self.grids:
            grid_tile_path = self.grid_output_dir / f'{grid.x}_{grid.y}' / 'tile.tif'
            if grid_tile_path.exists():
                files_to_merge.append(str(grid_tile_path))
            else:
                logger.warning(f'Tile file not found {grid_tile_path}, skipping.')

        if not files_to_merge:
            logger.info('No tile files found to merge.')
            return

        logger.info(f'Attempting to merge {len(files_to_merge)} tiles ...')

        try:
            merged_array, out_transform = merge(files_to_merge, res=1000.0 / self.meta.get('resolution'), resampling=Resampling.bilinear)

            # Get profile from the first file and update it for the merged output
            with rasterio.open(files_to_merge[0]) as src:
                out_meta = src.meta.copy()
            
            # Update metadata for the merged raster
            out_meta.update({
                'driver': 'COG',
                'height': merged_array.shape[1],
                'width': merged_array.shape[2],
                'transform': out_transform,
                'count': merged_array.shape[0],
                'dtype': merged_array.dtype,
            })

            output_merged_path = self.workspace_dir / 'MERGE_COG.tif'
            with rasterio.open(output_merged_path, 'w', **out_meta) as dest:
                dest.write(merged_array)

            logger.info(f'Successfully merged tiles to {output_merged_path}')

        except Exception as e:
            logger.error(f'Error during merging or writing merged COG: {e}')
            import traceback
            traceback.print_exc()
        
    def __del__(self):
        self.pool.close()
        self.pool.join()
