# ai-sql-assistant.py
# Natural Language → SQL using pgvector + Ollama

import psycopg2
from sentence_transformers import SentenceTransformer

# Connect (update your creds)
conn = psycopg2.connect(host="localhost", dbname="sales_db", user="aaron", password="pass")
cur = conn.cursor()

# Create table + index
cur.execute("""
CREATE TABLE IF NOT EXISTS query_embeddings (
    id SERIAL PRIMARY KEY,
    question TEXT,
    sql_query TEXT,
    embedding VECTOR(384)
);
CREATE INDEX IF NOT EXISTS idx_embedding ON query_embeddings USING ivfflat (embedding vector_cosine_ops);
""")
conn.commit()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Seed data
samples = [
    ("How many orders last month?", "SELECT COUNT(*) FROM orders WHERE order_date >= NOW() - INTERVAL '30 days';"),
    ("Top 5 customers by revenue?", "SELECT customer_id, SUM(amount) FROM orders GROUP BY 1 ORDER BY 2 DESC LIMIT 5;")
]
for q, sql in samples:
    emb = model.encode(q).tolist()
    cur.execute("INSERT INTO query_embeddings (question, sql_query, embedding) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (q, sql, emb))
conn.commit()

# Ask!
question = input("\nAsk a SQL question: ")
emb = model.encode(question).tolist()
cur.execute("SELECT sql_query FROM query_embeddings ORDER BY embedding <=> %s LIMIT 1;", (emb,))
result = cur.fetchone()
print("\nAI SQL:\n", result[0] if result else "No match.")
conn.close()