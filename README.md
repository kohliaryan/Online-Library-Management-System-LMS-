# Online Library Management System (LMS)

## Author
- Name: Aryan Kohli
- Roll number: 22f3001832
- Email: 22f3001832@ds.study.iitm.ac.in

## Description
This project, completed in the January 2024 term at IIT Madras, is an Online Library Management System (LMS). The LMS is a web application designed to streamline library operations. It provides a platform for users to interact with the library's catalog and for librarians to manage resources, aiming to enhance efficiency and transparency in academic libraries.

## Technologies Used
- Flask: A lightweight Python web framework for crafting web applications.
- SQLite3: A self-contained, serverless, and zero-configuration database engine.
- Flask_SQLAlchemy: A flask extension that adds SQLAlchemy support, a Python SQL toolkit and ORM.
- Bootstrap: A CSS framework for developing responsive and mobile-first web interfaces.
- Jinja: A templating language in Python, used for rendering dynamic web pages.
- Datetime and Timedelta: Used for handling date and time data.

## DB Schema Design
- User: System users, with attributes like userId, username, password, and role.
- Section: Library sections, with attributes like sectionId, sectionName, description, and dateCreated.
- Book: Books in the library, linked to sections. Attributes include bookId, author, bookName, sectionId, and content.
- IssuedBooks: Tracks book issuance, with attributes like issued_id, bookId, userId, and issueDate.
- Rating: Records user book reviews, with attributes like ratingId, userId, and comment.
- Requests: Stores user book requests, with attributes like ratingId, userId, bookId, and comment.
- History: Maintains transaction history, with attributes like historyId, issueDate, returnDate, bookId, userId, and bookName.

## Architecture and Features
The application follows a client-server architecture, with the backend developed using Flask and the frontend using HTML, and CSS from Bootstrap.

## Project Structure
- Project(Root folder): app.py, database.sqlite3
- Project/templates

## Video
- Youtube Link: https://www.youtube.com/watch?v=He7Ab_xnpAw
