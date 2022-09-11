import os
from flask import Flask, render_template, request, json, jsonify, Response, redirect, flash
import json
import pandas as pd
from bigse.celery.tasks import update_index
from bigse import model
from bigse.database import manager
from bigse.search import vector_search, id2details

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your secret key'

@app.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            # messages.append({'title': title, 'content': content})
            # return redirect(url_for('index'))
            dbm = manager.DatabaseInteractionManager()
            embedding = model.encode(title+' '+content, show_progress_bar=True) 
            dbm.create_doc_entry(title, content, "http://file" , json.dumps(embedding.tolist()))
            dbm.close_connection()
            update_index.delay()
            flash(f'Added {title} succesfully!')

    return render_template('create.html')

@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query')
    num_results = int(request.args.get('num'))
    D, I = vector_search([query], num_results=num_results)
    list = id2details(I)
    return jsonify([[list[idx][2] , float(D[0][idx])] for idx in range(len(I[0]))])

@app.route('/refresh', methods = ['GET'])
def refresh():
    update_index.delay()
    return jsonify(['done'])

@app.route('/add')
def add( ):
    dbm = manager.DatabaseInteractionManager()

    path = os.getcwd()
    path = os.path.join(path , 'files')
    print(path)

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            full_path = os.path.join(r, file)
            if dbm.get_doc_entry_from_path(full_path) is not None:
                print(f'skipping {full_path}')
            else:
                with open(full_path, 'r') as file_ptr:
                    embedding = model.encode(file_ptr.read(), show_progress_bar=True)
                    dbm.create_doc_entry(file, r, full_path , json.dumps(embedding.tolist()))
                files.append(os.path.join(r, file))

    dbm.close_connection()
    return jsonify(files)

@app.route('/new')
def new( ):
    dbm = manager.DatabaseInteractionManager()
    file = request.args.get('file')
    embedding = model.encode(file, show_progress_bar=True) 
    dbm.create_doc_entry(file, file, "http://file" , json.dumps(embedding.tolist()))
    dbm.close_connection()
    update_index.delay()
    return jsonify(['done'])


@app.route('/print')
def show( ):
    dbm = manager.DatabaseInteractionManager()
    ids, embs = dbm.get_ids_embeddings()
    dbm.close_connection()
    return jsonify(ids)

@app.route('/clean')
def clean( ):
    dbm = manager.DatabaseInteractionManager()
    dbm.empty()
    dbm.close_connection()
    return Response(status=200)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)