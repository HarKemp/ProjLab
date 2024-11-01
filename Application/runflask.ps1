# Create a virtual environment
python -m venv venv

# Activate the virtual environment
. .\venv\Scripts\Activate

# Set environment variables
#$env:FLASK_ENV="development"
#set FLASK_ENV=development
#set FLASK_APP=app

# Prompt the user to run the Tailwind watcher
$runTailwind = Read-Host "Do you want to run the Tailwind CSS watcher? (Y/N)"

if ($runTailwind -eq 'Y' -or $runTailwind -eq 'y') {
    # Start the tailwindcss watcher in a separate terminal window
    Start-Process powershell -ArgumentList "npx tailwindcss -i ./app/static/styles/input.css -o ./app/static/styles/tailwind.css --watch"
}

# Prompt if the flask server should be hosted locally
$hostLocally = Read-Host "Do you want to host the application locally? (Y/N)"
if ($hostLocally -eq 'Y' -or $hostLocally -eq 'y') {
    # Run flask with --host parameter
    flask --debug run --host=0.0.0.0
}
else {
    flask --debug run
}

# Run Flask in debug mode
flask --debug run