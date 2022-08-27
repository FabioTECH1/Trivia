import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_password = 12345
        self.database_path = "postgresql://postgres:{}@{}/{}".format(self.database_password,
                                                                     'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.question = {"question": "How many angles in a triangle?",
                         "answer": "three",
                         "category": '4',
                         'difficulty': 2}
        self.error_question = {"question": "How many angles in a circle?",
                               "answer": "zero",
                               "category": 4,
                               'difficulty': True}

        self.quiz = {'previous_questions': [],
                     'quiz_category': {"type": "Click", "id": 0}
                     }
        self.error_quiz = {'previous_questions': [],
                           'quiz_category': {"type": "History", "id": 10}
                           }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # # test get categories
    def test_get_categories(self):
        res = self.client().get("/api/v1.0/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    # add question
    def test_create_new_question(self):
        res = self.client().post("/api/v1.0/questions/create", json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # # error test foradding questio
    def test_422_if_question_creation_is_unprocessable(self):
        res = self.client().post("/api/v1.0/questions/create",
                                 json=self.error_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    # test get Questions
    def test_get_questions(self):
        res = self.client().get("/api/v1.0/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    # error get question beyond valid page
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/api/v1.0/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # test get Question based on category
    def test_get_category_based_questions(self):
        res = self.client().post('/api/v1.0/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], '4')

    # error get question with invalid category
    def test_404_questions_from_invalid_category(self):
        res = self.client().post("/api/v1.0/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # test search question
    def test_get_questions_search_with_results(self):
        res = self.client().post("/api/v1.0/questions/search",
                                 json={"searchTerm": "How many"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    # error for no question in search
    def test_404_sent_no_available_question_from_search(self):
        res = self.client().post("/api/v1.0/questions/search",
                                 json={"searchTerm": "Not available"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # # test delete Question
    def test_delete_questions(self):
        res = self.client().delete("/api/v1.0/questions/2/delete")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)

    # # error test for delete question
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/api/v1.0/questions/1000/delete")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    #     # test get quiz
    def test_get_quiz(self):
        res = self.client().post("/api/v1.0/quizzes", json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # error test for no question to return for quiz
    def test_404_if_no_question_for_quizz(self):
        res = self.client().post("/api/v1.0/quizzes", json=self.error_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
