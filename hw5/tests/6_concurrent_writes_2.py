import sys
sys.path.append('.')
from persistent_client import PersistentClient

def main():

    client = PersistentClient(5001)
    client.write(0, 'B')

if __name__ == "__main__":
    main()
    