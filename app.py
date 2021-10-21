from flask import Flask
from flask import render_template
from flask import request,session
import sqlite3
from flask import Flask, redirect, url_for, request

app = Flask(__name__)

conn = sqlite3.connect('cattledoc.db')
c = conn.cursor()

# c.execute('CREATE TABLE(DOC_ID TEXT PRIMARY KEY ,DOC_NAME TEXT NOT NULL, DOC_PSWD TEXT NOT NULL)')
# c.execute("INSERT INTO DOC VALUES ('KADOC069','Dr. Ram', '12345')")
# c.execute('DROP TABLE MEDICATION')

#### TO EMPTY DB
# c.execute('DELETE FROM CATTLE')
# c.execute('DELETE FROM MEDICATION')
# c.execute('DELETE FROM OWNER')
# c.execute('DELETE FROM UPDATES')

# c.execute('CREATE TABLE OWNER(ID TEXT PRIMARY KEY, NAME TEXT NOT NULL, PHONE INTEGER NOT NULL, ADRESS TEXT NOT NULL, EMAIL_ID TEXT NOT NULL, CATTLE_NO INTEGER NOT NULL )')
# c.execute('CREATE TABLE CATTLE(CATTLE_ID TEXT PRIMARY KEY, OWNER_ID TEXT NOT NULL, AGE INTEGER NOT NULL, BREED TEXT NOT NULL)')
# c.execute('CREATE TABLE MEDICATION(CATTLE_ID TEXT NOT NULL, MED_NAME TEXT NOT NULL, MED_DATE TEXT NOT NULL, MED_S_NO TEXT PRIMARY KEY)')
# c.execute('CREATE TABLE TRIGGER(CATTLE_ID TEXT, OWNER_ID TEXT NOT NULL, AGE INTEGER NOT NULL, BREED TEXT NOT NULL)')
# c.execute('ALTER TABLE TRIGGER RENAME TO UPDATES')
# c.execute('ALTER TABLE DOC RENAME TO DOCTOR')


@app.route('/')
def home():
   return redirect(url_for('login'))

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      usr_id=request.form['log_id']
      usr_password=request.form['log_password']
      conn = sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      query1= f'SELECT * FROM DOCTOR WHERE DOC_ID="{usr_id}" AND DOC_PSWD="{usr_password}"'
      rows=c.execute(query1)
      rows=rows.fetchall()
      conn.commit()
      conn.close()
      if len(rows)==1:
         return redirect(url_for('dashboard',usr=usr_id))
      else:
         return redirect(url_for('auth_error'))
   else:
      return render_template('login.html')

@app.route('/auth_error')
def auth_error():
   if request.method == "POST":
      return redirect(url_for('login'))
   else:
      return render_template('alert.html')

@app.route('/dashboard/<usr>')
def dashboard(usr):
   conn = sqlite3.connect('cattledoc.db')
   c=conn.cursor()
   c.execute(f'SELECT DOC_ID, DOC_NAME FROM DOCTOR WHERE DOC_ID="{usr}"')
   doc = c.fetchone()
   conn.commit()
   conn.close()
   return render_template('dashboard.html',doc = doc)

@app.route('/cattle/<cattle_id>', methods = ['POST', 'GET'])
def cattle(cattle_id):
   if request.method == "POST":
      conn = sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      s_no=request.form['s_no']
      name=request.form['name']
      date=request.form['date']
      print(date)
      print(name)
      c.execute(f"INSERT INTO MEDICATION VALUES ('{cattle_id}','{name}','{date}','{s_no}')")
      conn.commit()
      conn.close()
      return redirect(f'/cattle/{cattle_id}')
   else:
      conn = sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f'SELECT * FROM CATTLE WHERE CATTLE_ID="{cattle_id}"')
      c_data = c.fetchone()
      c.execute(f'SELECT * FROM MEDICATION WHERE CATTLE_ID="{cattle_id}"')
      m_data = c.fetchall()
      conn.commit()
      conn.close()
      return render_template('cattle.html',cattle_data = c_data ,medication_data = m_data)

@app.route('/delete/<c_id>/<s_no>',methods = ["POST","GET"])
def delete_med(s_no,c_id):
   conn=sqlite3.connect('cattledoc.db')
   c=conn.cursor()
   c.execute(f"DELETE FROM MEDICATION WHERE MED_S_NO='{s_no}'")
   conn.commit()
   conn.close()
   return redirect(f"/cattle/{c_id}")

@app.route('/dashboard/add_owner',methods = ["POST","GET"])
def add_owner():
   if request.method == "POST":
      id_=request.form['id_']
      name=request.form['name']
      phone=request.form['phone']
      adress=request.form['address']
      emailid=request.form['emailid']
      nocattle=request.form['nocattle']
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f"INSERT INTO OWNER VALUES ('{id_}','{name}',{phone},'{adress}','{emailid}',{nocattle})")
      conn.commit()
      conn.close()
      return render_template('db-created.html')
   else:
      return render_template('add_owner.html')

@app.route('/dashboard/owner-details',methods = ["POST","GET"])
def owner_details():
   if request.method == "POST":
      search_query=request.form['search']
      print(search_query)
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f"SELECT * FROM OWNER WHERE NAME='{search_query}' OR ID='{search_query}'")
      owner_details = c.fetchall()
      print(owner_details)
      
      cattle_details = []
      for i in owner_details:
         c.execute(f"SELECT * FROM CATTLE WHERE OWNER_ID='{i[0]}'")
         cattle_details = c.fetchall()
      
      print(cattle_details)
      conn.commit()
      conn.close()
      return render_template("owner_details.html",o_data = owner_details,c_data = cattle_details)
   else:
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute("SELECT * FROM OWNER")
      owner_details = c.fetchall()
      c.execute("SELECT * FROM CATTLE")
      cattle_details = c.fetchall()
      conn.commit()
      conn.close()
      return render_template("owner_details.html",o_data = owner_details,c_data = cattle_details)

@app.route('/delete/<id_>',methods = ["POST","GET"])
def delete(id_):
   conn=sqlite3.connect('cattledoc.db')
   c=conn.cursor()
   c.execute(f"DELETE FROM OWNER WHERE ID='{id_}'")
   conn.commit()
   conn.close()
   return redirect(url_for("owner_details"))

@app.route('/delete-cattle/<id_>',methods = ["POST","GET"])
def deleteCattle(id_):
   conn=sqlite3.connect('cattledoc.db')
   c=conn.cursor()
   c.execute(f"SELECT * FROM CATTLE WHERE CATTLE_ID='{id_}'")
   triggered_element = c.fetchone()
   c.execute(f"INSERT INTO UPDATES VALUES ('{triggered_element[0]}','{triggered_element[1]}',{triggered_element[2]},'{triggered_element[3]}')")
   c.execute(f"DELETE FROM CATTLE WHERE CATTLE_ID='{id_}'")
   conn.commit()
   conn.close()
   return redirect(url_for("owner_details"))

@app.route('/update/<id_>',methods = ["POST","GET"])
def update(id_):
   if request.method == "POST":
      name=request.form['name']
      phone=request.form['phone']
      adress=request.form['address']
      emailid=request.form['emailid']
      nocattle=request.form['nocattle']
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()

      c.execute(f"UPDATE OWNER SET NAME='{name}',PHONE={phone},ADRESS='{adress}',EMAIL_ID='{emailid}',CATLLE_NO={nocattle} WHERE ID='{id_}';")
      conn.commit()
      conn.close()
      return redirect(url_for("owner_details"))
   else:
      return render_template("update_owner.html")

@app.route('/update-cattle/<id_>',methods = ["POST","GET"])
def updateCattle(id_):
   if request.method == "POST":
      age=request.form[f'age']
      breed=request.form[f'breed']
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f"UPDATE CATTLE SET AGE={age},BREED='{breed}' WHERE CATTLE_ID='{id_}'")
      conn.commit()
      conn.close()
      return redirect(url_for("owner_details"))
   else:
      return render_template("update_cattle.html")

@app.route('/add-cattle/<id_>',methods = ["POST","GET"])
def addCattle(id_):
   if request.method == "POST":
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f"SELECT CATLLE_NO FROM OWNER WHERE ID='{id_}'")
      c_no = c.fetchone()
      
      for i in range(c_no[0]):
         cid_=request.form[f'id_{i}']
         age=request.form[f'age_{i}']
         breed=request.form[f'breed_{i}']
         c.execute(f"INSERT INTO CATTLE VALUES ('{cid_}','{id_}',{age},'{breed}')")
         conn.commit()
      conn.close()
      return redirect(url_for("owner_details"))
   else:
      conn=sqlite3.connect('cattledoc.db')
      c=conn.cursor()
      c.execute(f"SELECT CATLLE_NO FROM OWNER WHERE ID='{id_}'")
      c_no = c.fetchone()
      conn.commit()
      conn.close()
      return render_template("add_cattle.html",cattle_count = c_no[0])

@app.route('/dashboard/triggered',methods = ["GET"])
def triggered():
   conn=sqlite3.connect('cattledoc.db')
   c=conn.cursor()
   c.execute(f"SELECT * FROM UPDATES")
   t_details = c.fetchall()
   conn.commit()
   conn.close()
   return render_template("trigger.html",data = t_details)

conn.commit()
conn.close()

if __name__ == '__main__':
   app.run(debug = True)