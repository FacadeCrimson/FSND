import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from flaskr import create_app
from models import setup_db, Question, Category,db



class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.newquestion={
            'question':'What is your name?',
            'answer':'Simon',
            'category':'3',
            'difficulty':1

        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_category(self):
        res=self.client().get('/categories')
        self.assertEqual(res.status_code,200)
    
    def test_get_paginated_questions(self):
        res=self.client().get('/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_delete(self):
        res=self.client().delete('/questions/10')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,500)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Internal Server Error")

    
    def test_post(self):
        res=self.client().post('/questions',json=self.newquestion)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['id'])

    
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()