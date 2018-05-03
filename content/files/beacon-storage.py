#!/usr/bin/python3
import sys

# assumptions
STORAGE_SIZE = 16
OVERHEAD_PER_ENTRY = 0
BEACONS_PER_SECOND = 10

# constants
KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE
GIGABYTE = 1024 * MEGABYTE

def size_string(size):
    if size < GIGABYTE:
        if size < MEGABYTE:
            if size < KILOBYTE:
                return '{:0.0f} B'.format(size)
            return '{:0.0f} KB'.format(size // KILOBYTE)
        return '{:0.1f} MB'.format(size / MEGABYTE)
    return '{:0.1f} GB'.format(size / GIGABYTE)

def storage_per_second(bps):
    return 

def main(args):
    bps = BEACONS_PER_SECOND
    if len(args) > 0:
        bps = float(args[0])

    storage = (STORAGE_SIZE + OVERHEAD_PER_ENTRY) * bps
    print('Bytes per second:', size_string(storage))
    
    storage *= 60
    print('Bytes per minute:', size_string(storage))

    storage *= 60
    print('Bytes per minute:', size_string(storage))

    storage *= 24
    print('   Bytes per day:', size_string(storage))

    storage *= 365.25
    print('  Bytes per year:', size_string(storage))


if __name__ == '__main__':
    main(sys.argv[1:])