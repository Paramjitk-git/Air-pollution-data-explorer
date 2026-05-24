import csv
from datetime import datetime
import matplotlib.pyplot as plt


# Data model (class)
class PollutionRecord:
    """
    Stores air pollution data for one city on one date.
    """

    def __init__(self, city, date, pm25, pm10, no2, so2, co, o3):
        self.city = city
        self.date = date
        self.year = date.year
        self.pm25 = pm25
        self.pm10 = pm10
        self.no2 = no2
        self.so2 = so2
        self.co = co
        self.o3 = o3

    def __repr__(self):
        return f"{self.city} ({self.year}) PM2.5={self.pm25:.2f}"


# File handling and cleaning
def safe_float(value):
    """
    Converts a value to float.
    Returns 0.0 if the value is missing or invalid.
    """
    try:
        if value == "" or value is None or value.upper() == "NA":
            return 0.0
        return float(value)
    except ValueError:
        return 0.0


def load_data(filename):
    """
    Loads air pollution data from a CSV file
    and returns a list of PollutionRecord objects.
    """
    records = []

    try:
        with open(filename, encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    date = datetime.strptime(row["Date"], "%Y-%m-%d")
                except:
                    # skip rows with invalid dates
                    continue

                record = PollutionRecord(
                    city=row.get("City", "Unknown"),
                    date=date,
                    pm25=safe_float(row.get("PM2.5", "")),
                    pm10=safe_float(row.get("PM10", "")),
                    no2=safe_float(row.get("NO2", "")),
                    so2=safe_float(row.get("SO2", "")),
                    co=safe_float(row.get("CO", "")),
                    o3=safe_float(row.get("O3", "")),
                )

                records.append(record)

    except FileNotFoundError:
        print("Error: air_pollution.csv not found.")

    return records


# Data structures (grouping by city)
def group_by_city(data):
    """
    Groups records by city using a dictionary.
    """
    grouped = {}
    for record in data:
        if record.city not in grouped:
            grouped[record.city] = []
        grouped[record.city].append(record)
    return grouped


# Search and filter functions
def filter_by_city(data, city):
    """
    Returns all records for a given city.
    """
    return [r for r in data if r.city.lower() == city.lower()]


def search_city(data, city_name):
    """
    Searches for a city using linear search.
    """
    for record in data:
        if record.city.lower() == city_name.lower():
            return True
    return False


# Sorting functions
def sort_by_pm25(data):
    """
    Sorts records by PM2.5 using selection sort (highest first).
    """
    sorted_data = data[:]

    for i in range(len(sorted_data)):
        max_index = i
        for j in range(i + 1, len(sorted_data)):
            if sorted_data[j].pm25 > sorted_data[max_index].pm25:
                max_index = j
        sorted_data[i], sorted_data[max_index] = sorted_data[max_index], sorted_data[i]

    return sorted_data


# Analysis functions
def get_average_pm25(data, city):
    """
    Calculates the average PM2.5 for a city.
    """
    city_records = filter_by_city(data, city)
    if not city_records:
        return None
    return sum(r.pm25 for r in city_records) / len(city_records)


def find_most_polluted_city(data, year):
    """
    Finds the city with the highest average PM2.5 in a given year.
    """
    yearly_data = [r for r in data if r.year == year]
    if not yearly_data:
        return None, None

    city_groups = group_by_city(yearly_data)

    worst_city = None
    worst_avg = -1

    for city, records in city_groups.items():
        avg = sum(r.pm25 for r in records) / len(records)
        if avg > worst_avg:
            worst_avg = avg
            worst_city = city

    return worst_city, worst_avg


# Visualization functions
def plot_avg_pm25_by_city(data):
    """
    Shows a bar chart of average PM2.5 by city.
    """
    city_groups = group_by_city(data)

    cities = []
    averages = []

    for city, records in city_groups.items():
        cities.append(city)
        averages.append(sum(r.pm25 for r in records) / len(records))

    plt.bar(cities, averages)
    plt.xticks(rotation=45)
    plt.ylabel("Average PM2.5")
    plt.title("Average PM2.5 by City")
    plt.show()


def plot_pm25_trend(data, city):
    """
    Shows how PM2.5 changes over time for a city.
    """
    city_records = filter_by_city(data, city)
    if not city_records:
        print("City not found.")
        return

    yearly = {}
    for record in city_records:
        if record.year not in yearly:
            yearly[record.year] = []
        yearly[record.year].append(record.pm25)

    years = sorted(yearly.keys())
    averages = [sum(yearly[y]) / len(yearly[y]) for y in years]

    plt.plot(years, averages, marker="o")
    plt.xlabel("Year")
    plt.ylabel("Average PM2.5")
    plt.title(f"PM2.5 Trend for {city}")
    plt.grid(True)
    plt.show()


def plot_pm25_vs_pm10(data):
    """
    Shows the relationship between PM2.5 and PM10.
    """
    pm25 = [r.pm25 for r in data]
    pm10 = [r.pm10 for r in data]

    plt.scatter(pm25, pm10)
    plt.xlabel("PM2.5")
    plt.ylabel("PM10")
    plt.title("PM2.5 vs PM10")
    plt.show()


# Menu / user interface
def menu(data):
    """
    Displays the main menu and handles user input.
    """
    while True:
        print("\nWelcome to Global Air Pollution Data Explorer")
        print("---------------------------------------------")
        print("1. Get average PM2.5 for a city")
        print("2. Find most polluted city")
        print("3. Search for city data")
        print("4. Sort data by PM2.5")
        print("5. Visualization")
        print("6. Exit")

        choice = input("Enter choice (1-6): ")

        if choice == "1":
            city = input("Enter city name: ")
            avg = get_average_pm25(data, city)
            if avg is None:
                print("City not found.")
            else:
                print(f"Average PM2.5 in {city}: {avg:.2f}")

        elif choice == "2":
            try:
                year = int(input("Enter year: "))
                city, value = find_most_polluted_city(data, year)
                if city is None:
                    print("No data for that year.")
                else:
                    print(f"Most polluted city in {year}: {city} ({value:.2f})")
            except ValueError:
                print("Invalid year.")

        elif choice == "3":
            city = input("Enter city name: ")
            print("City found." if search_city(data, city) else "City not found.")

        elif choice == "4":
            sorted_data = sort_by_pm25(data)
            print("Top 10 highest PM2.5 records:")
            for record in sorted_data[:10]:
                print(record)

        elif choice == "5":
            print("1. Bar chart: Average PM2.5 by city")
            print("2. Line plot: PM2.5 trend for a city")
            print("3. Scatter plot: PM2.5 vs PM10")
            sub = input("Choose option: ")

            if sub == "1":
                plot_avg_pm25_by_city(data)
            elif sub == "2":
                city = input("Enter city name: ")
                plot_pm25_trend(data, city)
            elif sub == "3":
                plot_pm25_vs_pm10(data)
            else:
                print("Invalid option.")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    data = load_data("air_pollution.csv")
    if data:
        menu(data)
