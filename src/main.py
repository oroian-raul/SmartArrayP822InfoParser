from signal import signal, SIGINT
import argparse

from influx_exporter import InfluxExporter
from p822_info_parser import P822InfoParser


def handler(signal_received, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(0)


parser = argparse.ArgumentParser(description='Log parser for chia wallet')
parser.add_argument('--db_url', type=str, help='InfluxDB url. Only tested with InfuxDB V2'
                                               '(Example: http://192.168.50.189:8086)')
parser.add_argument('--db_token', type=str, help='InfluxDB token')
parser.add_argument('--db_organization', type=str, default="chia", required=False, help='InfluxDB organization')
parser.add_argument('--db_bucket', type=str, default="chia", required=False, help='InfluxDB bucket')
parser.add_argument('--parser_user', type=str, required=False, default="default_user",
                    help='Who is using this parser. Might be handy when more people save in the same database')
parser.add_argument('--sleep_interval', type=int, default=600, required=False,
                    help='sleep interval in seconds between commands')
parser.add_argument('--path_to_cli', type=str, required=True,
                    help='path to CLI executable (C:\\Program Files\\Compaq\\Hpacucli\\Bin)')
parser.add_argument('--dry_run', type=str, default=False, required=False,
                    help='If set to True data will not be saved to Database. Used for debugging.')

if __name__ == "__main__":
    args = parser.parse_args()
    signal(SIGINT, handler)

    harvesters_name_mapping = {}
    parser = P822InfoParser(parser_user=args.parser_user,
                            sleep_interval=args.sleep_interval,
                            path_to_cli=args.path_to_cli,
                            dry_run=args.dry_run == "True" or args.dry_run == "true",
                            data_exporter=InfluxExporter(database_address=args.db_url,
                                                         bucket=args.db_bucket,
                                                         org=args.db_organization,
                                                         token=args.db_token))
