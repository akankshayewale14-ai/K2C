from app.db.seed import seed
from app.db.session import SessionLocal


def main():
    db = SessionLocal()
    try:
        seed(db)
        print("Seed complete. Demo login: ananya@kabadiwala.local / DemoPass123!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
