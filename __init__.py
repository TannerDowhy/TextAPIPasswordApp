from flask import Flask, render_template, flash, request, url_for, redirect
from twilio import twiml
from dbconnect import connection
from wtforms import Form, StringField, validators
from MySQLdb import escape_string as thwart
import gc

app = Flask(__name__)
woken_up = False


@app.route('/', methods=["GET"])
def homepage():
    c, conn = connection()
    c.execute("SELECT * FROM passwords")
    list_all = c.fetchall()
    c.close()
    conn.close()
    gc.collect()
    return render_template('index.html', pws=list_all)
    # return render_template('index.html')


class CreateForm(Form):
    name = StringField('name', [validators.required()])
    password = StringField('password', [validators.required()])


@app.route('/create/', methods=["GET", "POST"])
def create_pw():
    try:
        form = CreateForm(request.form)

        if request.method == "POST":
            name = form.name.data
            password = form.password.data
            c, conn = connection()

            x = c.execute("SELECT * FROM passwords WHERE name = ('{0}')".format(thwart(name)))

            if int(x) > 0:
                flash("That entry already exists.")
                return render_template('create.html', form=form)
            else:
                c.execute("INSERT INTO passwords (name, password) VALUES ('{0}', '{1}')".format(thwart(name),
                                                                                                thwart(password)))
                conn.commit()

                flash("PW entered.")

                c.close()
                conn.close()
                gc.collect()

        return render_template('create.html', form=form)

    except Exception as e:
        return str(e)


def create_from_text(name, password):
    try:
        c, conn = connection()

        x = c.execute("SELECT * FROM passwords WHERE name = ('{0}')".format(thwart(name)))

        if int(x) > 0:
            flash("That entry already exists.")
        else:
            c.execute(
                "INSERT INTO passwords (name, password) VALUES ('{0}', '{1}')".format(thwart(name), thwart(password)))
            conn.commit()

            flash("PW entered.")

            c.close()
            conn.close()
            gc.collect()

    except Exception as e:
        return str(e)


def delete_from_text(name, password):
    try:
        c, conn = connection()

        x = c.execute("SELECT * FROM passwords WHERE name = ('{0}')".format(thwart(name)))

        if int(x) <= 0:
            flash("That entry doesn't exist.")
        else:

            c.execute(
                "DELETE FROM passwords WHERE name = '{0}' AND password = '{1}'".format(thwart(name), thwart(password)))
            conn.commit()

            flash("PW deleted.")

            c.close()
            conn.close()
            gc.collect()

    except Exception as e:
        return str(e)


def edit_from_text(name, password, new_name, new_password):
    try:
        c, conn = connection()

        c.execute(
            "UPDATE passwords SET name = '{0}', password = '{1}' WHERE name = '{2}' AND password = '{3}'"
                .format(thwart(new_name), thwart(new_password), thwart(name), thwart(password)))
        conn.commit()

        flash("PW Updated.")

        c.close()
        conn.close()
        gc.collect()

    except Exception as e:
        return str(e)


def show_from_text(name):
    try:
        c, conn = connection()

        c.execute(
            "Select * FROM passwords WHERE name = '{0}'"
                .format(thwart(name)))
        conn.commit()

        single_return = c.fetchone()
        c.close()
        conn.close()
        gc.collect()
        return single_return[2]

    except Exception as e:
        return str(e)


@app.route('/sms', methods=['POST'])
def sms():
    global woken_up
    message_body = request.form['Body']

    if message_body == ("Password"):
        woken_up = True
        resp = twiml.Response()
        resp.message("Commands are:\n\"Add [name] [password]\"\n\"Delete [name] [password]\"\n \"Edit [name] "
                     "[passsword] [new name] [new password]\"\n \"List\"\n")
        return str(resp)
    else:
        if woken_up == True:
            params = message_body.split()
            if params[0] == ("Add"):
                create_from_text(params[1], params[2])
                resp = twiml.Response()
                resp.message("Yay")
                return str(resp)
            if params[0] == ("Delete"):
                delete_from_text(params[1], params[2])
                resp = twiml.Response()
                resp.message("Deleted Password.")
                return str(resp)
            if params[0] == ("Edit"):
                edit_from_text(params[1], params[2], params[3], params[4])
                resp = twiml.Response()
                resp.message("Password Updated.")
                return str(resp)
            if params[0] == ("Show"):
                entry = show_from_text(params[1])
                resp = twiml.Response()
                resp.message(str(entry))
                return str(resp)
        else:
            resp = twiml.Response()
            resp.message("To wake the server up type 'Password'.")
            return str(resp)


if __name__ == "__main__":
    app.secret_key = 'cookies'
    app.run()
