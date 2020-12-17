from myproject import app
from myproject import g
from myproject.search.form import Searching
from myproject.models import Assignments, Saved_Assignemnts
from sqlalchemy import desc
from flask import render_template,redirect,url_for

g.init()

@app.route('/' ,methods=['GET', 'POST'])
def index():
    searchForm = Searching()
    studentLoggedIn = g.studentLoggedIn
    teacherLoggedIn = g.teacherLoggedIn
    
  
    all_assignments = Assignments.query.order_by(Assignments.assignment_rating.desc()).limit(20) #preference wala first kaam to howa wa hy
    # all_assignments = Assignments.query.all()

    #----------------------isko test kr lena aur khain bheja nehi hy mene do what ever you want from here----------------------
    display_assignments = []
    if studentLoggedIn:
        for assignment in Saved_Assignemnts.query.filter_by(student_id = g.whichStudent.id).all():
            c_id = assignment.assignment.course.id
            for prefed_assignment in Assignments.query.filter_by(course_id = c_id).all():
                if prefed_assignment != assignment: #basically kiye howe assignments wapis na dikhaye usko
                    display_assignments.append(prefed_assignment)
        
        print(display_assignments) #this working Perfectly so far (ab display krwa dena isko)
    #---------------------------------------------------------------------------------------------------------------------------


    if searchForm.validate_on_submit():
        return redirect(url_for('search.searching', searched = searchForm.searched.data))
    
    return render_template('home.html' , studentLoggedIn = studentLoggedIn , teacherLoggedIn = teacherLoggedIn, all_assignments = all_assignments, searchForm =searchForm)

if __name__ == '__main__':
    app.run(debug=True)