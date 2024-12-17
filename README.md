Holiday Application

The Holiday API Application is a Django-based web application designed to fetch and display holiday data for different countries and years. It integrates with the Calendarific API, a service that provides global holiday data. The application allows users to query holidays by specifying the country, year, and optionally the month. It provides a robust API for fetching this data, with added caching to optimize performance and minimize redundant API calls to Calendarific.



1. Clone the Repository
git clone https://github.com/sidharthsasi/Holiday-Project.git

2. Install Dependencies
pip install -r requirements.txt

3. Migrate the Database
python manage.py makemigrations
python manage.py migrate

4. Create Superuser (For Admin Access)
python manage.py createsuperuser

5. Run the Development Server
python manage.py runserver
