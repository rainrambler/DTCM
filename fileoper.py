import errno
import io
import os


def write_text_file(filename: str, content: str):
    try:
        # print(f"Writing to file: {filename}...")
        file_handle = io.open(filename, "w")
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
    else:
        with open(filename, encoding="utf-8", mode="w+") as file_obj:
            file_obj.write(content)


def file_exists(filename: str) -> bool:
    """Check file exists"""
    if not os.path.exists(filename):
        return False
    return os.path.isfile(filename)


def read_text_file(file_name: str) -> str:
    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()
        return content


def get_signed_name(filename: str) -> str:
    pure, _ = os.path.splitext(filename)
    return pure + "_signed.json"


def get_signed_vp(filename: str) -> str:
    pure, _ = os.path.splitext(filename)
    return pure + "_vp.json"
