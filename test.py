import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="testdb"
)

mycursor = db.cursor()

# create table named Person with columns name, age and fave_food
# mycursor.execute("""
#                  CREATE TABLE Person (name VARCHAR(50), age SMALLINT UNSIGNED, fave_food VARCHAR(255), personID INT PRIMARY KEY AUTO_INCREMENT);
# """)


# insert data into Person table
# mycursor.execute("INSERT INTO Person (name, age, fave_food) VALUES (%s, %s, %s);", ("John", 30, "pizza"))
# db.commit()

# get items inside the database
mycursor.execute("SELECT * FROM Person")
myresult = mycursor.fetchall()
for x in myresult:
    print(x)

