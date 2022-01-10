import datetime as dt
import json
import bs4
import requests
import dataclasses as dc


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
        if isinstance(holidayObj,Holiday):
            self.innerHolidays.append(holidayObj)
            print(f'{holidayObj} was added')
        
        else:
            print(f'{holidayObj} is not the correct type. Must be a Holiday object.')

    def findHoliday(self,HolidayName, Date):
        holidaylist = self.innerHolidays
        for obj in holidaylist:
            if obj.name == HolidayName and obj.date == Date:
                return obj
        
    def removeHoliday(self,HolidayName):
        holidaylist = self.innerHolidays
        count = 0
        for hol in holidaylist:
            if str(hol.name) == HolidayName:
                self.innerHolidays.remove(hol)
                count += 1
        if count == 0:
            inlist = False
        else:
            inlist = True
        return inlist
                
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
            obj_dict['date'] = str(obj.date)
            save_dictlist.append(obj_dict)
        # put into wrapper dict to format like initial json file
        finaldict = {}
        finaldict['holidays'] = save_dictlist
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
                if datehtml == None or namehtml == None:
                    break
                name = namehtml.string
                date = datehtml.string
                # convert date
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
        # want_weather will only be true if in current week and they ask for it
        filteredlist = self.filter_holidays_by_week(year,week_number)
        print(f'These are the holidays for {year} week #{week_number}')
        if len(filteredlist) != 0:
            for hol in filteredlist:
                print(hol)
        else:
            print(f'No holidays for week {week_number} of year {year}.')
            
    def getWeather(self,next_holidays,cityname,country_abbr):
        # the way the api works
        # if this function is being called, it must be called for the current date for api compatibility
        # put name of city where weather is desired, all lowercase, leave spaces
        hoststr = 'community-open-weather-map.p.rapidapi.com'
        keystr = '769e84dd57msh3d3b701bd3c0691p177eecjsn0ee78d73f801'
        url = 'https://community-open-weather-map.p.rapidapi.com/forecast/daily'
        placequery = f'{cityname},{country_abbr}'
        querystring = {'q':placequery}
        headers = {'x-rapidapi-host':hoststr,'x-rapidapi-key':keystr}
        response = requests.request("GET",url,headers=headers,params=querystring)
        
        try:
            weatherjson = json.loads(response.text)
        except:
            print(f'Something went wrong requesting from the API. Status Code: {response.status_code}')
            return None

        # now count through weather data to get list of dates and list of weather
        # two lists instead of a dictionary, easier indexing
        weatherlist = []
        datelist = []
        # calculated reference date for the api
        refdate = dt.date(1970,1,1)
        # get all days of next 7 and their weather
        for day in weatherjson['list']:
            datelist.append((refdate + dt.timedelta(seconds=day['dt'])).day+1)
            weatherlist.append(day['weather'][0]['main'])
        
        # now count through the holiday objects and return only the weather for those days
        # make weather strings for the matching holidays
        finalweathers = []
        for holiday in next_holidays:
            daynum = holiday.date.day
            index = datelist.index(daynum)
            finalweathers.append(weatherlist[index])

        return finalweathers
            

        # Convert weekNum to range between two days
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.

    def viewCurrentWeek(self):
        want_weather = False
        # hardcoded location for simplicity
        cityname = 'philadelphia'
        country_abbr = 'us'
        while want_weather != 'y' and want_weather != 'n':
            want_weather = input('Would you like to see this week\'s weather? [y/n]: ')

        # find what the holidays are for next 7 days
        nextweek = dt.date.today() + dt.timedelta(days=7)
        filterfunc = lambda x: x.date >= dt.date.today() and x.date <= nextweek
        next_holidays = list(filter(filterfunc,self.innerHolidays))
        
        if want_weather == 'y':
            # if they want the weather, display the holidays for the next 7 days
            next_weather = self.getWeather(next_holidays,cityname,country_abbr)

            for i in range(len(next_holidays)):
                print(f'{next_holidays[i]} - {next_weather[i]}')

        else:
            for i in range(len(next_holidays)):
                print(next_holidays[i])
        # # Use the Datetime Module to look up current week and year
        # Use your filter_holidays_by_week function to get the list of holidays 
        # for the current week/year
        # Use your displayHolidaysInWeek function to display the holidays in the week
        # Ask user if they want to get the weather
        # If yes, use your getWeather function and display results

def start_up():
    filelocation = 'holidays.json'
    print('Holiday Management')
    print('===================')
    holList = HolidayList()
    holList.read_json(filelocation)
    holList.scrapeHolidays()
    holList.numHolidays()
    place = 0
    return place,holList

def get_place():
    place = 0
    while place not in [1,2,3,4,5]:
        place = input('Navigate: ')
        try:
            place = int(place)
        except:
            print('Must enter an integer.')
    return place

def main_menu():
    print('Holiday Menu')
    print('==============')
    print('1. Add Holiday')
    print('2. Remove a Holiday')
    print('3. Save Holiday List')
    print('4. View Holidays')
    print('5. Exit')
    place = get_place()
    return place

def add(holList):
    print('Add a Holiday')
    print('===============')
    name = input('Holiday: ')
    date = input('Date (YYYY-MM-DD): ')
    datevalid = False
    while not datevalid:
        try:
            date = holList.convertDatefromJSON(date)
            holiday = Holiday(name,date)
            holList.addHoliday(holiday)
            print('Success: ')
            print(f'{holiday} has been added to the holiday list.')
            datevalid = True
            place = 0
        except:
            print('Error: ')
            print('Invalid date. Please try again.')
            date = input(f'Date for {name}: ')
    place = 0
    saved = False
    return place,saved

def remove(holList):
    print('Remove a Holiday')
    print('==================')
    name = input('Holiday Name: ')
    namevalid = holList.removeHoliday(name)
    while not namevalid:
        print('Error: ')
        print(f'{name} not found.')
        print()
        name = input('Holiday Name: ')
        namevalid = holList.removeHoliday(name)
    print('Success: ')
    print(f'{name} has been removed from the holiday list.')
    place = 0
    saved = False
    return place,saved

def save(holList,saved):
    print('Saving Holiday List')
    print('====================')
    want_save = input('Are you sure you want to save your changes? [y/n]: ')
    savename = 'HolidayList.json'
    while want_save != 'y' and want_save != 'n':
        print('Please enter y (yes) or n (no).')
        want_save = input('Are you sure you want to save your changes? [y/n]: ')

    if want_save == 'y':
        holList.save_to_json(savename)
        print('Success: ')
        print('Your changes have been saved.')
        saved = True
    
    else:
        print('Canceled: ')
        print('Holiday list file save canceled.')
        place = 0
    place = 0
    return place,saved

def view(holList):
    print('View Holidays')
    print('==============')
    year = input('Which year?: ')
    while len(year) != 4 or not year.isnumeric():
        year = input('Please enter a 4 digit integer. Year: ')
    
    weekvalid = False
    while not weekvalid:
        weeknum = input('Which week? #[1-52, Leave blank for the current week]: ')
        if weeknum.isnumeric() and int(weeknum)>=1 and int(weeknum)<=52:
            year = int(year)
            weeknum = int(weeknum)
            holList.displayHolidaysInWeek(year,weeknum)
            weekvalid = True

        elif weeknum == '':
            holList.viewCurrentWeek()
            weekvalid = True
    
        else:
            print('Error. Invalid entry. Enter an integer between 1 and 52.')
            weeknum = input('Which week? #[1-52, Leave blank for the current week]: ')
    place = 0
    return place

def exit(saved):
    print('Exit')
    print('=====')
    done = None
    if saved:
        while done != 'y' and done != 'n':
            done = input('Are you sure you want to exit? [y/n] ')
        if done == 'y':
            print('Goodbye!')
            place = None
        else:
            place = 0
    
    else:
        while done != 'y' and done != 'n':
            print('Your changes will be lost.')
            done = input('Are you sure you want to exit? [y/n] ')
        if done == 'y':
            print('Goodbye!')
            place = None
        else:
            place = 0

    return place

def main():
    place,holList = start_up()
    saved = False
    while place != None:
        if place == 0:
            place = main_menu()
        
        elif place == 1:
            place,saved = add(holList)

        elif place == 2:
            place,saved = remove(holList)

        elif place == 3:
            place,saved = save(holList,saved)
        
        elif place == 4:
            place = view(holList)
        
        elif place == 5:
            place = exit(saved)
        
        else:
            place = 0


if __name__ == '__main__':
    main()

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





