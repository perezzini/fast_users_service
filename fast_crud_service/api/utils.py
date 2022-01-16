from ast import literal_eval

from fast_users_service.api.rest.models import ImageRes


def translate_image_res(res: ImageRes) -> str:
    """Convert dictionary of image resolution
    into a pair of strings

    Args:
        res (ImageRes): An ImageRes object

    Returns:
        str: A string pair (height, width)
    """
    return str(res)


def from_str_to_image_res(res: str) -> ImageRes:
    """Convert a string pair of image resolution
    into a ImageRes object

    Args:
        res (str): A str pair representing an
        image resolution

    Returns:
        ImageRes: An ImageRes object
    """
    res = res.replace(" ", "").replace("),(", ") (")
    res = literal_eval(res)

    return ImageRes(height=res[0], width=res[1])
