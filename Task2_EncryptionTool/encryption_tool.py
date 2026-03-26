from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("key.key", "rb").read()

def encrypt_file(filename):
    key = load_key()
    f = Fernet(key)

    with open(filename, "rb") as file:
        data = file.read()

    encrypted = f.encrypt(data)

    with open(filename, "wb") as file:
        file.write(encrypted)

    print("File encrypted successfully!")

def decrypt_file(filename):
    key = load_key()
    f = Fernet(key)

    with open(filename, "rb") as file:
        data = file.read()

    decrypted = f.decrypt(data)

    with open(filename, "wb") as file:
        file.write(decrypted)

    print("File decrypted successfully!")

def main():
    print("1. Generate Key")
    print("2. Encrypt File")
    print("3. Decrypt File")

    choice = input("Enter your choice: ")

    if choice == "1":
        generate_key()
        print("Key generated!")

    elif choice == "2":
        filename = input("Enter file name: ")
        encrypt_file(filename)

    elif choice == "3":
        filename = input("Enter file name: ")
        decrypt_file(filename)

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()