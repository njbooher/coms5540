import sys
sys.path.append('.')
from persistent_client import PersistentClient

def main():

    client = PersistentClient(5000)
    client.write(0, 'A')
    client.read(0)

if __name__ == "__main__":
    main()
    