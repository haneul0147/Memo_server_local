from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename

from config import Config

from datetime import date, datetime


class MyPostinginfoResource(Resource) :
    @jwt_required()
 # 내가 쓴 포스팅 리스트 보기  
    def get(self,posting_id) :
     
        user_id = get_jwt_identity()

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()
            # 쿼리문 
            query = '''select p.id,u.nickname,p.img_url,p.content,p.created_at from user u
                        join posting p
                        on u.id=p.user_id
                        left join postcomment c 
                        on u.id = c.user_id && c.posting_id =p.id
                        where u.id= %s
                        order by p.created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            posting_list = cursor.fetchall()
            print(posting_list)


            query = '''select c.user_id,u.nickname,c.comment,c.created_at from user u
                        join posting p
                        on u.id=p.user_id
                        left join postcomment c 
                        on u.id = c.user_id && c.posting_id =p.id
                        where p.id= %s
                        order by p.created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            param = (posting_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            comment_list = cursor.fetchall()
            print(comment_list)
             ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
        
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return{'posting_list' : posting_list , 'comment_list':comment_list}

class AllPostinginfoResource(Resource) :
 # 모든 포스팅 리스트 보기  
    def get(self) :
     
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select u.nickname,p.img_url,p.content,p.created_at,c.comment from user u
                        join posting p
                        on u.id=p.user_id
                        left join postcomment c 
                        on u.id = c.user_id && c.posting_id =p.id 
                        order by created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

             ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = str(record['created_at'])
                i = i + 1
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return{'posting_list' : record_list}




class SearchPostinginfoResource(Resource) :
 #  검색한 포스팅 리스트 보기  
    def get(self,user_id) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()
            # 쿼리문 
            query = '''select p.id,u.nickname,p.img_url,p.content,p.created_at from user u
                        join posting p
                        on u.id=p.user_id
                        left join postcomment c 
                        on u.id = c.user_id && c.posting_id =p.id
                        where u.id= %s
                        order by p.created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            posting_list = cursor.fetchall()
            print(posting_list)


            query = '''select c.user_id,u.nickname,c.comment,c.created_at from user u
                        join posting p
                        on u.id=p.user_id
                        left join postcomment c 
                        on u.id = c.user_id && c.posting_id =p.id
                        where p.id= %s
                        order by p.created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            comment_list = cursor.fetchall()
            print(comment_list)
             ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
        
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return{'posting_list' : posting_list}