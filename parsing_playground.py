import argparse

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="learn to parse!")
    parser.add_argument("-la", "--list_a", type=str, nargs='+', help="a varible list of strings")
    parser.add_argument("-lb", "--list_b", type=str, nargs='+', help="a varible list of strings")
    args = parser.parse_args()

    print(args.list_a)
    print(args.list_b)
