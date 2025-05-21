import rasterio
import numpy as np
from pathlib import Path
from rio_tiler.io import COGReader
from rasterio.transform import from_bounds
from .schemas import Tile, Scene, GridHelper

INFINITY = 999999
BASE_SCENE: Scene | None = None
BASE_SCENE_CLOUD: int = INFINITY
CLOUD_BAND_CONTEXT_MAP: dict[str, COGReader] = {}

def process(minio_endpoint: str, grid: Tile, scenes: list[Scene], grid_helper: GridHelper, output_dir: str):
    # Get grid info
    grid_x, grid_y = grid.x, grid.y
    bBox = grid_helper.grid_to_box(grid_x, grid_y)
    
    # Create output path
    output_path = Path(output_dir) / f'tile.tif'

    # Get target scene with minimum cloud value
    min_cloud = INFINITY
    target_scene: Scene | None = None
    
    open_all_scene_context()
    for scene in scenes:
        result = calc_grid_cloud(scene)
        if result.get('cloud') == 0:
            target_scene = scene
            break
        elif result.get('cloud') < min_cloud:
            min_cloud = result.get('cloud')
            target_scene = scene
    close_all_scene_context()
    
    # Get grid tile from target scene
    rgb_data = read_RGB(target_scene)

    # Write grid tile to disk
    write_RGB_to_disk(rgb_data)
    
    # Mark as processed
    with open(Path(output_dir) / 'done', 'w') as f:
        f.write('Processed')

    # Local helpers ##################################################

    def open_all_scene_context():
        for scene in scenes:
            cloud_band_path = scene.cloudPath
            if cloud_band_path != None:
                full_url = minio_endpoint + '/' + scene.bucket + '/' + cloud_band_path
                opened_context = COGReader(full_url)
                CLOUD_BAND_CONTEXT_MAP[scene.sceneId] = opened_context
    
    def close_all_scene_context():
        for context in CLOUD_BAND_CONTEXT_MAP.values():
            context.close()
           
    def calc_grid_cloud_CloudBand(scene: Scene):
        ctx: COGReader = CLOUD_BAND_CONTEXT_MAP.get(scene.sceneId)
        bbox_wgs84 = grid_helper.grid_to_box(grid_x, grid_y)
        
        img_data = ctx.part(bbox=bbox_wgs84, indexes=[1])
        image_data = img_data.data[0]

        nodata_mask = img_data.mask  # shape: (H, W), dtype=uint8 or bool

        sensorName = scene.sensorName
        if 'Landsat' in sensorName:
            cloud_mask = (image_data & (1 << 3)) > 0  # Pick the 3rd bit
        if 'Landset' in sensorName:
            cloud_mask = (image_data & (1 << 3)) > 0  # Pick the 3rd bit
        elif 'MODIS' in sensorName:
            cloud_mask = (image_data & 1) > 0  # Pick the 0th bit
        elif "GF" in sensorName:
            cloud_mask = (image_data == 2)
        else:
            raise NotImplementedError(f"Cloud logic not implemented for sensor: {sensorName}")
        
        nodata = nodata_mask.astype(bool)
        cloud = cloud_mask.astype(bool)
        valid_mask = (~nodata) & (~cloud)
        
        return {
            'nodata': nodata,
            'cloud': cloud,
            'valid_mask': valid_mask,
            'cloud': np.sum(valid_mask) / np.sum(image_data) * 100
        }
         
    def calc_grid_cloud_SceneCloud(scene: Scene):
        return {
            'cloud': scene.cloud
        }
        
    def calc_grid_cloud(scene: Scene):
        if(scene.cloudPath != None):
            return calc_grid_cloud_CloudBand(scene)
        else:
            return calc_grid_cloud_SceneCloud(scene)

    def read_RGB(scene: Scene):
        # Get data paths of RGB bands
        mapper = scene.bandMapper
        red_path, green_path, blue_path = None, None, None
        for img in scene.images:
            if img.band == mapper.Red:
                red_path = img.tifPath
            elif img.band == mapper.Green:
                green_path = img.tifPath
            elif img.band == mapper.Blue:
                blue_path = img.tifPath

        # Open RGB contexts
        red_band_context = COGReader(f'{minio_endpoint}/{scene.bucket}/{red_path}')
        green_band_context = COGReader(f'{minio_endpoint}/{scene.bucket}/{green_path}')
        blue_band_context = COGReader(f'{minio_endpoint}/{scene.bucket}/{blue_path}')
        
        # Read RGB bands
        R = red_band_context.part(bbox=bBox, indexes=[1]).data[0]
        G = green_band_context.part(bbox=bBox, indexes=[1]).data[0]
        B = blue_band_context.part(bbox=bBox, indexes=[1]).data[0]

        grid_tile = np.stack([R, G, B], axis=0)  # shape: (3, H, W)
        
        # Close RGB contexts
        red_band_context.close()
        green_band_context.close()
        blue_band_context.close()
        
        return grid_tile
    
    def write_RGB_to_disk(data):
        # Get the grid boundaries for georeference
        bbox = grid_helper.grid_to_box(grid_x, grid_y)
        minx, miny, maxx, maxy = bbox
        
        # Setup transform
        height, width = data.shape[1], data.shape[2]
        transform = from_bounds(minx, miny, maxx, maxy, width, height)
        
        # Write the file
        with rasterio.open(
            output_path, 
            'w',
            driver='COG',
            height=height,
            width=width,
            count=3,
            dtype=data.dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(data)
            