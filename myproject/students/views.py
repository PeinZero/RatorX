from flask import Blueprint,render_template,redirect,url_for,flash,session
from myproject import db,g
from myproject.models import Student, Teacher, Settings
from myproject.students.forms import SignUp,LogIn,ProfileTab,AccountTab,PrivacyTab,DeactivateTab
from myproject.search.form import Searching
from sqlalchemy import func

students_blueprint = Blueprint('students', __name__ , template_folder='templates/students')

@students_blueprint.route('/signup',  methods=['GET', 'POST'])
def signup():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))
    
    form = SignUp()
    signupFailed1 = False
    signupFailed2 = False
    signupFailed3 = False

    if form.validate_on_submit():
        fname = form.fname.data.lower()
        lname = form.lname.data.lower()
        uname = form.uname.data.lower()
        email = form.email.data.lower()
        password1 = form.password1.data
        password2 = form.password2.data
        checkTeacherEmail = bool(Teacher.query.filter_by(teacher_email = email).first())
        checkStudentEmail = bool(Student.query.filter_by(student_email=email).first())
        checkTeacherUname = bool(Teacher.query.filter(func.lower(Teacher.teacher_uname) == func.lower(uname)).first())
        checkStudentUname = bool(Student.query.filter(func.lower(Student.student_uname) == func.lower(uname)).first())

         
        if checkTeacherUname or checkStudentUname: # Check if Uname is already taken
            return render_template('signup.html',form=form, signupFailed1 = True, searchForm = searchForm)      
        elif checkTeacherEmail or checkStudentEmail:  # Check if Email is already registered
            return render_template('signup.html',form=form, signupFailed2 = True, searchForm = searchForm)
       

        if password1 != '' and password1 == password2:
                new_student = Student(fname, lname, uname, email, password1, 0, 0, 0, 0, "", True, 1)
                db.session.add(new_student)
                db.session.commit()
                settings = Settings(new_student.id, True, True)
                db.session.add(settings)
                db.session.commit()
                return redirect(url_for('students.login'))
        else:
            return render_template('signup.html',form=form, signupFailed3 = True, searchForm = searchForm)
    
    return render_template('signup.html',form=form, searchForm = searchForm )


@students_blueprint.route('/login' , methods =['GET' , 'POST'])
def login():

    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))
    
    form = LogIn()
    loginFailed = False

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        CheckStudent = Student.query.filter_by(student_email = email).first()

        if CheckStudent != None and CheckStudent.student_email == email and CheckStudent.check_password(password):
            g.studentLoggedIn = True
            g.whichStudent = CheckStudent
            return redirect( url_for('index') )
        else:
            return render_template('login.html' , form=form , loginFailed = True, searchForm = searchForm)

    return render_template('login.html', form=form, loginFailed = False, searchForm = searchForm)
            
@students_blueprint.route('/' )
def signout():
    g.studentLoggedIn = False
    g.whichStudent = False 
    return redirect( url_for('index') )

@students_blueprint.route('/profile',  methods =['GET' , 'POST'])
def profile():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    form = ProfileTab()

    if form.validate_on_submit():
        user = Student.query.filter_by(student_email = g.whichStudent.student_email).first()
        if form.uname.data != "":
            CheckUser = bool(
                (Teacher.query.filter(func.lower(Teacher.teacher_uname) == func.lower(form.uname.data)).first())
                or
                (Student.query.filter(func.lower(Student.student_uname) == func.lower(form.uname.data)).first())
            )
            if not CheckUser:
                user.student_uname = form.uname.data
            else:
                pass
        if form.fname.data != "":
            user.student_fname = form.fname.data
        if form.lname.data != "":
            user.student_lname = form.lname.data
        if form.bio.data != "":
            user.student_bio = form.bio.data    
        db.session.add(user)
        db.session.commit()
        g.whichStudent = user
        form.fname.data = ""
        form.lname.data = ""
        form.bio.data = ""

    return render_template('profile.html', form = form, studentLoggedIn = g.studentLoggedIn , fname = g.whichStudent.student_fname.capitalize() , lname =g.whichStudent.student_lname.capitalize() , uname = g.whichStudent.student_uname, bio = g.whichStudent.student_bio, searchForm = searchForm )   


@students_blueprint.route('/photo'  , methods =['GET' , 'POST'])
def photo():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    return render_template('photo.html' , studentLoggedIn = g.studentLoggedIn , fname = g.whichStudent.student_fname, lname = g.whichStudent.student_lname,searchForm = searchForm) 

@students_blueprint.route('/account',  methods =['GET' , 'POST'] )
def account():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))
    
    form = AccountTab()
    passwordChangeFailed = False 
    passwordMatchFailed = False 

    if form.validate_on_submit():
        user = Student.query.filter_by(student_email = g.whichStudent.student_email).first()
        if not user.check_password(form.password1.data):
            passwordChangeFailed = True
            return render_template('account.html', form = form, studentLoggedIn = g.studentLoggedIn, fname = g.whichStudent.student_fname,
            lname = g.whichStudent.student_lname, passwordChangeFailed = passwordChangeFailed,passwordMatchFailed = passwordMatchFailed , userEmail = g.whichStudent.student_email, searchForm = searchForm) 
            
        if form.password2.data == form.password3.data:
            user.hash_password(form.password2.data)
            db.session.add(user)
            db.session.commit()
            g.whichStudent = user
        else:
            passwordMatchFailed = True

    return render_template('account.html', form = form, studentLoggedIn = g.studentLoggedIn, fname = g.whichStudent.student_fname,
        lname = g.whichStudent.student_lname,passwordChangeFailed = passwordChangeFailed,passwordMatchFailed = passwordMatchFailed , userEmail = g.whichStudent.student_email, searchForm = searchForm ) 

@students_blueprint.route('/payment_method' , methods =['GET' , 'POST'])
def payment_method():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    return render_template('payment_method.html' , studentLoggedIn = g.studentLoggedIn , fname = g.whichStudent.student_fname, lname = g.whichStudent.student_lname,  searchForm = searchForm)

@students_blueprint.route('/privacy',  methods =['GET' , 'POST']  )
def privacy():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    form = PrivacyTab()
    if form.validate_on_submit():
        user = Student.query.filter_by(student_email = g.whichStudent.student_email).first()
        if form.validate_on_submit():
            print(form.displayRank.data)
            print(form.displayStats.data)

            # additional code here
           
    return render_template('privacy.html', form = form, studentLoggedIn = g.studentLoggedIn ,  fname = g.whichStudent.student_fname, lname = g.whichStudent.student_lname,  searchForm = searchForm)  

@students_blueprint.route('/deactivate_account' ,  methods =['GET' , 'POST'] )
def deactivate_account():
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    form = DeactivateTab()
    passwordMatchFailed = False 
    if form.validate_on_submit():
        user = Student.query.filter_by(student_email = g.whichStudent.student_email).first()
       
        if user.check_password(form.password.data):
            
            settings = Settings.query.filter_by(student_id = g.whichStudent.id).first()
            db.session.delete(user)
            db.session.delete(settings)
            db.session.commit()
            whichStudent = False
            g.studentLoggedIn = False
            return redirect( url_for('students.signout') )
        else:
            passwordMatchFailed = True 

    return render_template('deactivate_account.html' , form = form, studentLoggedIn = g.studentLoggedIn , fname = g.whichStudent.student_fname, lname = g.whichStudent.student_lname, passwordMatchFailed = passwordMatchFailed, searchForm = searchForm)


@students_blueprint.route('/<uname>' , methods =['GET' , 'POST'])
def public_profile(uname):
    searchForm = Searching()
    if searchForm.searched.data != '' and  searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))

    student = Student.query.filter_by(student_uname = uname).first()
    return render_template('spublic_profile.html', student=student, searchForm = searchForm)
