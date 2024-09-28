import requests
from bs4 import BeautifulSoup

def test_author_detail():
    base_url = 'http://localhost:5000'
    session = requests.Session()

    # Log in
    login_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = session.post(f'{base_url}/login', data=login_data)
    if response.url.endswith('/login'):
        print("Login failed.")
        return

    # Access author detail page
    author_id = 1  # Assuming we have an author with id 1
    response = session.get(f'{base_url}/author/{author_id}')
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for author name
        author_name = soup.find('h1', class_='text-3xl font-bold mb-6')
        print(f"Author Name: {author_name.text if author_name else 'Not found'}")
        
        # Check for statistics
        stats = soup.find_all('dd', class_='mt-1 text-3xl font-semibold text-gray-900')
        if len(stats) == 4:
            print(f"Total Books: {stats[0].text}")
            print(f"Total Pages: {stats[1].text}")
            print(f"Average Pages: {stats[2].text}")
            print(f"Books Read Percentage: {stats[3].text}")
        else:
            print("Statistics not found or incomplete.")
    else:
        print(f"Failed to access author detail page. Status code: {response.status_code}")

if __name__ == '__main__':
    test_author_detail()
