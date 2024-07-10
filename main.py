from parsing_and_data.paring_data.all_def import *
import argparse

parser = argparse.ArgumentParser(
                    prog='parsing data about flat',
                    description='parse data from domclick to DB',
                    epilog='see README')

#parser.add_argument('--dbname', help='name of postgres database (need to connect)')
#parser.add_argument('--tablename', help='database table name')
#parser.add_argument('--dbuser', help='user of postgres database (need to connect)')
#parser.add_argument('--dbpaswd', help='paswd of postgres database (need to connect)')
#parser.add_argument('--dbhost', help='host of postgres database (need to connect)')
#parser.add_argument('--dbport', help='port of postgres database (need to connect)')
parser.add_argument('--file', help='name of file to save data')
parser.add_argument('--town', help='str city name')
args = parser.parse_args()
#if args.city is None:
#        main_parser_fn(get_guid_of_regione(args.town), str(args.dbname), str(args.dbuser), str(args.dbpaswd), str(args.dbhost), int(args.dbport), str(args.tablename))
        #print("Finish parsing: {args.town}")
#else:
f = open(args.town, 'r', encoding="utf-8")
f = list(f.read().split(","))
#        for i in f:
#            print(i)
#            main_parser_fn(get_guid_of_regione(i), str(args.dbname), str(args.dbuser), str(args.dbpaswd), str(args.dbhost), int(args.dbport), str(args.tablename))
            #print("Finish parsing: {i}")

if __name__ == '__main__':
    processes = []
    for i in f:
        process = Process(target=main_parser_fn, args=(get_guid_of_regione(i), args.file, ))
        processes.append(process)
        process.start()

    # Wait jobs done
    for process in processes:
        process.join()