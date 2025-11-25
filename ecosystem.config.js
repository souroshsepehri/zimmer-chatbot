module.exports = {
  apps: [
    {
      name: "chatbot-backend",
      script: "uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8000",
      cwd: "./backend",
      interpreter: "python",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
