import json
import io
import base64
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
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))

        print(post_data)

        name = post_data['name']
        type = post_data['type']
        details = post_data['details']
        rarity = post_data['rarity']
        description = post_data['description']
        art = self.map_art(post_data['art'])

        creator = Creator("assets/FontA_Cinzel-Bold.otf","assets/FontB_CrimsonPro-VariableFont_wght.ttf","assets/Leyfarer_card_item_Template_v1.png",art)
        png = creator.generate_card(name, type, details, rarity, description) 
        #png.save("renders/test.png")
        output = io.BytesIO()
        png.save(output, format='PNG')
        png_data = output.getvalue()

        base64_png = base64.b64encode(png_data).decode('utf-8')

        # Prepare response data with query parameters and body
        response_data = {
            "query_params": {key: value[0] for key, value in query_params.items()},
            "body": png_data
        }

        # Respond with the query parameters and body as JSON
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == "__main__":
    server_address = ('0.0.0.0', 8000)  # Bind to all addresses on port 8000
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Starting server on port 8000...")
    httpd.serve_forever()
