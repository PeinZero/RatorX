from flask import Blueprint,render_template,redirect,url_for,flash,session
from myproject import db,g
from myproject.models import Student
from myproject.students.forms import SignUp,LogIn,ShiftControl

students_blueprint = Blueprint('students', __name__ , template_folder='templates/students')

@students_blueprint.route('/signup',  methods=['GET', 'POST'])
def signup():
    form = SignUp()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 != '' and password1 == password2:
            new_student = Student(name,email,password1)
            db.session.add(new_student)
            db.session.commit()

            return redirect(url_for('index'))
    
    return render_template('signup.html',form=form )


@students_blueprint.route('/login' , methods =['GET' , 'POST'])
def login():
    form = LogIn()
    loginFailed = False

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        checkEmail = bool(Student.query.filter_by(student_email = email).first())

        if checkEmail:
            CheckStudent = Student.query.filter_by(student_email = email).first()

            if CheckStudent.student_email == email and CheckStudent.student_password == password:
                g.studentLoggedIn = True
                return redirect( url_for('index') )
            else:
                return render_template('login.html' , form=form , loginFailed = True)

        else:
            return render_template('login.html' , form=form , loginFailed = True)

    return render_template('login.html', form=form, loginFailed = False)
            
@students_blueprint.route('/' )
def signout():
    g.studentLoggedIn = False
    return redirect( url_for('index') )
