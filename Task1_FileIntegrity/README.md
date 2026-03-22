# File Integrity Checker

## Description
This project is a Python-based tool that checks file integrity using the SHA-256 hashing algorithm. It generates a unique hash value for a file and detects whether the file has been changed.

## Extended Description
The program creates a digital fingerprint (hash) of a file and stores it for future comparisons. When the file is checked again, a new hash is generated and compared with the stored one:

- If the hashes match, the file is unchanged  
- If the hashes differ, the file has been modified  

This tool is useful for detecting unauthorized or accidental file changes. It demonstrates basic cybersecurity concepts like file integrity, hashing, and data monitoring.

## Features
- Generates hash values for files  
- Stores hash values for comparison  
- Detects file modifications  
- Simple command-line interface for ease of use  

## How to Run
1. Open your terminal in the `Task1_FileIntegrity` folder.  
2. Run the program with:
   ```bash
   python file_checker.py
