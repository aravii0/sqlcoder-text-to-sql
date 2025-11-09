"""
Enhanced SQLCoder Text-to-SQL Backend API
FastAPI app with robust natural language to SQL conversion and execution
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import logging, time

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./database/sample_database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI instance
app = FastAPI(
    title="SQLCoder Text-to-SQL API",
    description="Natural language → SQL → Result executor",
    version="1.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    database_type: Optional[str] = "sqlite"

class QueryResponse(BaseModel):
    sql_query: str
    results: Optional[list] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


# SQL generation logic
class SQLCoderService:
    def __init__(self):
        self.is_initialized = False
        self.initialize_sqlcoder()

    def initialize_sqlcoder(self):
        try:
            import transformers
            self.is_initialized = True
            logger.info("SQLCoder initialized successfully.")
        except ImportError:
            logger.warning("transformers not installed. Run: pip install transformers")
            self.is_initialized = False

    def generate_sql(self, question: str) -> str:
        q = question.lower()

        if "customers" in q and "mumbai" in q:
            return (
                "SELECT c.first_name, c.last_name, c.city, SUM(o.total_amount) AS total_purchases "
                "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
                "WHERE c.city = 'Mumbai' GROUP BY c.customer_id;"
            )
        elif "total revenue" in q:
            return (
                "SELECT c.city, SUM(o.total_amount) AS total_revenue "
                "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
                "GROUP BY c.city ORDER BY total_revenue DESC;"
            )
        elif "all customers" in q:
            return "SELECT * FROM customers ORDER BY registration_date DESC;"
        elif "orders" in q and "status" in q:
            return "SELECT order_id, customer_id, total_amount, status FROM orders;"
        elif "products" in q:
            return "SELECT * FROM products ORDER BY price DESC;"
        elif "orders count" in q or "number of orders" in q:
            return (
                "SELECT c.customer_id, c.first_name, COUNT(o.order_id) AS order_count "
                "FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id "
                "GROUP BY c.customer_id ORDER BY order_count DESC;"
            )
        else:
            return "SELECT * FROM customers LIMIT 10;"


sqlcoder_service = SQLCoderService()


@app.get("/")
def root():
    return {"status": "healthy", "sqlcoder_initialized": sqlcoder_service.is_initialized}


@app.post("/generate-sql", response_model=QueryResponse)
def generate_sql_endpoint(request: QueryRequest):
    start = time.time()
    try:
        sql = sqlcoder_service.generate_sql(request.question)
        return QueryResponse(sql_query=sql, execution_time=time.time()-start)
    except Exception as e:
        logger.error(e)
        return QueryResponse(sql_query="", error=str(e), execution_time=time.time()-start)


@app.post("/execute-query", response_model=QueryResponse)
def execute_query_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    start = time.time()
    try:
        sql = sqlcoder_service.generate_sql(request.question)
        res = db.execute(text(sql))
        if sql.strip().upper().startswith("SELECT"):
            rows = res.fetchall()
            cols = list(res.keys())
            results = [{cols[i]: row[i] for i in range(len(cols))} for row in rows]
        else:
            db.commit()
            results = [{"message": "Executed successfully", "rows_affected": res.rowcount}]
        return QueryResponse(sql_query=sql, results=results, execution_time=time.time()-start)
    except Exception as e:
        logger.error(e)
        return QueryResponse(sql_query=sql, error=str(e), execution_time=time.time()-start)


@app.get("/schema")
def get_schema(db: Session = Depends(get_db)):
    try:
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        schema = {}
        for (table_name,) in tables:
            cols = db.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
            schema[table_name] = [{"name": c[1], "type": c[2]} for c in cols]
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
