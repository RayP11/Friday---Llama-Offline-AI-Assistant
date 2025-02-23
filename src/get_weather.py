import requests

#Get weather from National Weather Service

def get_weather():
    # Coordinates for Salisbury, MD
    lat = 38.363350
    lng = -75.605919

    # Initialize an empty string to store the weather details
    weather_report = ""

    # Get gridpoints using the latitude and longitude
    grid_url = f'https://api.weather.gov/points/{lat},{lng}'
    response = requests.get(grid_url)

    if response.status_code == 200:
        data = response.json()
        grid_x = data['properties']['gridX']
        grid_y = data['properties']['gridY']

        # Now get the forecast using the gridpoints
        forecast_url = f'https://api.weather.gov/gridpoints/{data["properties"]["gridId"]}/{grid_x},{grid_y}/forecast'
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']

            # Add a header to the report
            weather_report += "Weather forecast for Salisbury, MD:\n"

            # Add weather details for each period to the string
            for period in periods:
                name = period['name']
                temperature = period['temperature']
                temperature_unit = period['temperatureUnit']
                detailed_forecast = period['detailedForecast']
                weather_report += f"{name}: {temperature}{temperature_unit}\n"
                weather_report += f"  {detailed_forecast}\n"
        
        else:
            weather_report += "Error fetching forecast data from NWS.\n"
    else:
        weather_report += "Error: Could not find gridpoints for Salisbury, MD.\n"
    
    # Return the weather report string
    return weather_report