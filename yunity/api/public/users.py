from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.views.generic import View

from yunity.api.ids import user_id_uri_pattern, multiple_user_id_uri_pattern
from yunity.api.validation import validate_user_email, validate_user_display_name
from yunity.api.validation import validate_user_password
from yunity.utils.api.abc import ApiBase, body_as_json, resource_as_list, resource_as
from yunity.utils.request import Parameter
from yunity.models import Category as CategoryModel


def _has_rights_to_modify(request_user_id, modified_user_id):
    return request_user_id == modified_user_id


class UserAll(ApiBase, View):
    @body_as_json(parameters=[
        Parameter(name='email', validator=validate_user_email),
        Parameter(name='password', validator=validate_user_password),
        Parameter(name='display_name', validator=validate_user_display_name),
    ])
    def post(self, request):
        """register a new user
        ---
        tags:
            - User
        parameters:
            - in: body
              name: body
              schema:
                  id: create_user
                  required:
                    - email
                    - password
                    - display_name
                  properties:
                      email:
                          type: string
                          description: email address of new user
                          example: paul@example.com
                      password:
                          type: string
                          description: Password for user. Will be validated to specific rules
                          example: PaulsStrongPasswordWhichHeNeverForgets
                      display_name:
                          type: string
                          example: Paul
                          description: The public displayed name
        responses:
            201:
                description: User created
                schema:
                  id: user_information_response
                  allOf:
                          - $ref: '#/definitions/user_information'
                          - type: object
                            required:
                              - id
                            properties:
                              id:
                                type: number
                                description: Identifier of the User
                                example: 3
            409:
                description: That emailaddress is already registered
        ...

        :type request: HttpRequest
        """
        category = CategoryModel.objects.get(name='user.default')
        try:
            locations = [{
                'description': request.body['location_description'],
                'latitude': request.body['latitude'],
                'longitude': request.body['longitude'],
            }]
        except KeyError:
            locations = []
        try:
            with transaction.atomic():
                user = get_user_model().objects.create_user(
                    email=request.body['email'],
                    password=request.body['password'],
                    locations=locations,
                    category=category,
                    display_name=request.body['display_name'],
                )
        except IntegrityError:
            return self.conflict(reason='user already exists')

        return self.created({
            "id": user.id,
            "display_name": user.display_name,
        })


class UserMultiple(ApiBase, View):
    @resource_as_list('users', item_type=get_user_model())
    def get(self, request, users):
        """get details about all given users
        ---
        tags:
            - User
        parameters:
            - in: path
              name: userids
              type: array
              collectionFormat: csv
              items:
                  type: integer

        responses:
            201:
                description: User information
                schema:
                    type: object
                    properties:
                      users:
                        type: array
                        items:
                            $ref: '#/definitions/user_information_response'
            404:
                description: one or more users do not exist
        ...

        :type request: HttpRequest
        :type users: [UserModel]

        """
        return self.success({"users": [{
            'id': _.id,
            'display_name': _.display_name,
            'picture_url': _.picture_url,
        } for _ in users]})


class UserSingle(ApiBase, View):
    @resource_as('user', item_type=get_user_model())
    @body_as_json(parameters=[
        Parameter(name='display_name', validator=validate_user_display_name),
    ])
    def put(self, request, user):
        """Modify a user: Yourself or any user you have sufficient rights for.
        Only the provided fields will be changed. To clear fields, set them explicitly as empty.
        ---
        tags:
            - User
        parameters:
            - in: path
              name: userid
              type: integer
            - in: body
              name: body
              required: true
              schema:
                  id: user_information
                  properties:
                      display_name:
                        type: string
                        example: Paul
                        description: Display name of the user

        responses:
            201:
                description: User information
                schema:
                    $ref: '#/definitions/user_information_response'
            403:
                description: You are not allowed to modify that user
            404:
                description: the user does not exist
        ...

        :type request: HttpRequest
        :type user: UserModel
        """
        if not _has_rights_to_modify(request.user.id, user.id):
            return self.forbidden(reason='current user does not have rights to modify user {}'.format(user.id))

        user.display_name = request.body['display_name']
        user.save()

        return self.created({
            'id': user.id,
            'display_name': user.display_name,
        })


urlpatterns = [
    url(r'^$', UserAll.as_view()),
    url(r'^{user}/?$'.format(user=user_id_uri_pattern), UserSingle.as_view()),
    url(r'^{users}/?$'.format(users=multiple_user_id_uri_pattern), UserMultiple.as_view()),
]
