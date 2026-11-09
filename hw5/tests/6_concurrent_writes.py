import sys
sys.path.append('.')
from persistent_client import PersistentCausalClient
from multiprocessing import Pool

def client0():
    client = PersistentCausalClient(5000)
    client.write(0, 'A')

def client1():
    client = PersistentCausalClient(5001)
    client.write(0, 'B')

def run_client(index):
    globals()['client' + str(index)]()

def main():
    with Pool(processes=2) as pool:
        print(pool.map(run_client, range(2)))

if __name__ == "__main__":
    main()
    