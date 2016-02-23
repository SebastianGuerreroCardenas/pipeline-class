"""`main` is the top level module for your Flask application."""
# Imports
import os
import jinja2
import webapp2
import logging
import json
import urllib
import httplib2
import MySQLdb
import math

# this is used for constructing URLs to google's APIS
from googleapiclient.discovery import build


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'byte3-sgc:byte3-sgc-db'
_DB_NAME = 'mobile'
_USER = 'test1' # or whatever other user account you created

# if (os.getenv('SERVER_SOFTWARE') and
#     os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
#     _DB = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db=_DB_NAME, user=_USER)
# else:
#     _DB = MySQLdb.connect(host='173.194.104.23', port=3306, db=_DB_NAME, user=_USER, charset='utf8')

API_KEY = 'AIzaSyAlHYlXQBlsQua6x9KytaZdbfiB525reMw'
service = build('fusiontables', 'v1',developerKey=API_KEY)
# This uses discovery to create an object that can talk to the 
# fusion tables API using the developer key
TABLE_ID = '1WNFN_lwiWlL6hUWUiRsknn9GJRQav2KkpqKXTYrz'
CLEAN_TABLE_ID = '1TOdb9cHWdUkuXg6d5B9_xPX5rbQxlkFCJkZSvNd_'

# Import the Flask Framework
from flask import Flask, request

app = Flask(__name__)
app.debug = True


def get_all_data(SQLquery):
    response = service.query().sql(sql=SQLquery).execute()
    return response

def constructQueryByCols(cols,TABLE_ID):
    string_cols = ""
    if cols == []:
        cols = ['*']
    for col in cols:
        for c in col:
            if c.isspace():
                col = "'" + col + "'"
                break
        string_cols = string_cols + ", " + col
    string_cols = string_cols[2:len(string_cols)]
    query = "SELECT " + string_cols + " FROM " + TABLE_ID + " LIMIT 10"
    return query

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def index():
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        _DB = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db=_DB_NAME, user="root", charset='utf8',passwd= 'hello')
    else:
        _DB = MySQLdb.connect(host='173.194.104.23', port=3306, db=_DB_NAME, user=_USER, charset='utf8')

    cursor = _DB.cursor()

    locations = list(make_query(cursor, 'SELECT double_latitude, double_longitude FROM locations LIMIT 300') )
    for i,row  in enumerate(locations):
        locations[i] = list(row)

    template = JINJA_ENVIRONMENT.get_template('templates/index.html')
    allHeaders = get_all_data(constructQueryByCols([],TABLE_ID))
    cleanHeaders = get_all_data(constructQueryByCols([],CLEAN_TABLE_ID))


    return template.render(headers=allHeaders['columns'], content=allHeaders['rows'],
                            cleanHeaders=cleanHeaders['columns'], cleanContent=cleanHeaders['rows'], location= locations)

@app.route('/_update_table', methods=['POST']) 
def update_table():
    cols = request.json['cols']
    cleanCols = request.json['cleanCols']
    for col in range(0,len(cleanCols)):
        cleanCols[col] = cleanCols[col][5:]
    result = get_all_data(constructQueryByCols(cols,TABLE_ID))
    cleanResult = get_all_data(constructQueryByCols(cleanCols,CLEAN_TABLE_ID))
    return json.dumps({'content' : result['rows'], 'headers' : result['columns'],'cleanContent' : cleanResult['rows'], 'cleanHeaders' : cleanResult['columns']})


@app.route('/about')
def about():
    template = JINJA_ENVIRONMENT.get_template('templates/about.html')
    return template.render()

@app.route('/quality')
def quality():
    template = JINJA_ENVIRONMENT.get_template('templates/quality.html')
    return template.render()

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


def make_query(cursor, query):
    # this is for debugging -- comment it out for speed
    # once everything is working

    try:
        # try to run the query
        cursor.execute(query)
        app.logger.warning('it worked')
        # and return the results
        return cursor.fetchall()
    
    except Exception:
        # if the query failed, log that fact
        app.logger.warning("query making failed")
        app.logger.warning(query)

        # finally, return an empty list of rows 
        return []

def make_and_print_query(cursor, query, description):
    logging.info(description)
    logging.info(query)
    
    rows = make_query(cursor, query)