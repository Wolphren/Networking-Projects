import socket
import json
import base64
import os

class FileTransferClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
    
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.client_socket:
            self.client_socket.close()
            self.connected = False
            print("Disconnected from server")
    
    def send_request(self, request):
        """Send a request to the server and get response"""
        if not self.connected:
            print("Not connected to server")
            return None
        
        try:
            # Send request
            request_json = json.dumps(request)
            self.client_socket.send(request_json.encode('utf-8'))
            
            # Receive response
            response_data = self.client_socket.recv(1024 * 1024)  # 1MB buffer for large files
            response = json.loads(response_data.decode('utf-8'))
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def list_files(self):
        """List files on the server"""
        request = {'type': 'list_files'}
        response = self.send_request(request)
        
        if response and response.get('status') == 'success':
            files = response.get('files', [])
            print(f"\nServer has {response.get('count', 0)} files:")
            print("-" * 60)
            print(f"{'Name':<20} {'Size':<10} {'Modified':<20}")
            print("-" * 60)
            for file_info in files:
                print(f"{file_info['name']:<20} {file_info['size']:<10} {file_info['modified']:<20}")
            print("-" * 60)
        else:
            error_msg = response.get('message', 'Unknown error') if response else 'No response'
            print(f"Error listing files: {error_msg}")
    
    def download_file(self, filename, local_path=None):
        """Download a file from the server"""
        if not local_path:
            local_path = filename
        
        request = {'type': 'download_file', 'filename': filename}
        response = self.send_request(request)
        
        if response and response.get('status') == 'success':
            try:
                # Decode the base64 content
                encoded_content = response.get('content', '')
                file_content = base64.b64decode(encoded_content)
                
                # Save to local file
                with open(local_path, 'wb') as f:
                    f.write(file_content)
                
                file_size = response.get('size', len(file_content))
                print(f"File downloaded successfully: {filename} ({file_size} bytes) -> {local_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
        else:
            error_msg = response.get('message', 'Unknown error') if response else 'No response'
            print(f"Error downloading file: {error_msg}")
    
    def upload_file(self, local_path, remote_filename=None):
        """Upload a file to the server"""
        if not os.path.exists(local_path):
            print(f"Local file not found: {local_path}")
            return
        
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        try:
            # Read and encode file content
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            request = {
                'type': 'upload_file',
                'filename': remote_filename,
                'content': encoded_content
            }
            
            response = self.send_request(request)
            
            if response and response.get('status') == 'success':
                file_size = response.get('size', len(file_content))
                print(f"File uploaded successfully: {local_path} -> {remote_filename} ({file_size} bytes)")
            else:
                error_msg = response.get('message', 'Unknown error') if response else 'No response'
                print(f"Error uploading file: {error_msg}")
                
        except Exception as e:
            print(f"Error reading local file: {e}")
    
    def get_server_info(self):
        """Get server information"""
        request = {'type': 'server_info'}
        response = self.send_request(request)
        
        if response and response.get('status') == 'success':
            info = response.get('server_info', {})
            print("\nServer Information:")
            print("-" * 40)
            for key, value in info.items():
                if key == 'supported_operations':
                    print(f"{key}: {', '.join(value)}")
                else:
                    print(f"{key}: {value}")
            print("-" * 40)
        else:
            error_msg = response.get('message', 'Unknown error') if response else 'No response'
            print(f"Error getting server info: {error_msg}")
    
    def run_interactive(self):
        """Run interactive command-line interface"""
        print("File Transfer Client")
        print("Commands: list, download <filename>, upload <filepath>, info, help, quit")
        print("-" * 60)
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'list':
                    self.list_files()
                elif cmd == 'info':
                    self.get_server_info()
                elif cmd == 'download':
                    if len(command) < 2:
                        print("Usage: download <filename> [local_path]")
                    else:
                        local_path = command[2] if len(command) > 2 else None
                        self.download_file(command[1], local_path)
                elif cmd == 'upload':
                    if len(command) < 2:
                        print("Usage: upload <filepath> [remote_filename]")
                    else:
                        remote_name = command[2] if len(command) > 2 else None
                        self.upload_file(command[1], remote_name)
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("\nAvailable Commands:")
        print("  list                          - List files on server")
        print("  download <filename>           - Download file from server")
        print("  download <filename> <path>    - Download file to specific local path")
        print("  upload <filepath>             - Upload local file to server")
        print("  upload <filepath> <name>      - Upload with specific remote filename")
        print("  info                          - Get server information")
        print("  help                          - Show this help")
        print("  quit/exit                     - Exit the client")

def main():
    client = FileTransferClient()
    
    if client.connect():
        try:
            client.run_interactive()
        finally:
            client.disconnect()
    else:
        print("Could not connect to server. Make sure the server is running.")

if __name__ == '__main__':
    main()