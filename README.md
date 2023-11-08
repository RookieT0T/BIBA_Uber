# Uber_Coupon_Usage_Research
This summer research evaluated Uber’s coupon program for low-income populations living near Pittsburgh using spatial analysis tools such as Folium, Google Maps Geocoding API, and Google Maps Directions API to analyze participants’ geospatial trajectories.

# GPSData_SG00124.zip
This zip file contained all of raw data such as GPS coordinates and log files collected from an annoymous Uber user. Data analysis was done based on this.

# dataVisualization.py
The main program filtered dirty data, unpacked useful data, converted pick-up and drop-off addresses of Uber trips into latitude and longitude coordinates via the Google Maps
Geocoding API to call the Google Maps Directions API for suggested routes, and created visual representations of geospatial trajectories.
