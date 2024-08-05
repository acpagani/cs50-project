# BUILDATA
#### Video Demo:  <URL [https://youtu.be/RDXGWPb5yQI?si=aLBf_D-08Pa3KCFo]>
#### Description:

**Motivation**

Buildata is a Web Application service that facilitates all managing processes throughout a construction. Users are able to see and organize all data related to their constructions, including their workers as well. The platform was developed specially to make an easy-access connection between construction's managers and their clients, also to centralize all data a manager must handle, in a single interface.

**Functionalities**

Diving into Buildata's ecosystem, we are able to explore some features, linked with some pages as well. Once users are logged into the platform, there's a homepage containing all indepent features user can use.
* Workers: Users can register and delete workers from their accounts. When the first worker is registered, a table is created in the Manage workers page, showing workers' data. If there is no worker registered, a blue button will be shown right in the middle of the screen, leading users to register their first worker.
* Constructions: After the first worker's registration, the user can add a new construction to their account, specifying some construction's data, such as a name for it, the client's name, where's the construction's location - its address - and the duration of the process. After the first construction registration, at the Manage constructions page, there will be a card for each construction registered, containing its main specifications. Those cards are actually buttons, leading the user to a speciffic page with some more funcionalities.
* Construction's information page: When a card is clicked, that page will be brought on screen. In a simple and minimalistic interface, the page displays the main information about the construction at stake and show the responsible staff team as well.
* Posting updates: In addition, the user, as a manager, is able to update their clients about the constructions' progress, by posting all the modifications done during a certain time interval. Posts are a easy way of shorten the distance between a manager and their clients, by setting a continuos update connection, since clients can easily access all stuff done in their houses, appartments, etc, without the need to make frequent visits. Also followed by the possibility of seeing photos of those updates (up to the manager posting it or not).

**Technologies Used**

To make this idea possible, I had to put some technologies learned during the course together:
* Front-end: To create all the web interface, I have used HTML, CSS and even JS to help in some input formatting. In addition, the template Jinja2 was also used to simplify page structures and make the page's building process faster.
* Back-end: To make all logic operations and the integration of web structure and database, I have used, in Python, Flask library, and the SQL library from CS50 as well.
* Database: To store server's data, there is a SQLite database, containing the following tables:
    * users: Containing users' data, such as id, username and password (hash)
    * workers: Containing workers' data, and also a Users FK*
    * constructions: Containing constructions' data, such as their id, Users FK, their name, client name, address, starting and ending dates
    * selected_workers: Responsible for linking, when selected into the platform, a worker to a construction, meaning that worker will be in the staff team of the created construction
    * posts: Containing posts' data, such as id, Users FK, Constructions FK, the posting datetime, and the post information (Title and content)
    * photos: Will contain, not the photo bytes by themselves, but a file path to them. At the moment the user submits a post with photos, the script will save those photos to the local repository, in this case, cs50 Codespace. It works that way to ensure the photos' byte-content will not damage the integrity of the database, in case of multiple high-quality photos uploading, for example.

**_OBS:_** _something_ FK refers to a Foreign Key used to link the respective table with the _something_ table. Example: Users FK - refering that the topic table has a Foreign Key to the users table.

**Instructions**

Here are some instructions to facilitate the platform's flow during the usage:
* User registration system: The first screen shows a log in/sign in system, and that actually works! If you are not registered yet, you must create a new account, putting a username and choosing a password. Right after the account creation, you will be automatically redirected to the platform, not being necessary putting your data again just to log in. If you log out and want to return to the same account, you must put the exact same information (username and password) as before during the registration, but, this time, at the log in page.
* Construction registration: When adding a new construction, you MUST have at least one worker registered, otherwise, the application will send you an error message, advertising the missing data
* Worker deleting: If you delete a worker from your workers' table, he will be automatically deleted from all constructions attached to him.
* Selecting the same worker in the staff team: When adding a new construction, the staff interface allows you to select the same worker in different inputs. Although it is not ideal, if it occures, the application will just "group" data with the same values to insert into the database, so the selected workers links will be made once per worker's name.
