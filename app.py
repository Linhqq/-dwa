from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from aiohttp import ClientSession
import re
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configurations
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'close',
    'Referer': 'https://linkvertise.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x66) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
KEY_REGEX = re.compile(r'let content = \("([^"]+)"\);')

# Asynchronous fetch function
async def fetch(session, url, referer):
    headers = {**HEADERS, "Referer": referer}
    async with session.get(url, headers=headers) as response:
        content = await response.text()
        return content, response.status

# Processing link function with parallel requests
async def process_link(hwid):
    endpoints = [
        {
            "url": f"https://flux.li/android/external/start.php?HWID={hwid}",
            "referer": ""
        },
        {
            "url": "https://flux.li/android/external/check1.php",
            "referer": "https://linkvertise.com"
        },
        {
            "url": "https://flux.li/android/external/main.php",
            "referer": "https://linkvertise.com"
        }
    ]

    async with ClientSession() as session:
        tasks = [fetch(session, ep["url"], ep["referer"]) for ep in endpoints]
        responses = await asyncio.gather(*tasks)

    for i, (content, status) in enumerate(responses):
        if status != 200:
            return {
                "status": "error",
                "message": f"Failed to bypass at step {i} | Status code: {status}",
                "content": content
            }
        if i == len(endpoints) - 1:  # End of the bypass
            match = KEY_REGEX.search(content)
            if match:
                return {
                    "status": "success",
                    "key": match.group(1)
                }
            else:
                return {
                    "status": "error",
                    "message": "Bypass not successful! No key found.",
                    "content": content
                }

# Route to handle the fluxus API request
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

# Default route
@app.route('/')
def home():
    return '<h1>Hi! You</h1>'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1117)
