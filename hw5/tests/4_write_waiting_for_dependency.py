import sys
sys.path.append('.')
from persistent_client import PersistentClient

def main():

    client = PersistentClient(5000)
    client2 = PersistentClient(5000, 5001)

    client.write(0, 'A')
    client2.read(0)
    client2.write(1, 'B')

if __name__ == "__main__":
    main()
    