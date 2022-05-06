from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename



class commentResource(Resource) :
    @jwt_required()
 # 댓글 달기
    def post(self,posting_id) :
     
        user_id = get_jwt_identity()
        comment = request.form.get('comment')
        try :
            connection = get_connection()
            # 쿼리문 
            query = '''insert into postcomment
                        (user_id,posting_id,comment)
                        values
                        (%s, %s, %s);'''
            
            param = (user_id,posting_id,comment)
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query,param)

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