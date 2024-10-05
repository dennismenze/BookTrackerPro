from app import app, db
from models import Book, Author, List, Post, Translation
import json

def convert_to_translations(model, fields):
    print(f"Updating {model.__name__}")
    for item in model.query.all():
        for field in fields:
            current_value = getattr(item, field)
            if isinstance(current_value, str):
                try:
                    value_dict = json.loads(current_value)
                    if isinstance(value_dict, dict):
                        for lang, content in value_dict.items():
                            translation = Translation(
                                table_name=model.__tablename__,
                                row_id=item.id,
                                column_name=field,
                                language=lang,
                                content=content
                            )
                            db.session.add(translation)
                    else:
                        # If it's not a dict, assume it's in the default language (en)
                        translation = Translation(
                            table_name=model.__tablename__,
                            row_id=item.id,
                            column_name=field,
                            language='en',
                            content=current_value
                        )
                        db.session.add(translation)
                except json.JSONDecodeError:
                    # If it's not valid JSON, assume it's in the default language (en)
                    translation = Translation(
                        table_name=model.__tablename__,
                        row_id=item.id,
                        column_name=field,
                        language='en',
                        content=current_value
                    )
                    db.session.add(translation)
        
        # Clear the JSON data from the original field
        for field in fields:
            setattr(item, field, None)
    
    db.session.commit()

with app.app_context():
    convert_to_translations(Book, ['title', 'description'])
    convert_to_translations(Author, ['name', 'bio'])
    convert_to_translations(List, ['name', 'description'])
    convert_to_translations(Post, ['body'])

print("Manual data migration completed.")
