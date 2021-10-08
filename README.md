# IDEAS4EO

Intelligent Data Exploration & Analysis System For Earth Observations.

A python module to extract, read, analyze and visualize Earth Observations Products (such as MODIS MYD06)

Setup IDEAS4EO:

Step 1:

Clone the project on your local machine:

[IDEAS4EO GitHub Project](https://github.com/benjamin-hg-marchant/ideas4eo)

Step 2:

Edit the config.json file: enter your NASA laads_daac_token and enter the directory path where the files will be downloaded, for example:

    {
    "nasa_laads_daac_token": "Ym1hcmNoYW50OlltVnVhbUZ0YVc0dWJXRnlZMmhoYm5SQWJtRnpZUzVuYjNZPToxNjI0NzE3MjEwOjEwZmNhNWU4ODVlNzc3OGUyMzE3NzFkZjNmNjUwMGIzNjVhMDY4ZWY",
    "media_path": "/Users/Toto/Desktop/media/files"
    }

Step 3: enter in your terminal:

export PYTHONPATH="/Users/mb/Desktop/mb_root/github"

where /Users/mb/Desktop/mb_root/github is the path to IDEAS4EO module

Step 4: start to use it:

jupyter notebook