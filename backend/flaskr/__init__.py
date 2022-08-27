import os
from sre_constants import CATEGORY
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

# import sys
# sys.path.append('./')
from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in selection]
    formatted_questions = formatted_questions[start:end]
    return formatted_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    # app.debug = True
    setup_db(app)

    cors = CORS(app, resources={
                r"/api/*": {"origins": "*"}})  # Resource-Specific Usage

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # get categories
    @app.route('/api/v1.0/categories', methods=['GET'])
    def get_catetories():

        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            cat = {category.id: category.type}
            formatted_categories.update(cat)

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    # get questions
    @app.route('/api/v1.0/questions', methods=['GET'])
    def get_questions():

        questions = Question.query.all()
        categories = Category.query.all()
        formatted_categories = {}
        formatted_questions = paginate_questions(request, questions)

        for category in categories:
            cat = {category.id: category.type}
            current_category = category.type
            formatted_categories.update(cat)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': current_category,
            'categories': formatted_categories
        })

    # delete question with id
    @app.route('/api/v1.0/questions/<int:question_id>/delete', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'id': question_id
            })
        except:
            abort(422)

    # create a question
    @app.route('/api/v1.0/questions/create', methods=['POST'])
    def add_question():

        body = request.get_json()
        if body:
            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
        else:
            abort(404)
        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            return jsonify({
                'success': True,
            })
        except:
            abort(422)

    # search for questions using searchTerm
    @app.route('/api/v1.0/questions/search', methods=['POST'])
    def get_search_questions():

        body = request.get_json()
        search_term = body.get('searchTerm', None)

        questions = Question.query.filter(
            Question.question.ilike('%'+search_term+'%')).all()

        questions = [question.format() for question in questions]

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions),
        })

    # get questions based on category
    @app.route('/api/v1.0/categories/<string:cat_id>/questions', methods=['POST'])
    def get_category_based_question(cat_id):

        questions = Question.query.filter_by(category=cat_id).all()
        questions = [question.format() for question in questions]

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            "questions": questions,
            'current_category': cat_id,
            'total_questions': len(questions)
        })

    # get non-repetitive random question in a category for quizzz
    @app.route('/api/v1.0/quizzes', methods=['POST'])
    def post_question_to_quiz():
        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)['id']

        if quiz_category == 0:
            print(quiz_category)
            questions = Question.query.all()
        else:
            print(quiz_category)
            questions = Question.query.filter_by(
                category=format(quiz_category)).all()

        questions = [question.format() for question in questions]

        if len(questions) == 0:
            abort(404)
        elif len(previous_questions) == len(questions):
            next_question = None
        else:
            i = 0
            while i < len(questions):
                next_question = random.choice(questions)
                exists = previous_questions.count(next_question['id'])
            #  check to avoid question repetition
                if exists:
                    continue
                else:
                    break

        return jsonify({
            'success': True,
            "question": next_question,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
