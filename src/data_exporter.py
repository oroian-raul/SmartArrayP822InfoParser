from collections import namedtuple


class DataExporter:
    PhysicalDriveInfo = namedtuple("PhysicalDriveInfo",
                                   ["user_name", "ip", "slot", "array", "drive", "port", "box", "bay", "size",
                                    "rotational_speed", "phy_count", "phy_transfer_rate", "current_temp", "max_temp"])

    def __init__(self, database_address: str, bucket: str, org: str, token: str):
        raise NotImplementedError('Not implemented')

    def export_physical_drive_info(self, data: PhysicalDriveInfo):
        raise NotImplementedError('Not implemented')
