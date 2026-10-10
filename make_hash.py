from getpass import getpass
from werkzeug.security import generate_password_hash


password = getpass("Enter your current password: ")

hashed_password = generate_password_hash(password)

print("\nYour password hash is:")
print(hashed_password)