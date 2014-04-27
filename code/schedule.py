#!/usr/bin/python
import calendar
import time

path = '/home/radiolab/mag-stream'

day, month, year = time.strftime("%d/%m/%Y").split("/")

# Get input
cal = calendar.month(int(year),int(month))
print cal

start_date = raw_input("Select start date: ")
start_time = raw_input("Start time (HH:MM): ").split(':')
assert len(start_time) == 2, "Invalid start time. Enter in format HH:MM. Cannot schedule tasks with greater precision than a minute."

end_date = raw_input("Select end date: ")
end_time = raw_input("End time (HH:MM:SS): ")
assert len(start_time) == 2, "Invalid end time. Enter in format HH:MM:SS."

# Verify
end = "%s-%s-%s %s" % (month, end_date, year, end_time)
start = "%s %s %s %s * " % (start_time[1], start_time[0], start_date, month)
print "\nObservation scheduled to start at %s-%s-%s %s:%s" % (month, start_date,
        year, start_time[0], start_time[1])
print "Ending at: %s" % (end)
assert raw_input('Correct? (y/n): ').capitalize() == 'Y', 'Enter the correct date.'

# Sample cron job format:
# Minute   Hour   Day of Month       Month          Day of Week        Command
# (0-59)  (0-23)     (1-31)    (1-12 or Jan-Dec)  (0-6 or Sun-Sat)
log = 'echo "Starting observation on $(date)" >> %s/cronlog' % (path)
cmd = '%s/observe.py coordinates.npz --margin=1 --endtime="%s"'%(path, end)
log_job = start + log + "\n"
cron_job = start + cmd + ' &>> %s/cronlog\n'%(path)

with open("tabs", "a") as tabs:
        tabs.write(log_job)
        tabs.write(cron_job)
