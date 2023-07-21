'''
Description: this is a program of drawing GPS coordinates from mutiple csv files 
and routes suggested by google maps api between two locations on a map.

Authors: Zequan Tang,

Date: July 20, 2023
'''

import csv
import time
import folium
import calendar
import polyline
import googlemaps
from datetime import datetime


# This method returns the weekday of a date
def findDay(date):
    born = datetime.strptime(date, '%m %d %Y').weekday()
    return (calendar.day_name[born])


# This method reads date info from the csv file and makes date info in a certain format
def formatTime(list):
    name1 = 'Error'
    name2 = 'Error'
    # split the list by '/'
    try:
        element1 = str(list[0]).split('/')
        element2 = str(list[2]).split('/')
    except:
        return [name1, name2]
        
    month1 = element1[0]
    if len(month1) == 1:
        month1 = '0'+ month1
    day1 = element1[1]
    if len(day1) == 1:
        day1 = '0' + day1
    year1 = element1[2]

    month2 = element2[0]
    if len(month2) == 1:
        month2 = '0'+ month2
    day2 = element2[1]
    if len(day2) == 1:
        day2 = '0'+ day2
    year2 = element2[2]

    # format time info
    time_object1 = datetime.strptime(list[1], "%I:%M%p")
    time_24h1 = time_object1.strftime("%H:%M")

    time_object2 = datetime.strptime(list[3], "%I:%M%p")
    time_24h2 = time_object2.strftime("%H:%M")

    # merge the date and time into the name of csv file we will read
    name1 = year1 + '-' + month1 + '-' + day1 + ' ' + time_24h1[0:2] + '_00_00.csv'
    name2 = year2 + '-' + month2 + '-' + day2 + ' ' + time_24h2[0:2] + '_00_00.csv'

    return [name1, name2, day1, day2, time_24h1, time_24h2]


# This method opens another file and returns a list of GPS coordinates 10 minutes before the pickup time
def collectCoordinatesBefore(name, lower):
    list = []
    splittedName = name.split(' ')
    # last hour
    hour = int(splittedName[1][0:2]) - 1
    newName = splittedName[0] + ' ' + splittedName[1].replace(splittedName[1][0:2], str(hour))
    print(newName, '\n')
    # name of new csv file we will read
    fileName = "./Data/SG00124/gps/" + newName
    print(fileName, '\n')
    # set a point where we start reading
    start = lower - 10 + 60
    print('Start is ' + str(start))

    try:
        with open(fileName, 'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                    if row[1] == 'UTC time':
                        continue
                    index = row[1].find(':')
                    substring = row[1][index + 1: index + 3]
                    if int(substring) >= start:
                        tuple = [row[2], row[3]]
                        list.append(tuple)   # append GPS coordinates to the list
            print(list, '\n')
            print(len(list), '\n')
            return list
    except:
        print('File cannot been found', '\n')
        return list


# This method opens another file and returns a list of GPS coordinates 10 minutes after the dropoff time
def collectCoordinatesAfter(name, upper):
    list = []
    splittedName = name.split(' ')
    # next hour
    hour = int(splittedName[1][0:2]) + 1
    newName = splittedName[0] + ' ' + splittedName[1].replace(splittedName[1][0:2], str(hour))
    print(newName, '\n')
    # name of new csv file we will read
    fileName = "./Data/SG00124/gps/" + newName
    print(fileName, '\n')
    # set a point where we stop reading
    end = upper + 10 - 60
    print('End is ' + str(end))

    try:
        with open(fileName, 'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                    if row[1] == 'UTC time':
                        continue
                    index = row[1].find(':')
                    substring = row[1][index + 1: index + 3]
                    if int(substring) <= end:
                        tuple = [row[2], row[3]]
                        list.append(tuple)   # append GPS coordinates to the list
            print(list, '\n')
            print(len(list), '\n')
            return list
    except:
        print('File cannot been found', '\n')
        return list


# This method returns a list of coordinates for trip which is in the same hour
def collectCoordinatesOne(name, time_24h1, time_24h2):
    coordinates = []
    num = []
    tenMinutesAfter = []
    print(name, '\n')
    # create the name of file which stores GPS data
    fileName = "./Data/SG00124/gps/" + name
    print(fileName, '\n')

    lower = int(time_24h1[3:5])
    if ((lower - 10) < 0):
        print("10 minutes before\n")
        tenMinutesBefore = collectCoordinatesBefore(name, lower)
        for i in tenMinutesBefore:
            coordinates.append(i)
        lower = 0
        print(coordinates, '\n')
        print(len(coordinates), '\n')
    else:
        lower -= 10
                    
    upper = int(time_24h2[3:5])
    if ((upper + 10) > 59):
        print("10 minutes after\n")
        tenMinutesAfter = collectCoordinatesAfter(name, upper)
        upper = 59
    else:
        upper += 10
    
    print(lower, '\n')
    print(upper, '\n')
    try:
        # if file can be found, then return a list of coordinates
        with open(fileName, 'r') as file:
            csvreader = csv.reader(file)
            print('File can be found', '\n')
            for row in csvreader:
                if row[1] == 'UTC time':
                    continue
                index = row[1].find(':')
                substring = row[1][index + 1: index + 3]

                # collect all of GPS coordinates between request time and dropoff time of the trip 
                if int(substring) >= lower and int(substring) <= upper:
                    tuple = [row[2], row[3]]
                    coordinates.append(tuple)   # append GPS coordinates to the list
                    num.append(row[0])
            
            for i in tenMinutesAfter:
                coordinates.append(i)
            print(len(tenMinutesAfter), '\n')
            print(len(coordinates), '\n')
            # print(coordinates, '\n')
            return coordinates
    except:
            # if file cannot be found, return the list with a failure message
            print('File cannot been found', '\n')
            coordinates.append('Error')
            return coordinates


# This method returns a list of coordinates for trip which is in two consecutive hours or 
# two consecutive days
def collectCoordinatesTwo(name, time_24h, bottom):
    coordinates = []
    num = []
    # create the name of file which stores GPS data
    fileName = "./Data/SG00124/gps/" + name
    print(fileName, '\n')

    limit = int(time_24h[3:5])
    if bottom == 1:
        # check if we need to open another file to read GPS coordinates 10 minutes before the pickup time
        if ((limit - 10) < 0):
            print("10 minutes before\n")
            tenMinutesBefore = collectCoordinatesBefore(name, limit)
            for i in tenMinutesBefore:
                coordinates.append(i)
            limit = 0
            print(coordinates, '\n')
            print(len(coordinates), '\n')
        else:
            # if not, just decrement limit by 10
            limit -= 10
    else:
        # check if we need to open another file to read GPS coordinates 10 minutes after the dropoff time
        if((limit + 10) > 59):
            print("10 minutes after\n")
            tenMinutesAfter = collectCoordinatesAfter(name, limit)
            for i in tenMinutesAfter:
                coordinates.append(i)
            limit = 59
            print(coordinates, '\n')
            print(len(coordinates), '\n')
        else:
            # if not, just increment limit by 10
            limit += 10
    
    print("Limit is " + str(limit), '\n')

    try:
        # if file can be found, then return a list of coordinates
        with open(fileName, 'r') as file:
            csvreader = csv.reader(file)
            print('File can be found', '\n')
            for row in csvreader:
                if row[1] == 'UTC time':
                    continue
                index = row[1].find(':')
                substring = row[1][index + 1: index + 3]

                if bottom == 1: # collect all of GPS coordinates after the request time (the first GPS file)
                    if limit <= int(substring):
                        tuple = [row[2], row[3]]
                        coordinates.append(tuple)   # append GPS coordinates to the list
                        num.append(row[0])
                else:   # collect all of GPS coordinates before the dropoff time (the second GPS file)
                    if limit >= int(substring):
                        tuple = [row[2], row[3]]
                        coordinates.append(tuple)   # append GPS coordinates to the list
                        num.append(row[0])
            return coordinates
    except:
            # if file cannot be found, return the list with a failure message
            print('File cannot been found', '\n')
            coordinates.append('Error')
            return coordinates


# This method draws the GPS coordinates of the same day on the map
def drawGPS(list, map):
    # use for loop to draw each GPS location
    for k in range(len(list)):
        map.add_child(folium.Marker(location = list[k], popup = 'GPS' + str(k), icon = folium.Icon(color = 'darkblue', icon = 'map-pin', prefix = 'fa')))


# A helper method of drawRoutes()
def getGeoCode(address, request):
    while True:
        try:
            time.sleep(2)
            # call google maps api (Places). it returns a jason file which stores the coordinates of a place
            response = request.geocode(address)
        except:
            continue        # retry if proxy errors occur
        return response


# This method draws the routes suggested by google maps api between a pickup location and
# a dropoff location on the map
def drawRoutes(pickup, dropoff, map):
    api_key = 'AIzaSyBvj9R_7GWPHAkTIBNYLRekWQ4Gyb7UR78'
    request = googlemaps.Client(api_key)

    # call helper function to get the jason files sent by google maps api
    responseP = getGeoCode(pickup, request)
    responseD = getGeoCode(dropoff, request)
    # extract coordiantes of the pickup and dropoff locations from the jason files
    coordPick = [responseP[0]['geometry']['location']['lat'], responseP[0]['geometry']['location']['lng']]
    coordDrop = [responseD[0]['geometry']['location']['lat'], responseD[0]['geometry']['location']['lng']]
    # add the pickup and dropoff locations to the map
    map.add_child(folium.Marker(location = coordPick, popup = 'PickUp', icon = folium.Icon(color = 'lightred', icon = 'map-location-dot', prefix = 'fa')))
    map.add_child(folium.Marker(location = coordDrop, popup = 'DropOff', icon = folium.Icon(color = 'green', icon = 'map-location-dot', prefix = 'fa')))

    now = datetime.now()
    # call google maps api (Routes). it returns another jason file which stores all of coordinates of a route
    # or mutiple routes if "alternatives = 'true'"
    routes = request.directions(pickup, dropoff, mode = 'driving', alternatives = 'true', departure_time=now)
    for i in range(len(routes)):
        # decode the coordinates of routes
        routeCoordinates = polyline.decode(routes[i]['overview_polyline']['points'])
        # draw the routes
        folium.PolyLine(routeCoordinates, weight = 5, opacity = 0.8, popup = ('Route' + str(i))).add_to(map)


# This method draws the routes between pickup location and dropoff location within the same day on the map
def drawSameDayRoutes(nestedList, map):
    for i in range(len(nestedList)):
        pickup = nestedList[i][4]
        dropoff = nestedList[i][5]
        drawRoutes(pickup, dropoff, map)


# This method collects the GPS coordinates of the same day
def collectSameDayGPS(nestedList):
    finalList = []
    for i in range(len(nestedList)):
        sameHour = False
        sameDay = False
        list = formatTime(nestedList[i])
        if len(list) == 2 and list[0] == 'Error' and list[1] == 'Error':
            continue
        if list[2] == list[3]:
            sameDay = True
        if list[4][0:2] == list[5][0:2]:
            sameHour = True
        
        '''
        print("SameDay: " + str(sameDay), '\n')
        print("SameHour: " + str(sameHour), '\n')
        '''

        if sameDay and sameHour:
            returnList = collectCoordinatesOne(list[0], list[4], list[5])
            # print(returnList, '\n')
            # print(len(returnList), '\n')
            if len(returnList) == 0 or (len(returnList) > 0 and returnList[0] != 'Error'):
                for k in returnList:
                    finalList.append(k)
        else:
            returnList1 = collectCoordinatesTwo(list[0], list[4], 1)
            returnList2 = collectCoordinatesTwo(list[1], list[5], 0)
            con1 = (len(returnList1) == 0 or (len(returnList1) > 0 and returnList1[0] != 'Error'))
            con2 = (len(returnList2) == 0 or (len(returnList2) > 0 and returnList2[0] != 'Error'))
            # print(returnList1, '\n')
            # print(len(returnList1), '\n')
            # print(returnList2, '\n')
            # print(len(returnList2), '\n')
            if con1 and con2:
                for s in returnList1:
                    finalList.append(s)
                for g in returnList2:
                    finalList.append(g)
    
    return finalList


# This method finds all other trips within the same day
def findTrips(requestDate, requestTime):
    tripList = []
    with open("./Data/UberTrips.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            # ignore rows with masked location address
            if not(row[15][0].isdigit()) or not(row[16][0].isdigit()):
                continue
            if row[0] == 'SG00124' and row[2] == requestDate and row[3] != requestTime:
                trip = [row[2], row[3], row[6], row[7], row[15], row[16]]
                if '--' in trip:
                    continue
                tripList.append(trip)
    return tripList



with open("./Data/UberTrips.csv", 'r') as file:
    csvreader = csv.reader(file)
    num = 0
    checkedDate = []
    # read the csv file
    for row in csvreader:
        sameDay = False
        sameHour = False
        num += 1    # record the row number
        # only read the trip information of user SG00124
        if row[0] == 'SG00124':
            # ignore rows with masked location address
            if not(row[15][0].isdigit()) or not(row[16][0].isdigit()):
                continue
            
            if row[2] in checkedDate:
                continue

            # tuple stores UTC time of request and dropoff 
            tuple = (row[2], row[3], row[6], row[7])
            if '--' in tuple:
                continue    
            print('\n\nNew item: ' + str(tuple), '\n')

            # format date info
            try:
                element1 = str(row[2]).split('/')
                element2 = str(row[6]).split('/')
            except:
                continue

            month1 = element1[0]
            if len(month1) == 1:
                month1 = '0'+ month1
            day1 = element1[1]
            if len(day1) == 1:
                day1 = '0' + day1
            year1 = element1[2]

            month2 = element2[0]
            if len(month2) == 1:
                month2 = '0'+ month2
            day2 = element2[1]
            if len(day2) == 1:
                day2 = '0'+ day2
            year2 = element2[2]

            # format time info
            time_object1 = datetime.strptime(row[3], "%I:%M%p")
            time_24h1 = time_object1.strftime("%H:%M")

            time_object2 = datetime.strptime(row[7], "%I:%M%p")
            time_24h2 = time_object2.strftime("%H:%M")

            # merge the date and time into the name of csv file we will read
            name1 = year1 + '-' + month1 + '-' + day1 + ' ' + time_24h1[0:2] + '_00_00.csv'
            name2 = year2 + '-' + month2 + '-' + day2 + ' ' + time_24h2[0:2] + '_00_00.csv'

            '''
            # determine the weekday of a date
            local = row[4]
            try:
                localElements = str(local).split('/')
            except:
                continue
            localMonth = localElements[0]
            if len(localMonth) == 1:
                localMonth = '0'+ localMonth
            localDay = localElements[1]
            if len(localDay) == 1:
                localDay = '0' + localDay
            localYear = localElements[2]
            localDate = localMonth + ' ' + localDay + ' ' + localYear
            date = findDay(localDate)
            print(date, '\n')
            if date != 'Sunday' and date != 'Saturday':
                continue
            '''
            
            # check if the travel starts and ends in the same day
            if day1 == day2:
                sameDay = True
            # check if the travel starts and ends in the same hour
            if time_24h1[0:2] == time_24h2[0:2]:
                sameHour = True

            # read one csv file (one hour) if trip is in the same hour
            if sameDay and sameHour:
                    
                    # call another method to collect GPS coordinates
                    list = collectCoordinatesOne(name1, time_24h1, time_24h2)

                    # start to draw maps if the csv file exists
                    if len(list) == 0 or (len(list) > 0 and list[0] != 'Error'):
                        # print('Looks good 1 hour', '\n')
                        
                        # find other trips within the same day
                        tripLists = findTrips(row[2], row[3])
                        print('Trips found: ' + str(tripLists) + '\n')
                        if len(tripLists) != 0:
                            dataCollected = collectSameDayGPS(tripLists)
                            # print(dataCollected, '\n')
                            # print(len(dataCollected), '\n')
                            for g in dataCollected:
                                list.append(g)

                        # create a map & draw GPS points
                        map = folium.Map(location = list[0], zoom_start = 12)
                        drawGPS(list, map)

                        # read pickup address and dropoff address from csv file
                        pickup = row[15]
                        dropoff = row[16]
                        # call another method to draw routes suggested by google maps api
                        drawRoutes(pickup, dropoff, map)
                        drawSameDayRoutes(tripLists, map)

                        # avoid checking the same day trip again
                        checkedDate.append(row[2])

                        # save the map as a html file
                        fileName = year1 + '-' + month1 + '-' + day1 + '  #' + str(num) + '.html'
                        print(fileName, '\n')
                        map.save(fileName)

            else: # read two csv files (two hours) if trip starts and ends in two consecutive hours or consecutive days
                # call another method to collect GPS coordinates
                list1 = collectCoordinatesTwo(name1, time_24h1, 1)
                list2 = collectCoordinatesTwo(name2, time_24h2, 0)

                # check if the two csv files exist
                con1 = (len(list1) == 0 or (len(list1) > 0 and list1[0] != 'Error'))
                con2 = (len(list2) == 0 or (len(list2) > 0 and list2[0] != 'Error'))
                if con1 and con2:
                    # print('Looks good 2 hours', '\n')
                    # use for loop to merge two lists which store GPS coordinates
                    for i in list2:
                        list1.append(i)

                    # find other trips within the same day
                    tripLists = findTrips(row[2], row[3])
                    print('Trips found: ' + str(tripLists) + '\n')
                    if len(tripLists) != 0:   
                        dataCollected = collectSameDayGPS(tripLists)
                        # print(dataCollected, '\n')
                        for g in dataCollected:
                            list1.append(g)

                    # create a map & draw GPS points
                    map = folium.Map(location = list1[0], zoom_start = 12)
                    drawGPS(list1, map)
                    
                    # read pickup address and dropoff address from csv file
                    pickup = row[15]
                    dropoff = row[16]
                    # call drawRoutes to draw routes suggested by google maps api
                    drawRoutes(pickup, dropoff, map)
                    drawSameDayRoutes(tripLists, map)
                    
                    # avoid checking the same day trip again
                    checkedDate.append(row[2])

                    # save the map as a html file
                    fileName = year1 + '-' + month1 + '-' + day1 + '  #' + str(num) + '.html'
                    print(fileName, '\n')
                    map.save(fileName)