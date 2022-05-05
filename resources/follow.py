from flask import request
from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error
# 내가만든 커넥션 함수 임포트
from mysql_connection import get_connection

from flask_jwt_extended import jwt_required, get_jwt_identity

import boto3
from config import Config
from datetime import datetime


class FollowResource(Resource) :
    # 팔로우 추가
    @jwt_required() # 이 함수는 optional 파라미터가 False면, 무조건 토큰이 있어야 호출가능
    def post(self, f_user_id) :
        user_id = get_jwt_identity()
        try : 
            # 1. DB에 연결
            connection = get_connection()

            query = '''insert into follow
                        (follower_id, following_id)
                        values
                        (%s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = (user_id, f_user_id)
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error', e)
            return {'error' : 500, 'result' : str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
        # finally는 필수는 아니다.
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                return {'error' : 200, 'result' : "팔로우 추가했습니다."}, HTTPStatus.OK

            
    
    
    # 팔로우 삭제
    @jwt_required() 
    def delete(self, f_user_id) :
        user_id = get_jwt_identity()
        try : 
            # 1. DB에 연결
            connection = get_connection()
            query = '''delete from follow
                        where follower_id = %s and following_id = %s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = (user_id , f_user_id )
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error', e)
            return {'error' : 400, 'result' : str(e)}, HTTPStatus.BAD_REQUEST
        # finally는 필수는 아니다.
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
                return {'error' : 200,'result' : '잘 삭제되었습니다.'}, HTTPStatus.OK


class FollowListResource(Resource) :
    @jwt_required()
    def get(self) :
        user_id = get_jwt_identity()
        print(user_id)
        try :
            # 클라이언트가 GET 요청하면, 이 함수에서 우리가 코드를 작성해 주면 된다.
            
            # 1. db 접속
            connection = get_connection()

            # 2. 해당 테이블, recipe 테이블에서 select
            query = '''select f.follower_id, f.following_id, u.nickname, u.img_url
                        from
                        (select * from follow
                        where follower_id=%s) f
                        left join user u
                        on f.following_id = u.id
                        order by nickname; '''
            
            record = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            # select 문은 아래 내용이 필요하다.
            # 커서로 부터 실행한 결과 전부를 받아와라.
            record_list = cursor.fetchall()
            print(record_list)

        # 3. 클라이언트에 보낸다. 
        except Error as e :
            # 뒤의 e는 에러를 찍어라 error를 e로 저장했으니까!
            print('Error while connecting to MySQL', e)
            return {'error' : 500, 'list' : []}, HTTPStatus.INTERNAL_SERVER_ERROR
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally : 
            print('finally')
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return {'error' : 200, 'list' : record_list }, HTTPStatus.OK 


class SearchUserResource(Resource) :
    def get(self) :
        # 쿼리 파라미터 가져오기
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        keyword = request.args.get('keyword')

        try : 
            # 1. DB에 연결
            connection = get_connection()

         # 2. 해당 테이블, recipe 테이블에서 select
            query = '''SELECT user.id, user.nickname , user.img_url 
                        FROM user
                        where nickname like "%''' + keyword +'''%"
                        order by nickname
                        limit '''+ offset +''', '''+ limit + '''; '''
            
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, )
            # select 문은 아래 내용이 필요하다.
            # 커서로 부터 실행한 결과 전부를 받아와라.
            record_list = cursor.fetchall()
            print(record_list)
            
        # 3. 클라이언트에 보낸다. 
        except Error as e :
            # 뒤의 e는 에러를 찍어라 error를 e로 저장했으니까!
            print('Error while connecting to MySQL', e)
            return {'error' : 500, 'count' : 0, 'list' : []}, HTTPStatus.INTERNAL_SERVER_ERROR
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally : 
            print('finally')
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return {'error' : 200, 'count' : len(record_list), 'list' : record_list }, HTTPStatus.OK



