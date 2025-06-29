import datetime
import os
import time

# Function to sleep
def Wait():
    return

#
def CurrentTime():
    PrintAndLog(f"Attempting to capture current time via CurrentTime() function.")
    #
    try:
        raw_time = str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        PrintAndLog(f"Current time: {raw_time}")
        return raw_time
    #
    except Exception as error:
        ErrorHandler(f"Failed to capture current time via CurrentTime() function\n Error: {error}")
        return None

def FormattedCurrentTime():
    PrintAndLog(f"Attempting to format current time via FormattedCurrentTime() function.")
    #
    try:
        formatted_time = str(datetime.datetime.now().strftime("%m%d%Y_%H%M%S"))
        PrintAndLog(f"Successfully formatted current time: {formatted_time}")
        return formatted_time
    #
    except Exception as error:
        PrintAndLog(f"Failed to format current time via FormattedCurrentTime() function.\n Error: {error}")
        return None

# Enable logging, changing global variable. Functions will log actions
def EnableLogging():
    global LogEnable
    LogEnable = True

# Create Log File, default to user home directory and name prefix of "SeleniumLib"
def CreateLogFile(Directory=os.path.expanduser("~"), NamePrefix="SeleniumLib"):
    # Enable LogLocation to be Global
    global LogLocation

    # Create the filename
    filename = f"{NamePrefix}_{FormattedCurrentTime()}.txt"

    # Create the path of where it is going to be created
    if LogLocation is None:
        filepath = os.path.join(Directory, filename)
        LogLocation = filepath

    # Custom log filepath
    else:
        filepath = os.path.join(LogLocation, filename)
        LogLocation = filepath
    # Try creating the file
    try:
        with open(filepath, "w") as file:
            file.write(f"Log created at {FormattedCurrentTime()}\n"
                       f"Created by @dyeadal on GitHub\n"
                       f"Not liable for any damages caused by this script, please use responsibly\n")
            print(f"Log file {filepath} created at {FormattedCurrentTime()}")
            return filepath
    # If it fails print out message to terminal and ask if they want to quit or continue without logs
    except Exception as error:
        print(f"Failed to create {filename} log file.\nError: {error}")
        return None

# Function to print and write to log if variables are configured
def PrintAndLog(Message):
    global LogLocation

    # Default is to print out the message regardless if logging was not enabled nor configured
    print(Message)

    # Logging enabled, and custom filepath
    if LogEnable and LogLocation is not None:
        # Write to custom filepath
        WriteToLog(LogLocation, Message)

    # Logging was enabled, but likely no custom filepath
    elif LogEnable and LogLocation is None:
        # Create Log File with defaults
        CreateLogFile()
        WriteToLog(LogLocation, Message)

    # Logging is disabled and, and LogLocation is custom
    elif LogEnable is False and LogLocation is not None:
        print(f"LogLocation is configured to {LogLocation}, but logs are not enabled.\n"
              f"Enable Logging by running the function 'EnableLogging()' in your script.\n"
              f"Exiting script in 15 seconds...")
        time.sleep(15) # Can not use Wait() it will invoke PrintAndLog() again and loop
        exit()

    # Logging not enabled and no custom path set, default test behaviour
    else:
        return None

# Function to write to log
def WriteToLog(file, msg):
    # Logging enabled and custom filepath
    if LogEnable and LogLocation is not None:
        try: # write log to file
            with open(file, 'a') as file:
                file.write(CurrentTime() + " --- " + msg + "\n")
        except Exception as error:
            print(f"An error occurred writing to file: {error}")

    # Logging was enable but no custom filepath
    elif LogEnable and LogLocation is None:
        #Create Log File
        CreateLogFile()

        # Attempt to write log to file
        try:
            with open(file, 'a') as file:
                file.write(CurrentTime() + " --- " + msg + "\n")
        #
        except Exception as error:
            print(f"An error occurred writing to file: {error}")

    # Custom filepath for logging was set, but logging was NOT enabled
    else:
        print(f"LogLocation is configured to {LogLocation}, but logs are not enabled."
              f"Enable Logging by running the function 'EnableLogging()' in your script."
              f"Exiting script in 15 seconds...")
        Wait(15)
        exit()

# Handles errors that occur on website
def ErrorHandler(msg):

    # Print and log error
    PrintAndLog(f"\nError: \n{msg}")

    # Prompts user if they want to continue although error occurred
    prompttocontinue = input("Do you want to continue? [y/n] ")
    # If yes, attempt to continue
    if prompttocontinue.lower() == "y":
        PrintAndLog(f"User decided to continue after facing Error: {msg}.")
        return None

    # If no, logs termination due to error and quits
    else:
        PrintAndLog(f"User decided to terminate script after facing Error: {msg}.")
        exit()

def ThrowIntentionalError(msg):
    PrintAndLog(f" Throwing Intentional Error: \n{msg}\n")

    # Ask the user if they want to continue
    answer = input("Do you want to continue? [y/n]")

    # If yes, logs the error and the user wants to continue, returns None
    if answer == "y" or answer == "Y":
        PrintAndLog(f"\nUser decided to continue after facing Error: {msg}.\n")
        return None
    # If no, logs termination due to error and quits
    else:
        PrintAndLog(f"\nUser decided to terminate script after facing Error: {msg}.\n")
        raise Exception(f"{msg}\n")
        exit()