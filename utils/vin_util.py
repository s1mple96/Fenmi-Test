from utils.vin_recent_spider import get_recent_vins

def get_vin_list():
    return get_recent_vins(save_file=False)

def get_next_vin(vin_index=0):
    vin_list = get_vin_list()
    if vin_list:
        vin = vin_list[vin_index % len(vin_list)]
        return vin, vin_index + 1
    return '', vin_index 