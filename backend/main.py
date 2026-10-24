from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title='ZINC Beta', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:8081,http://127.0.0.1:8081').split(','), allow_methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Authorization', 'Content-Type', 'If-Match'])

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'ZINC Beta'}
