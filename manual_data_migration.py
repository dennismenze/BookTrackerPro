
from app import app, db
from models import Book, Author, List, Post
import json

def convert_to_json(value):
    if value is None:
        return json.dumps({})
    if isinstance(value, str):
        try:
            # Check if it's already valid JSON
            json.loads(value)
            return value
        except json.JSONDecodeError:
            # If not, convert it to JSON
            return json.dumps({"en": value})
    return json.dumps(value)

def update_model(model, fields):
    print(f"Updating {model.__name__}")
    for item in model.query.all():
        updates = {}
        for field in fields:
            current_value = getattr(item, field)
            new_value = convert_to_json(current_value)
            if current_value != new_value:
                updates[field] = new_value
        if updates:
            print(f"Updating {model.__name__} with id {item.id}")
            for field, value in updates.items():
                setattr(item, field, value)
    db.session.commit()

with app.app_context():
    update_model(Book, ['title', 'description'])
    update_model(Author, ['name', 'bio'])
    update_model(List, ['name', 'description'])
    update_model(Post, ['body'])

print("Manual data migration completed.")
