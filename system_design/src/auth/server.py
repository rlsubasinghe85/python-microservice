import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")
server.config["MYSQL_USERNAME"] = os.environ.get("MYSQL_USERNAME")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")

@server.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
    print(auth)

    if not auth:
        return "Missing Credentials", 401
    print("Connecting to mysql DB")
    cur = mysql.connection.cursor()
    res = cur.execut(
        "SELECT email, password FROM user WHERE email=%s", (auth.username)
    )

    print(res)
    
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        
        if auth.username != email or auth.password != password:
            return "Invalid Credentials", 401
        else:
            return createJWT(auth.username, os.enviorn.get("JWT_SECRET"), True)
    else:
        return "Invalid Credentials", 401
    
@server.route("/validate", methods = ["POST"] )
def validate():
    encoded_jwt = request.headers['Authorization']


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "expire": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
