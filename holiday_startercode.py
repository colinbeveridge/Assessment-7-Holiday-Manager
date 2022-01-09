import datetime as dt
import json
import bs4
import requests
import dataclasses as dc
import urllib

# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dc.dataclass
class Holiday:
    name: str
    date: dt.date       
    
    def __str__ (self):
        return f'{self.name} ({self.date})'
          
           
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
class HolidayList:
    def __init__(self):
       self.innerHolidays = []
    
    # print the current list of holiday objects when called
    def __str__(self):
        return str(self.innerHolidays)
    
    def getHTML(self,url):
        response = requests.get(url)
        return response.text
   
    def addHoliday(self,holidayObj):
        holtype = type(holidayObj)
        if holtype == Holiday:
            self.innerHolidays.append(holidayObj)
            print(f'{holidayObj} was added')
        
        else:
            print(f'{holidayObj} is not the correct type. Must be a Holiday object.')

    def findHoliday(self,HolidayName, Date):
        holidaylist = self.innerHolidays
        for count,obj in enumerate(holidaylist):
            if obj.name == HolidayName and obj.date == Date:
                return obj
            else:
                return None

    def removeHoliday(self,HolidayName, Date):
        holiday = self.findHoliday(HolidayName,Date)
        try:
            self.innerHolidays.remove(holiday)
            print(f'{holiday} has been removed from the holiday list.')
        except:
            print('Delete later: in removeHoliday')
            print('An exception occurred. See above message.')

    def read_json(self,filelocation):
        with open(filelocation) as json_file:
            json_data = json.load(json_file)
        holidaydictlist = json_data['holidays']
        for item in holidaydictlist:
            name,date = item['name'],item['date']
            date = self.convertDatefromJSON(date)
            holidayobj = Holiday(name,date)
            self.addHoliday(holidayobj)

    def save_to_json(self,filelocation):
        # Write out json file to selected file.
        obj_list = self.innerHolidays
        # init list of dictionaries
        save_dictlist = []
        # read objects into a dictionary to save
        for obj in obj_list:
            # intialize dict for each object
            obj_dict = {}
            # make name of object and date of object into pieces of dictionary
            obj_dict['name'] = obj.name
            obj_dict['date'] = obj.date
            save_dictlist.append(obj_dict)
        # put into wrapper dict to format like initial json file
        finaldict = {}
        finaldict['holidays'] = save_dictlist
        print(finaldict)
        with open(filelocation,'w',encoding='utf-8') as f:
            json.dump(finaldict,f)

    def getScrapeYears(self):
        # get current year
        today_year = dt.date.today()
        today_year = str(today_year)[0:4]
        today_year = int(today_year)
        yearlist = []
        totalyears = 5
        year = today_year - 2
        for i in range(totalyears):
            yearlist.append(year)
            year += 1

        return yearlist

    def convertDatefromCalendar(self,calendardate,year):
        # takes the text date and the year and returns a datetime object
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        calendarmonth = calendardate[0:3]
        month_index = months.index(calendarmonth)
        month_index += 1
        calendarday = int(calendardate[4:])
        finaldate = dt.date(year,month_index,calendarday)
        return finaldate
        
    def convertDatefromJSON(self,jsondate):
        year = int(jsondate[0:4])
        month = int(jsondate[5:7])
        day = int(jsondate[8:])
        date = dt.date(year,month,day)
        return date
        
    def scrapeHolidays(self):
        scrapeyears = self.getScrapeYears()
        for year in scrapeyears:
            url = f'https://www.timeanddate.com/calendar/print.html?year={year}&country=1&cols=3&hol=33554809&df=1'
            html = self.getHTML(url)
            soup = bs4.BeautifulSoup(html,'html.parser')
            # scrape parameters found from scanning html
            table = soup.find('div',attrs={'id':'calarea'}).find('table',attrs={'id':'ch1'}).find('tbody').find('tbody').find('tbody')
            # count through rows in table
            for row in table.find_all_next('tr'):
                datehtml = row.find_next('td')
                namehtml = datehtml.find_next('td')
                if year == 2020:
                    print(datehtml)
                    print(namehtml)
                if datehtml == None or namehtml == None:
                    break
                name = namehtml.string
                date = datehtml.string
                # convert date
                print('Converting Date')
                date = self.convertDatefromCalendar(date,year)
                # now need to check if holiday is currently in holiday list
                holiday_inlist = self.findHoliday(name,date)
                if holiday_inlist == None:
                    # returned none, holiday not already in list, add it
                    newholiday = Holiday(name,date)
                    self.addHoliday(newholiday)
                else:
                    print(f'{name} is already in this holiday list. It will not be added again.')
                    continue
            print(f'Year {year} scraped and added.')    

    def numHolidays(self):
        numholidays = len(self.innerHolidays)
        print(f'There are {numholidays} holidays in this list.')
        return numholidays
    
    def filter_holidays_by_week(self,year, week_number):
        # assume inputs are strings
        innerList = self.innerHolidays
        filterfunc = lambda x: x.date.isocalendar()[0] == year and x.date.isocalendar()[1] == week_number
        holidays = filter(filterfunc,innerList)
        holidays = list(holidays)
        return holidays


    def displayHolidaysInWeek(self,year,week_number):
        # count through week and print each holiday object
        filteredlist = self.filter_holidays_by_week(year,week_number)
        print(f'List of holidays for week {week_number} of year {year}: ')
        if len(filteredlist) == 0:
            print(f'No holidays for week {week_number} of year {year}.')
        for hol in filteredlist:
            print(hol)

    def getWeather(self,weekNum):
    #     # Convert weekNum to range between two days
    #     # Use Try / Except to catch problems
    #     # Query API for weather in that week range
    #     # Format weather information and return weather string.

    # def viewCurrentWeek():
    #     # Use the Datetime Module to look up current week and year
    #     # Use your filter_holidays_by_week function to get the list of holidays 
    #     # for the current week/year
    #     # Use your displayHolidaysInWeek function to display the holidays in the week
    #     # Ask user if they want to get the weather
    #     # If yes, use your getWeather function and display results



# def main():
#     # Large Pseudo Code steps
#     # -------------------------------------
#     # 1. Initialize HolidayList Object
#     # 2. Load JSON file via HolidayList read_json function
#     # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
#     # 3. Create while loop for user to keep adding or working with the Calender
#     # 4. Display User Menu (Print the menu)
#     # 5. Take user input for their action based on Menu and check the user input for errors
#     # 6. Run appropriate method from the HolidayList object depending on what the user input is
#     # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 


if __name__ == "__main__":
    filespot = 'holidays.json'
    writefile = 'test_write.json'
    holList = HolidayList()
    holList.scrapeHolidays()
    holList.displayHolidaysInWeek(2022,1)
    

# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.





