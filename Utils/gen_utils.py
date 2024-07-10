# import asyncio
import io
import urllib.request
from functools import wraps

import cv2
import httpx
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from Utils.error_template import BaseExceptionError

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


# def request_concurrency_limit_decorator(limit=10):
#     sem = asyncio.Semaphore(limit)

#     def executor(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             async with sem:
#                 return await func(*args, **kwargs)

#         return wrapper

#     return executor


def cv2_resize(img: np.ndarray, size: tuple) -> np.ndarray:
    """description:resize image
    param:
        img: np.array
        size: tuple(int,int)
    return:
        image: np.array
    """
    H = img.shape[0]
    if size[1] > H:
        img = cv2.resize(img, size, interpolation=cv2.INTER_CUBIC)
    else:
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    return img


# @request_concurrency_limit_decorator(10)
# async def download_image(url) -> np.ndarray:
#     """description:download image from url
#     param:
#         url: str
#     return:
#         image: np.array
#     """
#     if not url.startswith(("http", "https")):
#         raise BaseExceptionError("plese check url")
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             # img = misc.imread(response.content)
#             img = Image.open(io.BytesIO(await response.aread()))
#             img = ImageOps.exif_transpose(img)
#             img = palette_correct_pil(img)
#             return np.array(img)
#     except UnidentifiedImageError:
#         try:
#             resp = urllib.request.urlopen(url)
#             img = Image.open(resp)
#             img = ImageOps.exif_transpose(img)
#             img = palette_correct_pil(img)
#         except Exception as e:
#             raise BaseExceptionError("url is accessible", error_code=403, e=e)

#         return np.array(img)


def color_change(img: np.ndarray) -> np.ndarray:
    """description:return color chnage rgb or RGBA
    param:
        img: np.array
    return:
        image: np.array
    """
    if len(img.shape) == 2:
        return img
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def palette_correct_pil(img: Image.Image) -> Image.Image:
    """description:palette correct image
    param:
        img: Image.Image
    return:
        image: Image.Image
    """
    if img.mode == "P":
        if (np.array(img.convert("RGBA"))[:, :, 3] == 255).all():
            return img.convert("RGB")
        else:
            return img.convert("RGBA")
    else:
        return img


def crop_out(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """description:crop out image

    Args:
        img: np.ndarray
        x: int
        y: int
        w: int
        h: int

    Returns:
        np.ndarray: image
    """
    return img[y : y + h, x : x + w]


def get_bbox(bg_mask):
    """
    Gives bbox in (x,y,w,h) format
    Input: bg_mask: np.ndarray
    Output: bbox: tuple(int)
    """

    if len(bg_mask.shape) == 3:
        mask = bg_mask[..., -1]
    else:
        mask = bg_mask
    x, y, w, h = cv2.boundingRect(mask)
    return x, y, w, h


def get_bbox_pil(mask):
    """
    Gives bbox in (x,y,w,h) format
    Input: mask: PIL.Image
    Output: bbox: tuple(int)
    """

    box = mask.getbbox()
    x, y = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    return x, y, w, h


def crop_out_pil(img, x, y, w, h):
    """discription:crop out image PIL

    Args:
        img: np.ndarray
        x: int
        y: int
        w: int
        h: int

    Returns:
        np.ndarray: image
    """
    cropped_img = img.crop((x, y, x + w, y + h))
    return cropped_img


def resize_ar_height(img_arr: np.ndarray, height: int) -> np.ndarray:
    """discription:resize image to height

    Args:
        img_arr (np.ndarray): _description_
        height (int): _description_

    Returns:
        _type_: _description_
    """
    h, w, _ = img_arr.shape
    width = height * w / h
    img_arr = cv2_resize(img_arr, (int(width), int(height)))
    return img_arr


def resize_ar_width(img_arr: np.ndarray, width: int) -> np.ndarray:
    """discription:resize image to width

    Args:
        img_arr (np.ndarray): _description_
        width (int): _description_

    Returns:
        np.ndarray: _description_
    """
    h, w, _ = img_arr.shape
    height = width * (h / w)
    img_arr = cv2_resize(img_arr, (int(width), int(height)))
    return img_arr


def horizontal_pad(img: np.ndarray, W: int, H: int, color: tuple = (255, 255, 255)) -> np.ndarray:
    """discription:horizontal pad image

    Args:
        img (np.ndarray): _description_
        W (int): _description_
        H (int): _description_
        color (tuple, optional): _description_. Defaults to (255,255,255).

    Returns:
        np.ndarray: _description_
    """
    h, w, _ = img.shape
    if W != w:
        scale = W / w
        if (scale * h) > H:
            scale = H / h
        img = cv2_resize(img, (int(scale * w), int(scale * h)))
    h_pad = abs(H - img.shape[0]) // 2
    w_pad = abs(W - img.shape[1]) // 2
    img = cv2.copyMakeBorder(img, h_pad, h_pad, w_pad, w_pad, cv2.BORDER_CONSTANT, value=color)
    return img


def vertical_pad(img: np.ndarray, W: int, H: int, color: tuple = (255, 255, 255)) -> np.ndarray:
    """discription:horizontal pad image

    Args:
        img (np.ndarray): _description_
        W (int): _description_
        H (int): _description_
        color (tuple, optional): _description_. Defaults to (255,255,255).

    Returns:
        np.ndarray: _description_
    """
    h, w, _ = img.shape
    if H != h:
        scale = H / h
        if (scale * w) > W:
            scale = W / w
        img = cv2_resize(img, (int(scale * w), int(scale * h)))
    h_pad = abs(H - img.shape[0]) // 2
    w_pad = abs(W - img.shape[1]) // 2
    img = cv2.copyMakeBorder(img, h_pad, h_pad, w_pad, w_pad, cv2.BORDER_CONSTANT, value=color)
    return img


def resize_func(img: np.ndarray, save_params: dict) -> np.ndarray:
    """resize img as per save_params
    if height and width is given then resize image to height or width
    if pad is true then pad image to height and width
    pad_preference is horizontal or vertical

    Args:
        img (np.ndarray): _description_
        save_params (dict): _description_

    Returns:
        np.ndarray: _description_
    """
    if save_params.get("height", False) and not save_params.get("pad", False):
        return resize_ar_height(img, save_params["height"])
    elif save_params.get("width", False) and not save_params.get("pad", False):
        return resize_ar_width(img, save_params["width"])
    elif (
        save_params.get("pad", False)
        and save_params.get("height", False)
        and save_params.get("width", False)
        and save_params.get("padding_preference", False)
        and save_params.get("padding_color", False)
    ):
        if save_params["padding_preference"] == "horizontal":
            return horizontal_pad(img, save_params["width"], save_params["height"], save_params["padding_color"])
        else:
            return vertical_pad(img, save_params["width"], save_params["height"], save_params["padding_color"])
    else:
        return img
