"""Minimal Weather Tool Example - Shows MCP-KE entry point pattern"""

WEATHER_DATA = {
    "SF": "18°C Foggy",
    "NYC": "22°C Sunny",
    "London": "15°C Rainy"
}


def run(query: str) -> str:
    """Entry point for MCP-KE. Takes **kwargs, returns result."""
    for city in WEATHER_DATA.keys():
        if city.lower() in query.lower():
            return f"{city}: {WEATHER_DATA[city]}"
    return "City not found. Try: SF, NYC, London"


# Teams with complex logic can wrap classes:
class WeatherMAS:
    """Example: Your implementation can use classes."""
    def __init__(self):
        self.data = WEATHER_DATA

    def ask(self, query: str) -> str:
        for city in self.data.keys():
            if city.lower() in query.lower():
                return f"{city}: {self.data[city]}"
        return "City not found"


def run_with_class(query: str) -> str:
    """Alternative: Wrap your class in entry function."""
    mas = WeatherMAS()
    return mas.ask(query)


if __name__ == "__main__":
    print(run("What's the weather in NYC?"))
    # Output: NYC: 22°C Sunny
