import os
import uvicorn
from dotenv import load_dotenv


def main():
    "Main Entry point of the app"
    print("Hello from arab-bank-rewrite!")

    load_dotenv()
    # Run the FastAPI app using uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "development").lower() == "development",
    )


if __name__ == "__main__":
    main()
