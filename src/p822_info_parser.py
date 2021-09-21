import socket
from subprocess import check_output
from time import sleep

from data_exporter import DataExporter


class P822InfoParser:

    def __init__(self, parser_user: str,
                 dry_run: bool,
                 sleep_interval: int,
                 path_to_cli,
                 data_exporter: DataExporter):
        self.data_exporter = data_exporter
        self.parser_user = parser_user
        self.dry_run = dry_run
        self.sleep_interval = sleep_interval
        self.path_to_cli = path_to_cli

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        self.local_ip_address = s.getsockname()[0]

        self.start()

    @staticmethod
    def run_command(command: str, arguments: str):
        output = None

        try:
            output = check_output([command, arguments], shell=True).decode()
        except Exception as e:
            print(str(e))
            #

        return output.splitlines() if output else None

    @staticmethod
    def get_info_value(info: str, separator=" "):
        value_index_start = info.find(separator)
        if value_index_start == -1:
            return None

        value_index_start += len(separator) + 1

        value_index_end = info.find(" ", value_index_start)
        if value_index_end == -1:
            value_index_end = len(info)
        return info[value_index_start: value_index_end]

    def get_controllers_slots(self):
        controllers_str_list = self.run_command(f"{self.path_to_cli}\\hpacucli.exe", "controller all show")
        controllers_slots = []

        for item in controllers_str_list:
            if "in Slot" not in item:
                continue

            controllers_slots.append(self.get_info_value(item, "Slot"))

        return controllers_slots

    def get_controller_arrays(self, slot):
        arrays = []
        arrays_str_list = self.run_command(f"{self.path_to_cli}\\hpacucli.exe",
                                           f"controller slot={slot} array all show")

        for item in arrays_str_list:
            if "array" not in item:
                continue

            arrays.append(self.get_info_value(item, "array"))

        return arrays

    def get_drives_for_array(self, slot, array):
        physical_drives = []
        drives_list_str = self.run_command(f"{self.path_to_cli}\\hpacucli.exe",
                                           f"controller slot={slot} array {array} physicaldrive all show")

        for item in drives_list_str:
            if "physicaldrive" not in item:
                continue

            physical_drives.append(self.get_info_value(item, "physicaldrive"))

        return physical_drives

    def get_drive_info(self, slot, array, drive):
        drive_info_list_str = self.run_command(f"{self.path_to_cli}\\hpacucli.exe",
                                               f"controller slot={slot} array {array} physicaldrive {drive} show")
        data = {}
        for item in drive_info_list_str:
            if "Box" in item:
                data["box"] = int(self.get_info_value(item, ":"))
            elif "Port" in item:
                data["port"] = self.get_info_value(item, ":")
            elif "Bay" in item:
                data["bay"] = int(self.get_info_value(item, ":"))
            elif "Size" in item:
                data["size"] = float(self.get_info_value(item, ":"))
            elif "Rotational Speed" in item:
                data["rotational_speed"] = int(self.get_info_value(item, ":"))
            elif "Current Temperature" in item:
                data["current_temp"] = int(self.get_info_value(item, ":"))
            elif "Maximum Temperature" in item:
                data["max_temp"] = int(self.get_info_value(item, ":"))
            elif "PHY Count" in item:
                data["phy_count"] = int(self.get_info_value(item, ":"))
            elif "PHY Transfer Rate" in item:
                data["phy_transfer_rate"] = self.get_info_value(item, ":")

        data["user_name"] = self.parser_user
        data["ip"] = self.local_ip_address
        data["slot"] = slot
        data["array"] = array
        data["drive"] = drive

        return DataExporter.PhysicalDriveInfo(**data)

    def export_controler_info(self):
        # get controllers
        drive_info = []
        for slot in self.get_controllers_slots():
            for array in self.get_controller_arrays(slot):
                for drive in self.get_drives_for_array(slot, array):
                    drive_info.append(self.get_drive_info(slot, array, drive))

        print(drive_info)
        self.data_exporter.export_physical_drive_info(drive_info)

    def start(self):
        while True:
            self.export_controler_info()
            sleep(self.sleep_interval)
