
Demonstrate a good grasp of database normalization.

The Artists and Venues models are in third normal form.

The code has accurate SQL queries wrapped in SQLAlchemy commands per API endpoint, calling to define data models and serving expected responses per API endpoint.

Use SQL to create records with uniqueness constraints.

Code connects the New Artist and New Venue forms to a database by successfully using SQLAlchemy to insert new records into the database upon form submission.

Code correctly uses SQL constraints to ensure fields that need to be unique, and fields that are required, are given these constraints on the database level, throwing an error if otherwise.


A user cannot submit an invalid form submission (e.g. using an invalid State enum, or with required fields missing; missing city, missing name, or missing genre is not required).
A user cannot submit an invalid form submission (e.g. without required fields)

CHALLENGE: Implement time availability, so that an artist is only available to be booked at certain dates/times. Disable the ability to create book an artist for a show outside of their availability.

Show Recent Listed Artists and Recently Listed Venues on the homepage, returning results for Artists and Venues sorting by newly created. Limit to the 10 most recently listed items.

Showcase what albums and songs an artist has on the Artist’s page.

Implement form submissions There should be proper constraints, powering the /create endpoints that serve the create form templates, to avoid duplicate or nonsensical form submissions. Submitting a form should create proper new records in the database.

flask db migrate should work, and populate my local postgres database with properly configured tables for this application's objects, including proper columns, column data types, constraints, defaults, and relationships that completely satisfy the needs of this application. The proper type of relationship between venues, artists, and shows should be configured.


Implement artist availability. An artist can list available times that they can be booked. Restrict venues from being able to create shows with artists during a show time that is outside of their availability.
Show Recent Listed Artists and Recently Listed Venues on the homepage, returning results for Artists and Venues sorting by newly created. Limit to the 10 most recently listed items.
Implement Search Artists by City and State, and Search Venues by City and State. Searching by "San Francisco, CA" should return all artists or venues in San Francisco, CA.
