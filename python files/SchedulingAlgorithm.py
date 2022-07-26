from SchedulingData import SchedulingData, StudentCourseRequest, CourseOffering
from queue import PriorityQueue
import random

#TODO: Need to handle double periods
#TODO: Need to handle multi-day courses (Athletes) IC-M, IC-T courses and all atheletes add as a required course
#TODO: Scan course requests- build #sections/course based on min enrollment numbers - assign sections to random (or not) periods
#TODO: adapt method to schedule all courses at the same time rather than by semester (student request by course, not course-semester)
class ScheduleCourses:

    def __init__(self, schedule_data: SchedulingData):
        self.schedule_data = schedule_data
        self.unscheduled_priority_queue: PriorityQueue = PriorityQueue()
        self.schedule_conflict = []

    def create_unscheduled_priority_queue(self):
        self.unscheduled_priority_queue.empty()
        for unscheduled_item in self.schedule_data.unscheduled_course_requests:
            class_density = self.schedule_data.course_data.get_number_periods_and_students(
                    unscheduled_item.course_name) #(num_periods, #seats)
            student_courses = self.schedule_data.student_lookup.students[unscheduled_item.student_name]['requests']          
            busy_periods = 0
            for course in student_courses:
                busy_periods += \
                self.schedule_data.course_data.courses[course.course_name].contact
            student_free_periods = 24 - busy_periods
            objective_value = self.normalize_student_flexibility(student_free_periods) * \
                              self.normalize_number_course_periods_to_min(class_density[0]) * \
                              self.normalize_number_seats(class_density[1]) + 0.01*random.random()
            pqItem = (objective_value, unscheduled_item)
            # print(pqItem) # for debugging
            self.unscheduled_priority_queue.put(pqItem)

    @staticmethod
    def normalize_number_courses_student_to_min(number_classes):
        if number_classes > 14:
            return 0
        if number_classes <= 9:
            return 1
        return (15 - number_classes) / 9
        
    @staticmethod
    def normalize_student_flexibility(free_periods):
        # Alt 
        if free_periods <= 0:
            return 0
        elif free_periods >= 15:
            return 1
        else:
            return (free_periods / 15)

    @staticmethod
    def normalize_number_course_periods_to_min(number_periods):
        return (number_periods - 1) / 8 + 0.01

    @staticmethod
    def normalize_number_seats(number_seats):
        if number_seats < 30:
            return 0.1
        if number_seats < 100:
            return 0.5
        return 1

    def match_courses_greedy_algorithm(self):
        # capture initial amount for reporting
        number_courses_to_schedule = len(self.schedule_data.unscheduled_course_requests)
        # create priority queue for order of challenging schedules
        self.create_unscheduled_priority_queue()

        while self.unscheduled_priority_queue.qsize() > 0:
            course_to_schedule: StudentCourseRequest = self.unscheduled_priority_queue.get()[1]
            # Find which periods are available: [(semester, period)]
            available_periods = self.schedule_data.course_data.get_course_periods_available(
                course_to_schedule.course_name)
            if len(available_periods) == 0:
                print("No course period available for",course_to_schedule.course_name)
                self.schedule_conflict.append(course_to_schedule)
                continue

            # eliminate periods from the available list: [(semester, period)]
            scheduled_periods = self.schedule_data.student_lookup.list_periods_scheduled(
                course_to_schedule.student_name)
                
            # Include artificial periods in scheduled periods to avoid double period conflicts
            # If scheduled period is odd then add an artificial period before 
            # For example, if period 1 (M2) then add artificial in 0 (M1)
            if self.schedule_data.course_data.courses[course_to_schedule.course_name].contact == 2:
                to_add = []
                for period in scheduled_periods:
                    if period[1] % 2 == 1:
                        to_add.append((period[0], period[1]-1))
                        
            # create lookup of course load (TODO: ac only) by semester
            course_load_by_semester = [0, 0, 0]
            
            # Remove available periods based on current schedule
            # and calculate current course load distribution
            for period in scheduled_periods:
                course_load_by_semester[period[0]] += 1
                if period in available_periods:
                    available_periods.remove(period)

            if len(available_periods) == 0:
                # no periods exist
                self.schedule_conflict.append(course_to_schedule)
                continue
            
            # create a list of best choices for each semester
            # best choice is the one with most seats available
            # list values are (period, seats available) tuples
            available_by_semester = [None, None, None]
            for period in available_periods:
                seats = self.schedule_data.course_data.lookupByPeriod[
                period[0]][period[1]][course_to_schedule.course_name].number_seats_available()
                
                if available_by_semester[period[0]] is None:
                    available_by_semester[period[0]] = (period[1], seats)
                elif seats > available_by_semester[period[0]][1]:
                    available_by_semester[period[0]] = (period[1], seats)
                
            # pick a course that distributes their course load across trimesters
            # and then the period with the most seats available
            period = None
            for i in range(len(available_by_semester)):
                if available_by_semester[i] is None:
                    continue
                if period is None:
                    # first semester with an available course
                    period = (i, available_by_semester[i][0])
                elif course_load_by_semester[i] < course_load_by_semester[period[0]]:
                    # current semester load is less than current best choice
                    period = (i, available_by_semester[i][0])
                elif course_load_by_semester[i] == course_load_by_semester[period[0]] and \
                available_by_semester[i][1] > available_by_semester[period[0]][1]:
                    # current semester load is same as current best choice but
                    # current availability is better than current best choice
                    period = (i, available_by_semester[i][0])

            course_offering: CourseOffering = self.schedule_data.course_data.lookupByPeriod[
                period[0]][period[1]][course_to_schedule.course_name]
            self.schedule_data.assign_student_to_course(course_to_schedule, course_offering)

        # print("Scheduler Completed.  {} courses scheduled, {} conflicts were unresolved".format(
            # number_courses_to_schedule, self.unscheduled_priority_queue.qsize()))
            
        print("Scheduler Completed.  {} courses scheduled, {} conflicts were unresolved".format(
            number_courses_to_schedule-len(self.schedule_conflict), len(self.schedule_conflict)))

