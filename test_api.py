import httpx
import json

BASE = "http://localhost:8000/api/v1"

def test_login():
    try:
        with httpx.Client() as c:
            r = c.post(f"{BASE}/auth/login", json={"username": "admin", "password": "123456"})
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
            if r.status_code == 200:
                print(f"JSON: {r.json()}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_login()
