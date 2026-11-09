import sys
sys.path.append('.')
from persistent_client import PersistentCausalClient

def main():

    client = PersistentCausalClient(5000)
    client.write(0, 'A')

if __name__ == "__main__":
    main()
    