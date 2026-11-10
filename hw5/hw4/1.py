import sys
sys.path.append('.')
from persistent_client import PersistentCausalClient
from multiprocessing import Pool
from io import StringIO
from contextlib import redirect_stdout
import time
import random
import argparse

def client0():
    client = PersistentCausalClient(5000)
    client.write(0, 'A', bin='x')
    client.read(0, bin='x')
    client.write(0, 'D', bin='x')

def client1():
    client = PersistentCausalClient(5001)
    client.read(0, bin='x')
    client.write(0, 'B', bin='x')

def client2():
    client = PersistentCausalClient(5002)
    client.read(0, bin='x')
    client.read(0, bin='x')
    client.write(0, 'C', bin='x')

def client3():
    client = PersistentCausalClient(5003)
    client.read(0, bin='x')
    client.read(0, bin='x')
    client.read(0, bin='x')
    client.read(0, bin='x')

def run_client(index):
    time.sleep(random.randrange(5))
    stdout = StringIO()
    with redirect_stdout(stdout):
        globals()['client' + str(index)]()
    return f'Client{index} Output:\n' + stdout.getvalue()

def run_sequential():
    client0 = PersistentCausalClient(5000)
    client1 = PersistentCausalClient(5001)
    client2 = PersistentCausalClient(5002)
    client3 = PersistentCausalClient(5003)
    client0.write(0, 'A', bin='x')
    time.sleep(7)
    client0.read(0, bin='x')
    client1.read(0, bin='x')
    client2.read(0, bin='x')
    client3.read(0, bin='x')
    client1.write(0, 'B', bin='x')
    time.sleep(7)
    client2.read(0, bin='x')
    client3.read(0, bin='x')
    client2.write(0, 'C', bin='x')
    time.sleep(7)
    client3.read(0, bin='x')
    client0.write(0, 'D', bin='x')
    time.sleep(7)
    client3.read(0, bin='x')

def main():
    parser = argparse.ArgumentParser(
                        prog='1.py',
                        description='test case for hw4 problem 1')
    parser.add_argument('--sequential', action='store_true')
    args = parser.parse_args()

    if args.sequential:
        run_sequential()
    else:
        results = []
        with Pool(processes=4) as pool:
            results = pool.map(run_client, range(4))

        for result in results:
            print(result)

if __name__ == "__main__":
    main()
    