import sys
sys.path.append('.')
from persistent_client import PersistentClient

def main():

    client = PersistentClient(5000, 5001, 5002)
    client.write(0, 'A')
    client.write(1, 'B')
    client.write(2, 'C')

if __name__ == "__main__":
    main()
    