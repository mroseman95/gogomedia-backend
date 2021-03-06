# GoGoMedia                                                                                                  
                                                                                                             
tracks a users list of media they would like to consume, and what they have already consumed
        
## REQUIREMENTS                                                                                              
PostgreSQL server                                                                                            
Python 3.6                                                                                                   
                                                                                                             
## SETUP                                                                                                     
1. `pip install -r requirements.txt` to install the python dependencies                                      
                                                                                                             
2. Startup a *PostgreSQL* server                                                                               
                                                                                                             
3. create a production database                                                                              
                                                                                                             
4. create a test database (optional)                                                                         
                                                                                                             
5. `cp config_template.ini config.ini`
change the `sqlalchemy.url` to the correct value
change the `sqlalchemy.test.url` to the correct value (optional)                                             

6. `export DATABASE_URL=postgresql://username:password@databaseserver/gogomedia`
                                                                                                             
7. run `alembic upgrade head` to setup the production database                                               
                                                                                                             
## Running                                                                                                   
run `python app.py` to start the server                                                                      
                                                                                                             
## Testing                                                                                                   
run `python run_tests.py` to run the tests                                                                       
                                                                                                             
## Endpoints

Response Format:

```
{
    'success': True/False,
    'message': A string detailing what wen't wrong/right on the server,
    'data': Some JSON representing relevant data to the request,
    'auth_token': JWT authentication token returned from login endpoint
        Put the JWT authentication in headers of requests to endpoints
        that require login
}
```

- **/register [POST]** adds a new user
    
    Request Body:
    
    ```
    {
        'username': 'JohnSmith'
        'password': 'pass123'
    }
    ```
    
    Response Messages:
    
    - 422: 'missing parameter \'username\''
    - 422: 'missing parameter \'password\''
    - 422: 'username taken'
    - 201: 'user successfully registered'
    

- **/login [POST]** logs in a user

  Request Body:

  ```
  {
    'username': 'JohnSmith'
    'password': 'pass123'
  }
  ```

  Response Messages:
  
  - 422: 'missing parameter \'username\''
  - 422: 'missing parameter \'password''
  - 401: 'incorrect password'
  - 422: 'user doesn\'t exist'
  - 200: 'user successfully logged in'

- **/logout [GET] (login required)** logs a user out

  Response Messages:
  
  - 200: 'user successfully logged out'
                                                                                                             
- **/user/\<username>/media [PUT] (login required)** add/update a media element for this user

    Request Body:
    
    ```
    {
        'id': unique number
        'name': 'medianame',
        'medium': 'other'/'film'/'audio'/'literature' (optional),
        'consumed_state': 'not started'/'started'/'finished' (optional),
        'description': 'any string <= 500 characters' (optional)
    }
    ```
    
    Response Messages:
    
    - 422: 'missing parameter \'name\' or parameter \'id\''
    - 422: 'id parameter must be type integer'
    - 422: 'name parameter must be type string'
    - 422: 'medium parameter must be \'film\', \'audio\', \'literature\', or \'other\''
    - 422: 'consumed_state parameter must be \'not started\', \'started\', or \'finished\''
    - 422: 'user doesn\'t exist'
    - 422: 'description parameter must be type string'
    - 401: 'not logged in as this user'
    - 401: 'logged in user doesn\'t have media with given id'
    - 200: 'successfully added/updated media element'
    
- **/user/\<username>/media [GET] (login required)** get all media elements for this user

    Response Messages:
    
    - 422: 'user doesn\'t exist'
    - 401: 'not logged in as this user'
    - 200: 'successfully got media for the logged in user'

- **/user/\<username>/media?consumed-state=not-started/started/finished [GET] (login required)** get all consumed or unconsumed media elements for this user

    Response Messages:
    
    - 422: 'user doesn\'t exist'
    - 422: 'consumed-state url parameter must be \'not-started\', \'started\', or \'finished\''
    - 401: 'not logged in as this user'
    - 422: 'consumed url parameter must be \'yes\' or \'no\''
    - 200: 'successfully got media for the logged in user'

- **/user/\<username>/media?medium=other/film/audio/literature [GET] (login required)** get all media elements for this user of a specified medium type

    Response Messages:
    
    - 422: 'user doesn\'t exist'
    - 422: 'medium url parameter must be \'film\', \'audio\', \'literature\', or \'other\''
    - 401: 'not logged in as this user'
    - 422: 'medium url parameter must be \'film\', \'audio\', \'literature\', or \'other\''
    - 200: 'successfully got media for the logged in user'

- **/user/\<username>/media [DELETE] (login required)** delete a media element for this user

    Request Body:
    
    ```
    {
        'id': unique number
    }
    ```
    
    Response Messages:
    
    - 422: 'user doesn\'t exist'
    - 401: 'not logged in as this user'
    - 422: 'missing parameter \'id\''
    - 422: 'id parameter must be type integer'
    - 200: 'successfully deleted media element'

- **all login required endpoints**

    Request Headers:
    
    ```
    {
        'Authorization': 'JWT <auth token>'
    }
    ```
    
    Response Messages:
    - 422: 'authorization header malformed
    - 401: 'auth token blacklisted'
    - 401: 'signature expired'
    - 401: 'invalid token'
    - 401: 'no authorization header'

