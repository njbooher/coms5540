import sys
sys.path.append('.')
from persistent_client import PersistentClient

def main():

    client = PersistentClient(5000, 5001)
    client.write(0, 'A')
    client.read(1)

if __name__ == "__main__":
    main()
    