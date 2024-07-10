from concurrent.futures import ThreadPoolExecutor
import io
import json
import redis
import requests
from PIL import Image,ImageOps
from Utils.file_utils import save_to_cloud
import numpy as np
import uuid
import cv2
from Utils.error_template import BaseExceptionError
from dataclasses import dataclass
from typing import Optional, Dict, Union, List, Tuple,Dict
from enum import Enum
import datetime
# from dataclass_wizard import JSONWizard
from dataclasses_json import dataclass_json
from configs.databse import collection_name

# bgbuilder_redis = redis.Redis(
#     host="carbgbuilder-001.gmaq4a.0001.use1.cache.amazonaws.com",
#     port=6379,
#     db=0,
#     decode_responses=True,
# )




class Members(Enum):
    fcbcff64388b3ed69e2fe7cb3bc = "murtaza"
    e73b7bc22f44c87beb34bc7b55a = "AI"
    afe75b642a7adf51f3c7095dc7c = "Afnan"
    c548ef63084f9da5bea73499929 = "Nitin"
    a860df327534450af0362d50e1e = "Agrim"
    b2e54d6519a46d298e3a6140b3c = "Jayant"
    c3609810016b14eb8984dbf1eb0 = "Amar"
    e5f278e122c8344cc9515c43710 = "Shreyank"
    cd7ab3372afb46319cc6f5aec90 = "Shivam"
    cd7ab3372afb46319cc6f5aec77 = "OLD"
    i909033c7f32473da956dc881d7 = "Tech"
    edb314e6aaa4edda1fad2a1c046 = "megha"

class AIModel(Enum):
    Spinny = "Spinny_BG"
    # Krypton= "Krypton_BG"
    # Carbon=  "Carbon_BG"
    # Aluminium = "Aluminium2_BG"
    Marble = "Marble_BG"
    # SpaceGrey= "Space_Grey"
    Transparent= "Transparent_BG"
    Krypton_plus = "Transparent-Krypton"
    Marble_plus =  "Transparent-Marble"
    # marble_bg_old1= "marble_bg_new1"
    Mirror_plus= "Transparent-Mirror"
    # Mirror_plus_old="Transparent-Mirror-OLD",
    Synthetica="Synthetica"
        # SD_Mirror_plus="Transparent-sd_Mirror"
    Hard_Shadow = "Umbra"

class CarModels(Enum):
    Hatchback="Hatchback"
    SUV="SUV"
    Sedan="Sedan"
    Truck="Truck"
    Van = "Van"
    Convertible = "Convertible"
    Jeep = "Jeep"
    Pickup = "Pickup"

class BlendModes(Enum):
    multiply = "multiply"
    addition="addition"
    darken_only = "darken_only"
    difference ="difference"
    divide = "divide"
    dodge ="dodge"
    hard_light = "hard_light" 
    lighten_only ="lighten_only"
    normal ="normal"
    overlay = "overlay"
    soft_light ="soft_light"
    subtract ="subtract"


ai_model_names = {
    "Spinny":      "Spinny_BG",
    "Krypton":     "Krypton_BG",
    "Carbon":      "Carbon_BG",
    "Aluminium":   "Aluminium2_BG",
    "Marble":      "Marble_BG",
    "SpaceGrey":   "Space_Grey",
    "Transparent": "Transparent_BG",
    "Krypton+": "Transparent-Krypton",
    "Marble+": "Transparent-Marble",
    "marble_bg_old1":"marble_bg_new1",
    "Mirror+": "Transparent-Mirror",
    "Mirror+_old":"Transparent-Mirror-OLD",
    "Synthetica":"Synthetica"
     # "sd_mirror+":"Transparent-sd_Mirror"
}
angles = [i*5 for i in range(1, 72)]+[0]

@dataclass_json
@dataclass
class Bginfo:
    bg_id:str   
    AI_Model:AIModel = AIModel.Marble
    car_height:Union[int,Dict[Union[int,str],Union[int,Dict[CarModels,int]]]] | None =700
    car_floor_spacing:Union[int,Dict[Union[int,str],Union[int,Dict[CarModels,int]]]]| None = 100
    car_side_margin: Union[int,Dict[CarModels,int]] | None = 50
    created_by:Members = Members.cd7ab3372afb46319cc6f5aec90
    last_modified_by: Members = Members.cd7ab3372afb46319cc6f5aec90
    created_time : datetime.datetime = datetime.datetime.now()
    last_modified_time : datetime.datetime = datetime.datetime.now()
    shadow_intensity:float | None =  None
    shadow_blur:int | None  =  None
    shadow_len:int | None =  None
    light_bg:bool =  False
    ColorOnColor:bool = False
    mutli_wall_process:bool = False
    reflection_transparency:float | None = None
    wall_url:Union[List[str], str] | None  = None
    floor_url:Union[List[str], str]| None  = None
    alpha: float | None  = None
    make_transparent:bool =  False
    add_shadow:bool = True
    gamma: float | None  = None
    floor_ring_url:Union[List[str], str] | None  = None
    floor_base_url:str | None  = None
    logo_width:int | None  = None
    logo_x:int | None  = None
    logo_y:int | None  = None
    logo_shadow:bool | None = None
    logo_transparency:float | None  =  None
    logo_blendmode: BlendModes | None  = None
    logo_metallic:bool  =False
    logo_metallic_depth:float | None = None
    logo_wall_dynamic:bool  =False
    see_through_transparency:float| None  = None
    ar43:bool = False
    tilt_correction:bool = False
    output_zoom_percent:Union[int,Dict[Union[int,str],Union[int,Dict[CarModels,int]]]] | None  = None
    aspect_ratio:Tuple[int] | None = None
    dynamic_place:int = 0
    int_background_color: Union[Tuple[int],str] | None  = None
    window_correction: str = "0"
    numberplate_config: str = "{}"
    wall_logo_url:str | None  = None
    Exposure_Correction:bool = False
    Color_Correction:bool = False
    tyre_floor_url:str | None = None
    tyre_floor_alpha :float| None  = None
    tyre_floor_gamma :float| None  = None
    trunk_floor_url:str | None = None
    trunk_wall_url:str | None = None
    trunk_alpha :float| None  = 0.4
    trunk_gamma :float| None  = 0.6
    glare_url:Union[List[str], str] | None  = None
    glare_intensity:int = 70
    front_angle_horizon_pct:int = 66
    tyre_shadow_url:str | None = None
    crop_margin:Union[int,Dict[Union[int,str],int]] | None = None
    dynamic_preserve_wall:bool = False
    tyre_horizon_offset:int | None  =  -15
    open_door_palcement_thresh:float | None = 1.0
    windows_old:bool = False
    NWP:int | None = 10
    NHP:int | None = 10
    studio_bg:bool | None =True
    super_resolution:bool | None = False
    mirror_fill_url:Union[Tuple[int],str] | None  = None
    custom_color:Union[Tuple[int],str] | None  = None
    skip_preprocessing: bool = False
    assert_correct: bool = False
    skirting_size:int | None = 0
    mode: str| None = None
    banner_url: str| None = None
    skirting_url: str | None = None
    dynamic_logo: int | None = None
    cut_wall_bottom: bool| None = False
    save_params: dict | None = None

    def __post_init__(self):
        is_360_bg = True
        if isinstance(self.wall_url, list) and len(self.wall_url) > 36:
            is_360_bg = True

        if self.assert_correct:
            assert self.window_correction is not None, f"window_correction cannot be None, got {self.window_correction = }"
            assert self.numberplate_config is not None, f"numberplate_config cannot be None, got {self.numberplate_config = }"
            assert self.dynamic_place is not None, f"dynamic_place cannot be None, got {self.dynamic_place = }"

            if not is_360_bg:
                assert self.tyre_floor_url is not None, f"tyre_floor_url cannot be None, got {self.tyre_floor_url = }"
                assert self.tyre_floor_alpha is not None, f"tyre_floor_alpha cannot be None, got {self.tyre_floor_alpha = }"
                assert self.int_background_color is not None, f"int_background_color cannot be None, got {self.int_background_color = }"

            assert self.glare_intensity is not None, f"glare_intensity cannot be None, got {self.glare_intensity = }"
            assert self.tyre_floor_gamma is not None, f"tyre_floor_gamma cannot be None, got {self.tyre_floor_gamma = }"
            assert self.tilt_correction in [True,False], f"tilt_correction should be boolean, got {self.tilt_correction = }"

            # assert self.wall_url is not None, f"wall_url cannot be None, got {self.wall_url = }"
            # assert self.floor_url is not None, f"floor_url cannot be None, got {self.floor_url = }"

        ### car height
        if isinstance(self.car_height, dict):
            angle_list = self.car_height.keys()
            if not ('default' in angle_list):
                raise BaseExceptionError( f"Background Update Failed : Car height cannot be {self.car_height}.please add all angles and default value. Try Changing it.")
            for angle in angles:
                value = self.car_height[str(angle)] if (
                    str(angle) in angle_list) else self.car_height['default']
                self.car_height[str(angle)] = value
                if isinstance(value, dict):
                    for i in value.keys():
                        v = value[i]
                        if v is None or v <= 0 or v > 1080:
                            raise BaseExceptionError(  f"Background Update Failed :  Car Height cannot be {self.car_height} for angle {angle if (str(angle) in angle_list) else 'default'}. Try Changing it.")
                else:
                    if value is None or value <= 0 or value > 1080:
                        raise BaseExceptionError( f"Background Update Failed :  Car Height cannot be {self.car_height} for angle {angle if (str(angle) in angle_list) else 'default'}. Try Changing it.")
        else:
            if self.car_height is None or self.car_height <= 0 or self.car_height > 1080:
                raise BaseExceptionError( f"Background Update Failed : Car Height cannot be {self.car_height}. Try Changing it.")

        ### car floar specing
        if isinstance(self.car_floor_spacing, dict):
            # new_data["car_floor_spacing"] = new_car_floor_spacing
            angle_list = self.car_floor_spacing.keys()
            if not ('default' in angle_list):
                raise BaseExceptionError(  f"Background Update Failed : Car floor spacing cannot be {self.car_floor_spacing}.please add all angles and default value. Try Changing it.")
            for angle in angles:
                value = self.car_floor_spacing[str(angle)] if (
                    str(angle) in angle_list) else self.car_floor_spacing['default']
                self.car_floor_spacing[str(angle)] = value
                if isinstance(value, dict):
                    for i in value.keys():
                        v = value[i]
                        if (
                            v is None
                            or v < 0
                            or v > 1080
                            or (1080 - v - ((self.car_height[str(angle)][i] if isinstance(self.car_height[str(angle)], dict) else self.car_height[str(angle)]) if isinstance(self.car_height, dict) else self.car_height)) <= 0
                        ):
                            raise BaseExceptionError(  f"Background Update Failed : Car floor spacing cannot be {self.car_floor_spacing} for angle {angle if (str(angle) in angle_list) else 'default'}. Try Changing it.")
                else:
                    if (
                        value is None
                        or value < 0
                        or value > 1080
                        or (1080 - value - ((max(list(self.car_height[str(angle)].values())) if isinstance(self.car_height[str(angle)], dict) else self.car_height[str(angle)]) if isinstance(self.car_height, dict) else self.car_height)) <= 0
                    ):
                        raise BaseExceptionError(  f"Background Update Failed : Car floor spacing cannot be {self.car_floor_spacing} for angle {angle if (str(angle) in angle_list) else 'default'}. Try Changing it.")
        else:
            if (
                self.car_floor_spacing is None
                or self.car_floor_spacing < 0
                or self.car_floor_spacing > 1080
                or (1080 - self.car_floor_spacing - (max([max(list(self.car_height[i].values())) if isinstance(self.car_height[i], dict) else self.car_height[i] for i in self.car_height.keys()]) if isinstance(self.car_height, dict) else self.car_height)) <= 0
            ):
                raise BaseExceptionError(  f"Background Update Failed : Car floor spacing cannot be {self.car_floor_spacing}. Try Changing it.")

        #####################################################################################################
        # wall_logo
        if all(getattr(self, item) is not None for item in ['logo_width', 'logo_x', 'logo_y', "logo_transparency", 'logo_blendmode']):
            if self.logo_width > 1920:
                raise BaseExceptionError(  f"Background Update Failed : plese add logo_width below 1920. Try Changing it.")
            if self.logo_x > 1920 and self.logo_x <= 0:
                raise BaseExceptionError(  f"Background Update Failed : plese add 0<logo_x < 1920. Try Changing it.")
            if self.logo_y > 1080 and self.logo_y <= 0:
                raise BaseExceptionError(  f"Background Update Failed : plese add 0<logo_y < 1080. Try Changing it.")
            if self.logo_transparency > 1 and self.logo_transparency < 0:
                raise BaseExceptionError(  "Please Add logo_transparency : values should be in between 0 to 1 [-0.99 whould be darker,-0.01 is lighter ] ")
            if self.logo_metallic and self.logo_metallic_depth < 0.01 and self.logo_metallic_depth > 0.05:
                raise BaseExceptionError(  "Please Add logo_metallic_depth : values should be in between 0.01 to 0.05  ")
        elif not all(getattr(self, item) is None for item in ['logo_width', 'logo_x', 'logo_y', "logo_transparency", 'logo_blendmode']):
            raise BaseExceptionError(  f"Background Update Failed : plese add this params {['logo_width','logo_x','logo_y','logo_shadow','logo_transparency','logo_blendmode']}. Try Changing it.")

        if self.floor_url is not None:
            if self.assert_correct:
                assert self.alpha is not None, f"alpha cannot be None when floor_url is not None, got {self.alpha = }"
                assert self.gamma is not None, f"gamma cannot be None when floor_url is not None, got {self.gamma = }"

            if self.alpha is not None:
                if self.alpha > 1 or self.alpha < 0:
                    raise BaseExceptionError(  "Background Update Failed : Alpha should be between 0 and 1")
                if self.gamma > 1 or self.gamma < 0:
                    raise BaseExceptionError(  "Background Update Failed : Gamma should be between 0 and 1")

        if self.AI_Model in [AIModel.Transparent,AIModel.Hard_Shadow, AIModel.Marble_plus, AIModel.Krypton_plus]:
            if self.wall_url is None and  self.ColorOnColor != True:
                raise BaseExceptionError( "Please Add Background Url")
        # elif self.AI_Model == "Transparent_BG_REFL":
        #     if self.wall_url is None:
        #         raise BaseExceptionError( "Please Add Background Url")
        #     if self.shadow_intensity is None or not (
        #         -1 < self.shadow_intensity < 0
        #     ):
        #         raise BaseExceptionError(
        #             "Please Add shadow intensity : values should be in between 0 to 1 [-0.99 whould be darker,-0.01 is lighter shadow] "
        #         )
        #     if self.shadow_blur is None or not (
        #         0 < self.shadow_blur < 200
        #     ):
        #         raise BaseExceptionError( "Please Add shadow blur :values should be int and  bigger then 0 and less then 200")
        #     if self.reflection_transparency is None or not (
        #         0 < self.reflection_transparency < 1
        #     ):
        #         raise BaseExceptionError( "Please Add reflection transparency :values should be float and in between 0 to 1  [add light_bg true for white bg] ")
        elif self.shadow_intensity is not None:
            if self.shadow_intensity is None or not (
                -1 < self.shadow_intensity < 1
            ):
                raise BaseExceptionError( 
                    "Please Add shadow intensity : values should be in between -1 to 1 [-0.99 whould be darker,+0.99 is lighter shadow]  "
                )
            if self.shadow_len is None or not (
                3 < self.shadow_len < 10
            ):
                raise BaseExceptionError( "Please Add shadow len :values should be in between 3 to 10 [bigger the values less shadow len]")

        if self.assert_correct:
            if self.shadow_intensity is None or not (-1 <= self.shadow_intensity <= 0):
                raise BaseExceptionError(
                    "Please Add shadow intensity : values should be in between 0 to 1 [-0.99 whould be darker,-0.01 is lighter shadow] "
                )
            if self.shadow_blur is None or not (0 <= self.shadow_blur < 200):
                raise BaseExceptionError(
                    "Please Add shadow blur :values should be int and  bigger then 0 and less then 200"
                )

        see_through_transparency = self.see_through_transparency
        if see_through_transparency is not None:
            if not 0 <= see_through_transparency <= 1:
                raise BaseExceptionError( "Background Update failed, values should be between 0 and 1 for see_through_transparency")

        if self.output_zoom_percent is not None:
            if isinstance(self.output_zoom_percent, dict):
                angle_list = self.output_zoom_percent.keys()
                if not ('default' in angle_list):
                    raise BaseExceptionError( f"Background Update Failed : Car output Zoom cannot be {self.output_zoom_percent}.please add all angles and default value. Try Changing it.")
                for angle in angles:
                    value = self.output_zoom_percent[str(angle)] if (
                        str(angle) in angle_list) else self.output_zoom_percent['default']
                    self.output_zoom_percent[str(angle)] = value
                    if isinstance(value, dict):
                        for i in value.keys():
                            v = value[i]
                            if not 0 <= v <= 100:
                                raise BaseExceptionError( "Background Update failed, values should be between 0 and 100 for output_zoom_percent")
                            max_allowed_height = ((self.car_height[str(angle)][i] if isinstance(self.car_height[str(angle)], dict) else self.car_height[str(angle)]) if isinstance(self.car_height, dict) else self.car_height) * \
                                (1+v/100) + ((self.car_floor_spacing[str(angle)][i] if isinstance(self.car_floor_spacing[str(angle)], dict)
                                              else self.car_floor_spacing[str(angle)]) if isinstance(self.car_floor_spacing, dict) else self.car_floor_spacing)
                            if max_allowed_height > 1080:
                                raise BaseExceptionError(f"Background Update failed, zoom percentage is too high! for angle {angle}. Try Changing it.")
                    else:
                        if not 0 <= value <= 100:
                            raise BaseExceptionError( "Background Update failed, values should be between 0 and 100 for output_zoom_percent")
                        max_allowed_height = ((max(list(self.car_height[str(angle)].values())) if isinstance(self.car_height[str(angle)], dict) else self.car_height[str(angle)]) if isinstance(self.car_height, dict) else self.car_height) * \
                            (1+value/100) + ((max(list(self.car_floor_spacing[str(angle)].values())) if isinstance(self.car_floor_spacing[str(
                                angle)], dict) else self.car_floor_spacing[str(angle)]) if isinstance(self.car_floor_spacing, dict) else self.car_floor_spacing)
                        if max_allowed_height > 1080:
                            raise BaseExceptionError( f"Background Update failed, zoom percentage is too high! for angle {angle}. Try Changing it.")
            else:
                if not 0 <= self.output_zoom_percent <= 100:
                    raise BaseExceptionError( "Background Update failed, values should be between 0 and 100 for output_zoom_percent")
                max_allowed_height = (max([max(list(self.car_height[i].values())) if isinstance(self.car_height[i], dict) else self.car_height[i] for i in self.car_height.keys()]) if isinstance(self.car_height, dict) else self.car_height) * \
                    (1+self.output_zoom_percent/100) + (max([max(list(self.car_floor_spacing[i].values())) if isinstance(self.car_floor_spacing[i], dict) else self.car_floor_spacing[i]
                                                        for i in self.car_floor_spacing.keys()]) if isinstance(self.car_floor_spacing, dict) else self.car_floor_spacing)
                if max_allowed_height > 1080:
                    raise BaseExceptionError(  "Background Update failed, zoom percentage is too high!")
        if self.crop_margin is not None:
            if isinstance(self.crop_margin, dict):
                crop_margin_angles = self.crop_margin.keys()
                if 'default' not in crop_margin_angles:
                    raise BaseExceptionError(   f"Background Update Failed : crop_margin cannot be {self.crop_margin}.please add all angles and default value. Try Changing it.")
                for angle in angles:
                    value = self.crop_margin[str(angle)] if (
                        str(angle) in crop_margin_angles) else self.crop_margin['default']
                    self.crop_margin[str(angle)] = value

        if self.glare_intensity < 0 or self.glare_intensity > 100:
            raise BaseExceptionError(  "Background Update Failed : glare_intensity should be between 0 and 100")    
        if self.dynamic_place>0:
            if self.wall_url is None:
                raise BaseExceptionError(   "Can't enable dynamic_place without wall_url, please upload.")
            if self.floor_url is None:
                raise BaseExceptionError(   "Can't enable dynamic_place without floor_url, please upload.")
            if self.assert_correct:
                assert self.front_angle_horizon_pct is not None, f"front_angle_horizon_pct cannot be None when dynamic_place is True, got {self.front_angle_horizon_pct = }"
                assert self.dynamic_preserve_wall is not None, f"dynamic_preserve_wall cannot be None when dynamic_place is True, got {self.dynamic_preserve_wall = }"
                assert self.tyre_horizon_offset is not None, f"tyre_horizon_offset cannot be None when dynamic_place is True, got {self.tyre_horizon_offset = }"

        if not 80>=self.front_angle_horizon_pct>=20:
            raise BaseExceptionError( "front_angle_horizon_pct should be between 20 and 80.")


#########################
def check_username_password(uname)-> Members:
    try:
        member = Members[uname]
    except:
        raise BaseExceptionError("username is not listed")
    
    return member



class BGBuilderAuto:
    # def add_bg_new(self,data):
    #     old_bg_data = self.get_info(data['bg_id'])
    #     data['created_by'] = old_bg_data.get("created_by",data['last_modified_by'])
    #     data['created_time'] =  old_bg_data.get("created_time",data['last_modified_time'])
    #     data['assert_correct'] = True
    #     bginfo_obj = Bginfo.from_dict(data)
    #     bgbuilder_redis.set(str(bginfo_obj.bg_id), bginfo_obj.to_json())
    #     return bginfo_obj.to_dict()
    
    

    def add_bg_new(self, data):
        # old_bg_data = self.get_info(data['bg_id'])
        # data['created_by'] = old_bg_data.get("created_by", data['last_modified_by'])
        # data['created_time'] = old_bg_data.get("created_time", data['last_modified_time'])
        # data['assert_correct'] = True
        # bginfo_obj = Bginfo.from_dict(data)
        # bginfo_json = json.loads(bginfo_obj.to_json())

        # collection_name.update_one(
        #     {'bg_id': bginfo_obj.bg_id},
        #     {'$set': bginfo_json},
        #     upsert=True
        # )
        
        # return bginfo_obj.to_dict()
    

        old_bg_data = self.get_info(data['bg_id'])

        if old_bg_data:
            collection_name.update_one(
                {'bg_id': data['bg_id'], 'is_active': True},
                {'$set': {'is_active': False}}
            )
            data['created_by'] = old_bg_data.get("created_by", data['last_modified_by'])
            data['created_time'] = old_bg_data.get("created_time", data['last_modified_time'])
        else:
            data['created_time'] = datetime.now()

        data['last_modified_time'] = datetime.now()
        data['assert_correct'] = True
        data['is_active'] = True 

        bginfo_obj = Bginfo.from_dict(data)

        bginfo_json = bginfo_obj.to_dict()

        collection_name.insert_one(bginfo_json)

        return bginfo_obj.to_dict()


        
    def update_bg(self,data:Bginfo):
        # bgbuilder_redis.set(str(data.bg_id), data.to_json())
        
        # collection_name.update_one(
        # {'bg_id': data.bg_id},
        # {'$set': data.to_dict()},
        # upsert=True
        # )
        # return data.to_dict()

        # current_active_version = collection_name.find_one({'bg_id': data.bg_id, 'is_active': True})

        # if current_active_version:
        #     # Deactivate the current active version
        #     collection_name.update_one(
        #         {'_id': current_active_version['_id']},
        #         {'$set': {'is_active': False}}
        #     )

        # # Set new data fields

        # data.created_time = datetime.now()
        # data.last_modified_time = datetime.now()
        # data.assert_correct = True
        # data.is_active = True  # Ensure the new version is active

        # # Insert the new version
        # collection_name.insert_one(data.to_dict())

        # return data.to_dict()

        latest_active_version = collection_name.find_one({'bg_id': data.bg_id, 'is_active': True})
        if latest_active_version:
            collection_name.update_one(
                {'_id': latest_active_version['_id']},
                {'$set': {'is_active': False}}
            )

        latest_version = collection_name.find_one({'bg_id': data.bg_id}, sort=[('version_number', -1)])
        if latest_version:
            new_version_number = latest_version.get('version_number', 0) + 1
        else:
            new_version_number = 1

        data_dict = data.to_dict()
        data_dict['version_number'] = new_version_number
        data_dict['is_active'] = True
        data_dict['last_modified_time'] = datetime.now()

        collection_name.update_one(
            {'bg_id': data.bg_id, 'version_number': new_version_number},
            {'$set': data_dict},
            upsert=True
        )

        return data_dict
    

    def filter_config(self):
        # with bgbuilder_redis.pipeline() as pipe:
        #     for k in bgbuilder_redis.keys():
        #         pipe.get(k)
        #     data = pipe.execute()
        # return [json.loads(x) for x in data if not isinstance(x, int)]

        cursor = collection_name.find({"is_active" : True})
        data = [doc for doc in cursor]
        return data

    
    def get_info(self, bg_id):
        result = collection_name.find_one({'bg_id': bg_id, 'is_active': True})
     
        from fastapi.encoders import jsonable_encoder
        if result:
            result['_id'] = str(result['_id'])
            return jsonable_encoder(result)
        return None
    


    def delete_bg(self, bg_id):
        # status = bgbuilder_redis.delete(bg_id)
        # if status == 1:
        #     return f"Background Delete Success : {bg_id}"
        # else:
        #     return f"Background ID Not Present: {bg_id}"

        # result = collection_name.delete_one({'bg_id': bg_id})
        # if result.deleted_count == 1:
        #     # self.redis.delete(bg_id)
        #     return f"Background Delete Success : {bg_id}"
        # else:
        #     return f"Background ID Not Present: {bg_id}"
        

        current_active_version = collection_name.find_one({'bg_id': bg_id, 'is_active': True})

        if current_active_version:
            collection_name.update_one(
                {'_id': current_active_version['_id']},
                {'$set': {'is_active': False}}
            )
            return f"Background Deactivated: {bg_id}"
        else:
            return f"No active background found with ID: {bg_id}"
        
    def bulk_update(bg_data):
        bg_ids = [data['bg_id'] for data in bg_data]

        collection_name.update_many(
        {'bg_id': {'$in': bg_ids}, 'is_active': True},
        {'$set': {'is_active': False}}
        )

        latest_versions = collection_name.aggregate([
            {'$match': {'bg_id': {'$in': bg_ids}}},
            {'$sort': {'bg_id': 1, 'version_number': -1}},
            {'$group': {'_id': '$bg_id', 'latest_version': {'$first': '$version_number'}}}
        ])

        latest_versions_dict = {doc['_id']: doc['latest_version'] for doc in latest_versions}

        new_datas = []
        for data in bg_data:
            bg_id = data['bg_id']
            new_version_number = latest_versions_dict.get(bg_id, 0) + 1

            new_data = {
                **data,
                'created_at': datetime.now(),
                'last_modified_time': datetime.now(),
                'version_number': new_version_number,
                'is_active': True
            }
            new_datas.append(new_data)

        if new_datas:
            collection_name.insert_many(new_datas)

        return new_datas





def url_tester(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        _ = Image.open(io.BytesIO(resp.content))
        return True
    except:
        return False


def check_urls(urls, text=""):
    urls = urls.replace(' ', '').split(',')
    with ThreadPoolExecutor(10) as exe:
        futures = []
        for url in urls:
            futures.append(exe.submit(url_tester, url))
    for future in futures:
        if future.result() is False:
            raise BaseExceptionError(
                f"Background Update Failed : Wrong {text} URL uploaded. Try Changing it.")
    if len(urls) ==1:
        return urls[0]
    return urls
def gen_url(image):
    img = np.array(ImageOps.exif_transpose(Image.open(image.file)))
    if img.shape[2]==4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output_url = save_to_cloud(img=img, imagename=str(uuid.uuid4()), key=None,
                                   process="car_BGBuilder", save_params={
            "extension": ".png",
            "quality": 100
        })
    return output_url,image.filename.split('.')[0]


def genrate_url(urls):
    info = {}
    with ThreadPoolExecutor(10) as exe:
        futures = []
        for url in urls:
            futures.append(exe.submit(gen_url, url))
    for future in futures:
        output_url,image =future.result()
        info[image]= output_url    
    output = []
    for i in info.keys():
        output.append(info[i])
    if len(output) ==1:
        return output[0]  
    return output
