from typing import Optional
from typing import List
import sentry_sdk
from fastapi import APIRouter, Form, Response, status,UploadFile,File
from Utils.file_utils import *
from Utils.error_template import BaseExceptionError
from bg_builder.bg_builder import BGBuilderAuto,genrate_url,check_urls,Bginfo,ai_model_names,check_username_password,BlendModes
import json
from pydantic.types import Json
from Utils.custom_encoder import custom_jsonable_encoder
from fastapi.encoders import jsonable_encoder
import datetime
router = APIRouter()

bgbuilder_auto = BGBuilderAuto()

#######################################################################################################


@router.post("/automobile/bgbuilder/")
def automobile_bgbuilder(
    bg_id: str = Form(...,description=r'whatever id u want add'),
    username:str = Form(...),
    AI_Model: str = Form(...,description=f'AI_Model select from {list(ai_model_names.keys())}'),
    car_height: str = Form(...,description=r'add only number if apply for all angle else {"5": 20,"90": { "Hatchback":20,"SUV":20,"Sedan":20},"default":10} for each angle (car height respective  to 1024 full img ) '),
    car_floor_spacing: str = Form(...,description=r'add only number if apply for all angle else {"5": 20,"90": {"Hatchback":20,"SUV":20,"Sedan":20},"default":10}  for each angle (car bottom floor spacing respective  to 1024 full img)'),
    car_side_margin : Optional[str] = Form(...,description=r'add only number if apply for models else { "Hatchback":20,"SUV":20,"Sedan":20} for each car type (car side margin  respective  to  input img) '),
    shadow_intensity: float = Form(None,description="shadow intensity (+1.0 to -1.0) if it's value close to +1 then shadow is lighter else if it's values is negetive then shadow is darker"),
    shadow_blur: int = Form(None,description='blur on shadow values beetween (1,200) bigger the more blur'),
    shadow_len: int = Form(None,description="len of shaodw to be selected (for ai model 'Spinny', 'Krypton', 'Carbon', 'Aluminium', 'Marble', 'SpaceGrey') range 3-10 (bigger the values less shadow len)"),
    light_bg: Optional[bool]= Form(False,description = "used for Transparent bgs (true if wall is ligter )"),
    reflection_transparency: float = Form(None,description="reflection transperency (values should be float and in between 0 to 1 )"),
    alpha: Optional[float] = Form(None,description="alpha values should be between 0 to 1 (it's used for overlay based bg's "),
    make_transparent : Optional[bool]= Form(False ,description = "if u want transparent img as output make this true"),
    add_shadow : Optional[bool]= Form(True ,description = "if u want transparent img from make_transparent to without shadow make this false"),
    gamma: Optional[float] = Form(None,description="gamma values should be between 0 to 1 (it's used for overlay based bg's "),
    wall_url: Optional[str] = Form(None,description=r'wall_url add single or seprated by ,   (wall is upper part of bg )'),
    wall_files: List[UploadFile] = File(None,description = "select multiple walls  (wall is upper part of bg ) (use any one of this either urls or files )"),
    floor_url: Optional[str] = Form(None,description=r'floor_url add single or seprated by , (floor is lowwer part of bg)'),
    floor_files: List[UploadFile] = File(None,description = "select multiple floor  (wall is upper part of bg ) (use any one of this either urls or files )"),\
    glare_url: Optional[str] = Form(None,description=r'glare_url add single or seprated by , (glare is  part of window)'),
    glare_files: List[UploadFile] = File(None,description = "select multiple glare  (use any one of this either urls or files )"),
    glare_intensity:Optional[int] = Form(70,description="glare_intensity values should be between 0 to 100"),
    floor_ring_url: Optional[str] = Form(None,description="add ring if u want ring on floor "),
    floor_base_url: Optional[str] = Form(None,description="extra floor for new dynamic placement feature"),
    floor_ring_url_files: List[UploadFile] = File(None,description = "select single ring  (add ring if u want ring on floor) (use any one of this either urls or files )"),
    logo_width: Optional[int] = Form(None,description="wall logo width values is in int and respective to wall "),
    logo_x:  Optional[int] = Form(None,description="wall logo x cood. (left most corner) values is in int and respective to wall "),
    logo_y:  Optional[int] = Form(None,description="wall logo x cood. (left most corner) values is in int and respective to wall "),
    logo_shadow:  Optional[bool] = Form(False ,description = "make this true if u want shadow on wall logo"),
    logo_transparency:  Optional[float] = Form(None ,description= "wall logo transparency is between [-0.99 whould be darker,-0.01 is lighter ] "),
    logo_blendmode:  Optional[str] = Form(None,description = f"selct wall logo blanding mode {BlendModes}"),
    logo_metallic: Optional[bool] = Form(False,description='make this true if u want matalic effect on wall logo'),
    logo_metallic_depth:  Optional[float] = Form(None,description="wall logo merallic depth ( between 0.01 to 0.05)"),
    logo_wall_dynamic: Optional[bool] = Form(False,description='make this true if u wall logo place on dynemic wall'),
    see_through_transparency:  Optional[float] = Form(None,description="see through marging with raw transperency (values between 1.0 to 0.0) "),
    ar43: Optional[bool] = Form(False,description="make this true if u want aspect ratio 4:3"),
    tilt_correction: Optional[bool] = Form(True,description="if this is true tilt correction is enabled"),
    output_zoom_percent: Optional[str]  = Form(None,description=r'add only number if apply for all angle else {"5": 20,"90": { "Hatchback":20,"SUV":20,"Sedan":20},"default":10}  for each angle  (zoom is processed after floor gen.)'),
    window_correction: Optional[str] = Form('0',description="params for process:{'TRANSPARENCY':0.5,'TINT_COLOR':(255,20,255),'SEE_THROUGH_TRANSPARENCY':0.5} and set 0 for no process ( TRANSPARENCY (0.0-1.0) tint transparency,TINT_COLOR color of tint, SEE_THROUGH_TRANSPARENCY tint value applied on see-through(0.0-1.0)" ),
    numberplate_config: Optional[str] = Form('0',description="params for process:{'logo_url':0,'pad_logo':True,'logo_border_url':'https://spyne-prod-tech.s3.amazonaws.com/api/upload/input_808ae7e9-e1ff-4b2a-b863-0627fbe3a95d.png','scale_h':1.04,'scale_w':1.04,'height_pedding':10,'width_pedding':10} and set 0 for no process" ),
    wall_logo_url: Optional[str] = Form(None,description="set default wall logo"),
    aspect_ratio: Optional[str] = Form(None,description="add custom aspect ratio (aspect_ratio must be in the format: w-h)"),
    int_background_color: Optional[str] = Form(None,description="interior bg. color (int_background_color must be in the format: R-G-B) and value in [0-255]  and also add url for BG in interior"),
    int_background_url_files: List[UploadFile] = File(None,description = "select single BG  (use any one of this either urls or files )"),
    dynamic_place: Optional[int] = Form(0, description="make this 1, if u want wall placement accroding to car tyre"),
    skirting_size : Optional[int] = Form(0, description="add skirting size in floor when floor image height is 1080, this can be negetive to when bottom padding is bigger then top"),
    ColorOnColor: Optional[bool] = Form(False,description=r'make true if u want wall color same as car color'),
    Exposure_Correction: Optional[bool] = Form(False,description=r'make true if u want to fix Exposure'),
    Color_Correction: Optional[bool] = Form(False,description=r'make true if u want to yellow or red reflection glare'),
    tyre_floor_url: Optional[str] = Form('https://spyne-prod-tech.s3.amazonaws.com/api/upload/input_a6a8133d-3876-47ec-b4ba-91bd9982fabb.jpg',description="add if u want focused tyre image with BG Specific floor"),
    tyre_floor_alpha:Optional[float] = Form(0.4,description="alpha values should be between 0 to 1 (it's used for overlay based bg's "),
    tyre_floor_gamma: Optional[float] = Form(0.6,description="gamma values should be between 0 to 1 (it's used for overlay based bg's "),
    tyre_shadow_url: Optional[str] = Form(None,description="Add if you want shadow with BG Specific floor"),
    front_angle_horizon_pct: Optional[int] = Form(50, description="Floor horizon for front and back angles, from 0 to 100% of car height"),
    crop_margin: Optional[str] = Form(None, description=r'add only number if apply for all angle else {"5": 20,"default":10}  for each angle'),
    dynamic_preserve_wall: Optional[bool] = Form(False, description="Make True to preserve wall base."),
    tyre_horizon_offset: Optional[int] = Form(-15, description="Set margin between tyre top and floor start"),
    studio_bg: Optional[bool] = Form(True ,description="make this False for no studio background"),
    open_door_palcement_thresh: Optional[float] = Form(1.0, description="Floor placement for open door bg transformation"),
    windows_old: Optional[bool] = Form(False),
    super_resolution: Optional[bool] = Form(False),
    mutli_wall_process: Optional[bool] = Form(False),
    mirror_fill_url: Optional[str]=Form(None),
    trunk_floor_url: Optional[str] = Form(None,description="add if u want trunk  image with BG Specific floor"),
    trunk_wall_url: Optional[str] = Form(None,description="add if u want trunk  image  with BG Specific wall"),
    trunk_alpha:Optional[float] = Form(None,description="alpha values should be between 0 to 1 (it's used for overlay based bg's "),
    trunk_gamma: Optional[float] = Form(None,description="gamma values should be between 0 to 1 (it's used for overlay based bg's "),
    skip_preprocessing: bool = Form(False),
    mode: str = Form('', description="'wall' for wall replacement bgid"),
    banner_url: Optional[str] = Form(None, description="banner url"),
    skirting_url: Optional[str] = Form(None, description="wall skirting url"),
    dynamic_logo:  Optional[int] = Form(0, description="make this 1, if u want wall placement accroding to car tyre"),
    cut_wall_bottom: Optional[bool] = Form(False, description="cut wall from bottom, else cut from Top"),
    save_params: Json = Form(None, description="save params for overwriting replacebg save params"),
    response: Response = None
):      
    try:
        if wall_url is None:
            if wall_files is None:
                wall_url = None
            else:
                wall_url = genrate_url(wall_files)
        else:
            wall_url = check_urls(wall_url,'wall')
        if floor_url is None:
            if floor_files is None:
                floor_url = None
            else:
                floor_url = genrate_url(floor_files)
        else:
            floor_url = check_urls(floor_url,'floor')
        if glare_url is None:
            if glare_files is None:
                glare_url = None
            else:
                glare_url = genrate_url(glare_files)
        else:
            glare_url = check_urls(glare_url,'floor')
        
        if floor_ring_url is not None:
            floor_ring_url = check_urls(floor_ring_url,'floor_ring_url')
        elif floor_ring_url_files is not None:
            floor_ring_url = genrate_url(floor_ring_url_files)
        
        if int_background_color is not None and 'http' in int_background_color:
            int_background_color = check_urls(int_background_color,'int_background_color')
        elif int_background_url_files is not None:
            int_background_color = genrate_url(int_background_url_files)
        if mirror_fill_url is not None and 'http' in mirror_fill_url:
            mirror_fill_url = check_urls(mirror_fill_url,'mirror_fill_url')
        elif int_background_url_files is not None:
            int_background_color = genrate_url(int_background_url_files)
        if floor_base_url is not None:
            floor_base_url =check_urls(floor_base_url,'floor_base_url')
                
        def check_params(x):
            if x is None:
                return None
            x = json.loads(x)
            if isinstance(x,dict):
                return x
            else:
                try:
                    return int(x)
                except:
                    raise BaseExceptionError("plese check {x}")
                
        
        def check_parmas2(x,n=3):
            if x is None:
                return x
            if len(x.split('-'))!=n:
                return x
            return tuple([int(i.strip()) for i in x.split('-')])
                 
         
        member = check_username_password(username)
                
        new_data = {
            "bg_id": bg_id,
            "AI_Model": ai_model_names[AI_Model],
            "car_height": check_params(car_height), 
            "car_floor_spacing": check_params(car_floor_spacing),
            "shadow_intensity": shadow_intensity,
            "shadow_blur": shadow_blur,
            "shadow_len": shadow_len,
            "light_bg": light_bg,
            "ColorOnColor":ColorOnColor,
            "reflection_transparency": reflection_transparency,
            "wall_url": wall_url,
            "floor_url": floor_url,
            "alpha": alpha,
            "make_transparent": make_transparent,
            "add_shadow":add_shadow,
            "gamma": gamma,
            "floor_ring_url": floor_ring_url,
            "floor_base_url": floor_base_url,
            "logo_width": logo_width,
            "logo_x": logo_x,
            "logo_y": logo_y,
            "logo_shadow": logo_shadow,
            "logo_transparency": logo_transparency,
            "logo_blendmode": logo_blendmode,
            "logo_metallic": logo_metallic,
            "logo_metallic_depth": logo_metallic_depth,
            "logo_wall_dynamic":logo_wall_dynamic,
            "see_through_transparency": see_through_transparency,
            "ar43": ar43,
            "tilt_correction": tilt_correction,
            "output_zoom_percent": check_params(output_zoom_percent),
            "aspect_ratio": check_parmas2(aspect_ratio,2),
            "car_side_margin": check_params(car_side_margin),
            "dynamic_place": dynamic_place,
            "int_background_color":check_parmas2(int_background_color),
            "window_correction":window_correction,
            "numberplate_config":numberplate_config,
            "wall_logo_url":wall_logo_url,
            "Exposure_Correction":Exposure_Correction,
            "Color_Correction":Color_Correction,
            "tyre_floor_url": tyre_floor_url,
            "tyre_floor_alpha" :tyre_floor_alpha,
            "tyre_floor_gamma": tyre_floor_gamma,
            "glare_url":glare_url,
            "glare_intensity":glare_intensity,
            "front_angle_horizon_pct": front_angle_horizon_pct,
            "tyre_shadow_url":tyre_shadow_url,
            "crop_margin": check_params(crop_margin),
            "dynamic_preserve_wall": dynamic_preserve_wall,
            "tyre_horizon_offset": tyre_horizon_offset,
            "windows_old":windows_old,
            "mirror_fill_url":check_parmas2(mirror_fill_url),
            "studio_bg":studio_bg,
            "open_door_palcement_thresh":open_door_palcement_thresh,
            "super_resolution":super_resolution,
            "last_modified_by":member,
            "mutli_wall_process":mutli_wall_process,
            "last_modified_time":datetime.datetime.now(),
            "trunk_floor_url":trunk_floor_url,
            "trunk_wall_url":trunk_wall_url,
            "trunk_alpha" :trunk_alpha,
            "trunk_gamma" :trunk_gamma,
            "skip_preprocessing": skip_preprocessing,
            "skirting_size":skirting_size,
            "mode": mode,
            "banner_url": banner_url,
            "skirting_url":skirting_url,
            "dynamic_logo":dynamic_logo,
            "cut_wall_bottom":cut_wall_bottom,
            "save_params": save_params,
        }
        
        bginfo_obj = Bginfo.from_dict(new_data)
        bg_info = bginfo_obj.to_dict()
        bg_info = custom_jsonable_encoder(bg_info)
        message = bgbuilder_auto.add_bg_new(bg_info)

        return {
            "status": 200,
            "message": message         
        }
    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp


#######################################################################################################


@router.post("/automobile/bgbuilder/filter_config/")
def filter_automobile_bgbuilder(response: Response = None):
    try:
        data = bgbuilder_auto.filter_config()
        return custom_jsonable_encoder(data)
    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp


#######################################################################################################
@router.post("/automobile/bgbuilder/update/")
def update_automobile_bgbuilder(bg_id: str = Form(...),
                              data:Json = Form(...),
                              username:str = Form(...),
                              response: Response = None):
    try:
        old_data = bgbuilder_auto.get_info(bg_id)
        for key in data.keys():
            if key in ['created_by','last_modified_by','created_time','last_modified_time','bg_id']:
                continue
            old_data[key] = data[key]
        old_data['last_modified_by'] = check_username_password(username)
        if old_data.get("created_by",None) is None:
            old_data['created_by'] = check_username_password(username)
            old_data['created_time'] = datetime.datetime.now()
            old_data['last_modified_time'] = datetime.datetime.now()
        else:
            old_data['last_modified_time'] = datetime.datetime.now()
        old_data['bg_id'] = bg_id
        old_data.update({"assert_correct": True})
        bginfo_obj = Bginfo.from_dict(old_data)
        response = bgbuilder_auto.update_bg(bginfo_obj)
        return response
    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp


#######################################################################################################

@router.post("/automobile/bgbuilder/info/")
def info_automobile_bgbuilder(bg_id: str = Form(...),
                               response: Response = None):
    try:
        data = bgbuilder_auto.get_info(bg_id)
        return custom_jsonable_encoder(data)
    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp


#######################################################################################################

#######################################################################################################


@router.post("/automobile/bgbuilder/delete/")
def delete_automobile_bgbuilder(bg_id: str = Form(...),username:str = Form(...),
                               response: Response = None):
    try:
        check_username_password(username)
        data = bgbuilder_auto.delete_bg(bg_id)
        return data
    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp


#######################################################################################################


@router.post("/automobile/bgbuilder/bulk_update/")
def bulk_update_automobile_bgbuilder(bg_datas: Json = Form(...),
                              username:str = Form(...),
                              response: Response = None):
    try:
        username = check_username_password(username)
        message = bgbuilder_auto.bulk_update(bg_datas,username)
        return {
            "status": 200,
            "message": message         
        }

    except BaseExceptionError as e:
        resp = {"status": e.args[1], "message":e.args[0],"e":e.args[2]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    except Exception as e:
        sentry_sdk.capture_exception(e)
        resp = {
            "status": 500,
            "message": f"Something went wrong !! ({type(e)} | {e} | {e.args})",
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return resp
