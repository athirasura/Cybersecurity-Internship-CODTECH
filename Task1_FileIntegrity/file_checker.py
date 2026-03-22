import hashlib

# Function to calculate file hash
def calculate_hash(file_path):
    hash_algo = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    
    except FileNotFoundError:
        print("File not found!")
        return None


# Function to save hash
def save_hash(file_path, hash_value):
    with open("hash_store.txt", "a") as f:
        f.write(file_path + ":" + hash_value + "\n")


# Function to check integrity
def check_integrity(file_path):
    new_hash = calculate_hash(file_path)
    
    try:
        with open("hash_store.txt", "r") as f:
            for line in f:
                stored_path, stored_hash = line.strip().split(":")
                
                if stored_path == file_path:
                    if stored_hash == new_hash:
                        print("File is unchanged")
                    else:
                        print("File has been modified")
                    return
        
        print("No record found for this file")
    
    except FileNotFoundError:
        print("No hash file found. Save hash first.")


# Main program
print("1. Save file hash")
print("2. Check file integrity")

choice = input("Enter your choice: ")
file_path = input("Enter file name (example: test.txt): ")

if choice == "1":
    hash_value = calculate_hash(file_path)
    if hash_value:
        save_hash(file_path, hash_value)
        print("Hash saved successfully")

elif choice == "2":
    check_integrity(file_path)

else:
    print("Invalid choice")
    