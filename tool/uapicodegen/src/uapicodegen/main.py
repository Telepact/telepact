import argparse


def main() -> None:
    # Add your CLI logic here
    parser = argparse.ArgumentParser(description='My Python CLI App')
    parser.add_argument('input', help='Input argument')
    args = parser.parse_args()

    # Example functionality
    print(f"Input argument: {args.input}")


if __name__ == '__main__':
    main()
