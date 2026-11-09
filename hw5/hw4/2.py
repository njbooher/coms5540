import sys
sys.path.append('.')
from persistent_client import PersistentCausalClient
from multiprocessing import Pool
from io import StringIO
from contextlib import redirect_stdout
import time
import random

def client0():
    client = PersistentCausalClient(5000)
    client.write(0, 'A', bin='x')

def client1():
    client = PersistentCausalClient(5001)
    client.write(0, 'B', bin='x')

def client2():
    client = PersistentCausalClient(5002)
    client.read(0, bin='x')
    client.read(0, bin='x')

def client3():
    client = PersistentCausalClient(5003)
    client.read(0, bin='x')
    client.read(0, bin='x')

def run_client(index):
    time.sleep(random.randrange(5))
    stdout = StringIO()
    with redirect_stdout(stdout):
        globals()['client' + str(index)]()
    return f'Client{index} Output:\n' + stdout.getvalue()

def main():

    results = []
    with Pool(processes=4) as pool:
        results = pool.map(run_client, range(4))

    for result in results:
        print(result)

if __name__ == "__main__":
    main()
    