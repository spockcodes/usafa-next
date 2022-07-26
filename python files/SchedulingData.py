import csv

class Course:
    """Stores information about a single course"""
    def __init__(self, course_name, dept, credits, contact, min_seats, max_seats):
        self.course_name = course_name
        self.dept = dept
        self.credits = credits
        self.contact = contact
        self.min_seats = min_seats
        self.max_seats = max_seats

class CourseOffering:
    """Stores information for a single course"""
    period_lookup = {
    0: 'M1',
    1: 'M2',
    2: 'M3',
    3: 'M4',
    4: 'T1',
    5: 'T2',
    6: 'T3',
    7: 'T4'
    }

    semester_lookup = {
    0: 'Fall',
    1: 'Winter',
    2: 'Spring'
    }
    def __init__(self, course_name, semester, period, number_seats, course_info):
        """initializes a new instance of the object
        course_name: eg CompSci 110 or CompSci 110S
        semester: 0 (fall), 1 (winter), or 2 (spring)
        period: 0 (M1) - 7 (T4)
        number_seats: max capacity * number of simultaneous sections
        """
        self.course_name = course_name 
        self.period = period
        self.semester = semester
        self.number_seats_total = number_seats
        self.course_info = course_info # Course object
        self.students_enrolled = []

    def number_seats_available(self):
        return self.number_seats_total - len(self.students_enrolled)

class Student:
    """Stores info about a student"""
    def __init__(self, student_name, year, sport=None, gender=None):
        self.student_name = student_name
        self.year = year
        self.sport = sport
        self.gender = gender
        
    def get_flexibility(self, requests):
        busy_periods = 0
        for course in requests:
            busy_periods += \
            self.schedule_data.course_data.courses[course.course_name].contact
        
class SportInfo:
    """Stores info about each team like when they practice and their offseason"""
    def __init__(self, sport, gender, practice_m, practice_t, offseason):
        self.sport = sport
        self.gender = gender
        self.practice_m = practice_m # period 0 or 3
        self.practice_t = practice_t # period 0 or 3
        self.offseason = offseason # may be useful if IC's get more than period 4

class StudentCourseRequest:
    """Stores a student-course request and assignment (when made) pairing"""

    def __init__(self, student_name, course_name):
        self.student_name = student_name
        self.course_name = course_name

        self.assigned_course: CourseOffering = None

    def summary_request(self):
        return "{},{}".format(self.student_name,self.course_name)
        

class SchedulingData:
    """
    Stores the data structures for accessing and manipulating the schedule
    There are four primary data structures for accessing:
    - Unscheduled StudentCourseRequests - list of course requests that have not been matched
    - Course info not specific to a semester/period
    - Student Data Lookup by Student
    - Course Data Lookup:
    -- Course info not specific to semester/period
    -- Course Offering Lookup by Semester->Period->Name
    -- Course Offering Lookup by Semester->Name->Period
    """
    def __init__(self, number_semesters, number_periods):
        self.unscheduled_course_requests = []
        self.sport_info = {}
        self.student_lookup = StudentLookupData(number_semesters)
        self.course_data = CourseLookupData(number_semesters, number_periods)
        
    def input_course_data(self, csv_file_name):
        # Header: dept, subject, course number, credits, contact, periods, core, min, max
        with open(csv_file_name) as csvfile:
            course_reader = csv.reader(csvfile)
            header = True
            
            for row in course_reader:
                if header:
                    header = False
                    continue
                # course_name, dept, credits, contact, min_seats, max_seats
                course_name = row[1] + " " + row[2]
                course = \
                Course(course_name, row[0], row[3], int(row[5]), row[7], row[8])
                
                self.course_data.add_course_data(course)
                    
    def input_student_data(self, csv_file_name):
        # Header: cadet, year, squadron, major, sec major, sport, sport gender
        with open(csv_file_name) as csvfile:
            student_reader = csv.reader(csvfile)
            header = True
            
            row_num = 0
            for row in student_reader:
                if header:
                    header = False
                    continue
                    
                student_info = Student(row[0], row[1], row[5], row[6])
                
                self.student_lookup.add_student_info(student_info)
                
                row_num += 1
                
        print("Read in {} students".format(row_num))
                    

    def input_student_demand(self, csv_file_name):
        # Header: student ID, Semester, Course, Sec1, Sec2, Period, Subject, Number, course number, suffix, course lookup
        with open(csv_file_name) as csvfile:
            student_reader = csv.reader(csvfile)
            header = True
            
            for row in student_reader:
                if header:
                    header = False
                    continue
                
                if self.course_data.courses[row[10]].contact == 0:
                    continue
                    
                if row[1][:6] == "Summer":
                    if row[6] in ['Space', 'Cyber', 'ArmnShp', 'UAS']:
                        # Only scheduling these courses if in Fall/Spring
                        continue
                    
                student_course_request = StudentCourseRequest(row[0], row[10])
                
                self.student_lookup.add_course_request(student_course_request)
                self.unscheduled_course_requests.append(student_course_request)

    def input_pco(self, csv_file_name):
        # Header: Dept, Course, Contact, Semester, Period, Sections, Max
        with open(csv_file_name) as csvfile:
            course_reader = csv.reader(csvfile)
            header = True
            
            row_num = 0
            for row in course_reader:
                if header:
                    header = False
                    continue
                
                # Translate semester to integer
                if row[3] == "Fall":
                    semester = 0
                elif row[3] == "Winter":
                    semester = 1
                else:
                    semester = 2
                    
                # Translate period to integer
                if row[4][0] == "M":
                    period = int(row[4][1])-1 # M-day
                else:
                    period = int(row[4][1])+3 # T-day
                    
                # Number of seats
                num_seats = int(row[5])*int(row[6])
                
                course_offering = CourseOffering(row[1], semester, period, num_seats, self.course_data.courses[row[1]])
                self.course_data.add_course_offering(course_offering)
                
                row_num += 1
                
        print("Read in {} course offerings".format(row_num))
        
    def input_sport_data(self, csv_file_name):
        # Header: sport, gender, practiceM, practiceT, offseason, season
        with open(csv_file_name) as csvfile:
            sport_reader = csv.reader(csvfile)
            header = True
            
            for row in sport_reader:
                if header:
                    header = False
                    continue
                    
                if (row[0], row[1]) not in self.sport_info:
                    # Determine offseason
                    if row[4] == "Fall":
                        offseason = 0
                    elif row[4] == "Winter":
                        offseason = 1
                    else:
                        offseason = 2
                    
                self.sport_info[(row[0], row[1])] = \
                SportInfo(row[0], row[1], row[2], row[3], offseason)
                
    def add_pe_courses(self):
        # pe_lookup = {
        # ('practice_m', 'AM'): ['PhyEd 711','PhyEd 712','PhyEd 721','PhyEd 722','PhyEd 731','PhyEd 732'],
        # ('practice_t', 'AM'): ['PhyEd 715','PhyEd 716','PhyEd 725','PhyEd 726','PhyEd 735','PhyEd 736'],
        # ('practice_m', 'PM'): ['PhyEd 714','PhyEd 713','PhyEd 724','PhyEd 723','PhyEd 734','PhyEd 733'],
        # ('practice_t', 'PM'): ['PhyEd 718','PhyEd 717','PhyEd 728','PhyEd 727','PhyEd 738','PhyEd 737']
        # }
        pe_ic_lookup = {
        ('practice_m', 'AM'): ['PhyEd 711','PhyEd 721','PhyEd 731'],
        ('practice_t', 'AM'): ['PhyEd 715','PhyEd 725','PhyEd 735'],
        ('practice_m', 'PM'): ['PhyEd 714','PhyEd 724','PhyEd 734'],
        ('practice_t', 'PM'): ['PhyEd 718','PhyEd 728','PhyEd 738']
        }
        pe_lookup = ['PhyEd 701','PhyEd 702','PhyEd 703']
        num = 0
        for student, val in self.student_lookup.students.items():
            if not self.student_lookup.students[student]['requests']:
                continue
            if val['info'].sport == "":
                for i in range(3):
                    if i != num:
                        student_course_request = StudentCourseRequest(student, pe_lookup[i])
                        
                        self.student_lookup.add_course_request(student_course_request)
                        self.unscheduled_course_requests.append(student_course_request)
                num += 1
                if num > 2:
                    num = 0
            else:
                for day in ['practice_m', 'practice_t']:
                    time = getattr(self.sport_info[(val['info'].sport, val['info'].gender)], day)
                    off = self.sport_info[(val['info'].sport, val['info'].gender)].offseason
                    for pos, pe in enumerate(pe_ic_lookup[(day, time)]):
                        # if 2*off+1 == pos:
                            # continue
                        
                        student_course_request = StudentCourseRequest(student, pe)
                        
                        self.student_lookup.add_course_request(student_course_request)
                        self.unscheduled_course_requests.append(student_course_request)
                        
    def add_armnshp_courses(self):
        ip_lookup = {
        'ArmnShp 461': ['ArmnShp 461F', 'ArmnShp 461W', 'ArmnShp 461S'],
        'ArmnShp 465': ['ArmnShp 465F', 'ArmnShp 465W', 'ArmnShp 465S'],
        'ArmnShp 474': ['ArmnShp 474F', 'ArmnShp 474W', 'ArmnShp 474S'],
        'ArmnShp 475': ['ArmnShp 475F', 'ArmnShp 475W', 'ArmnShp 475S'],
        'ArmnShp 491': ['ArmnShp 491F', 'ArmnShp 491W', 'ArmnShp 491S'],
        'ArmnShp 496': ['ArmnShp 496F', 'ArmnShp 496W', 'ArmnShp 496S']
        }
        ip = ['ArmnShp 461','ArmnShp 465','ArmnShp 474','ArmnShp 475','ArmnShp 491','ArmnShp 496']
        for student, val in self.student_lookup.students.items():
            for item in val['requests']:
                if item in ip:
                    for request in ip_lookup[item]:
                        student_course_request = StudentCourseRequest(student, request)
                        
                        self.student_lookup.add_course_request(student_course_request)
                        self.unscheduled_course_requests.append(student_course_request)
                    break
                

    def assign_student_to_course(self, student_course_request: StudentCourseRequest, course_offering: CourseOffering):
        # Attach student course request to the course offering (and decrement counter)
        course_offering.students_enrolled.append(student_course_request)
        # Attach offering to the course request
        student_course_request.assigned_course = course_offering
        # Remove from the unassigned list
        self.unscheduled_course_requests.remove(student_course_request)

    def remove_student_from_course(self, student_name, semester, course_name, period):
        student_course_request: StudentCourseRequest = \
            self.student_lookup.students[student_name]['requests'] # how to find StudentCourseRequest in list?
        course_offering:CourseOffering = self.course_data.lookupByClassID[semester][course_name][period]
        course_offering.students_enrolled.remove(student_course_request)
        student_course_request.assigned_course = None
        self.unscheduled_course_requests.append(student_course_request)

    def print_unscheduled_report(self):
        for item in self.unscheduled_course_requests:
            print(item.summary_request())



class CourseLookupData:
    """
    Lookup data structures for courses by period/semester
    self.courses{course}
    lookupByPeriod:  [semester]->[periods]->{courseID}<-course_offering
    lookupByClassID:  [semester]->{courseID}->[period]<-course_offerings
    """
    def __init__(self, number_semesters, number_periods):
        self.courses = {}
        self.lookupByPeriod = []
        self.lookupByClassID = []
        self.number_periods = number_periods
        for i in range(number_semesters):
            self.lookupByPeriod.append([])  # semesters
            self.lookupByClassID.append({})
            for j in range(number_periods):
                self.lookupByPeriod[i].append({})  # periods
                
    def add_course_data(self, course_info: Course):
        self.courses[course_info.course_name] = course_info

    def add_course_offering(self, course_offering: CourseOffering):
        self.lookupByPeriod[course_offering.semester][course_offering.period][course_offering.course_name] = course_offering
        if course_offering.course_name not in self.lookupByClassID[course_offering.semester]:
            self.lookupByClassID[course_offering.semester][course_offering.course_name] = []
            # temp = self.lookupByClassID[course_offering.semester][course_offering.course_name]
            for i in range(self.number_periods):  #create array of periods
                self.lookupByClassID[course_offering.semester][course_offering.course_name].append(None)
        if self.lookupByClassID[course_offering.semester][course_offering.course_name][course_offering.period] is None:
            self.lookupByClassID[course_offering.semester][course_offering.course_name][course_offering.period]=course_offering
        else:
            temp_schedule = self.lookupByClassID[course_offering.semester][course_offering.course_name][course_offering.period]
            temp_schedule.number_seats_total = temp_schedule.number_seats_total + course_offering.number_seats_total
        
    def get_course(self, semester, course_name):
        return self.lookupByClassID[semester][course_name]

    def get_course_periods_available(self, course_name):
        """
        Gets the number of seats available per period for a course/semester pair
        :param course_name: course_name of interest
        :return: [(semester, period)]
        """
        offering_list = []
        for ind, semester in enumerate(self.lookupByClassID):
            if course_name in semester:
                for offering in semester[course_name]:
                    if offering is not None:
                        if offering.number_seats_total > 0:
                            offering_list.append((ind, offering.period))
        return offering_list

    def print_course_offering_report(self, semester, course_name):
        course_info = self.lookupByClassID[semester][course_name]
        if course_info is None:
            print(course_name, "does not have any scheduled offerings for semester", semester)
            return

        for period_offering in course_info:
            if period_offering is not None:
                print(semester, course_name, period_offering.period, period_offering.number_seats_total)

    def print_semester_course_report(self, semester):
        for course in self.lookupByClassID[semester].items():
            for period_offering in course:
                if period_offering is not None:
                    print(semester, period_offering.course_name, period_offering.period, period_offering.number_seats_total)

    def get_number_periods_and_students(self, course_name):
        """
        Returns the number of periods a course is offered and the number of seats offered
        :param course_name:
        :return: (number of periods, number of seats available)
        """
        num_periods = 0
        num_seats = 0
        for semester in self.lookupByClassID:
            if course_name in semester:
                for offering in semester[course_name]:
                    if offering is not None:
                        if offering.number_seats_total > 0:
                            num_periods += 1
                            num_seats += offering.number_seats_total
        return num_periods, num_seats


class StudentLookupData:
    """
    Stores students as a dictionary for easy retrieval by-name
    self.students{student_name}{'info'} <- Student
    self.students{student_name}{'requests'} <- [course_request]
    """

    def __init__(self, number_semesters):
        self.students = {}
        self.number_semesters = number_semesters
        
    def add_student_info(self, student_info: Student):
        """Adds the student info to the student"""
        if student_info.student_name not in self.students:
            self.students[student_info.student_name] = {
            'info': student_info,
            'requests': []
            }

    def add_course_request(self, student_course_request: StudentCourseRequest):
        """
        Adds the course request to the student
        """
        if student_course_request.student_name not in self.students:
            self.students[student_course_request.student_name] = {
            'info': None,
            'requests': []
            }

        self.students[student_course_request.student_name]['requests'].append(student_course_request)

    def list_periods_scheduled(self, student_name):
        """
        Returns a list of semester-period tuples that a student is scheduled
        This is used in the greedy algorithm to eliminate periods that a course
        is offered
        :param student_name: ID of student
        :return: [(semester, period)]
        """
        courses = self.students[student_name]['requests'] # list of student course requests
        periods = []
        for course in courses:
            if course.assigned_course is not None:
                periods.append((course.assigned_course.semester, course.assigned_course.period))
                
                if course.assigned_course.course_info.contact == 2:
                    periods.append((course.assigned_course.semester, course.assigned_course.period + 1))
                    
        return periods

    def print_student_schedule(self, student_name):
        courses = self.students[student_name]['requests']
        for course in courses:
            if course.assigned_course is None:
                print(course.course_name, "NOT ASSIGNED")
            else:
                print(course.course_name, "@", course.assigned_course.semester_lookup[course.assigned_course.semester], "period", course.assigned_course.period_lookup[course.assigned_course.period])

    def print_all_schedules(self, semester):
        for key, val in self.students.items():
            print("{} in Semester {}".format(key,semester))
            for course_request in val['requests']:
                if course_request.assigned_course is None:
                    print(course_request.course_name,"***Not Assigned***")
                elif course_request.assigned_course.semester == semester:
                    print(course_request.assigned_course.period,course_request.course_name)
                    
    def output_student_schedules(self, csv_file_name):
        with open(csv_file_name, 'w', newline='') as csvfile:
            schedule_writer = csv.writer(csvfile)
            
            # Write header: student, semester, course, period
            header = ['student', 'semester', 'course', 'period']
            schedule_writer.writerow(header)
            
            for key, val in self.students.items():
                for course_request in val['requests']:
                    row = [key] # Student name
                    if course_request.assigned_course is None:
                        row.append("") # semester
                        row.append(course_request.course_name)
                        row.append("") # period
                    else:
                        row.append(course_request.assigned_course.semester_lookup[course_request.assigned_course.semester])
                        row.append(course_request.course_name)
                        row.append(course_request.assigned_course.period_lookup[course_request.assigned_course.period])
                        
                    schedule_writer.writerow(row)

    def get_number_courses(self, student_name):
        return len(self.students[student_name])
        
    def get_flexibility(self, student_name):
        """
        calculates student scheduling flexibility for a given academic year:
        24 AY periods - the number of sections a student needs to be scheduled
        :param student_name: ID of student
        :returns an integer from 0-15 (assuming 9 is the min AY course load
        """
        periods = 0
        courses = self.students[student_name]
        for course in courses:
            periods += course.number_periods # doesnt work without Course object
            
        return (24 - periods)