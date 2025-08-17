import unittest
from unittest.mock import patch
from datetime import datetime
from bella_vista import app, db, Menu, Reservation, Contact

class TestBellaVista(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_homepage(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bella Vista Restaurant', response.data)

    def test_menu(self):
        # Add some menu items
        appetizer = Menu(category='Appetizers', item='Bruschetta', price=8.99)
        main = Menu(category='Mains', item='Spaghetti Bolognese', price=16.99)
        dessert = Menu(category='Desserts', item='Tiramisu', price=6.99)
        db.session.add_all([appetizer, main, dessert])
        db.session.commit()

        response = self.app.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bruschetta', response.data)
        self.assertIn(b'Spaghetti Bolognese', response.data)
        self.assertIn(b'Tiramisu', response.data)

    def test_reservation(self):
        data = {
            'name': 'John Doe',
            'date': '2023-05-01',
            'time': '19:00',
            'party_size': 4
        }
        response = self.app.post('/reserve', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your reservation has been made', response.data)

        reservation = Reservation.query.first()
        self.assertEqual(reservation.name, 'John Doe')
        self.assertEqual(reservation.date, datetime(2023, 5, 1))
        self.assertEqual(reservation.time, '19:00')
        self.assertEqual(reservation.party_size, 4)

    def test_contact(self):
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'Hello, I have a question about your restaurant.'
        }
        response = self.app.post('/contact', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message', response.data)

        contact = Contact.query.first()
        self.assertEqual(contact.name, 'Jane Doe')
        self.assertEqual(contact.email, 'jane@example.com')
        self.assertEqual(contact.message, 'Hello, I have a question about your restaurant.')

    @patch('bella_vista.send_email')
    def test_contact_email(self, mock_send_email):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, I have a question about your restaurant.'
        }
        response = self.app.post('/contact', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message', response.data)
        mock_send_email.assert_called_with('john@example.com', 'New message from Bella Vista Restaurant', 'Hello, I have a question about your restaurant.')

if __name__ == '__main__':
    unittest.main()