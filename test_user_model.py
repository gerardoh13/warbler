"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User

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


class UserModelTestCase(TestCase):
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

        u = User.signup(
            email="test3@test3.com",
            username="testuser3",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        # test repr
        self.assertEqual(str(u), f"<User #{u.id}: testuser3, test3@test3.com>")

    def test_valid_password(self):
        self.assertEqual(User.authenticate(
            self.u1.username, "HASHED_PASSWORD"), self.u1)

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(
            self.u1.username, "wrong_password"), self.u1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate(
            "wrong_username", "HASHED_PASSWORD"))

    def test_is_following(self):
        self.assertFalse(self.u1.is_following(self.u2))
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))

    def test_is_followed_by(self):
        self.assertFalse(self.u1.is_followed_by(self.u2))
        self.u2.following.append(self.u1)
        db.session.commit()
        self.assertTrue(self.u1.is_followed_by(self.u2))

    def test_valid_signup(self):
        self.assertTrue(str(User.signup(email="test4@test4.com", username="testuser4",
                        password="HASHED_PASSWORD", image_url=None)), "<User #None: testuser4, test4@test4.com>")

    def test_invalid_signup(self):
        User.signup(email="test1@test1.com", username="testuser1", password="HASHED_PASSWORD", image_url=None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
