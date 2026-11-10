import sys
sys.path.append('.')
from persistent_client import PersistentCausalClient
from multiprocessing import Pool
from io import StringIO
from contextlib import redirect_stdout

def client0():
    client = PersistentCausalClient(5000)
    client.write(0, 'A')

def client1():
    client = PersistentCausalClient(5001)
    client.write(0, 'B')

def run_client(index):
    stdout = StringIO()
    with redirect_stdout(stdout):
        globals()['client' + str(index)]()
    return f'Client{index} Output:\n' + stdout.getvalue()

def main():

    results = []
    with Pool(processes=2) as pool:
        results = pool.map(run_client, range(2))

    for result in results:
        print(result)

if __name__ == "__main__":
    main()
    