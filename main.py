from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re
import datetime
from datetime import datetime

connection = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='MusicSystem',
    user='',    # USERNAME
    password='' # PASSWORD
)

app = Flask(__name__)
app.debug = True
app.secret_key = "super secret key"

@app.route("/fostr", methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('Select * from userinfo where email = %s AND password = %s;', (email, password))
        user = cursor.fetchone()

        # If user exists in userinfo table in our database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['id']
            session['email'] = user['email']
            session['username'] = user['full_name']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'

    return render_template('index.html', msg='')


# http://localhost:5000/fostr/logout - this will be the logout page
@app.route('/fostr/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   #session.pop('id', None)
   session.pop('username', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/fostr/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/fostr/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password", "email", "address" and "dob"  POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'addr' in request.form and 'dob' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        addr = request.form['addr']
        dob = request.form['dob']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from userinfo where email = %s;', (email,))
        user = cursor.fetchone()
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not addr or not dob:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO userinfo VALUES (%s, %s, %s, %s, %s)', (username, email, password, addr, dob))
            connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/fostr/home - this will be the home page, only accessible for loggedin users
@app.route('/fostr/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/fostr/profile - this will be the profile page, only accessible for loggedin users
@app.route('/fostr/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM userinfo WHERE email = %s', (session['email'],))
        user = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', user=user)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/fostr/allsongs - this will show all songs, only accessible for loggedin users
@app.route('/fostr/allsongs')
def allsongs():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the songs to be displayed on the page
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM songs')
        all_songs = cursor.fetchall()
        # Show all songs info
        return render_template('allsongs.html', songs=all_songs)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/fostr/add_to_fav', methods=['GET', 'POST'])
def add_to_fav():   # function to add a song to favourite list
    if request.method == 'POST':
        # Create variables for easy access
        title = request.form['title']
        year = request.form['year']
        email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from favourite_songs where title = %s AND year= %s AND email = %s;', (title, year, email))
        fav_song = cursor.fetchone()

        if fav_song:
            print('Already added to the favorites\n')
        else:
            cursor.execute('INSERT INTO favourite_songs VALUES (%s, %s, %s)', (title, year, email))
            connection.commit()
            print('Song added to favourites')
    return redirect(url_for('allsongs'))


@app.route('/fostr/favourite_songs')
def favourite_songs():  # function to list the favourite songs
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the songs to be displayed on the page
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT songs.title, songs.year, songs.album, songs.artist FROM songs, favourite_songs where songs.title = favourite_songs.title AND songs.year = favourite_songs.year AND favourite_songs.email = %s;', (session['email'],))
        fav_songs = cursor.fetchall()
        # Show all songs info
        return render_template('favSongs.html', songs=fav_songs)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/fostr/remove_favourite_songs', methods=['GET', 'POST'])
def remove_favourite_songs():   # function used for removing a song from favourite song list
    print('check')
    if request.method == 'POST':
        # Create variables for easy access
        title = request.form['title']
        year = request.form['year']
        email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('delete from favourite_songs where title = %s AND year= %s AND email = %s;', (title, year, email))
        connection.commit()
    return redirect(url_for('favourite_songs'))


@app.route('/fostr/friends')
def friends():  # function to show the friend list
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT full_name, email FROM userinfo where email IN (select friend_email from friends where user_email = %s);', (session['email'],))
        friend = cursor.fetchall()
        return render_template('friends.html', friends=friend)
    return redirect(url_for('login'))


@app.route('/fostr/fan_groups')
def fan_groups():   #function to display joined fan groups
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM artist_fan_group where group_name IN (select group_name from group_members where member_email = %s);', (session['email'],))
        fan_groups = cursor.fetchall()
        return render_template('fanGroups.html', groups=fan_groups)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/fostr/remove_friends', methods=['GET', 'POST'])
def remove_friends():   # function to remove a friend from the friend list
    if request.method == 'POST':
        # Create variables for easy access
        friend_email = request.form['email']
        user_email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('delete from friends where user_email = %s AND friend_email = %s;', (user_email, friend_email))
        print(friend_email + ' deleted successfully')
        connection.commit()
    return redirect(url_for('friends'))


@app.route('/fostr/msg_friends', methods=['GET', 'POST'])
def msg_friends():  # function to render the msgFriend.html
    if request.method == 'POST':
        friend_email = request.form['email']
        return render_template('msgFriend.html', email=friend_email)
    return redirect(url_for('friends'))


@app.route('/fostr/send_msg_friend', methods=['GET', 'POST'])
def send_msg_friend():  # function to send message to a friend
    if request.method == 'POST' and 'subject' in request.form and 'body' in request.form:
        # Create variables for easy access
        date = str(datetime.now())
        friend_email = request.form['email']
        subject = request.form['subject']
        body = request.form['body']
        cursor = connection.cursor(dictionary=True)

        if not subject or not body:
            msg = 'Please do not leave fields empty'
        else:
            cursor.execute('INSERT INTO message VALUES (%s, %s, %s, %s, %s)', (date, session['email'], friend_email, subject, body))
            connection.commit()
            print('Message sent !!!!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        print('Please do not leave fields empty')
    # Show registration form with message (if any)
    return redirect(url_for('friends'))


@app.route('/fostr/msg_group', methods=['GET', 'POST'])
def msg_group():    # function to render msgGroup.html page
    if request.method == 'POST':
        group_name = request.form['group_name']
        return render_template('msgGroup.html', groupName=group_name)
    return redirect(url_for('fan_groups'))


@app.route('/fostr/send_msg_group', methods=['GET', 'POST'])
def send_msg_group():   # function to send message to each member in a fan group
    if request.method == 'POST' and 'subject' in request.form and 'body' in request.form:
        # Create variables for easy access
        date = str(datetime.now())
        group_name = request.form['groupName']
        subject = request.form['subject']
        body = request.form['body']
        cursor = connection.cursor(dictionary=True)

        if not subject or not body:
            print('Please do not leave fields empty')
        else:
            cursor.execute('SELECT member_email from group_members WHERE group_name = %s AND member_email != %s;', (group_name, session['email']))
            emails = cursor.fetchall()

            for item in emails:
                cursor.execute('INSERT INTO message VALUES (%s, %s, %s, %s, %s)', (date, session['email'], item['member_email'], subject, body))
                connection.commit()
            print('Message sent !!!!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        print('Please do not leave fields empty')
    # Show registration form with message (if any)
    return redirect(url_for('fan_groups'))


@app.route('/fostr/exit_group', methods=['GET', 'POST'])
def exit_group():   # function to leave a fan group
    if request.method == 'POST':
        # Create variables for easy access
        group_name = request.form['group_name']
        user_email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('delete from group_members where group_name = %s AND member_email = %s;', (group_name, user_email))
        print('You exited from ' + group_name)
        connection.commit()

        cursor.execute('select * from group_members where group_name = %s;', (group_name,))
        member = cursor.fetchone()
        if member == None:
            cursor.execute('delete from artist_fan_group where group_name = %s', (group_name,))
            connection.commit()
            print(group_name + ' has zero members so ' + group_name + ' does not exists !!!')

    return redirect(url_for('fan_groups'))


@app.route('/fostr/search_songs', methods=['GET', 'POST'])
def search_songs(): # function to search a song with a keyword
    if request.method == 'POST':
        # Create variables for easy access
        keyword = request.form['title']
        title = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM songs where title like %s;', (title,))
        all_songs = cursor.fetchall()
    return render_template('searchSong.html', songs=all_songs, keyword=keyword)


@app.route('/fostr/add_search_song', methods=['GET', 'POST'])
def add_search_song():  # function to add a song to favourite song list from searched songs
    if request.method == 'POST':
        # Create variables for easy access
        title = request.form['title']
        year = request.form['year']
        email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from favourite_songs where title = %s AND year= %s AND email = %s;', (title, year, email))
        fav_song = cursor.fetchone()

        if fav_song:
            print('Already added to the favorites\n')
        else:
            cursor.execute('INSERT INTO favourite_songs VALUES (%s, %s, %s)', (title, year, email))
            connection.commit()
            print('Song added to favourites')

        keyword = request.form['keyword']
        song_like = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM songs where title like %s;', (song_like,))
        all_songs = cursor.fetchall()
    return render_template('searchSong.html', songs=all_songs, keyword=keyword)


@app.route('/fostr/search_friends', methods=['GET', 'POST'])
def search_friends():   # function to search freinds using keyword
    if request.method == 'POST':
        # Create variables for easy access
        keyword = request.form['name']
        friend_name = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT full_name, email FROM userinfo where full_name like %s AND email != %s;', (friend_name, session['email']))
        all_friends = cursor.fetchall()
    return render_template('searchFriend.html', friends=all_friends, keyword=keyword)


@app.route('/fostr/add_search_friend', methods=['GET', 'POST'])
def add_search_friend():    # function to add a friend from searched friends to friend list
    if request.method == 'POST':
        # Create variables for easy access
        friend_email = request.form['email']
        user_email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from friends where user_email = %s AND friend_email = %s;', (user_email, friend_email))
        fav_song = cursor.fetchone()

        if fav_song:
            print('Already added to the friends\n')
        else:
            cursor.execute('INSERT INTO friends VALUES (%s, %s)', (user_email, friend_email))
            connection.commit()
            print('User added to friend list')

        keyword = request.form['keyword']
        friend_like = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM userinfo where full_name like %s AND email != %s;', (friend_like, session['email']))
        all_friends = cursor.fetchall()
    return render_template('searchFriend.html', friends=all_friends, keyword=keyword)


@app.route('/fostr/search_groups', methods=['GET', 'POST'])
def search_groups():    # function to search fan groups using keyword
    if request.method == 'POST':
        # Create variables for easy access
        keyword = request.form['group']
        group_name = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM artist_fan_group where group_name like %s;', (group_name,))
        all_groups = cursor.fetchall()
    return render_template('searchGroup.html', groups=all_groups, keyword=keyword)


@app.route('/fostr/add_search_group', methods=['GET', 'POST'])
def add_search_group(): # function to join a searched fan group
    if request.method == 'POST':
        # Create variables for easy access
        group_name = request.form['group_name']
        user_email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from group_members where group_name = %s AND member_email = %s;', (group_name, user_email))
        fav_song = cursor.fetchone()

        if fav_song:
            print('Already a member of ' + group_name + ' group')
        else:
            cursor.execute('INSERT INTO group_members VALUES (%s, %s);', (group_name, user_email))
            connection.commit()
            print('U have joined ' + group_name)

        keyword = request.form['keyword']
        group_like = "%" + keyword + "%"
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM artist_fan_group where group_name like %s;', (group_like,))
        all_groups = cursor.fetchall()
    return render_template('searchGroup.html', groups=all_groups, keyword=keyword)


@app.route('/fostr/goto_create_roup', methods=['GET', 'POST'])
def goto_create_group():    # function to render createGroup.html page
    return render_template('createGroup.html')


@app.route('/fostr/create_group', methods=['GET', 'POST'])
def create_group(): # function to create a new fan group
    if request.method == 'POST' and 'group_name' in request.form and 'fav_artist' in request.form and 'description' in request.form:
        # Create variables for easy access
        group_name = request.form['group_name']
        fav_artist = request.form['fav_artist']
        description = request.form['description']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select * from artist_fan_group where group_name = %s;', (group_name,))
        group = cursor.fetchone()
        if group:
            print('Group already exists !!!')
        else:
            if not group_name or not fav_artist or not description:
                print('Please do not leave fields empty')
            else:
                cursor.execute('INSERT INTO artist_fan_group VALUES (%s, %s, %s);', (group_name, fav_artist, description))
                cursor.execute('INSERT INTO group_members VALUES (%s, %s);', (group_name, session['email']))
                connection.commit()
                print('Fan group created !!!!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        print('Please do not leave fields empty')
    return redirect(url_for('home'))


@app.route('/fostr/inbox')
def inbox():    # function to show messages in inbox
    # Check if user is loggedin
    if 'loggedin' in session:
        email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('select date_time, sender, receiver, subject, body from message where sender = %s OR receiver = %s;', (email, email))
        msg = cursor.fetchall()
        return render_template('inbox.html', msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/fostr/remove_msg', methods=['GET', 'POST'])
def remove_msg():   # function to delete a message from inbox
    if request.method == 'POST':
        # Create variables for easy access
        date = request.form['date']
        email = session['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('UPDATE message SET sender = IF(sender = %s, NULL, sender), receiver = IF(receiver = %s, NULL, receiver) WHERE date_time= %s', (email, email, date))
        cursor.execute('DELETE from message WHERE sender = NULL AND receiver = NULL;')
        print('Message deleted successfully')
        connection.commit()

        cursor.execute('select date_time, sender, receiver, subject, body from message where sender = %s OR receiver = %s;', (email, email))
        msg = cursor.fetchall()
    return render_template('inbox.html', msg=msg)


@app.route('/fostr/update_form', methods=['GET', 'POST'])
def update_form():  # function to render updateProfile.html page
    return render_template('updateProfile.html')


@app.route('/fostr/update', methods=['GET', 'POST'])
def update():   # function to update the profile details
    if 'loggedin' in session:
        if request.method == 'POST':
            # Create variables for easy access
            name = request.form['name']
            password = request.form['password']
            addr = request.form['addr']
            cursor = connection.cursor(dictionary=True)
            cursor.execute('UPDATE userinfo SET full_name = %s, password = %s, street_addr = %s WHERE email = %s', (name, password, addr, session['email']))
            print('Profile updated successfully')
            connection.commit()
        return redirect(url_for('profile'))
    return redirect(url_for('login'))


@app.route('/fostr/generate_report', methods=['GET', 'POST'])
def generate_report():  # function to generate a report for a user
    if request.method == 'POST' and 'email' in request.form:
        # Create variables for easy access
        email = request.form['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT full_name, email FROM userinfo where email IN (select friend_email from friends where user_email = %s);', (email,))
        friends = cursor.fetchall()

        cursor.execute('SELECT * FROM artist_fan_group where group_name IN (select group_name from group_members where member_email = %s);', (email,))
        groups = cursor.fetchall()

        cursor.execute('select date_time, sender, receiver, subject, body from message where sender = %s OR receiver = %s;', (email, email))
        msg = cursor.fetchall()
    return render_template('report.html', friends=friends, groups=groups, msg=msg)
