import psycopg2
from db.database import DATABASE_URL

def update_schema():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Add driver_id to cab_bookings
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='cab_bookings' AND column_name='driver_id';
        """)
        if not cur.fetchone():
            print("Adding 'driver_id' to 'cab_bookings'...")
            cur.execute("ALTER TABLE cab_bookings ADD COLUMN driver_id INTEGER REFERENCES drivers(id);")
        
        # Add owner_id to vehicles
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='vehicles' AND column_name='owner_id';
        """)
        if not cur.fetchone():
            print("Adding 'owner_id' to 'vehicles'...")
            cur.execute("ALTER TABLE vehicles ADD COLUMN owner_id INTEGER REFERENCES users(id);")
            
        conn.commit()
        print("Schema updated successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_schema()
