from db_helper import get_db_connection

try:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        print("DATABASE CONNECTION OK")
        print("USERS:")
        print(users)

except Exception as e:
    print("DATABASE ERROR:")
    print(repr(e))