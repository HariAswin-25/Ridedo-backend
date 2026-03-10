import psycopg2
from db.database import DATABASE_URL

def verify_schema():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        tables = ['users', 'drivers', 'vehicles', 'cab_bookings', 'driver_bookings', 'vehicle_rentals']
        
        for table in tables:
            print(f"\n--- Columns in {table} ---")
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}';")
            columns = cur.fetchall()
            if not columns:
                print(f"Table {table} not found!")
            for col in columns:
                print(f"{col[0]}: {col[1]}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_schema()
