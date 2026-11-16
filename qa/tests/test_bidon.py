import sqlite3

PASSWORD = "SuperSecret123!"          # secret en dur -> vulnérabilité / hotspot

def get_user(conn, name):
    # injection SQL : concaténation dans la requête -> vulnérabilité
    return conn.execute(f"SELECT * FROM users WHERE name = '{name}'").fetchall()

def ratio(a):
    return a / 0                       # division par zéro -> bug (S3518)

def check(x):
    if x == 1:
        return "a"
    elif x == 1:                       # condition dupliquée -> bug (S1862)
        return "b"