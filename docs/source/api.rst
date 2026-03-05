API Documentation
==================

Aura Art provides a REST API for programmatic access to your data.

API Overview
------------

The API is built using Django REST Framework and provides:

* Full CRUD operations for all models
* Filtering and searching capabilities
* Pagination support
* Authentication and permissions
* Serialized data in JSON format

Base URL
--------

All API endpoints are prefixed with ``/api/``:

**Production**: https://aura-art.org/api/

**Development**: http://localhost:8000/api/

Authentication
--------------

API Key Authentication
~~~~~~~~~~~~~~~~~~~~~~

The API supports API key authentication:

.. code-block:: bash

   curl -H "Authorization: Api-Key your-api-key" https://aura-art.org/api/artworks/

Session Authentication
~~~~~~~~~~~~~~~~~~~~~~

For web applications, session authentication is supported:

.. code-block:: bash

   curl -H "Cookie: sessionid=your-session-id" https://aura-art.org/api/artworks/

Endpoints
---------

Artworks API
~~~~~~~~~~~~

List Artworks
^^^^^^^^^^^^^

.. code-block:: http

   GET /api/artworks/

Response:

.. code-block:: json

   {
       "count": 150,
       "next": "https://your-domain.com/api/artworks/?page=2",
       "previous": null,
       "results": [
           {
               "id": 1,
               "title": "Mona Lisa",
               "artist": {
                   "id": 1,
                   "name": "Leonardo da Vinci"
               },
               "year": 1503,
               "medium": "Oil on canvas",
               "dimensions": "77 x 53 cm",
               "created_at": "2025-01-01T00:00:00Z",
               "updated_at": "2025-01-01T00:00:00Z"
           }
       ]
   }

Get Artwork
^^^^^^^^^^^

.. code-block:: http

   GET /api/artworks/{id}/

Create Artwork
^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/artworks/

Request body:

.. code-block:: json

   {
       "title": "New Artwork",
       "artist": 1,
       "year": 2025,
       "medium": "Oil on canvas",
       "dimensions": "50 x 40 cm"
   }

Update Artwork
^^^^^^^^^^^^^^

.. code-block:: http

   PUT /api/artworks/{id}/

Delete Artwork
^^^^^^^^^^^^^^

.. code-block:: http

   DELETE /api/artworks/{id}/

Artists API
~~~~~~~~~~~

List Artists
^^^^^^^^^^^^

.. code-block:: http

   GET /api/artists/

Get Artist
^^^^^^^^^^

.. code-block:: http

   GET /api/artists/{id}/

Create Artist
^^^^^^^^^^^^^

.. code-block:: http

   POST /api/artists/

Update Artist
^^^^^^^^^^^^^

.. code-block:: http

   PUT /api/artists/{id}/

Delete Artist
^^^^^^^^^^^^^

.. code-block:: http

   DELETE /api/artists/{id}/

Collections API
~~~~~~~~~~~~~~~

List Collections
^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/collections/

Get Collection
^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/collections/{id}/

Create Collection
^^^^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/collections/

Update Collection
^^^^^^^^^^^^^^^^^

.. code-block:: http

   PUT /api/collections/{id}/

Delete Collection
^^^^^^^^^^^^^^^^^

.. code-block:: http

   DELETE /api/collections/{id}/

Exhibitions API
~~~~~~~~~~~~~~~

List Exhibitions
^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/exhibitions/

Get Exhibition
^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/exhibitions/{id}/

Create Exhibition
^^^^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/exhibitions/

Update Exhibition
^^^^^^^^^^^^^^^^^

.. code-block:: http

   PUT /api/exhibitions/{id}/

Delete Exhibition
^^^^^^^^^^^^^^^^^

.. code-block:: http

   DELETE /api/exhibitions/{id}/

Contacts API
~~~~~~~~~~~~

List Contacts
^^^^^^^^^^^^^

.. code-block:: http

   GET /api/contacts/

Get Contact
^^^^^^^^^^^

.. code-block:: http

   GET /api/contacts/{id}/

Create Contact
^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/contacts/

Update Contact
^^^^^^^^^^^^^^

.. code-block:: http

   PUT /api/contacts/{id}/

Delete Contact
^^^^^^^^^^^^^^

.. code-block:: http

   DELETE /api/contacts/{id}/

Notes API
~~~~~~~~~

List Notes
^^^^^^^^^^^

.. code-block:: http

   GET /api/notes/

Get Note
^^^^^^^^

.. code-block:: http

   GET /api/notes/{id}/

Create Note
^^^^^^^^^^^

.. code-block:: http

   POST /api/notes/

Update Note
^^^^^^^^^^^

.. code-block:: http

   PUT /api/notes/{id}/

Delete Note
^^^^^^^^^^^

.. code-block:: http

   DELETE /api/notes/{id}/

Filtering and Search
--------------------

Query Parameters
~~~~~~~~~~~~~~~~

All list endpoints support the following query parameters:

* ``search``: Search across relevant fields
* ``ordering``: Sort results by field name
* ``page``: Page number for pagination
* ``page_size``: Number of items per page

Field-Specific Filters
~~~~~~~~~~~~~~~~~~~~~~

Each endpoint supports field-specific filters:

* ``artist__name``: Filter by artist name
* ``year__gte``: Filter by year greater than or equal
* ``year__lte``: Filter by year less than or equal
* ``medium``: Filter by medium
* ``created_at__date``: Filter by creation date

Example Filtering
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Search for artworks by Leonardo da Vinci
   curl "https://your-domain.com/api/artworks/?artist__name=Leonardo"

   # Get artworks from 2020 onwards
   curl "https://your-domain.com/api/artworks/?year__gte=2020"

   # Search for oil paintings
   curl "https://your-domain.com/api/artworks/?search=oil"

Error Handling
--------------

Error Responses
~~~~~~~~~~~~~~~

The API returns appropriate HTTP status codes:

* ``200 OK``: Successful request
* ``201 Created``: Resource created successfully
* ``400 Bad Request``: Invalid request data
* ``401 Unauthorized``: Authentication required
* ``403 Forbidden``: Permission denied
* ``404 Not Found``: Resource not found
* ``500 Internal Server Error``: Server error

Error Format
~~~~~~~~~~~~

Error responses include detailed information:

.. code-block:: json

   {
       "error": "Validation failed",
       "details": {
           "title": ["This field is required."],
           "year": ["Enter a valid year."]
       }
   }

Rate Limiting
-------------

API Limits
~~~~~~~~~~~

The API implements rate limiting to ensure fair usage:

* **Authenticated users**: 1000 requests per hour
* **Anonymous users**: 100 requests per hour

Rate Limit Headers
~~~~~~~~~~~~~~~~~~

Rate limit information is included in response headers:

.. code-block:: http

   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1640995200
