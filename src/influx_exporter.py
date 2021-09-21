from datetime import datetime
import traceback

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from data_exporter import DataExporter


class InfluxExporter(DataExporter):
    def __init__(self, database_address: str, bucket: str, org: str, token: str):
        self.db_client = InfluxDBClient(url=database_address, token=token, retries=0)
        self.write_api = self.db_client.write_api(write_options=ASYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def write(self, data):
        try:
            self.write_api.write(self.bucket, self.org, data)
        except:
            print(traceback.format_exc())

    def export_physical_drive_info(self, data: [DataExporter.PhysicalDriveInfo]):
        points = []
        for item in data:
            points.append(Point("physical_drive_info")
                          .tag("user_name", item.user_name)
                          .tag("ip", item.ip)
                          .tag("slot", item.slot)
                          .tag("array", item.array)
                          .tag("drive", item.drive)
                          .tag("port", item.port)
                          .tag("box", item.box)
                          .tag("bay", item.bay)
                          .field("size", item.size)
                          .field("rotational_speed", item.rotational_speed)
                          .field("phy_count", item.phy_count)
                          .field("phy_transfer_rate", item.phy_transfer_rate)
                          .field("current_temp", item.current_temp)
                          .field("max_temp", item.max_temp)
                          .time(datetime.utcnow(), WritePrecision.NS))

        self.write(points)
