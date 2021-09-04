from datetime import datetime
import time

t = datetime(2010,1,1,0,0).strftime('%s')
print(t)
# datetime(year,month,1,0,0).strftime('%s')
month = 1
year = 2010
s = "01/"+str(month)+"/"+str(year)+" 00:00:00"
d = datetime.strptime(s, "%d/%m/%Y %H:%M:%S")
r = time.mktime(d.timetuple())
print(int(r))
