import math
import numpy as np
from pydantic import BaseModel

class Tile(BaseModel):
    x: int
    y: int

class BandMapper(BaseModel):
    Red: str
    Green: str
    Blue: str
    NIR: str

class Geometry(BaseModel):
    type: str
    coordinates: list[list[list[float]]]

class Bbox(BaseModel):
    type: str
    geometry: Geometry

class Image(BaseModel):
    band: str
    bucket: str
    tifPath: str

class Scene(BaseModel):
    bandMapper: BandMapper
    bbox: Bbox
    bucket: str
    cloud: int
    images: list[Image]
    productName: str
    sceneId: str
    sceneTime: str
    sensorName: str
    cloudPath: str | None = None

EARTH_CIRCUMFERENCE_EQUATOR = 40075.0
EARTH_CIRCUMFERENCE_MERIDIAN = 40008.0
INFINITY = 999999

class GridHelper:
    def __init__(self, grid_resolution_in_kilometer: float = 1):
        self.degreePerGridX = (360.0 * grid_resolution_in_kilometer) / EARTH_CIRCUMFERENCE_EQUATOR
        self.degreePerGridY = (180.0 * grid_resolution_in_kilometer) / EARTH_CIRCUMFERENCE_MERIDIAN * 2.0

        self.grid_num_x = int(math.ceil(360.0 / self.degreePerGridX))
        self.grid_num_y = int(math.ceil(180.0 / self.degreePerGridY))

    def grid_to_box(self, grid_x: int, grid_y: int):

        left_lng, top_lat = self.grid_to_lnglat(grid_x, grid_y)
        right_lng, bottom_lat = self.grid_to_lnglat(grid_x + 1, grid_y + 1)
        return [left_lng, bottom_lat, right_lng, top_lat]

    def grid_to_lnglat(self, grid_x: int, grid_y: int):

        lng = (grid_x / self.grid_num_x) * 360.0 - 180.0
        lat = 90.0 - (grid_y / self.grid_num_y) * 180.0
        return lng, lat
