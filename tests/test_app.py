from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, jsonify)


def test_index(app, client):
    res = client.get('/')
    assert res.status_code == 200


def test_public(app, client):
    res = client.get('/public')
    assert res.status_code == 200


def test_public_page(app, client):
    res = client.get('/public?page_number=2')
    assert res.status_code == 200


def test_login(app, client):
    res = client.get('/login')
    assert res.status_code == 200


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_logout(client):
    """Make sure login and logout works."""

    username = "keith"
    password = "keith"

    rv = login(client, username, password)
    assert b'Dashboard' in rv.data

    rv = logout(client)
    assert b'You have been logged out' in rv.data

    rv = login(client, f"{username}x", password)
    assert b'Incorrect Username and/or Password' in rv.data

    rv = login(client, username, f'{password}x')
    assert b'Incorrect Username and/or Password' in rv.data


def test_signup(client):
    res = client.post('/signup', data = {'firstName' : 'test', 'lastName' : 'user', 'email' : 'test@user.org', 'username': 'xcvxcvxv', 'password' : '12'}, follow_redirects=True)

    assert b'Registration Successful! You can now login' in res.data
