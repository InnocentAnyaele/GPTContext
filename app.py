from flask import Flask, render_template, request, redirect
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, download_loader
from werkzeug.utils import secure_filename
import pickle
import os
import io
import uuid
import threading
import time
import shutil
# from dotenv import load_dotenv

app = Flask(__name__)
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
    # return "<p>Hi</p>"
    return render_template('home/index.html')
        


@app.route('/addContext', methods=['POST'])
def add_context():
    if request.method == 'POST':
        files = request.files.getlist('file')
        dirName = os.path.join('./uploads/', str(uuid.uuid1()))
        os.makedirs(dirName)
        
        for file in files:
            filename = file.filename
            new_filename = os.path.join(dirName,secure_filename(filename))
            file.save(new_filename)   
         
        t = threading.Thread(target=delete_context, args=(dirName,))
        t.start()
        
        
        SimpleDirectoryReader = download_loader('SimpleDirectoryReader')
        loader = SimpleDirectoryReader(dirName, recursive=True)  
        documents = loader.load_data()
        index = GPTSimpleVectorIndex(documents)
        indexPath = os.path.join(dirName,'index.json')
        index.save_to_disk(indexPath)
        # response = index.query("What is his hobbies?")
        # return str(response)
        print (index)
        return ('index has been built')
    
    
    
@app.route('/getResponse', methods=['POST'])
def get_response():
    if request.method == 'POST':
        indexKey = request.form['indexKey']
        prompt = request.form['prompt']
        
        if len(indexKey) < 1:
            return 'No index has been built yet for this prompt'
        
        indexPath = os.path.join('uploads',indexKey,'index.json')
        
        print (indexPath)
        
        if os.path.exists(indexPath):
            index = GPTSimpleVectorIndex.load_from_disk(indexPath)
            response = index.query(prompt)
            return str(response)
        else:
            return 'Index has expired for this prompt'    
        

@app.route('/deleteAllContext', methods=['DELETE'])
def deleteAllContext():
    if request.method == 'DELETE':
        
        
# @app.route('/deleteContext', methods=[])
# def delete_context():
#     pass

if __name__ == '__main__':
    app.run()
    
    
    