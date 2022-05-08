from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename
import boto3

from config import Config

from datetime import date, datetime


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PostingResource(Resource) :
    @jwt_required()
    #포스팅 업로드
    def post(self) :

        user_id = get_jwt_identity()

        # image, content
        content = request.form.get('content')

        # form-data 의 file 형식에서 데이터 가져오는 경우
        if 'image' not in request.files:
            
            return {'error':'파일을 업로드 하세요'}, 400
         
        file = request.files['image']

        if file.filename == '':
            
            return {'error':'파일명을 정확히 입력하세요'}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 파일명은, 유니크하게 해줘야, S3에 업어쳐지지 않고 올라갈수있다.
            current_time = datetime.now()            
            current_time = current_time.isoformat().replace(':', '_')
            filename = 'photo_' + current_time + '.jpg'

            # 파일을 파일시스템에 저장하는 코드 : S3에 올릴거니까, 코멘트처리
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # S3에 올리는 코드 작성
            s3 = boto3.client('s3', 
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS )
            try :
                s3.upload_fileobj(
                                file, 
                                Config.S3_BUCKET,
                                filename,
                                ExtraArgs = { 'ACL' : 'public-read',
                                            'ContentType' : file.content_type}
                                )
            except Exception as e :
                return {'error' : str(e)}   

        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into posting
                        (user_id, img_url, content)
                        values
                        (%s, %s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (user_id, Config.S3_LOCATION + filename , content)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            
            return {'error' : '포스팅 에러입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')     

        return {'result' : '포스팅이 업로드 되었습니다.'}

   
class PostingeditResource(Resource) :
    @jwt_required()
    #포스팅 수정
    def post(self, posting_id) :

        user_id = get_jwt_identity()

        # image, content
        content = request.form.get('content')


        # form-data 의 file 형식에서 데이터 가져오는 경우
        if 'image' not in request.files:
            
            return {'error':'파일을 업로드 하세요'}, 400
         
        file = request.files['image']

        if file.filename == '':

            # 사진이 수정되지 않았으니, S3에 데이터를 올리지않고
            # DB에 content 내용만 수정해서 저장한다.

            try :
                # 1. DB 에 연결
                connection = get_connection()
            
                # 2. 쿼리문 만들고
                query = '''update posting
                            set content = %s
                            where id = %s;'''
                # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
                # 써준다.
                record = (content, posting_id)
                
                # 3. 커넥션으로부터 커서를 가져온다.
                cursor = connection.cursor()

                # 4. 쿼리문을 커서에 넣어서 실행한다.
                cursor.execute(query, record)

                # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
                connection.commit()


            except Error as e:
                print('Error ', e)
                # 6. username이나 email이 이미 DB에 있으면,
                
                return {'error' : '포스팅 에러입니다.'} , HTTPStatus.BAD_REQUEST
            finally :
                if connection.is_connected():
                    cursor.close()
                    connection.close()
                    print('MySQL connection is closed')     
           
            return {'result':'수정 되었습니다.'}, 200

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 파일명은, 유니크하게 해줘야, S3에 업어쳐지지 않고 올라갈수있다.
            current_time = datetime.now()            
            current_time = current_time.isoformat().replace(':', '_')
            filename = 'photo_' + current_time + '.jpg'

            # 파일을 파일시스템에 저장하는 코드 : S3에 올릴거니까, 코멘트처리
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # S3에 올리는 코드 작성
            s3 = boto3.client('s3', 
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS )
            try :
                s3.upload_fileobj(
                                file, 
                                Config.S3_BUCKET,
                                filename,
                                ExtraArgs = { 'ACL' : 'public-read',
                                            'ContentType' : file.content_type}
                                )
            except Exception as e :
                return {'error' : str(e)}   


        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''update posting
                        set img_url = %s, content = %s
                        where id = %s ;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (Config.S3_LOCATION + filename , content, posting_id)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()


        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            
            return {'error' : '포스팅 에러입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')     

        return {'result':'포스팅이 수정 되었습니다.'}
class delPostingResource(Resource) :
    @jwt_required()
    #포스팅 삭제
    def delete(self, posting_id) :
        
        user_id = get_jwt_identity()

        # 삭제하기전에 이유저가 작성한 포스팅이 맞는지 먼저 확인
        try :
            connection = get_connection()

            query = '''select * 
                        from posting
                        where id = %s; '''
            
            param = (posting_id, )
            
            cursor = connection.cursor(dictionary = True)

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
                
                # 2. 쿼리문 만들고
                query = '''delete from posting
                            where id = %s;'''
                # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
                # 써준다.
                record = (posting_id, )
                
                # 3. 커넥션으로부터 커서를 가져온다.
                cursor = connection.cursor()

                # 4. 쿼리문을 커서에 넣어서 실행한다.
                cursor.execute(query, record)

                # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
                connection.commit()

            else :
                return {'error' : '작성한 포스팅이 아닙니다.'}, 400

            
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

      
        return {'result' : '포스팅 글이 삭제 되었습니다.'}

