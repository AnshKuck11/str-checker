from cache import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM jurisdictions WHERE status = ?", ("verified",))
deleted_count = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted_count} verified jurisdiction(s).")