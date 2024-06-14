from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.urls import url_quote
import asyncio
from aiohttp import ClientSession
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.urls import url_quote
import asyncio
from aiohttp import ClientSession
import re
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'close',
    'Referer': 'https://linkvertise.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x66) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

key_regex = r'let content = \("([^"]+)"\);'

async def fetch(session, url, referer):
    headers["Referer"] = referer
    async with session.get(url, headers=headers) as response:
        content = await response.text()
        if response.status != 200:
            return None, response.status, content
        return content, response.status, None

async def process_link(hwid):
    endpoints = [
        {
            "url": f"https://serahub.site/getkey?token{hwid}",
            "referer": ""
        },
        {
            "url": "https://serahub.site/getkey",
            "referer": "https://linkvertise.com
        }
    ]
    
    async with ClientSession() as session:
        for i, endpoint in enumerate(endpoints):
            url = endpoint["url"]
            referer = endpoint["referer"]
            content, status, error_content = await fetch(session, url, referer)
            if error_content:
                return {
                    "status": "error",
                    "message": f"Failed to bypass at step {i} | Status code: {status}",
                    "content": error_content
                }

            if i == len(endpoints) - 1:  # End of the bypass
                match = re.search(key_regex, content)
                if match:
                    return {
                        "status": "success",
                        "key": match.group(1)
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Bypassed not successfully! No key found.",
                        "content": content
                    }

@app.route('/api/fluxus', methods=['GET'])
def handle_request():
    start_time = time.time()  # Start time
    link = request.args.get('link')
    if not link:
        return jsonify({"error": "No link provided"}), 400

    hwid = link.split("HWID=")[-1]
    result = asyncio.run(process_link(hwid))
    end_time = time.time()  # End time
    execution_time = end_time - start_time  # Calculate execution time
    result['execution_time'] = execution_time  # Add execution time to the result
    return jsonify(result)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1117)
