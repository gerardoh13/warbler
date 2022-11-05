"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=production python -m unittest test_user_views.py


import os
from unittest import TestCase
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
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

    def test_list_users(self):
        """Tests list_users show function"""

        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            self.assertIn("testuser2", str(resp.data))

    def test_users_show(self):
        """Test users_show view function"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))

    def test_show_following(self):
        """Test show_following view function"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("Unfollow", str(resp.data))

    def test_show_following_not_logged_in(self):
        """Test show_following view function if not logged in"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_users_followers(self):
        """Test users_followers view function"""
        self.testuser2.following.append(self.testuser)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/followers")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("Follow", str(resp.data))

    def test_users_followers_not_logged_in(self):
        """Test users_followers view function if not logged in"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_follow(self):
        """test following a user"""
        with self.client as c:
            follow_id = self.testuser2.id
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/follow/{follow_id}")
            self.assertEqual(resp.status_code, 302)
            following = User.query.get(self.testuser.id).following
            self.assertEqual(self.testuser2.username, following[0].username)

    def test_add_follow_not_logged_in(self):
        """Test following a user if not logged in"""
        follow_id = self.testuser2.id
        with self.client as c:
            resp = c.post(f"/users/follow/{follow_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_stop_following(self):
        """test unfollowing a user"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()
        with self.client as c:
            unfollow_id = self.testuser2.id
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            following_before = User.query.get(self.testuser.id).following
            self.assertEqual(len(following_before), 1)
            resp = c.post(f"/users/stop-following/{unfollow_id}")
            self.assertEqual(resp.status_code, 302)
            following_after = User.query.get(self.testuser.id).following
            self.assertEqual(len(following_after), 0)

    def test_stop_following_not_logged_in(self):
        """test unfollowing a user if not logged in"""
        self.testuser.following.append(self.testuser2)
        db.session.commit()
        with self.client as c:
            unfollow_id = self.testuser2.id
            resp = c.post(f"/users/stop-following/{unfollow_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


    def test_show_likes(self):
        """Test show_likes view function"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        self.testuser.likes.append(m)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/likes")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Message", str(resp.data))
            self.assertIn("btn-primary", str(resp.data))

    def test_show_likes_not_logged_in(self):
        """Test show_likes view function if not logged in"""
        m = Message(text="Test Message", user_id=self.testuser2.id)
        db.session.add(m)
        self.testuser.likes.append(m)
        db.session.commit()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/likes", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


