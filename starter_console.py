from address_converter.converter import Converter
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
Address string parser
    Returns a list of separated values into output file:
    [<input text>];[<resulting formatted address>];<ID address objects>...''')

    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('--showinput', '--si', default=0, choices=[0, 1],
                        type=int, help='return <input text>',
                        dest='show_input')
    parser.add_argument('--showaddress', '--sa', default=0, choices=[0, 1],
                        help='return <resulting formatted address>',
                        type=int, dest='show_address')
    parser.add_argument('--checkgramm', '--gr', default=0, choices=[0, 1],
                        help='check grammar',
                        type=int, dest='check_grammar')
    parser.add_argument('--errorlog', '--el', default=0, choices=[0, 1],
                        help='write the error log',
                        type=int, dest='write_error_log')
    args = parser.parse_args()

    with Converter(write_error_log=args.write_error_log) as converter:
        for input_str in args.infile:
            address_list = converter.convert(
                address=input_str,
                is_check_grammar=args.check_grammar)
            for address in address_list:
                result = []
                if args.show_input:
                    result.append(input_str[:-1])
                if args.show_address:
                    result.append(address.calc_address_string())
                result.extend([addrobj.aoguid for addrobj
                               in address.addr_path])
                args.outfile.write(';'.join(result) + '\n')
                args.outfile.flush()


if __name__ == "__main__":
    main()
