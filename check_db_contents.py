from app import app, db
from models import Book, Author, List, Post, Translation
import json

def print_table_contents(model, fields):
    print(f"\n{model.__name__} Table Contents:")
    for item in model.query.all():
        print(f"ID: {item.id}")
        for field in fields:
            value = getattr(item, field)
            if isinstance(value, str):
                try:
                    parsed_json = json.loads(value)
                    print(f"{field}: {parsed_json}")
                except json.JSONDecodeError:
                    print(f"{field}: {value} (Not valid JSON)")
            else:
                print(f"{field}: {value}")
        print("---")

with app.app_context():
    print_table_contents(Book, ['title', 'description'])
    print_table_contents(Author, ['name', 'bio'])
    print_table_contents(List, ['name', 'description'])
    print_table_contents(Post, ['body'])
    print_table_contents(Translation, ['table_name', 'row_id', 'column_name', 'language', 'content'])
