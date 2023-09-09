from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK,HTTP_201_CREATED
from .serializers import *
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import permission_classes
from .models import *


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data
            print('Data: ', data)
            response = {"status": "success", "data": "", "http_status": HTTP_201_CREATED} 
            serializer = CustomUserSerializer(data=data)

            if serializer.is_valid():
                # Hash the password before saving
                password = make_password(data.get('password'))
                serializer.validated_data['password'] = password

                # Save the user object
                user = serializer.save()
                print("User is: ", user)
                response['status'] = "success"
                response["data"] = serializer.data
            else:
                response["status"] = "error"
                response["http_status"] = HTTP_400_BAD_REQUEST
                response["data"] = serializer.errors

        except Exception as e:
            response["status"] = "error"
            response["http_status"] = HTTP_400_BAD_REQUEST
            response["data"] = str(e)

        return JsonResponse(response, status=response.get('http_status', HTTP_200_OK))
            

class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer

    def post(self, request):
        response = {"status": "success", "data": "", "http_status": HTTP_200_OK}

        # Extract email and password from the request data
        email = request.data.get("email")
        password = request.data.get("password")

        if email and password:  # Check if email and password are provided
            # Authenticate the user
            user = authenticate(request=request, username=email, password=password)
            print("user is : ", user)

            if user is not None:
                login(request, user)
                response['status'] = "success"
                response['data'] = "logged in successfully"
            else:
                response['status'] = "failed"
                response['data'] = "invalid credentials"
                response['http_status'] = HTTP_400_BAD_REQUEST
        else:
            response["status"] = "error"
            response["http_status"] = HTTP_400_BAD_REQUEST
            response["data"] = "email and password are required"

        return JsonResponse(response, status=response.get('http_status', HTTP_200_OK))



class CreateContentView(APIView):

    def post(self, request):
        response = {"status": "success", "data": "", "http_status": HTTP_201_CREATED}

        username = request.data.get('username')
        user_queryset = CustomUser.objects.filter(username=username)
        user = user_queryset.first()
        
        if user.role == 'author':
            serializer = ContentItemSerializer(data=request.data.get('content'))
            
            if serializer.is_valid():
               content_item  =  serializer.save(author = user)
               response["data"] = ContentItemSerializer(content_item).data
        else:
            response["status"] = "error"
            response["data"] = 'Only authors can create content'
            response['http_status'] = HTTP_400_BAD_REQUEST

        return JsonResponse(response, status=response["http_status"])
    


class GetAllContentView(APIView):
    def post(self, request):
        response = {"status": "success", "data": "", "http_status": HTTP_200_OK}
        username = request.data.get('username')
        user_queryset = CustomUser.objects.filter(username=username)
        user = user_queryset.first()  # Get the first matching user, if any

        if user is not None:
            if user.role == 'admin':

                query_set = ContentItem.objects.all()
                serializers = ContentItemSerializer(query_set, many=True)
                response['status'] = "success"
                response["data"] = serializers.data

            elif user.role == 'author':

                # Retrieve content items created by the author
                query_set = ContentItem.objects.filter(author=user)
                serializers = ContentItemSerializer(query_set, many=True)
                response['status'] = "success"
                response["data"] = serializers.data

        
        return JsonResponse(response, status=response.get('http_status', HTTP_200_OK))


