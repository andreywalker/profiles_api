# Profiles API

REST API for the Profiles app: people, the groups they belong to, and custom fields that can be added at any time.

**Stack:** Flask, Flask-SQLAlchemy, PostgreSQL 18, Docker Compose

## How to run

1. Put the `.env` file in the project root (it is in the submitted zip).
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. The API runs at `http://localhost:8000`.

On first start the tables are created with the group "No group" and the custom fields "Favorite color", "Wishlist" and "Facts".

To stop: `docker compose down`. To also delete the data: `docker compose down -v`.

## Endpoints

**Groups**
- `GET /api/groups/`: list groups ("No group" is last)
- `GET /api/groups/{id}`: one group with its persons
- `POST /api/groups/`: create a group
    ```json
    {
      "name": "Friends"
    }
    ```
- `PUT /api/groups/{id}`: rename a group
    ```json
    {
      "name": "Close friends"
    }
    ```
- `DELETE /api/groups/{id}`: delete a group; its persons move to "No group"

**Custom fields**
- `GET /api/fields/`: list fields ("Facts" is last)
- `GET /api/fields/{id}`: one field
- `POST /api/fields/`: create a field; `type` is `TEXT`, `NUMBER`, `DATE` or `BOOLEAN` (default `TEXT`)
    ```json
    {
      "name": "Shoe size",
      "type": "NUMBER"
    }
    ```
- `PUT /api/fields/{id}`: update a field
    ```json
    {
      "name": "Shoe size EU"
    }
    ```
- `DELETE /api/fields/{id}`: delete a field together with its values

**Persons**
- `GET /api/persons/`: list persons
    - `group_id`: only persons in this group
    - `search`: match in first name or surname
    - Example: `/api/persons/?group_id=2&search=ann`
- `GET /api/persons/{id}`: one person
- `POST /api/persons/`: create a person (`first_name`, `surname`, `birth_date` are required)
    ```json
    {
      "first_name": "Anna",
      "surname": "Ivanova",
      "birth_date": "2003-05-14",
      "group_id": 2,
      "met": "University, first year",
      "phone": "+77001234567",
      "telegram": "@anna",
      "custom_fields": {
        "Favorite color": "Green",
        "Facts": "Loves cats"
      }
    }
    ```
- `PUT /api/persons/{id}`: update any fields; `""` removes a custom value
    ```json
    {
      "subtitle": "Best friend",
      "custom_fields": {
        "Wishlist": "Headphones",
        "Favorite color": ""
      }
    }
    ```
- `DELETE /api/persons/{id}`: delete a person

"No group" and "Facts" cannot be deleted.

## Status codes
- `200` OK
- `201` Created
- `400` Invalid data, or "No group" / "Facts" can't be changed
- `404` Not found
- `405` Method not allowed
- `409` Name already exists

## Documentation and Postman

- Full API reference: `docs/API.md`
- Import `postman/Profiles-API.postman_collection.json` and run the folders top to bottom.
