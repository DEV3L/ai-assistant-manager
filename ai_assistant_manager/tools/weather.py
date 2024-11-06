def get_weather(location: str = "Medina, Ohio") -> str:
    mock_weather_data = {
        "Medina, Ohio": "sunny with a temperature of 75°F.",
        "New York": "cloudy with a temperature of 65°F.",
        "London": "rainy with a temperature of 60°F.",
    }

    weather = mock_weather_data.get(location, "weather data not available for this location.")
    return f"The current weather in {location} is {weather}"
