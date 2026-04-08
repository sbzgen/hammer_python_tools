import os
import io
import sys
import argparse
import hashlib

parser = argparse.ArgumentParser()

parser.add_argument("-cf", "--content_for", required = True, help = "content folder to remove redundant files from")
parser.add_argument("-ca", "--content_against", required = True, help = "content folder to pull models from (ie: 'custom' when folder structure is 'custom/models')")

def main():
    args = parser.parse_args()
    content_for = os.path.normpath(args.content_for)
    content_against = os.path.normpath(args.content_against)

    if not os.path.exists(content_for):
        print(f"{content_for} doesn't exist.\nExiting...")
        sys.exit(-1)

    if not os.path.exists(content_against):
        print(f"{content_against} doesn't exist.\nExiting...")
        sys.exit(-1)

    remove_count = 0

    for dir_path, _, files in os.walk(args.content_for):
        for file_path in files:
            for_path = os.path.join(dir_path, file_path)
            against_path = os.path.join(content_against, os.path.relpath(os.path.join(dir_path, file_path), content_for))

            if not os.path.exists(against_path):
                continue

            with io.open(for_path, "rb") as file:
                for_hash = hashlib.sha256(file.read()).hexdigest()

            with io.open(against_path, "rb") as file:
                against_hash = hashlib.sha256(file.read()).hexdigest()

            if for_hash == against_hash:
                print(f"{for_path} matches {against_path}, removing file...")
                os.remove(for_path)
                remove_count += 1

    print(f"Finished removing '{remove_count}' redundant files.\nExiting...")

if __name__ == "__main__":
    main()