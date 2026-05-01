import typer
import httpx
import json
import os
from pathlib import Path

app = typer.Typer()
BASE_URL = os.getenv("VANGUARD_API_URL", "http://localhost:8000")
SESSION_FILE = Path.home() / ".vanguard_session"

def get_client():
    cookies = {}
    if SESSION_FILE.exists():
        cookies = json.loads(SESSION_FILE.read_text())
    return httpx.Client(base_url=BASE_URL, cookies=cookies)

@app.command()
def login(user_id: str):
    client = httpx.Client(base_url=BASE_URL)
    res = client.post("/agent/login", json={"user_id": user_id})
    if res.status_code == 200:
        SESSION_FILE.write_text(json.dumps(client.cookies.get_dict()))
        typer.echo("Login successful")
    else:
        typer.echo("Login failed")

@app.command()
def start():
    client = get_client()
    res = client.post("/agent/scrape")
    typer.echo(res.json())

@app.command()
def tasks():
    client = get_client()
    res = client.get("/agent/tasks")
    typer.echo(res.json())

if __name__ == "__main__":
    app()
