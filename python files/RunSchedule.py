from SchedulingData import SchedulingData
from SchedulingAlgorithm import ScheduleCourses
import os.path
# TODO: Create a counter to compare requests to offerings - make sure enough offerings for requests
# TODO: Create report to report class rosters
# TODO: Create report for semester/period/class/(#enrolled/available)


def main():
    print("Loading Data")
    current_directory = os.path.dirname(__file__)
    schedule_data = SchedulingData(3, 8)
    schedule_data.input_course_data(current_directory + "/../Courses.csv")
    schedule_data.input_student_data(current_directory + "/../Cadets.csv")
    schedule_data.input_sport_data(current_directory + "/../Sports.csv")
    schedule_data.input_pco(current_directory + "/../PCO.csv")
    schedule_data.input_student_demand(current_directory + "/../Demand.csv")
    schedule_data.add_pe_courses()
    schedule_data.add_armnshp_courses()
    print("Read in {} course requests".format(len(schedule_data.unscheduled_course_requests)))
    # schedule_data.print_unscheduled_report()

    scheduler = ScheduleCourses(schedule_data)
    scheduler.match_courses_greedy_algorithm()
    print("Scheduler Complete")
    print("--------------Unscheduled Courses--------------")
    #schedule_data.print_unscheduled_report()
    print("--------------Student Schedules----------------")
    schedule_data.student_lookup.output_student_schedules("Schedule Data.csv")
    schedule_data.student_lookup.print_student_schedule(next(iter(schedule_data.student_lookup.students)))
    #schedule_data.student_lookup.print_all_schedules(1)

main()
