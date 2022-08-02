import os
from synology_dsm import SynologyDSM, exceptions
from prometheus_client import start_http_server, Gauge, Info, Enum
from time import sleep

prometheus_prefix = "syno"


def require_environmental_variable(variable_name):
    if variable_name not in os.environ.keys():
        print('Variable {} missing.'.format(variable_name))
        exit(1)
    return os.environ[variable_name]


def metric(_name):
    return "{}_{}".format(prometheus_prefix, _name)


def set_static_info(api):
    model = str(api.information.model)
    amount_of_ram = str(api.information.ram)
    serial_number = str(api.information.serial)
    dsm_version = str(api.information.version_string)

    Info(metric("model_metadata"), "Model metadata").info({
        "model": model,
        "amount_of_ram": amount_of_ram,
        "serial_number": serial_number,
        "dsm_version": dsm_version
    })


def general_info(api, temp_gauge, uptime_gauge, cpu_gauge):
    temperature = str(api.information.temperature)
    uptime = str(api.information.uptime)
    cpu_load = api.utilisation.cpu_total_load

    if cpu_load:
        cpu_gauge.set(cpu_load)
    temp_gauge.set(temperature)

    uptime_gauge.set(uptime)



def stats(api, memory_used_gauge, memory_total_gauge, network_up_gauge, network_down_gauge,
    volume_status_enum, volume_size_gauge, volume_size_used_gauge,
    s_status_enum, status_enum, disk_name_info, disk_temp_gauge
):
    memory_use_percentage = int(api.utilisation.memory_real_usage)
    memory_total = api.utilisation.memory_size(human_readable=False)
    memory_total_used = (memory_use_percentage / 100) * memory_total

    memory_used_gauge.set(memory_total_used)
    memory_total_gauge.set(memory_total)

    network_up = api.utilisation.network_up(human_readable=False)
    network_down = api.utilisation.network_down(human_readable=False)

    network_up_gauge.set(network_up)
    network_down_gauge.set(network_down)

    for volume_id in api.storage.volumes_ids:
        volume_status = str(api.storage.volume_status(volume_id))
        volume_status_enum.labels(volume_id).state(volume_status)

        volume_size_used = str(api.storage.volume_size_used(volume_id, human_readable=False))
        volume_size_used_gauge.labels(volume_id).set(volume_size_used)

        volume_size_total = str(api.storage.volume_size_total(volume_id, human_readable=False))
        volume_size_gauge.labels(volume_id).set(volume_size_total)

    for disk_id in api.storage.disks_ids:
        disk_name = str(api.storage.disk_name(disk_id))
        disk_name_info.labels(disk_id, disk_name).info({"disk_name": disk_name})

        smart_status = str(api.storage.disk_smart_status(disk_id))
        s_status_enum.labels(disk_id, disk_name).state(smart_status)

        status = str(api.storage.disk_status(disk_id))
        status_enum.labels(disk_id, disk_name).state(status)

        disk_temp = api.storage.disk_temp(disk_id)
        disk_temp_gauge.labels(disk_id, disk_name).set(disk_temp)


if __name__ == '__main__':
    url = require_environmental_variable('SYNOLOGY_URL')
    port = require_environmental_variable('SYNOLOGY_PORT')
    usr = require_environmental_variable('SYNOLOGY_USER')
    password = require_environmental_variable('SYNOLOGY_PASSWORD')
    https = os.getenv('SYNOLOGY_HTTPS', 'false').lower() in ('true', '1')
    verify = os.getenv('SYNOLOGY_VERIFY_SSL', 'false').lower() in ('true', '1')
    frequency = int(os.getenv('FREQUENCY', 15))

    api = SynologyDSM(url, port, usr, password, use_https=https, verify_ssl=verify, timeout=60)

    start_http_server(9999)
    set_static_info(api)

    temp_gauge = Gauge(metric("temperature"), "Temperature")
    uptime_gauge = Gauge(metric("uptime"), "Uptime")
    cpu_gauge = Gauge(metric("cpu_load"), "DSM version")

    memory_used_gauge = Gauge(metric("memory_used"), "Total memory used")
    memory_total_gauge = Gauge(metric("memory_total"), "Total memory")

    network_up_gauge = Gauge(metric("network_up"), "Network up")
    network_down_gauge = Gauge(metric("network_down"), "Network down")

    volume_status_enum = Enum(metric("volume_status"), "Status of volume", labelnames=["Volume_ID"], states=["normal"])
    volume_size_gauge = Gauge(metric("volume_size"), "Size of volume", ["Volume_ID"])
    volume_size_used_gauge = Gauge(metric("volume_size_used"), "Used size of volume", ["Volume_ID"])

    s_status_enum = Enum(metric("disk_smart_status"), "Smart status about disk", labelnames=["Disk_ID", "Disk_name"], states=["normal"])
    status_enum = Enum(metric("disk_status"), "Status about disk", labelnames=["Disk_ID","Disk_name"], states=["normal"])
    disk_name_info = Info(metric("disk_status"), "Name of disk", ["Disk_ID", "Disk_name"])
    disk_temp_gauge = Gauge(metric("disk_temp"), "Temperature of disk", ["Disk_ID", "Disk_name"])

    while True:
        try:
            api.utilisation.update()
            api.information.update()
            api.storage.update()
            api.share.update()

        except exceptions.SynologyDSMRequestException as e:
            print( "The Module couldn't reach the Synology API:" )
            print(e)
            exit(1)

        general_info(api, temp_gauge, uptime_gauge, cpu_gauge)
        stats(
            api, memory_used_gauge, memory_total_gauge, network_up_gauge, network_down_gauge,
            volume_status_enum, volume_size_gauge, volume_size_used_gauge,
            s_status_enum, status_enum, disk_name_info, disk_temp_gauge
        )
        sleep(frequency)
