import time
from models import db, Author, Book, UserBook, BookList, Translation
from flask import current_app
import requests
from typing import Dict, Any, Optional
import csv
import io
from datetime import datetime


def calculate_read_percentage(books, user_id):
    if not books:
        return 0
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    return (read_books / len(books)) * 100


def calculate_read_main_works_percentage(books, user_id):
    main_works = [book for book in books if book.is_main_work]
    if not main_works:
        return 0
    return calculate_read_percentage(main_works, user_id)


def get_books_stats(books, user_id):
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    main_works = [book for book in books if book.is_main_work]
    read_main_works = sum(1 for book in main_works
                          if is_book_read(book, user_id))
    return {
        'total_books':
        len(books),
        'read_books':
        read_books,
        'read_percentage':
        calculate_read_percentage(books, user_id),
        'total_main_works':
        len(main_works),
        'read_main_works':
        read_main_works,
        'read_main_works_percentage':
        calculate_read_main_works_percentage(books, user_id)
    }


def is_book_read(book, user_id):
    user_book = UserBook.query.filter_by(user_id=user_id,
                                         book_id=book.id).first()
    return user_book.is_read if user_book else False

def map_author_data(author, user_id):  
    books = [map_book_data(book, user_id) for book in author.books]
    book_stats = get_books_stats(author.books, user_id)    
    
    author_data = {
        'id': author.id,
        'name': author.name,
        'image_url': author.image_url,
        'books': books,
        'total_books': book_stats['total_books'],
        'read_books': book_stats['read_books'],
        'read_percentage': book_stats['read_percentage'],
        'total_main_works': book_stats['total_main_works'],
        'read_main_works': book_stats['read_main_works'],
        'read_main_works_percentage': book_stats['read_main_works_percentage']
    }

    if not author.image_url:
        author.image_url = get_author_image_from_wikimedia(author.name)
        db.session.commit()
    return author_data

def get_author_image_from_wikimedia(author_name):
    # Definiere die API-Endpunkt-URL
    url = "https://en.wikipedia.org/w/api.php"

    # Parameter für die Wikipedia-API, um die Seite des Autors zu suchen
    params = {
        "action": "query",
        "titles": author_name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 500  # Die Größe des gewünschten Thumbnails in Pixeln
    }

    # Anfrage an die Wikipedia-API senden
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Extrahiere die Bild-URL aus der Antwort
    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]

    return None

def map_book_data(book, user_id):
    book_data = {
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': is_book_read(book, user_id),
        'is_main_work': book.is_main_work,
        'cover_image_url': book.cover_image_url
        or '/static/images/no-cover.png',
        'isbn': book.isbn,
        'description': book.description,
        'page_count': book.page_count,
        'published_date': book.published_date,
        'lists': []
    }

    if not all([
            book.isbn, book.description, book.cover_image_url, book.page_count,
            book.published_date
    ]):
        google_books_info = fetch_google_books_info(book.title,
                                                    book.author.name)

        book_data['isbn'] = book.isbn or google_books_info.get('isbn')
        book_data['description'] = book.description or google_books_info.get(
            'description')
        book_data[
            'cover_image_url'] = book.cover_image_url or google_books_info.get(
                'cover_image_url')
        book_data['page_count'] = book.page_count or google_books_info.get(
            'page_count')
        book_data[
            'published_date'] = book.published_date or google_books_info.get(
                'published_date')

        book.isbn = book_data['isbn']
        book.description = book_data['description']
        book.cover_image_url = book_data['cover_image_url']
        book.page_count = book_data['page_count']
        book.published_date = book_data['published_date']

        db.session.commit()
    return book_data


def fetch_google_books_info(title: str, author: str) -> Optional[Dict[str, Any]]:
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title}+inauthor:{author}",
        "langRestrict": "en",
        "maxResults": 1
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("totalItems", 0) > 0:
            volume_info = data["items"][0]["volumeInfo"]
            book_info = {
                'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
                'description_en': volume_info.get('description', ''),
                'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                'page_count': volume_info.get('pageCount'),
                'published_date': volume_info.get('publishedDate')
            }

            # Fetch German version
            params["langRestrict"] = "de"
            response_de = requests.get(base_url, params=params)
            response_de.raise_for_status()
            data_de = response_de.json()

            if data_de.get("totalItems", 0) > 0:
                volume_info_de = data_de["items"][0]["volumeInfo"]
                book_info['description_de'] = volume_info_de.get('description', '')
                book_info['title_de'] = volume_info_de.get('title', '')
                book_info['cover_image_url_de'] = volume_info_de.get('imageLinks', {}).get('thumbnail', '')

            return book_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching book info: {e}")
        return None


def fetch_google_authors_info(author_name: str) -> Optional[Dict[str, Any]]:
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"inauthor:{author_name}",
        "langRestrict": "en",
        "maxResults": 1
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("totalItems", 0) > 0:
            volume_info = data["items"][0]["volumeInfo"]
            author_info = {
                "name": author_name,
                "biography_en": volume_info.get("description", ""),
                "image_url": volume_info.get("imageLinks", {}).get("thumbnail", "")
            }

            # Fetch German version
            params["langRestrict"] = "de"
            response_de = requests.get(base_url, params=params)
            response_de.raise_for_status()
            data_de = response_de.json()

            if data_de.get("totalItems", 0) > 0:
                volume_info_de = data_de["items"][0]["volumeInfo"]
                author_info['name_de'] = volume_info_de.get("title", "")
                author_info['biography_de'] = volume_info_de.get("description", "")

            return author_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching author info: {e}")
        return None

def fetch_openlibrary_books_info(title: str, author: str) -> Optional[Dict[str, Any]]:
    search_url = "https://openlibrary.org/search.json"
    search_params = {
        "title": title,
        "author": author,
        "limit": 1
    }

    try:
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data.get("numFound", 0) > 0:
            work_key = search_data["docs"][0].get("key")
            if not work_key:
                return None

            book_info = {}

            # Suche nach der deutschen Edition
            editions_url = f"https://openlibrary.org/works/{work_key}/editions.json"
            editions_response = requests.get(editions_url)
            editions_response.raise_for_status()
            editions_data = editions_response.json()

            for edition in editions_data.get('entries', []):
                if edition.get('languages') and any(lang.get('key') == '/languages/ger' for lang in edition['languages']):
                    book_info['title_de'] = edition.get('title', '')
                    break

            return book_info
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching book info from OpenLibrary: {e}")
        return None

def search_german_title_wikidata1(author, title):
    # Step 1: Find the work by author and title using Wikidata API
    url = "https://www.wikidata.org/w/api.php"
    work_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f"{author} {title}",
        'format': 'json',
    }

    try:
        # Send request to Wikidata to get the work by author and title
        response = requests.get(url, params=work_params)
        response.raise_for_status()  # Check for errors
        data = response.json()
        # Process the work query results
        work_results = data.get("query", {}).get("search", [])
        if not work_results:
            return f"No matching title found for '{title}' by author '{author}'."

        # Assuming the first result is the correct work
        work_id = work_results[0].get("title")
        if not work_id:
            return f"No work ID found for '{title}' by author '{author}'."

        work_id = work_id.replace("Q", "")

        # Step 2: Find the German label for the work
        labels_params = {
            'action': 'wbgetentities',
            'ids': f'Q{work_id}',
            'props': 'labels',
            'languages': 'de',
            'format': 'json'
        }

        # Send request to Wikidata to get the German label
        response = requests.get(url, params=labels_params)
        response.raise_for_status()  # Check for errors
        data = response.json()

        german_title = data.get("entities", {}).get(f"Q{work_id}", {}).get("labels", {}).get("de", {}).get("value", "Unknown Title")
        return german_title

    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"


import requests
from fuzzywuzzy import process

def search_german_title_wikidata(author, title):
    url = "https://www.wikidata.org/w/api.php"
    author_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': author,
        'format': 'json',
    }

    try:
        response = requests.get(url, params=author_params)
        response.raise_for_status()
        data = response.json()

        author_results = data.get("query", {}).get("search", [])
        if not author_results:
            return title

        author_id = author_results[0].get("title")
        if not author_id:
            return title

        author_id = author_id.replace("Q", "")

        sparql_url = "https://query.wikidata.org/sparql"
        works_query = f"""
        SELECT ?work ?workLabel WHERE {{
          ?work wdt:P31 wd:Q7725634;
                wdt:P50 wd:Q{author_id};
                rdfs:label ?workLabel.
          FILTER(LANG(?workLabel) = "en")
        }}
        """

        params = {
            'query': works_query,
            'format': 'json'
        }

        response = requests.get(sparql_url, params=params)
        response.raise_for_status()
        data = response.json()

        works_results = data.get("results", {}).get("bindings", [])
        if not works_results:
            return title

        titles = {result.get("work", {}).get("value"): result.get("workLabel", {}).get("value", "") for result in works_results}
        best_match = process.extractOne(title, titles.values())

        if not best_match:
            return title

        best_match_title = best_match[0]
        best_match_work_id = [key for key, value in titles.items() if value == best_match_title][0]

        labels_params = {
            'action': 'wbgetentities',
            'ids': best_match_work_id.split('/')[-1],
            'props': 'labels',
            'languages': 'de',
            'format': 'json'
        }

        response = requests.get(url, params=labels_params)
        response.raise_for_status()
        data = response.json()

        german_title = data.get("entities", {}).get(best_match_work_id.split('/')[-1], {}).get("labels", {}).get("de", {}).get("value", title)
        return german_title

    except requests.exceptions.RequestException as e:
        print(e)
        return title

import requests
from fuzzywuzzy import process

def search_german_author_name_wikidata(author):
    url = "https://www.wikidata.org/w/api.php"
    author_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': author,
        'format': 'json',
    }

    try:
        response = requests.get(url, params=author_params)
        response.raise_for_status()
        data = response.json()

        author_results = data.get("query", {}).get("search", [])
        if not author_results:
            return f"No author found for '{author}'."

        author_id = author_results[0].get("title")
        if not author_id:
            return f"No author ID found for '{author}'."

        author_id = author_id.replace("Q", "")

        sparql_url = "https://query.wikidata.org/sparql"
        labels_query = f"""
        SELECT ?germanLabel WHERE {{
          wd:Q{author_id} rdfs:label ?germanLabel.
          FILTER(LANG(?germanLabel) = "de")
        }}
        """

        params = {
            'query': labels_query,
            'format': 'json'
        }

        response = requests.get(sparql_url, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {}).get("bindings", [])
        if not results:
            return author   

        german_name = results[0].get("germanLabel", {}).get("value", author)
        return german_name

    except requests.exceptions.RequestException as e:
        print(e)
        return author
