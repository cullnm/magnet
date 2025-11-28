from sqlalchemy import text
from app.core.db import engine

with engine.connejct() as conn:
    result = conn.execute(text("SELECT 1"))
    print("DB result:", result.scalar())