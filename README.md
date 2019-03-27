# CMPUT404-Winter-2019-GroupProject

![Lagoon](docs/images/lagoon.png)

| Build Status | Coverage Status | Documentation Status | 
| ------------ | ----------- | --------------- | 
|[![Build Status](https://travis-ci.org/Zhipeng-Chang/CMPUT404-Winter-2019-GroupProject.svg?branch=master)](https://travis-ci.org/Zhipeng-Chang/CMPUT404-Winter-2019-GroupProject)|[![Coverage Status](https://coveralls.io/repos/github/Zhipeng-Chang/CMPUT404-Winter-2019-GroupProject/badge.svg?branch=master)](https://coveralls.io/github/Zhipeng-Chang/CMPUT404-Winter-2019-GroupProject?branch=master)|[![Documentation Status](https://img.shields.io/badge/docs-stable-brightgreen.svg)](https://github.com/Zhipeng-Chang/CMPUT404-Winter-2019-GroupProject/blob/master/docs/APIsDoc.pdf)

## To run the project locally:
```
On your terminal:

# Create a virtual environment
1. virtualenv venv --python=python3

# Activate your virtual environment
2. source venv/bin/activate

# Install all dependencies
3. pip install -r requirements.txt (please note that requirements_CI.txt is for TravisCI only)

# Run database migrations
4. python3 manage.py migrate

# Create a local super user
5. python3 manage.py createsuperuser

# Run the server locally (by defult it's on http://127.0.0.1:8000/)
6. python3 manage.py runserver
```

## Codebase overview

```
myBlog/
├── url.py           # All app level endpoints 
├── ...Handlers.py   # Handlers to each public endpoints
└── Helpers.py       # All functions used locally

mysite/
├── setting.py       # Settings to both myBlog app and the project 
└── url.py           # All project level endpoints
```

## Team members: <br />
Zhipeng Chang (zchang@ualberta.ca) <br />
Taijie Yang (taijie@ualberta.ca)<br />
Farhad Makiabady (makiabad@ualberta.ca) <br />
Tianyi Liang (tianyi4@ualberta.ca) <br />
Malcolm MacArthur (mimacart@ualberta.ca) <br />

## License
Copyright 2019 CMPUT 404 Team 4. All Rights Reserved. You may use, distribute, or modify this code under terms and conditions of the Code of Student Behavior at the University of Alberta. You may find a copy of the license in this project. Otherwise please contact us directly.
