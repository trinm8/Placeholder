# Technologies
This file contains an overview of which technologies we're going to use and how they're related to each other.
## Dependencies
When someone requests to view our site using their _client_ (browser), this requests gets sent to the _webserver_. The webserver accesses a _data service_, which accesses a _relational database_.
### Client (Web Design)
We will use **Javascript**, **CSS** and **HTML**, as well as **Bootstrap**. Those are all used for the layout of our system. (JQuery?, Material Design? or Bulma instead of Bootstrap?)
### Web server
We'll use python with the **Flask** library to use it as webserver. Flask uses Jinja2 to load personalized HTML-templates. (REST?)
Flask will render everything client-side. You can also choose to render your site on the client-side by using JavaScript, JQuery and Ajax.
### Data service
We wil use **psycopg2** to handle SQL-requests in python to our database. (Pandas? Scikit-learn? preprocessing?)
### Relational Database
As described in the assignment, we'll use **PostgreSQL**.
### Hosting
When you do a request using your client to a site, you get sent to the place where the site is hosted. This will be **Google Cloud Platform** for our project.
### Database Design
For visualizing our database design, we'll use **DBdiagram**.
### Map
We need to use an api to display a map on the site, to calculate an efficient route, ... We'll use **OpenStreetMap API** for this.
### Version Control System
**GitHub** will be used for version control.
### Planning
We're using **toggl** to plan our deadlines and get an overview of who will work when on which feature.
### API
To test and document our API, we'll use apiary.