# module for all user interface functions, so all input getting and menu jumping
from os import getpid
import holiday_startercode as classes

def start_up():
    filelocation = 'holidays.json'
    print('Holiday Management')
    print('===================')
    holList = classes.HolidayList()
    holList.read_json(filelocation)
    holList.scrapeHolidays()
    print(f'There are {len(holList.innerHolidays)} holidays stored in the system.')
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
    


if __name__ == '__main__':
    place = start_up()


