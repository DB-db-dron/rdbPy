from rdb import RDB_server, Request, Response
from dbql import QuestionAnswerDatabase

app = RDB_server()

db = QuestionAnswerDatabase("forumdb.db")
db.create_tables()

@app.route("/", "GET")
def index(req: Request, res: Response):
    f = open("forumui.html", "r")
    res.setStatus(200).html(str(f.read()))

@app.route("/askqs", "POST")
def index(req: Request, res: Response):
    print(req.body)
    db.create_question(req.body["question"])
    res.json({"question": req.body["question"]})

@app.route("/fetchqs", "POST")
def index(req: Request, res: Response):
    questions = db.read_questions()
    print(questions)
    res.json({"questions": questions})

@app.route("/question", "GET")
def index(req: Request, res: Response):
    f = open("question.html", "r")
    res.setStatus(200).html(str(f.read()))

@app.route("/question", "POST")
def index(req: Request, res: Response):
    question_id = req.query["id"][0]
    questions = db.get_answers_for_question(question_id)

    print(questions)
    res.json(questions)

@app.route("/answerqs", "POST")
def index(req: Request, res: Response):
    print("BODY--> ", req.body)
    try:
        db.create_answer(req.body["id"], req.body["ans"])
        res.json({"msg": "success"})
    except Exception as e:
        print(e)
        res.json({"msg": "failed"})

@app.route("/deleteqs", "POST")
def index(req: Request, res: Response):
    print("BODY--> ", req.body)
    try:
        db.delete_question_and_answers(req.body["id"])
        res.json({"msg": "success"})
    except Exception as e:
        print(e)
        res.json({"msg": "failed"})

@app.route("/deleteans", "POST")
def index(req: Request, res: Response):
    print("BODY--> ", req.body)
    try:
        db.delete_answer(req.body["ansid"])
        res.json({"msg": "success"})
    except Exception as e:
        print(e)
        res.json({"msg": "failed"})

@app.route("404", "")
def custom404(req: Request, res: Response):
    f = open("404.html", "r")
    res.setStatus(400).html(str(f.read()))

app.run(domain="localhost", port=4000)
