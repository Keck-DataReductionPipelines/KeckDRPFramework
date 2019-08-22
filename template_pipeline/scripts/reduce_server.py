'''
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
'''
import os.path

import argparse
import requests
import os


def reduce(file_name):

    dirname = os.path.dirname(file_name)
    if dirname == '':
        cwd = os.getcwd()
        file_name = os.path.join(cwd, file_name)
    r = requests.get('http://127.0.0.1:50100/add_next_file_event?file_name=%s' % file_name)
    

def main():

    parser = argparse.ArgumentParser(description='Process a single file.')
    parser.add_argument('frame', nargs=1, type=str, help='input image file')

    args = parser.parse_args()

    reduce(args.frame[0])

if __name__ == "__main__":
    main()
