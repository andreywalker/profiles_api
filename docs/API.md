# Profiles API

Base URL: `http://localhost:8000` · JSON

## Data types

**Group**
- `id`: integer (read-only)
- `name`: string (required, unique)
- `is_default`: boolean (read-only, `true` = "No group")
- `person_count`: integer (read-only)

**Field**
- `id`: integer (read-only)
- `name`: string (required, unique)
- `type`: `TEXT` | `NUMBER` | `DATE` | `BOOLEAN` (default `TEXT`)
- `deletable`: boolean (read-only, `false` = "Facts")
- `position`: integer (read-only)

**Person**
- `id`: integer (read-only)
- `first_name`: string (required)
- `surname`: string (required)
- `birth_date`: string `YYYY-MM-DD` (required)
- `age`: integer (read-only)
- `group_id`: integer (input, default = "No group")
- `group`: `{ id, name }` (read-only)
- `met`, `subtitle`, `phone`, `telegram`, `instagram`, `other_media`: string (optional)
- `custom_fields`: `{ "field name": value }` (optional; `""` removes a value)

## Endpoints

**Groups**
- `GET` `/api/groups/`: list groups
- `GET` `/api/groups/{id}`: one group with its persons
- `POST` `/api/groups/`: create, body `{ name }`
    ```json
    {
      "name": "Friends"
    }
    ```
- `PUT` `/api/groups/{id}`: rename, body `{ name }`
    ```json
    {
      "name": "Close friends"
    }
    ```
- `DELETE` `/api/groups/{id}`: delete; its persons move to "No group"

**Fields**
- `GET` `/api/fields/`: list fields
- `GET` `/api/fields/{id}`: one field
- `POST` `/api/fields/`: create, body `{ name, type? }`
    - `TEXT`, `NUMBER`, `DATE`, `BOOLEAN` (default `TEXT`)
    ```json
    {
      "name": "Shoe size",
      "type": "NUMBER"
    }
    ```
- `PUT` `/api/fields/{id}`: update, body `{ name?, type? }`
    ```json
    {
      "name": "Shoe size EU"
    }
    ```
- `DELETE` `/api/fields/{id}`: delete, together with its values

**Persons**
- `GET` `/api/persons/`: list persons; filters `?group_id=` and `?search=`
- `GET` `/api/persons/{id}`: one person
- `POST` `/api/persons/`: create, body Person
    ```json
    {
      "first_name": "Anna",
      "surname": "Ivanova",
      "birth_date": "2003-05-14",
      "group_id": 2,
      "met": "University, first year",
      "subtitle": "Classmate",
      "phone": "+77001234567",
      "telegram": "@anna",
      "instagram": "@anna.iv",
      "other_media": "https://example.com/anna",
      "custom_fields": {
        "Favorite color": "Green",
        "Wishlist": "Kindle",
        "Facts": "Loves cats"
      }
    }
    ```
- `PUT` `/api/persons/{id}`: update, body any Person fields
    ```json
    {
      "subtitle": "Best friend",
      "group_id": 1,
      "custom_fields": {
        "Wishlist": "Headphones",
        "Favorite color": ""
      }
    }
    ```
- `DELETE` `/api/persons/{id}`: delete

## Status codes
- `200` OK
- `201` Created
- `400` Invalid data, or "No group" / "Facts" can't be changed
- `404` Not found
- `405` Method not allowed
- `409` Name already exists
