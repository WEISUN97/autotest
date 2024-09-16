from datetime import datetime

# Get the current date and time
current_time = datetime.now()

# Format the date and time as 'year_month_day_hour_min'
formatted_time = current_time.strftime("%Y_%m_%d_%H_%M")

# Print the formatted time
print(formatted_time)
