from graph_database import conn

try:
    conn.execute("DROP TABLE Event")
except:
    pass

try:
    query = """
    CREATE NODE TABLE Event (
        title STRING, 
        event_date STRING, 
        start_time STRING, 
        end_time STRING, 
        location STRING,
        status STRING,
        PRIMARY KEY (title)
    )
    """
    conn.execute(query)
    print("✅ تم بناء جدول الأحداث (Event) شاملاً جميع الحقول بنجاح!")
except Exception as e:
    print(f"⚠️ ملاحظة: {e}")