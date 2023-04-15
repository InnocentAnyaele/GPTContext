from flask import Flask, request, make_response, jsonify
from llama_index import GPTSimpleVectorIndex, download_loader
from werkzeug.utils import secure_filename
import os
import uuid
import threading
import time
import shutil
from flask_cors import CORS
from functools import wraps

import pandas as pd
from gpt_index.indices.struct_store import GPTPandasIndex


#from keys
# import keys
# os.environ['OPENAI_API_KEY'] = keys.OPENAI_API_KEY
# BEARER_TOKEN = keys.BEARER_TOKEN
    
# from environment
BEARER_TOKEN = os.environ['BEARER_TOKEN']
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')


root = os.path.dirname(__file__)

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True

# function to delete documents from the context directory 
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


# this function is to valid the request through a token sent from the client side
def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers['Authorization']
        print('front-token', token)
        
        if not token:
            response = make_response('Authorization is required')
            response.status_code = 500
            return response   

        if BEARER_TOKEN != token:
            response = make_response('Invalid Token')
            response.status_code = 500
            return response   
        
        return func(*args, **kwargs)

    return decorated_function
        

# function to handle file uploads, and create the initial indexes from documents uploaded
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
            # saving the documents uploaded to a unique folder path.   
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
            
            #this starts a thread to delete those documents in 5 minutes. 
            t = threading.Thread(target=delete_context, args=(dirName,))
            t.start()
            
            
            #check the extension of the file uploaded. Only interested in the last file in the array because of the file upload limit (1)
            def checkAndReturnExtension():
                path = os.path.join(dirName, secure_filename(fileNamesArray[-1]))
                curr_fileName = fileNamesArray[-1]
                curr_fileExtension = curr_fileName.split('.')
                curr_fileExtensionOnly = curr_fileExtension[-1]
                print ('curr_fileName', curr_fileName)
                print ('curr_fileExtensionSplit', curr_fileExtension)
                print ('curr_fileExtensionOnly', curr_fileExtension[-1])
                return curr_fileExtensionOnly
            
            # this takes in the documents / file and creates indices using the GPTSimpleVectorIndex
            def createIndexAndReturnResponse(documents):
                index = GPTSimpleVectorIndex(documents)
                print ('this is the index', index)
                indexPath = os.path.join(dirName,'index.json')
                index.save_to_disk(indexPath)
                response = make_response(indexKey)
                response.status_code = 200
                print ('this is the response', response)
                return response
                 
            # handles csv files uploaded using the PandasCSVReader
            def csvHandler():
                path = os.path.join(dirName, secure_filename(fileNamesArray[-1]))
                print ('csv path', path)
                PandasCSVReader = download_loader("PandasCSVReader")
                loader = PandasCSVReader()
                documents = loader.load_data(path)
                return createIndexAndReturnResponse(documents)
                    
            # handles docx, pdfs etc. uploaded using the SimpleDirectoryReader
            def directoryReader():
                SimpleDirectoryReader = download_loader('SimpleDirectoryReader')
                loader = SimpleDirectoryReader(dirName, recursive=True)  
                documents = loader.load_data()
                return createIndexAndReturnResponse(documents)

            try:
                # directs files based on their file extensions to their appropriate handlers
                if checkAndReturnExtension() == 'csv':
                    print ('Handling CSV')
                    return csvHandler()
                elif checkAndReturnExtension() == 'xlsx':
                    response = make_response(indexKey)
                    response.status_code = 200
                    return response
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
        
        
        
    
# this api handles queries from the user about their document 
@app.route('/api/getResponse', methods=['POST'])
@token_required
def get_response():
    if request.method == 'POST':
        
        # getting request parameters
        indexKey = request.form['indexKey']
        prompt = request.form['prompt']
        fileType = request.form['fileType']
        fileName = request.form['fileName']
        print (indexKey)        
        print (prompt)
        print (fileType)
        print (fileName)
                    
        try:      
            print ('this is the fileType gotten from the frontend', fileType)
            
            # checks if index exists in parameter
            if len(indexKey) < 1:
                response = make_response('No index has been built yet for this prompt')
                response.status_code = 404
                return response
            
            # handles xlsx request. For xlsx, it rebuilds the query from the xlsx file stored everytime the user queries
            if (fileType == 'xlsx'):
                xlsxPath = os.path.join('uploads', indexKey, secure_filename(fileName))
                df = pd.read_excel(xlsxPath)
                index = GPTPandasIndex(df = df)
                indexResponse = index.query(prompt)
                print (indexResponse)
                response = make_response(str(indexResponse))
                response.status_code = 200
                return response
            
            # builds the path to the stored indexes using the unique key passed from client
            indexPath = os.path.join('uploads',indexKey,'index.json')
            
            print (indexPath)
            
            # if that saved index exists, it loads it from disk and queries it             
            if os.path.exists(indexPath):
                index = GPTSimpleVectorIndex.load_from_disk(indexPath)
                # index = GPTPandasIndex.load_from_disk(indexPath)
                res = index.query(prompt)
                response = make_response(str(res))
                response.status_code = 200
                return response
            else:
                # if index does not exist, it means the files has been deleted (session expired)
                response = make_response('Index has expired for this prompt')
                response.status_code = 404
                return response
        # catches unseen errors    
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
    
    
    