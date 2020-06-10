import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql import func

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/*": {"origins": "*"}})

  
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


  @app.route('/categories')
  def get_categories():
    query=Category.query.order_by(Category.id).all()
    categories=[Category.type for Category in query]
    return jsonify({
      'success':True,
      'categories':categories,
      'total_categories':len(query)
    })

  def pagination(request,selection):
    page=request.args.get('page',1,type=int)
    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE
    questions=[question.format() for question in selection ]
    current_questions=questions[start:end]
    return current_questions

  
  @app.route('/questions')
  def get_questions():
    selection=Question.query.order_by(Question.id).all()
    current_questions=pagination(request,selection)
    query=Category.query.order_by(Category.id).all()
    categories=[Category.type for Category in query]
    if len(current_questions)==0:
      abort(404)
    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(selection),
      'current_category':0,
      'categories':categories
    })


  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_questions(question_id):
    
    Q= Question.query.get(question_id)
    if not Q:
      abort(500)
    try:
      db.session.delete(Q)
      db.session.commit()
    except():
      db.session.rollback()
    finally:
      db.session.close()
    return jsonify({
      'success':True,
    })

  
  @app.route('/questions',methods=['POST'])
  def add_questions():
    text=request.get_json()
    question,answer,category,difficulty=text['question'],text['answer'],text['category'],text['difficulty']
    Qid='0'
    try:
      Q=Question(question=question,answer=answer,category=int(category)+1,difficulty=difficulty)
      db.session.add(Q)
      db.session.commit()
      db.session.refresh(Q)
      Qid=Q.id
    except():
      db.session.rollback()
      abort(500)
    finally:
      db.session.close()

    return jsonify({
      'success':True,
      'id':Qid
    })


  @app.route('/search',methods=['POST'])
  def search():
    data=request.get_json()['searchTerm']
    selection=Question.query.filter(Question.question.ilike('%'+data+'%')).all()

    if len(selection)==0:
      return "Failed"
    current_questions=pagination(request,selection)
   
    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(selection),
      'current_category':1
    })


  

  @app.route('/categories/<int:Cid>/questions')
  def category_questions(Cid):
    selection=Question.query.join(Category,Category.id==Question.category).filter(Category.id==Cid+1).order_by(Question.id).all()
    current_questions=pagination(request,selection)
    if len(current_questions)==0:
      abort(404)
    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(selection),
      'current_category':Cid+1
    })


  @app.route('/quizzes',methods=['POST'])
  def quiz():
    previous=request.get_json()['previous_questions']
    R=request.get_json()['quiz_category']
    if R['type']=='click':
      Q=Question.query.filter(Question.id.notin_(previous)).order_by(func.random()).first()
    else:
      Ca=int(R['id'])
      Q=Question.query.filter(Question.category==Ca+1).filter(Question.id.notin_(previous)).order_by(func.random()).first()
    if not Q:
      return jsonify({
      'success':False,
    })
    x=Q.format()

    return jsonify({
      'success':True,
      'question':x
    })

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":400,
      "message":"bad request"
    }),400

  @app.errorhandler(500)
  def internal(error):
    return jsonify({
      "success":False,
      "error":500,
      "message":"Internal Server Error"
    }),500


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"not found"
    }),404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":422,
      "message":"Unprocessable"
    }),422
  
  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success":False,
      "error":405,
      "message":"Method not allowed"
    }),405
  
  return app

    