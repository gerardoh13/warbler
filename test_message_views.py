"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from werkzeug import exceptions
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)                                    

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_not_logged_in(self):
        """Can a message be added if user is not logged in?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_like_message(self):
        """Can user like a message?"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            likes_before = User.query.get(self.testuser.id).likes
            self.assertEqual(len(likes_before), 0)
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/like")
            self.assertEqual(resp.status_code, 302)
            likes_after = User.query.get(self.testuser.id).likes
            self.assertEqual(len(likes_after), 1)

    def test_unlike_message(self):
        """Can user unlike a message?"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        self.testuser.likes.append(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            likes_before = User.query.get(self.testuser.id).likes
            self.assertEqual(len(likes_before), 1)
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/like")
            self.assertEqual(resp.status_code, 302)
            likes_after = User.query.get(self.testuser.id).likes
            self.assertEqual(len(likes_after), 0)

    def test_delete_message(self):
        """Can user delete a message?"""
        m = Message(text="Test Message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(resp.status_code, 302)
            with self.assertRaises(exceptions.NotFound) as context:
                Message.query.get_or_404(msg.id)

    def test_delete_message_unauthorized(self):
        """Can user delete a message they didn't post?"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_delete_message_not_logged_in(self):
        """Can a message be deleted if no user is logged in?"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_show_message(self):
        """Does the show message function work?"""
        m = Message(text="Test Message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message.query.one()
            resp = c.get(f"/messages/{msg.id}")
            self.assertEqual(resp.status_code, 200)

    def test_show_nonexisting_message(self):
        """Does a request for a non-existing message return 404?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get("/messages/404")
            self.assertEqual(resp.status_code, 404)
