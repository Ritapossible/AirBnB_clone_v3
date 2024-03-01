#!/usr/bin/python3
"""The API endpoint for /api/v1/places"""
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State


def get_places_with_states(state_ids):
    """get places in states"""
    states = []
    for state_id in state_ids:
        state = storage.get(State, state_id)
        if state:
            states.append(state)
    cities = [city for state in states for city in state.cities]
    places = [place for city in cities for place in city.places]
    return places


def get_places_with_cities(city_ids):
    """get places in cities"""
    cities = []
    for city_id in city_ids:
        city = storage.get(City, city_id)
        if city:
            cities.append(city)
    places = [place for city in cities for place in city.places]
    return places


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """search"""
    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    states = data.get("states", [])
    cities = data.get("cities", [])
    amenities = data.get("amenities", [])

    places = []
    if states:
        states_places = get_places_with_states(states)
        places += states_places

    if cities:
        cities_places = get_places_with_cities(cities)
        places += cities_places

    if not cities and not states:
        places = list(storage.all(Place).values())

    if amenities:
        amenities_places = [
            place
            for place in places
            if all(amenity_id in place.amenity_ids for amenity_id in amenities)
        ]
        places = amenities_places

    result = [place.to_dict() for place in places]
    return jsonify(result)


@app_views.route(
    "/cities/<city_id>/places",
    methods=["GET"],
    strict_slashes=False,
)
def get_places_by_city(city_id):
    """get places by city"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route(
    "/places/<place_id>",
    methods=["GET"],
    strict_slashes=False,
)
def get_place(place_id):
    """get place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route(
    "/places/<place_id>",
    methods=["DELETE"],
    strict_slashes=False,
)
def delete_place(place_id):
    """delete place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route(
    "/cities/<city_id>/places",
    methods=["POST"],
    strict_slashes=False,
)
def create_place(city_id):
    """create place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.is_json:
        abort(400, description="Not a JSON")
    data = request.get_json()
    if "user_id" not in data:
        abort(400, description="Missing user_id")
    user_id = data["user_id"]
    if not storage.get(User, user_id):
        abort(404)
    if "name" not in data:
        abort(400, description="Missing name")
    new_place = Place(**data)
    new_place.city_id = city_id
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route(
    "/places/<place_id>",
    methods=["PUT"],
    strict_slashes=False,
)
def update_place(place_id):
    """update place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.is_json:
        abort(400, description="Not a JSON")
    data = request.get_json()
    for key, value in data.items():
        if key not in ["id", "user_id", "city_id", "created_at", "updated_at"]:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200
