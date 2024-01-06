from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import subprocess

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://ezra:fbVFtTwornawziKT@cluster0.owft8n4.mongodb.net/?retryWrites=true&w=majority")
db = client['spotify_data']
artists_collection = db['artists']

@app.route('/artists', methods=['GET'])
def get_artists():
    try:
        artists_data = list(artists_collection.find({
            'playlist_count': {'$gte': 2}
        }).sort([
            ('playlist_count', -1),
            ('artist_followers', 1),
            ('popularity', 1)
        ]))
        print(artists_data[0])
        data = []
        for doc in artists_data:
            doc['_id'] = str(doc['_id'])
            data.append(doc)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai', methods=['GET'])
def run_ai():
    artist_name = request.args.get('name')

    try:
        result = subprocess.check_output(['python', 'testing.py', artist_name])
        print(result)

        # Update MongoDB document with the result
        artist = artists_collection.find_one({'name': artist_name})

        if artist:
            # Check if 'description' field exists, create it if not
            if 'description' in artist:
                artists_collection.update_one({'name': artist_name}, {'$set': {'description': result.decode()}})
            else:
                artists_collection.update_one({'name': artist_name}, {'$set': {'description': result.decode()}})
        else:
            return jsonify({'error': f'Artist {artist_name} not found in the database'}), 404

        return jsonify({'result': result.decode()})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error running AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=3001)
