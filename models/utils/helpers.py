import json
import os
import pairs
import threading

def round_to_minprice(pair: str, price: float):
    price_decimals = pairs.get_price_decimals(pair)
    return round(price, price_decimals)

def round_to_minqty(pair: str, qty: float):
    qty_decimals = pairs.get_qty_decimals(pair)
    first_try = round(qty, qty_decimals)
    if first_try * (10 ** qty_decimals) % 2 == 0:
        return first_try
    else:
        return first_try + 10**-qty_decimals
    
def run_on_thread(worker, args={}): 
    t = threading.Thread(target=worker, kwargs=args)
    t.start()
    return t

def get_param(pair: str, param: str):
    script_dir_path = os.path.dirname(os.path.abspath(__file__))
    params_file_path = os.path.join(script_dir_path, "..", "..", 'params.json')
    try:
        with open(params_file_path, "r", encoding="utf-8") as file:
            params = json.load(file)
            return params[pair][param]
    except FileNotFoundError: return exit(1)
    except json.JSONDecodeError: return exit(1)

def get_root_path(path: str):
    parts = path.split("/")
    path  = os.path.join(*parts)
    root_dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root_dir_path, path)

def create_file_if_not_exists(rel_filepath: str, default: dict):
    full_filepath = get_root_path(rel_filepath)
    if not os.path.exists(full_filepath):
        with open(full_filepath, "w") as file:
            file.write(json.dumps(default, indent=4))

def get_dict_from_file(rel_filepath: str):
    full_filepath = get_root_path(rel_filepath)
    try:
        with open(full_filepath, "r+") as file:
            return json.loads(file.read())
    except FileNotFoundError: return exit(1)
    except json.JSONDecodeError: return exit(1)

def file_rewrite_dict(rel_filepath: str, data: dict):
    full_filepath = get_root_path(rel_filepath)
    with open(full_filepath, "w") as file:
        file.write(json.dumps(data, indent=4))

def price_offset(pair: str, base_price: float, offset_perc: float):
    price = (1.0 + offset_perc/100.0) * base_price
    return round_to_minprice(pair, price)
