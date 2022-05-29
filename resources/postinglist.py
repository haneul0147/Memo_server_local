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
    def get(self) :
     
        user_id = get_jwt_identity()

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()
            # 쿼리문
            query = '''select pl.id,pl.user_id,pl.nickname,pl.img_url,pl.content,pl.created_at,pcl.mpid as comment_id ,cl.id as comment_user_id,cl.nickname as comment_nickname,pcl.comment,pcl.created_at as comment_created_at
                        from  (select posting.id, posting.user_id, user.nickname, posting.img_url, posting.content, posting.created_at
                        from posting
                        left join user
                        on posting.user_id = user.id
                        order by posting.created_at desc
                        limit '''+ offset + ','+limit+''') as pl
                        left join
                        (select p.id,p.posting_id, max(p.id) as mpid,p.comment,p.created_at,p.user_id
                        from postcomment p
                        group by posting_id
                        order by posting_id desc) as pcl
                        on pl.id = pcl.posting_id && pcl.id=pcl.mpid
                        left join 
                        (select u.id,u.nickname
                        from user u)as cl
                        on pcl.user_id = cl.id
                        where pl.user_id = %s ;'''
            
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            posting_list = cursor.fetchall()
            print(posting_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            l = 0
            for record in posting_list:
                posting_list[i]['created_at'] = str(record['created_at'])
                posting_list[l]['comment_created_at'] = str(record['comment_created_at'])
                i = i + 1
                l = l + 1 

            
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
        return{'posting_list' : posting_list }

class AllPostinginfoResource(Resource) :
 # 모든 포스팅 리스트 보기  
    def get(self) :
     
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select pl.id,pl.user_id,pl.nickname,pl.img_url,pl.content,pl.created_at,pcl.mpid as comment_id ,cl.id as comment_user_id,cl.nickname as comment_nickname,pcl.comment,pcl.created_at as comment_created_at
                        from  (select posting.id, posting.user_id, user.nickname, posting.img_url, posting.content, posting.created_at
                        from posting
                        left join user
                        on posting.user_id = user.id
                        order by posting.created_at desc
                        limit '''+ offset + ','+limit+''') as pl
                        left join
                        (select p.id,p.posting_id, max(p.id) as mpid,p.comment,p.created_at,p.user_id
                        from postcomment p
                        group by posting_id
                        order by posting_id desc) as pcl
                        on pl.id = pcl.posting_id && pcl.id=pcl.mpid
                        left join 
                        (select u.id,u.nickname
                        from user u)as cl
                        on pcl.user_id = cl.id ;'''
            
            
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,)

            # select 문은 아래 내용이 필요하다.
             # select 문은 아래 내용이 필요하다.
            posting_list = cursor.fetchall()
            print(posting_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            l = 0
            for record in posting_list:
                posting_list[i]['created_at'] = str(record['created_at'])
                posting_list[l]['comment_created_at'] = str(record['comment_created_at'])
                i = i + 1
                l = l + 1 

            
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




class SearchPostinginfoResource(Resource) :
 #  검색한 포스팅 리스트 보기  
    def get(self,user_id) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()
          # 쿼리문
            query = '''select pl.id,pl.user_id,pl.nickname,pl.img_url,pl.content,pl.created_at,pcl.mpid as comment_id ,cl.id as comment_user_id,cl.nickname as comment_nickname,pcl.comment,pcl.created_at as comment_created_at
                        from  (select posting.id, posting.user_id, user.nickname, posting.img_url, posting.content, posting.created_at
                        from posting
                        left join user
                        on posting.user_id = user.id
                        order by posting.created_at desc
                        limit '''+ offset + ','+limit+''') as pl
                        left join
                        (select p.id,p.posting_id, max(p.id) as mpid,p.comment,p.created_at,p.user_id
                        from postcomment p
                        group by posting_id
                        order by posting_id desc) as pcl
                        on pl.id = pcl.posting_id && pcl.id=pcl.mpid
                        left join 
                        (select u.id,u.nickname
                        from user u)as cl
                        on pcl.user_id = cl.id
                        where pl.user_id = %s ;'''
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

            # select 문은 아래 내용이 필요하다.
            posting_list = cursor.fetchall()
            print(posting_list)
            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            l = 0
            for record in posting_list:
                posting_list[i]['created_at'] = str(record['created_at'])
                posting_list[l]['comment_created_at'] = str(record['comment_created_at'])
                i = i + 1
                l = l + 1 
            
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