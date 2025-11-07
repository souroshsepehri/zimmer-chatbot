# Upload Chatbot Project to Cloud Server

## Option 1: Upload via SCP (from your local Windows machine)

Open PowerShell on your **local Windows machine** and run:

```powershell
# Navigate to your local project directory
cd C:\chatbot2

# Upload entire project to server
scp -r . chatbot@vm-185117:~/chatbot2

# Or upload specific directories
scp -r backend chatbot@vm-185117:~/
scp -r frontend chatbot@vm-185117:~/
scp requirements.txt chatbot@vm-185117:~/
```

## Option 2: Upload via SFTP (using FileZilla or WinSCP)

1. **Download FileZilla** (free FTP/SFTP client)
2. **Connect to your server:**
   - Host: `vm-185117` (or your server IP)
   - Username: `chatbot`
   - Password: (your password)
   - Port: `22`
   - Protocol: `SFTP`

3. **Upload files:**
   - Left side: Your local `C:\chatbot2` folder
   - Right side: Server `~/chatbot2` folder
   - Drag and drop the entire project

## Option 3: Clone from Git (if you have a repository)

On your **cloud server**, run:

```bash
cd ~
git clone https://github.com/your-username/chatbot2.git
cd chatbot2
```

## Option 4: Create Project Structure Manually

If you want to recreate the project structure on the server, I can help you set that up.



