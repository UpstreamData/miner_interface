import asyncio
import ipaddress
import time

from API import APIError
from cfg_util.func.parse_data import safe_parse_api_data
from cfg_util.func.ui import update_ui_with_data, update_prog_bar, set_progress_bar_len
from cfg_util.layout import window
from cfg_util.miner_factory import miner_factory
from config.bos import bos_config_convert
from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS


async def import_config(idx):
    await update_ui_with_data("status", "Importing")
    miner = await miner_factory.get_miner(ipaddress.ip_address(window["ip_table"].Values[idx[0]][0]))
    await miner.get_config()
    config = miner.config
    await update_ui_with_data("config", str(config))
    await update_ui_with_data("status", "")


async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("hr_total", "")
    window["ip_table"].update([])
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    await set_progress_bar_len(2 * network_size)
    progress_bar_len = 0
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
            # can output "Identifying" for each found item, but it gets a bit cluttered
            # and could possibly be confusing for the end user because of timing on
            # adding the IPs
            # window["ip_table"].update([["Identifying...", "", "", "", ""] for miner in miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = miner_factory.get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip), "", "", "", ""] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("ip_count", str(len(all_miners)))
    await update_ui_with_data("status", "")


async def miner_light(ips: list):
    await asyncio.gather(*[flip_light(ip) for ip in ips])


async def flip_light(ip):
    ip_list = window['ip_table'].Widget
    miner = await miner_factory.get_miner(ip)
    index = [item[0] for item in window["ip_table"].Values].index(ip)
    index_tags = ip_list.item(index)['tags']
    if "light" not in index_tags:
        ip_list.item(index, tags=([*index_tags, "light"]))
        window['ip_table'].update(row_colors=[(index, "white", "red")])
        await miner.fault_light_on()
    else:
        index_tags.remove("light")
        ip_list.item(index, tags=index_tags)
        window['ip_table'].update(row_colors=[(index, "black", "white")])
        await miner.fault_light_off()


async def send_config_generator(miners: list, config):
    loop = asyncio.get_event_loop()
    config_tasks = []
    for miner in miners:
        if len(config_tasks) >= CONFIG_THREADS:
            configured = asyncio.as_completed(config_tasks)
            config_tasks = []
            for sent_config in configured:
                yield await sent_config
        config_tasks.append(loop.create_task(miner.send_config(config)))
    configured = asyncio.as_completed(config_tasks)
    for sent_config in configured:
        yield await sent_config


async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    await set_progress_bar_len(2 * len(ips))
    progress_bar_len = 0
    get_miner_genenerator = miner_factory.get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    config_sender_generator = send_config_generator(all_miners, config)
    async for _config_sender in config_sender_generator:
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "")


async def get_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    if len(ips) == 0:
        ips = [ipaddress.ip_address(ip) for ip in [item[0] for item in window["ip_table"].Values]]
    await set_progress_bar_len(len(ips))
    progress_bar_len = 0
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in ips])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            ip_table_data[ip_table_index] = [
                data_point["IP"], data_point["host"], str(data_point['TH/s']) + " TH/s", data_point["temp"], data_point['user'], str(data_point['wattage']) + " W"
            ]
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    hashrate_list = [float(item[2].replace(" TH/s", "")) for item in window["ip_table"].Values if not item[2] == '']
    total_hr = round(sum(hashrate_list), 2)
    window["hr_total"].update(f"{total_hr} TH/s")

    await update_ui_with_data("status", "")


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await miner_factory.get_miner(ip)
    try:
        miner_data = await miner.api.multicommand("summary", "devs",  "temps", "tunerstatus", "pools")
    except APIError:
        return {'TH/s': "Unknown", 'IP': str(miner.ip), 'host': "Unknown", 'user': "Unknown", 'wattage': 0}
    host = await miner.get_hostname()

    if "summary" in miner_data.keys():
        if 'MHS 5s' in miner_data['summary'][0]['SUMMARY'][0].keys():
            th5s = round(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'MHS 5s') / 1000000, 2)
        elif 'GHS 5s' in miner_data['summary'][0]['SUMMARY'][0].keys():
            if not miner_data['summary'][0]['SUMMARY'][0]['GHS 5s'] == "":
                th5s = round(float(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'GHS 5s')) / 1000,
                             2)
            else:
                th5s = 0
        else:
            th5s = 0
    else:
        th5s = 0
    temps = 0

    if "temps" in miner_data.keys() and not miner_data["temps"][0]['TEMPS'] == []:
        if "Chip" in miner_data["temps"][0]['TEMPS'][0].keys():
            for board in miner_data["temps"][0]['TEMPS']:
                if board["Chip"] is not None and not board["Chip"] == 0.0:
                    temps = board["Chip"]

    elif "devs" in miner_data.keys() and not miner_data["devs"][0]['DEVS'] == []:
        if "Chip Temp Avg" in miner_data["devs"][0]['DEVS'][0].keys():
            for board in miner_data["devs"][0]['DEVS']:
                if board['Chip Temp Avg'] is not None and not board['Chip Temp Avg'] == 0.0:
                    temps = board['Chip Temp Avg']

    if "pools" not in miner_data.keys():
        user = "?"
    elif not miner_data['pools'][0]['POOLS'] == []:
        user = await safe_parse_api_data(miner_data, 'pools', 0, 'POOLS', 0, 'User')
    else:
        user = "Blank"

    if "tunerstatus" in miner_data.keys():
        wattage = await safe_parse_api_data(miner_data, "tunerstatus", 0, 'TUNERSTATUS', 0, "PowerLimit")
        # data['tunerstatus'][0]['TUNERSTATUS'][0]['PowerLimit']
    elif "Power" in miner_data["summary"][0]["SUMMARY"][0].keys():
        wattage = await safe_parse_api_data(miner_data, "summary", 0, 'SUMMARY', 0, "Power")
    else:
        wattage = 0

    return {'TH/s': th5s, 'IP': str(miner.ip), 'temp': round(temps), 'host': host, 'user': user, 'wattage': wattage}


async def generate_config(username, workername, v2_allowed):
    if username and workername:
        user = f"{username}.{workername}"
    elif username and not workername:
        user = username
    else:
        return

    if v2_allowed:
        url_1 = 'stratum2+tcp://v2.us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt'
        url_2 = 'stratum2+tcp://v2.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt'
        url_3 = 'stratum+tcp://stratum.slushpool.com:3333'
    else:
        url_1 = 'stratum+tcp://ca.stratum.slushpool.com:3333'
        url_2 = 'stratum+tcp://us-east.stratum.slushpool.com:3333'
        url_3 = 'stratum+tcp://stratum.slushpool.com:3333'

    config = {'group': [{
        'name': 'group',
        'quota': 1,
        'pool': [{
            'url': url_1,
            'user': user,
            'password': '123'
        }, {
            'url': url_2,
            'user': user,
            'password': '123'
        }, {
            'url': url_3,
            'user': user,
            'password': '123'
        }]
    }],
        'format': {
            'version': '1.2+',
            'model': 'Antminer S9',
            'generator': 'upstream_config_util',
            'timestamp': int(time.time())
        },
        'temp_control': {
            'target_temp': 80.0,
            'hot_temp': 90.0,
            'dangerous_temp': 120.0
        },
        'autotuning': {
            'enabled': True,
            'psu_power_limit': 900
        }
    }
    window['config'].update(await bos_config_convert(config))
