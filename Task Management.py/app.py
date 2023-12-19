from flask import Flask, request, jsonify
import sqlite3
import json
import unittest
app = Flask(__name__)

def db_connection():
    conn = None
    try:
         conn = sqlite3.connect("task_list.sqlite")
    except sqlite3.Error as e:
        print(e)
    return conn


    

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    conn = db_connection()
    cursor = conn.cursor()


    if request.method == "GET":
         sort_by = request.args.get("sort_by", "id")  
         order = request.args.get("order", "asc")  
         filter_status = request.args.get("filter_status", None)

        
         sql = f"SELECT * FROM task_list"
         if filter_status:
            sql += f" WHERE Status='{filter_status}'"
         sql += f" ORDER BY {sort_by} {order}"

         cursor.execute(sql)
         page = request.args.get('page', default=1, type=int)
         per_page = request.args.get('per_page',default=3,type=int)
         offset = (page - 1) * per_page
         cursor.execute("SELECT * FROM task_list LIMIT ? OFFSET ?",(per_page,offset))
         tasks = [
            dict(id=row[0], Title=row[1], Description=row[2], DueDate=row[3],Status=row[4])
            for row in cursor.fetchall()]
         return jsonify(tasks)   

    if request.method == "POST":
        new_title = request.form["Title"]
        new_description = request.form["Description"]
        new_duedate = request.form["DueDate"]
        new_status = request.form["Status"]
        sql = """INSERT INTO task_list (Title, Description, DueDate,Status)
                 VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (new_title, new_description, new_duedate, new_status))
        conn.commit()
        return f"Task with the id: {cursor.lastrowid} created successfully", 201

@app.route("/tasks/<int:id>", methods=["GET", "PUT", "DELETE"])
def single_task(id):
    conn = db_connection()
    cursor = conn.cursor()
    task = None

    if request.method == "GET":
        cursor.execute("SELECT * FROM task_list WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            task = dict(id=row[0], Title=row[1], Description=row[2], DueDate=row[3], Status=row[4])
            return jsonify(task), 200
        else:
            return "Task not found", 404

    if request.method == "PUT":
        sql = """UPDATE task_list
                SET Title=?,
                    Description=?,
                    DueDate=?,
                    Status=?
                WHERE id=? """
        title = request.form["Title"]
        description = request.form["Description"]
        duedate = request.form["DueDate"]
        status = request.form["Status"]
        updated_task = {
            "id": id,
            "Title": title,
            "Description": description,
            "DueDate": duedate,
            "Status" : status,
        }
        cursor.execute(sql, (title, description, duedate, status, id))
        conn.commit()
        return jsonify(updated_task)

    if request.method == "DELETE":
        sql = """DELETE FROM task_list WHERE id=?"""
        cursor.execute(sql, (id,))
        conn.commit()
        return f"The task with id: {id} has been deleted.", 200

@app.route("/tasks/<int:id>/complete", methods=["PUT"])
def complete_task(id):
    conn = db_connection()
    cursor = conn.cursor()
    sql = """UPDATE task_list
             SET Status='Completed'
             WHERE id=?"""
    cursor.execute(sql, (id,))
    conn.commit()
    return f"The task with id: {id} has been marked as completed.", 200

class TestTaskAPI(unittest.TestCase):

    def setUp(self):
        
        self.app = app.test_client()
        self.app.testing = True

        
        self.conn = db_connection()
        self.cursor = self.conn.cursor()

    def tearDown(self):
        
        self.conn.close()

    def test_get_tasks(self):
        
        response = self.app.get('/tasks')

        
        self.assertEqual(response.status_code, 200)

        

    def test_post_task(self):
        
        data = {
            'Title': 'Test Task',
            'Description': 'This is a test task',
            'DueDate': '2023-12-31',
            'Status': 'Pending'
        }
        response = self.app.post('/tasks', data=data)

        
        self.assertEqual(response.status_code, 201)

        

    def test_get_single_task(self):
        
        response = self.app.get('/tasks/1')

        
        self.assertEqual(response.status_code, 200)

        

    def test_complete_task(self):
        
        response = self.app.put('/tasks/1/complete')

        
        self.assertEqual(response.status_code, 200)

        

if __name__ == "__main__":
    app.run(debug=True)
    unittest.main()