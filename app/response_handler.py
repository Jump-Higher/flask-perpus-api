from http import HTTPStatus
from flask import make_response,jsonify

def ok(data, message):
    response = {
            "code": "200",
            "status": "OK",
            "data": data,
            "message": message
    }
    return make_response(jsonify(response)),HTTPStatus.OK.value

def ok_with_meta(data, meta):
    response = {
            "code": "200",
            "status": "OK",
            "data": data,
            "meta": meta
    }
    return make_response(jsonify(response)),HTTPStatus.OK.value

def created(data, message):
    response = {
            "code": "201",
            "status": "CREATED",
            "data": data,
            "message": message
    }
    return make_response(jsonify(response)),HTTPStatus.CREATED.value

def bad_request(data):
    response = {
        "code": "400",
        "status": "BAD_REQUEST",
        "errors": data
    }
    return make_response(jsonify(response)),HTTPStatus.BAD_REQUEST.value

def conflict(data):
    response = {
        "code": "409",
        "status": "CONFLICT",
        "errors": data
    }
    return make_response(jsonify(response)),HTTPStatus.CONFLICT.value


def bad_gateway(data):
    response = {
        "code": "500",
        "status": "BAD_GATEWAY",
        "errors": data
    }
    return make_response(jsonify(response)),HTTPStatus.BAD_GATEWAY.value

def forbidden(data):
    return make_response(jsonify(data)),HTTPStatus.FORBIDDEN.value

def unautorized(data):
    response = {
        "code": "401",
        "status": "UNAUTHORIZED",
        "errors": data
    }
    return make_response(jsonify(response)),HTTPStatus.UNAUTHORIZED.value

def not_found(data):
    response = {
        "code": "404",
        "status": "NOT_FOUND",
        "errors": data
    }
    return make_response(jsonify(response)),HTTPStatus.NOT_FOUND.value