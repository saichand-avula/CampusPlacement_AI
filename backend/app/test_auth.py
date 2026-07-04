from services.google.auth import get_credentials

creds = get_credentials()

print("Authenticated!")
print(creds.valid)