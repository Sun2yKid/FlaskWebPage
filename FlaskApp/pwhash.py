from passlib.hash import sha256_crypt

password = sha256_crypt.encrypt("password")

password2 = sha256_crypt.encrypt("password")

print password
print password2

if password == password2:
    print("yay")
else:
    print("fail")
