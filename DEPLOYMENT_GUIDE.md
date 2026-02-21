# BATYR BOL Deployment Guide

This guide explains how to deploy the BATYR BOL platform with proper domains for both the website and Telegram bot.

## Domain Setup Instructions

### 1. Website Domain Configuration

#### Option A: Using a Custom Domain with Hosting Provider
1. Purchase a domain (e.g., batyrbol.kz) from a domain registrar
2. Configure DNS settings to point to your hosting provider:
   - A record: @ → [IP address of your server]
   - CNAME record: www → [your-domain.com]

#### Option B: Using Free Services (for testing)
- GitHub Pages: Create a repository and use github.io subdomain
- Netlify: Deploy and get a netlify.app subdomain
- Vercel: Deploy and get a vercel.app subdomain

#### Example DNS Configuration:
```
Type    Name    Value               TTL
A       @       192.0.2.1           3600
CNAME   www     your-domain.com     3600
```

### 2. Telegram Bot Domain Integration

The Telegram bot doesn't require a domain for basic functionality, but for webhook support:
1. Set up a domain with SSL certificate (HTTPS required)
2. Configure webhook URL:
   ```
   https://api.telegram.org/bot[YOUR_BOT_TOKEN]/setWebhook?url=https://your-domain.com/webhook
   ```

### 3. Production Server Setup

#### Requirements:
- Python 3.8+
- Flask
- python-telegram-bot
- Web server (Nginx/Apache)
- SSL certificate (Let's Encrypt)

#### Sample Nginx Configuration:
```nginx
server {
    listen 80;
    server_name batyrbol.kz www.batyrbol.kz;
    
    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name batyrbol.kz www.batyrbol.kz;
    
    # SSL certificate configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Environment Variables

Create a `.env` file with your configuration:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=production
HOST=0.0.0.0
PORT=8000
DOMAIN_NAME=https://batyrbol.kz
```

### 5. Production Deployment Steps

1. Clone the repository to your server:
   ```bash
   git clone https://github.com/yourusername/batyrbol.git
   cd batyrbol
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up systemd service for the Flask app:
   ```ini
   # /etc/systemd/system/batyrbol.service
   [Unit]
   Description=BATYR BOL Web Service
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/batyrbol
   ExecStart=/path/to/python server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. Enable and start the service:
   ```bash
   sudo systemctl enable batyrbol
   sudo systemctl start batyrbol
   ```

### 6. SSL Certificate Setup (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d batyrbol.kz -d www.batyrbol.kz
```

## Recommended Domain Names

1. batyrbol.kz
2. batyrbol.kz
3. qazaqboly.kz
4. kazakhstanheroes.kz
5. learnkazakhhistory.kz

## Troubleshooting

### Common Issues:
1. **Domain not resolving**: Check DNS propagation (can take up to 48 hours)
2. **SSL certificate errors**: Ensure certificate matches domain name exactly
3. **Mixed content warnings**: Ensure all resources use HTTPS

### Testing:
```bash
# Test domain resolution
nslookup batyrbol.kz

# Test HTTPS connection
curl -I https://batyrbol.kz

# Check certificate validity
openssl s_client -connect batyrbol.kz:443 -servername batyrbol.kz
```

## Maintenance

1. Regularly renew SSL certificates (Let's Encrypt renews automatically)
2. Monitor server logs for errors
3. Backup user data regularly
4. Update dependencies periodically

---

*For any deployment issues, contact your hosting provider's support team.*