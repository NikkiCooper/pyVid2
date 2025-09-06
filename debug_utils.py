# debug_utils.py
import inspect

def debug(*args):
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)  
    print(f"{info.filename}, line {info.lineno}, in {info.function}: ", *args)
    