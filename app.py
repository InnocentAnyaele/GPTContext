from flask import Flask, request, make_response, jsonify
from llama_index import GPTSimpleVectorIndex, download_loader
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
import shutil
import keys
from flask_cors import CORS
from functools import wraps

import pandas as pd
# from gpt_index.indices.struct_store import GPTPandasIndex

# os.environ['OPENAI_API_KEY'] = 'key-here'
os.environ['OPENAI_API_KEY'] = keys.OPENAI_API_KEY

root = os.path.dirname(__file__)

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True


def delete_context(dirName):
    time.sleep(300)
    if os.path.exists(dirName):
        shutil.rmtree(dirName)
    else:
        print('Path does not exist')
        
    return 'completed'

@app.route("/")
def hello_world():
    # print (os.environ['OPENAI_API_KEY'])
    return "<p>The Flask API route for GPTContext</p>"


def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers['Authorization']
        print('front-token', token)
        print('back-token', keys.BEARER_TOKEN)
        
        if not token:
            response = make_response('Authorization is required')
            response.status_code = 500
            return response   

        if keys.BEARER_TOKEN != token:
            response = make_response('Invalid Token')
            response.status_code = 500
            return response   
        
        return func(*args, **kwargs)

    return decorated_function
        


@app.route('/api/addContext', methods=['POST'])
@token_required
def add_context():
    if request.method == 'POST':
        # sending from postman
        # try:
        #     files = request.files.getlist('file')
        #     indexKey = str(uuid.uuid1())
        #     dirName = os.path.join('./uploads/', indexKey)
        #     os.makedirs(dirName)
            
        #     for file in files:
        #         filename = file.filename
        #         new_filename = os.path.join(dirName,secure_filename(filename))
        #         file.save(new_filename)   
            
        try:            
            indexKey = str(uuid.uuid1())
            dirName = os.path.join('./uploads/', indexKey)
            os.makedirs(dirName)
            fileNamesArray = []
            print ('this is the file length', request.form['fileLength'])
            for i in range(int(request.form['fileLength'])):
                currFileName = 'file'+str(i)
                print ('currFileName', currFileName)
                currFile = request.files[currFileName]
                filename = currFile.filename
                secureFileName = secure_filename(filename)
                new_filename = os.path.join(dirName,secureFileName)
                fileNamesArray.append(filename)
                currFile.save(new_filename)  
            
            t = threading.Thread(target=delete_context, args=(dirName,))
            t.start()
            
            
            def checkAndReturnExtension():
                path = os.path.join(dirName, secure_filename(fileNamesArray[-1]))
                curr_fileName = fileNamesArray[-1]
                curr_fileExtension = curr_fileName.split('.')
                curr_fileExtensionOnly = curr_fileExtension[-1]
                print ('curr_fileName', curr_fileName)
                print ('curr_fileExtensionSplit', curr_fileExtension)
                print ('curr_fileExtensionOnly', curr_fileExtension[-1])
                return curr_fileExtensionOnly
            
            def createIndexAndReturnResponse(documents):
                index = GPTSimpleVectorIndex(documents)
                indexPath = os.path.join(dirName,'index.json')
                index.save_to_disk(indexPath)
                response = make_response(indexKey)
                response.status_code = 200
                return response
                 
            
            def csvHandler():
                path = os.path.join(dirName, secure_filename(fileNamesArray[-1]))
                print ('csv path', path)
                PandasCSVReader = download_loader("PandasCSVReader")
                loader = PandasCSVReader()
                documents = loader.load_data(path)
                return createIndexAndReturnResponse(documents)
        
#             def xlsxHandler():
#                 path = os.path.join(dirName, secure_filename(fileNamesArray[-1]))
#                 df = pd.read_excel(path)
#                 print (df.head())
#                 index = GPTPandasIndex(df = df).save_to_disk(os.path.join(dirName, 'index.json'))
# #                 indexResponse = index.query(
# #     "What colours are in the document and what numbers are in the document?",
# # )
# #                 print ('test response', indexResponse)
#                 response = make_response(indexKey)
#                 response.status_code = 200
#                 return response
                

            def directoryReader():
                SimpleDirectoryReader = download_loader('SimpleDirectoryReader')
                loader = SimpleDirectoryReader(dirName, recursive=True)  
                documents = loader.load_data()
                return createIndexAndReturnResponse(documents)

            
            try:
                # return directoryReader()
                # return csvHandler()
                # checkAndReturnExtension()
                
                
                if checkAndReturnExtension() == 'csv':
                    print ('Handling CSV')
                    return csvHandler()
                # elif checkAndReturnExtension() == 'xlsx':
                #     print ('Handling XLSX')
                #     return xlsxHandler()
                else:
                    print ('Handling Other')
                    return directoryReader()
            
            except Exception as e:
                print (e)
                response = make_response('Could not build index')
                response.status_code = 500
                return response
            
        except Exception as e:
            print (e)
            response = make_response('Could not upload files')
            response.status_code = 500
            return response           
        
        
        
    
    
    
@app.route('/api/getResponse', methods=['POST'])
@token_required
def get_response():
    if request.method == 'POST':

        indexKey = request.form['indexKey']
        prompt = request.form['prompt']
        
        print (indexKey)        
        print (prompt)
                    
        try:
            indexKey = request.form['indexKey']
            prompt = request.form['prompt']
            fileType = request.form['fileType']
            
            print ('this is the fileType gotten from the frontend', fileType)
            
            if len(indexKey) < 1:
                response = make_response('No index has been built yet for this prompt')
                response.status_code = 404
                return response
            
            indexPath = os.path.join('uploads',indexKey,'index.json')
            
            print (indexPath)
            
            if os.path.exists(indexPath):
                index = GPTSimpleVectorIndex.load_from_disk(indexPath)
                # index = GPTPandasIndex.load_from_disk(indexPath)
                res = index.query(prompt)
                response = make_response(str(res))
                response.status_code = 200
                return response
            else:
                response = make_response('Index has expired for this prompt')
                response.status_code = 404
                return response    
        except Exception as e:
            print (e)
            response = make_response('Something went wrong')
            response.status_code = 500
            return response
            
            
        

@app.route('/api/deleteAllContext', methods=['DELETE'])
@token_required
def deleteAllContext():
    if request.method == 'DELETE':
        try:
            path = './uploads'
            if os.path.exists(path):
                shutil.rmtree(path)
                response = make_response('Folder removed!')
                response.status_code = 200
                return response
        except Exception as e:
            print (e)
            response = make_response('Could not delete')
            response.status_code = 500
            return response
        
if __name__ == '__main__':
    app.run()
    
    
    