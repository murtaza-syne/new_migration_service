from fastapi import FastAPI
# from configs.databse import collection_name
from bg_builder.bg_builder_api import router
app = FastAPI()
# from configs.databse import collection_name

app.include_router(router=router)

document = {
    "bg_id": "bg001",
    "AI_Model": "Marble",
    "car_height": 700,
    "car_floor_spacing": 100,
    "car_side_margin": 50,
    "last_modified_by": "user123",
    "shadow_intensity": 0.5,
    "shadow_blur": 5,
    "shadow_len": 10,
    "light_bg": True,
    "ColorOnColor": False,
    "mutli_wall_process": False,
    "reflection_transparency": 0.8,
    "wall_url": ["url1", "url2"],
    "floor_url": ["url3"],
    "alpha": 0.5,
    "make_transparent": True,
    "add_shadow": True,
    "gamma": 1.2,
    "floor_ring_url": ["url4"],
    "floor_base_url": "url5",
    "logo_width": 100,
    "logo_x": 10,
    "logo_y": 20,
    "logo_shadow": True,
    "logo_transparency": 0.6,
    "logo_blendmode": "Normal",
    "logo_metallic": False,
    "logo_metallic_depth": 0.3,
    "logo_wall_dynamic": True,
    "see_through_transparency": 0.7,
    "ar43": False,
    "tilt_correction": True,
    "output_zoom_percent": 80,
    "aspect_ratio": [16, 9],
    "dynamic_place": 1,
    "int_background_color": [255, 255, 255],
    "window_correction": "1",
    "numberplate_config": "{}",
    "wall_logo_url": "url6",
    "Exposure_Correction": True,
    "Color_Correction": True,
    "tyre_floor_url": "url7",
    "tyre_floor_alpha": 0.5,
    "tyre_floor_gamma": 1.0,
    "trunk_floor_url": "url8",
    "trunk_wall_url": "url9",
    "trunk_alpha": 0.4,
    "trunk_gamma": 0.6,
    "glare_url": ["url10"],
    "glare_intensity": 70,
    "front_angle_horizon_pct": 66,
    "tyre_shadow_url": "url11",
    "crop_margin": 10,
    "dynamic_preserve_wall": True,
    "tyre_horizon_offset": -15,
    "open_door_palcement_thresh": 1.0,
    "windows_old": False,
    "NWP": 10,
    "NHP": 10,
    "studio_bg": True,
    "super_resolution": False,
    "mirror_fill_url": "url12",
    "custom_color": [255, 0, 0],
    "skip_preprocessing": False,
    "assert_correct": True,
    "skirting_size": 5,
    "mode": "auto",
    "banner_url": "url13",
    "skirting_url": "url14",
    "dynamic_logo": 1,
    "cut_wall_bottom": False,
    "save_params": {"param1": "value1"}
}
# result = collection_name.insert_one(document)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/read_me")
def read_me_api():
    return {"a":1}
