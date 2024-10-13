import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from cardcreatorLib import Creator

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def map_art(self, name):
        # try:
        #     # Attempt to retrieve the value
        #     value = my_dict[name]
        #     print(f"Value found: {value}")
        # except KeyError:
        #     # Handle the exception if the key is not found
        #     print(f"KeyError: '{key_to_access}' not found in the dictionary.")
        return "art/Giants_ring_of_little_folk_Cfallon.png"
    
    def do_POST(self):
        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Read the content length and body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        print(query_params)

        name = query_params['name']
        type = query_params['type']
        details = query_params['details']
        rarity = query_params['rarity']
        description = query_params['description']
        art = self.map_art(query_params['art'])

        creator = Creator("assets/FontA_Cinzel-Bold.otf","assets/FontB_CrimsonPro-VariableFont_wght.ttf","assets/Leyfarer_card_item_Template_v1.png",art)
        png = creator.generate_card(name, type, details, rarity, description) 
        png.save("renders/test.png")

        # Prepare response data with query parameters and body
        response_data = {
            "query_params": {key: value[0] for key, value in query_params.items()},
            "body": post_data
        }

        # Respond with the query parameters and body as JSON
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == "__main__":
    server_address = ('0.0.0.0', 8000)  # Bind to all addresses on port 8000
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Starting server on port 8000...")
    httpd.serve_forever()
