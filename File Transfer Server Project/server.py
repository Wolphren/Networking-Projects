import socket
import threading
import json
import os
import base64
from datetime import datetime

class FileTransferServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.files_directory = 'server_files'
        
        # Create server files directory if it doesn't exist
        if not os.path.exists(self.files_directory):
            os.makedirs(self.files_directory)
            
        # Create some sample files for testing
        self.create_sample_files()
    
    def create_sample_files(self):
        """Create sample files for testing"""
        sample_files = {
            'hello.txt': 'Hello, World! This is a sample text file.',
            'data.json': '{"name": "John", "age": 30, "city": "New York"}',
            'info.md': '# File Transfer Server\n\nThis is a markdown file for testing.'
        }
        
        for filename, content in sample_files.items():
            filepath = os.path.join(self.files_directory, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)
    
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"File Transfer Server started on {self.host}:{self.port}")
            print(f"Files directory: {os.path.abspath(self.files_directory)}")
            print("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New connection from {client_address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            while True:
                # Receive request from client
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                    
                    # Send response back to client
                    response_json = json.dumps(response)
                    client_socket.send(response_json.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = {
                        'status': 'error',
                        'message': 'Invalid JSON format'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection closed for {client_address}")
    
    def process_request(self, request):
        """Process different types of requests"""
        request_type = request.get('type', '')
        
        if request_type == 'list_files':
            return self.list_files()
        elif request_type == 'download_file':
            return self.download_file(request.get('filename', ''))
        elif request_type == 'upload_file':
            return self.upload_file(request.get('filename', ''), request.get('content', ''))
        elif request_type == 'server_info':
            return self.get_server_info()
        else:
            return {
                'status': 'error',
                'message': f'Unknown request type: {request_type}'
            }
    
    def list_files(self):
        """List all available files"""
        try:
            files = []
            for filename in os.listdir(self.files_directory):
                filepath = os.path.join(self.files_directory, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'modified': file_modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return {
                'status': 'success',
                'files': files,
                'count': len(files)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error listing files: {str(e)}'
            }
    
    def download_file(self, filename):
        """Download a file from the server"""
        if not filename:
            return {
                'status': 'error',
                'message': 'Filename not provided'
            }
        
        filepath = os.path.join(self.files_directory, filename)
        
        if not os.path.exists(filepath):
            return {
                'status': 'error',
                'message': f'File not found: {filename}'
            }
        
        try:
            with open(filepath, 'rb') as f:
                file_content = f.read()
                # Encode binary content as base64 for JSON transmission
                encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            return {
                'status': 'success',
                'filename': filename,
                'content': encoded_content,
                'size': len(file_content)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error reading file: {str(e)}'
            }
    
    def upload_file(self, filename, encoded_content):
        """Upload a file to the server"""
        if not filename or not encoded_content:
            return {
                'status': 'error',
                'message': 'Filename and content are required'
            }
        
        try:
            # Decode base64 content
            file_content = base64.b64decode(encoded_content)
            filepath = os.path.join(self.files_directory, filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            return {
                'status': 'success',
                'message': f'File uploaded successfully: {filename}',
                'size': len(file_content)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error uploading file: {str(e)}'
            }
    
    def get_server_info(self):
        """Get server information"""
        return {
            'status': 'success',
            'server_info': {
                'host': self.host,
                'port': self.port,
                'files_directory': self.files_directory,
                'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'supported_operations': ['list_files', 'download_file', 'upload_file', 'server_info']
            }
        }
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped")

def main():
    server = FileTransferServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == '__main__':
    main()