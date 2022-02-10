import os
import sys
import csv
import json
from random import randrange
from shutil import copy
import argparse

METADATA_CSV = 'metadata.csv'
METADATA_TEMPLATE = 'metadata-template.json'
ASSET_DIR = './assets'
TARGET_DIR = './target'
LIMIT = 0

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def generate(args):
    limit = args.limit

    if not os.path.exists(args.metadata_csv):
        exit('The metadata csv file does not exist.')

    with open(args.metadata_csv, newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        metadata_list = []
        for row in csvreader:
            metadata_list.append(row)

        if len(metadata_list) <= 0:
            exit('The metadata csv file is empty.')

        trait_types = metadata_list.pop(0) # First row is header
        trait_types.pop(0) # Remove first column 'File Name'
        trait_type_count = len(trait_types)

        count = len(metadata_list)
        limit = min(count, limit) if limit > 0 else count
    
    if not os.path.exists(args.metadata_template):
        exit('The metadata template file does not exist.')

    with open(args.metadata_template) as template_file:
        template = json.load(template_file)

    if not os.path.exists(args.asset_dir):
        exit('The asset directory does not exist.')

    if not os.path.exists(args.target_dir):
        os.mkdir(args.target_dir)
    else:
        if not query_yes_no('The directory \'{}\' already exists. Are you sure to generate in it?'.format(args.target_dir), 'no'):
            exit()

    index = 0
    while count > 0 and index < limit:
        selected_item_index = randrange(0, count)
        
        trait_values = metadata_list.pop(selected_item_index)
        
        asset_source_file_name = trait_values.pop(0)
        asset_target_file_name = '{}.png'.format(index)

        # Copy file_name into assets/{file} 
        asset_source_file_path = os.path.join(args.asset_dir, asset_source_file_name)
        asset_target_file_path = os.path.join(args.target_dir, asset_target_file_name)
        if os.path.isfile(asset_source_file_path):
            copy(asset_source_file_path, asset_target_file_path)
        else:
            print('Cannot find asset file {}.'.format(asset_source_file_name))
        # print(asset_source_file_path)
        # print(asset_target_file_path)

        attributes = [{'trait_type': trait_types[i], 'value': trait_values[i]} for i in range(trait_type_count)]

        metadata = template.copy()
        metadata['name'] = '{} #{}'.format(metadata['name'], index + 1) 
        # metadata['symbol'] = '{}#{}'.format(metadata['symbol'], index)
        # metadata['description'] = '{} #{}'.format(metadata['description'], index)
        metadata['image'] = asset_target_file_name
        metadata['attributes'] = attributes
        metadata['properties']['files'][0]['uri']=asset_target_file_name

        metadata_target_file_path = os.path.join(args.target_dir, '{}.json'.format(index))
        with open(metadata_target_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        # print(index)

        index += 1
        count -= 1

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='Generate metadata and artworks based on metadata csv given')
    ap.add_argument("metadata_csv", metavar='metadata', default=METADATA_CSV, nargs='?', help='path to the metadata csv file')
    ap.add_argument("--metadata-template", default=METADATA_TEMPLATE, help='path to the metadata template file')
    ap.add_argument("--asset-dir", default=ASSET_DIR, help='path to the artwork dir')
    ap.add_argument("--target-dir", default=TARGET_DIR, help='path to the target artwork/metdata dir')
    ap.add_argument("--limit", default=LIMIT, type=int, help='number of artwork/metadata to generate')
    args = ap.parse_args()

    generate(args)
