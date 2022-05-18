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
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query,param)
            
            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : '댓글 업로드 에러입니다.'} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        
        return{'result' : '댓글이 업데이트 되었습니다.'},200



class editcommentResource(Resource) :
    @jwt_required()
    #댓글 수정하기 
    def post(self, posting_id,comment_id) :

        user_id = get_jwt_identity()
        comment = request.form.get('comment')

        # 삭제하기전에 이유저가 작성한 포스팅이 맞는지 먼저 확인
        try :
            connection = get_connection()

            #Select 문을 이용해서 현재 user_id와 posting_id가 같은지 확인한다.
            query = '''select * 
                        from postcomment
                        where user_id=%s AND posting_id= %s AND id= %s; '''
                                    
            param = (user_id,posting_id,comment_id)
            #  커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            #  쿼리문을 커서에 넣어서 실행한다.
            # 이때 커밋하거나 커넥션을 닫아두지 않는다.
            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = str(record['created_at'])
                i = i + 1

            # 해당 포스팅의 정보를 가져온다.
            posting_info = record_list[0]
            if user_id == posting_info['user_id'] :  
        
                # 2. 업데이트 쿼리문을 이용하여 수정시킨다.
                query = '''update postcomment
                            set comment = %s
                            where user_id=%s AND posting_id= %s AND id= %s;'''
                # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써준다.
                record = (comment,user_id,posting_id,comment_id)
                
                # 3. 커넥션으로부터 커서를 가져온다.
                cursor = connection.cursor()

                # 4. 쿼리문을 커서에 넣어서 실행한다.
                cursor.execute(query, record)

                # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
                connection.commit()

            else :
                return {'result':'존재하지 않는 댓글입니다.'}, 202

        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
    
            return {'error' : '댓글 수정 에러입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')     
    
        return {'result':'댓글이 수정 되었습니다.'}, 200

        
class delcommentResource(Resource) :
    @jwt_required()
    # 댓글 삭제
    def delete(self, posting_id,comment_id) :
        
        user_id = get_jwt_identity()

        # 삭제하기전에 이유저가 작성한 포스팅이 맞는지 먼저 확인
        try :
            connection = get_connection()

            query = '''select * 
                        from postcomment
                        where user_id=%s AND posting_id= %s AND id= %s; '''
            
            param = (user_id,posting_id,comment_id)
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
    

            # 해당 포스팅의 정보를 가져온다.
            posting_info = record_list[0]

            if user_id == posting_info['user_id'] :              
                
                # 2. 쿼리문 만들고
                query = '''delete from postcomment
                            where id = %s;'''
                # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
                # 써준다.
                record = (comment_id, )
                
                # 3. 커넥션으로부터 커서를 가져온다.
                cursor = connection.cursor()

                # 4. 쿼리문을 커서에 넣어서 실행한다.
                cursor.execute(query, record)

                # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
                connection.commit()

            else :
                return {'error' : '존재하지 않는 댓글입니다.'}, 202

            
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

      
        return {'result' : '댓글이 삭제 되었습니다.'},200
         
class getcommentResource(Resource) :
    # 포스팅의 모든 댓글 리스트 보기  
    def get(self,posting_id) :
     
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select c.posting_id,c.user_id,u.img_url,u.nickname,c.comment,c.created_at
                        from postcomment c 
                        join user u 
                        on u.id = c.user_id
                        where posting_id = %s
                        order by c.created_at desc
                        limit '''+ offset + ','+limit+''';'''
            
            param = (posting_id, )

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
        return{'comment_list' : record_list}