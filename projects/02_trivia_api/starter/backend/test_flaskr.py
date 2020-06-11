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

        self.badquestion={
            'question':'What is your name?',
            'answer':'Simon',
            'category':'10',
            'difficulty':10

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
    
    def test_get_paginated_questions_failure(self):
        res=self.client().get('/questions?page=10')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"not found")

  
    def test_post(self):
        res=self.client().post('/questions',json=self.newquestion)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['id'])
    
    def test_post_failure(self):
        res=self.client().post('/questions',json=self.badquestion)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,500)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Internal Server Error")

    def test_delete(self):
        res=self.client().delete('/questions/20')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_delete_failure(self):
        res=self.client().delete('/questions/1')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Unprocessable")

    def test_search(self):
        res=self.client().post('/search',json={'searchTerm':'la'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])

    def test_search_failure(self):
        res=self.client().post('/search',json={'search':'asasda'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"bad request")
    
    def test_get_category_question(self):
        res=self.client().get('/categories/1/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['current_category'],2)
        self.assertTrue(data['total_questions'])

    def test_get_category_question_failure(self):
        res=self.client().get('/categories/10/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"bad request")
    
    
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()