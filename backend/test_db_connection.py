import psycopg2
import os

def main():
    print("Teste Verbindungsdaten:")
    print("DB_HOST:", os.getenv("DB_HOST", "127.0.0.1"))  # Default value for host
    print("DB_PORT:", os.getenv("DB_PORT", 5432))
    print("DB_NAME:", os.getenv("DB_NAME"))
    print("DB_USER:", os.getenv("DB_USER"))
    print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))

    try:
        conn = psycopg2.connect(
            host=(os.getenv("DB_HOST", "127.0.0.1")),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("Verbindung zur Datenbank erfolgreich!")
        conn.close()
    except Exception as e:
        print("Fehler bei der Verbindung zur Datenbank:", e)

if __name__ == "__main__":
    main()