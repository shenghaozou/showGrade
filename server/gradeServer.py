import base64, boto3, botocore, logging, os, sys, json
from flask import Flask
from flask_cors import CORS

logging.basicConfig(
    handlers=[
        logging.FileHandler("gradeServer.log"),
        logging.StreamHandler()
    ],
    level=logging.INFO)

CODE_DIR = "./submission"
RESULT_PATH="ta/grading/{project}/{netId}.json"
TEST_DIR = "/tmp/test/{netId}"
SUBMISSIONS = 'submissions'
BUCKET = 'caraza-harter-cs301'
session = boto3.Session(profile_name='cs301ta')
s3 = session.client('s3')

app = Flask(__name__)
CORS(app)


# General template to fetch from s3
def s3Fetcher(path, name, raiseError = True):
    try:
        response = s3.get_object(Bucket=BUCKET, Key=path)
        return response['Body'].read().decode('utf-8')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            logging.info(
                "key {} doesn't exist when look up for {}.".format(path, name))
        else:
            logging.warning(
                "Unexpected error {} when look up for {}.".format(e.response['Error']['Code'], name))
            if raiseError:
                raise e

def lookupNetId(googleId):
    path = 'users/google_to_net_id/%s.txt' % googleId
    return s3Fetcher(path, "netId", False)

def lookupGrade(netId, project):
    resultPath = RESULT_PATH.format(project=project, netId=netId)
    response = s3Fetcher(resultPath, "Grade Result", False)
    return response

def htmlGrade(resultStr):
    result = json.loads(resultStr)
    grade = result.get("score", 0)
    tests = result.get("tests", None)
    template = "<ul><li> Grade: {grade}{tests}</ul>"
    testsHtml = ""
    if tests:
        for test in tests:
            tTest = test.get("test", "")
            tResult = test.get("result", "")
            testsHtml += "<li>test: {} result: {}".format(tTest, tResult)
    headerInfo = template.format(grade=grade, tests=testsHtml)
    if grade == 100:
        comments = "Good work!"
    else:
        comments = "There are some errors in your script. Please make sure you run test.py before submission!"
    return json.dumps({"detail" : headerInfo, "comments" : comments})

@app.route('/')
def index():
    return "index"

@app.route('/<project>/<googleId>')
def gradingJson(project, googleId):
    netId = lookupNetId(googleId)
    result = lookupGrade(netId, project)
    if result:
        return htmlGrade(result)
    else:
        return json.dumps({"detail" : "", "comments" : ""})
