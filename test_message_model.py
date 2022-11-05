"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
from app import app
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup(
            email="test1@test1.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            image_url=None
        )
        u2 = User.signup(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.commit()
        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        m = Message(text="Test Message", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        self.assertEqual(str(m), f"<Message #{m.id}: Test Message, User#{self.u1.id}>")
        self.assertEqual(len(self.u1.messages), 1)
    
    def test_msg_likes(self):
        """Tests like count before and after liking a message"""
        m = Message(text="Test Message", user_id=self.u1.id)
        self.assertEqual(len(self.u2.likes), 0)
        self.u2.likes.append(m)
        db.session.commit()
        self.assertEqual(len(self.u2.likes), 1)


