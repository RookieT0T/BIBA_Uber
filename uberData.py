'''
Description: this is a program of drawing GPS coordinates from mutiple csv files 
and routes suggested by google maps api between two locations on a map.

How to run: place this program in the same directory with the folder 'Data' and then you
can run this program.

Authors: Zequan Tang,

Date: July 4, 2023
'''


import csv
import time
import folium
import polyline
import googlemaps
from datetime import datetime


# This method returns a list of coordinates for trip which is in the same hour
def collectCoordinatesOne(name, time_24h1, time_24h2):
    coordinates = []
    num = []
    # create the name of file which stores GPS data
    fileName = "./Data/SG00124/gps/" + name
    print(fileName, '\n')
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
                if int(substring) >= int(time_24h1[3:5]) and int(substring) <= int(time_24h2[3:5]):
                    tuple = [row[2], row[3]]
                    coordinates.append(tuple)   # append GPS coordinates to the list
                    num.append(row[0])
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
                    if int(time_24h[3:5]) <= int(substring):
                        tuple = [row[2], row[3]]
                        coordinates.append(tuple)   # append GPS coordinates to the list
                        num.append(row[0])
                else:   # collect all of GPS coordinates before the dropoff time (the second GPS file)
                    if int(time_24h[3:5]) >= int(substring):
                        tuple = [row[2], row[3]]
                        coordinates.append(tuple)   # append GPS coordinates to the list
                        num.append(row[0])
            return coordinates
    except:
            # if file cannot be found, return the list with a failure message
            print('File cannot been found', '\n')
            coordinates.append('Error')
            return coordinates



# A helper method of drawRoutes()
def getGeoCode(address, request):
    while True:
        try:
            time.sleep(5)
            # call google maps api (Places). it returns a jason file which stores the coordinates of a place
            response = request.geocode(address)
        except:
            continue        # retry if proxy errors occur
        return response



# This method draws the routes suggested by google maps api between a pickup location and
# a dropoff location on the map
def drawRoutes(pickup, dropoff, map):
    api_key = 'YOUR API KEY'
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



with open("./Data/UberTrips.csv", 'r') as file:
    csvreader = csv.reader(file)
    num = 0
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
            print(day1, '\n')
            print(day2, '\n')
            print(time_24h1[0:2], '\n')
            print(time_24h2[0:2], '\n')
            print(time_24h1, '\n')
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
                        
                        # create a map
                        map = folium.Map(location = list[0], zoom_start = 12)

                        # use for loop to draw each GPS location
                        for k in range(len(list)):
                            map.add_child(folium.Marker(location = list[k], popup = 'GPS' + str(k), icon = folium.Icon(color = 'darkblue', icon = 'map-pin', prefix = 'fa')))
                    
                        # read pickup address and dropoff address from csv file
                        pickup = row[15]
                        dropoff = row[16]
                        # call another method to draw routes suggested by google maps api
                        drawRoutes(pickup, dropoff, map)
                        # save the map as a html file
                        fileName = 'drawMap ' + str(num)
                        print(fileName, '\n')
                        map.save(fileName + '.html')

            else: # read two csv files (two hours) if trip starts and ends in two consecutive hours or consecutive days
                # call another method to collect GPS coordinates
                list1 = collectCoordinatesTwo(name1, time_24h1, 1)
                list2 = collectCoordinatesTwo(name2, time_24h2, 0)

                # check if the two csv files exist
                con1 = (len(list1) == 0 or (len(list1) > 0 and list1[0] != 'Error'))
                con2 = (len(list2) == 0 or (len(list2) > 0 and list2[0] != 'Error'))
                if con1 and con2:
                    # use for loop to merge two lists which store GPS coordinates
                    for i in list2:
                        list1.append(i)
                    # print('Looks good 2 hours', '\n')
                    # print(list1)

                    # create a map
                    map = folium.Map(location = list1[0], zoom_start = 12)

                    # use for loop to draw each GPS location
                    for k in range(len(list1)):
                        map.add_child(folium.Marker(location = list1[k], popup = ('GPS' + str(k)), icon = folium.Icon(color = 'darkblue', icon = 'map-pin', prefix = 'fa')))
                    
                    # read pickup address and dropoff address from csv file
                    pickup = row[15]
                    dropoff = row[16]
                    # call drawRoutes to draw routes suggested by google maps api
                    drawRoutes(pickup, dropoff, map)
                    # save the map as a html file
                    fileName = 'drawMap ' + str(num)
                    print(fileName, '\n')
                    map.save(fileName + '.html')