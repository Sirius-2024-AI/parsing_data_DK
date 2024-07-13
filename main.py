from parsing_and_data.all_def import *
import argparse
from multiprocessing import *

parser = argparse.ArgumentParser(
                    prog='parsing data about flat',
                    description='parse data from domclick to DB',
                    epilog='see README')

parser.add_argument('--file', help='name of file to save data')
parser.add_argument('--town', help='str city name')
args = parser.parse_args()

f = open(args.town, 'r', encoding="utf-8")
f = list(f.read().split(","))


if __name__ == '__main__':
    processes = []
    for i in f:
        process = Process(target=main_parser_fn, args=(get_guid_region(i), args.file, ))
        processes.append(process)
        process.start()

    # Wait jobs done
    for process in processes:
        process.join()