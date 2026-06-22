import sqlite3

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

DATABASE_PATH = "pipeline_cli_teste.db"

app = FastAPI(title="API Mockada")

class ClientPayload(BaseModel):
    external_id: str
    name: str
    email: str | None = None
    document: str | None = None
    phone: str | None = None
    zip_code: str | None = None
    street: str | None = None
    neighborhood: str | None = None
    city: str | None = None
    state: str | None = None


def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
        external_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        document TEXT,
        phone TEXT,
        zip_code TEXT,
        street TEXT,
        neighborhood TEXT,
        city TEXT,
        state TEXT
        )
        """
    )

    connection.commit()
    connection.close()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/clients")
def upsert_client(payload: ClientPayload, response: Response):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT external_id FROM clients WHERE external_id = ?",
        (payload.external_id,),
    )

    client_exists = cursor.fetchone() is not None

    if client_exists:
        cursor.execute(
            """
            UPDATE clients
            SET name = ?,
                email = ?,
                document = ?,
                phone = ?,
                zip_code = ?,
                street = ?,
                neighborhood = ?,
                city = ?,
                state = ?
            WHERE external_id = ?
            """,
            (
                payload.name,
                payload.email,
                payload.document,
                payload.phone,
                payload.zip_code,
                payload.street,
                payload.neighborhood,
                payload.city,
                payload.state,
                payload.external_id,
            ),
        )

        response.status_code = status.HTTP_200_OK
        action = "updated"

    else:
        cursor.execute(
            """
            INSERT INTO clients (
                external_id,
                name,
                email,
                document,
                phone,
                zip_code,
                street,
                neighborhood,
                city,
                state
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.external_id,
                payload.name,
                payload.email,
                payload.document,
                payload.phone,
                payload.zip_code,
                payload.street,
                payload.neighborhood,
                payload.city,
                payload.state,
            ),
        )

        response.status_code = status.HTTP_201_CREATED
        action = "created"

    connection.commit()
    connection.close()

    return {
        "external_id": payload.external_id,
        "action": action,
    }