from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Attendance System Backend is running!"
    }


@app.post("/login")
def login(username: str, password: str):

    # Temporary login for testing
    if username == "admin" and password == "1234":
        return {
            "success": True,
            "message": "Login successful",
            "username": username
        }

    return {
        "success": False,
        "message": "Invalid username or password"
    }