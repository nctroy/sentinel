#!/bin/bash
# Automated Let's Encrypt SSL certificate setup for Sentinel
# Uses certbot with nginx plugin
#
# Usage: ./setup-ssl.sh <domain> <email>
# Example: ./setup-ssl.sh sentinel.troyneff.com troy@example.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Error: This script must be run as root${NC}"
    echo "   Please run: sudo $0 $@"
    exit 1
fi

# Parse arguments
DOMAIN="${1}"
EMAIL="${2}"

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Error: Domain name is required${NC}"
    echo ""
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 sentinel.yourdomain.com admin@yourdomain.com"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo -e "${RED}❌ Error: Email address is required${NC}"
    echo ""
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 sentinel.yourdomain.com admin@yourdomain.com"
    exit 1
fi

echo -e "${GREEN}🔐 Setting up SSL/TLS for Sentinel${NC}"
echo -e "   Domain: ${YELLOW}$DOMAIN${NC}"
echo -e "   Email: ${YELLOW}$EMAIL${NC}"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}📦 Installing certbot...${NC}"

    # Detect OS and install certbot
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    elif [ -f /etc/redhat-release ]; then
        yum install -y certbot python3-certbot-nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install certbot
    else
        echo -e "${RED}❌ Error: Unsupported OS. Please install certbot manually.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ certbot installed${NC}"
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}📦 Installing nginx...${NC}"

    if [ -f /etc/debian_version ]; then
        apt-get install -y nginx
    elif [ -f /etc/redhat-release ]; then
        yum install -y nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install nginx
    else
        echo -e "${RED}❌ Error: Unsupported OS. Please install nginx manually.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ nginx installed${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p /var/www/certbot
mkdir -p /etc/nginx/.htpasswd
mkdir -p /var/www/sentinel

# Copy nginx configuration
echo -e "${YELLOW}📄 Deploying nginx configuration...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cp "$PROJECT_ROOT/nginx/nginx.conf" /etc/nginx/sites-available/sentinel
ln -sf /etc/nginx/sites-available/sentinel /etc/nginx/sites-enabled/sentinel

# Remove default site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
echo -e "${YELLOW}🔍 Testing nginx configuration...${NC}"
nginx -t

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi

# Reload nginx
echo -e "${YELLOW}🔄 Reloading nginx...${NC}"
systemctl reload nginx || service nginx reload

# Obtain SSL certificate
echo -e "${GREEN}🔐 Obtaining SSL certificate from Let's Encrypt...${NC}"
echo -e "${YELLOW}   This may take a minute...${NC}"
echo ""

certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN" \
    --redirect

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ SSL certificate obtained successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}   Possible issues:${NC}"
    echo "   - Domain DNS not pointing to this server"
    echo "   - Firewall blocking port 80/443"
    echo "   - Server not publicly accessible"
    exit 1
fi

# Set up auto-renewal
echo ""
echo -e "${YELLOW}⏰ Setting up auto-renewal...${NC}"

# Add cron job for certificate renewal
CRON_CMD="0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo -e "${YELLOW}   Auto-renewal already configured${NC}"
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo -e "${GREEN}   ✅ Auto-renewal cron job added${NC}"
fi

# Test renewal process
echo -e "${YELLOW}🧪 Testing renewal process...${NC}"
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Renewal test successful${NC}"
else
    echo -e "${RED}❌ Renewal test failed - please check configuration${NC}"
fi

# Create basic auth passwords
echo ""
echo -e "${YELLOW}🔑 Setting up basic authentication...${NC}"

# Function to create htpasswd file
create_htpasswd() {
    local file=$1
    local username=$2
    local password=$3

    # Use openssl to create password hash
    echo -e "${YELLOW}   Creating $file...${NC}"
    echo "$username:$(openssl passwd -apr1 "$password")" > "$file"
    chmod 640 "$file"
}

# Create passwords for ops and executive dashboards
create_htpasswd "/etc/nginx/.htpasswd_ops" "admin" "changeme_ops_$(openssl rand -hex 4)"
create_htpasswd "/etc/nginx/.htpasswd_executive" "admin" "changeme_exec_$(openssl rand -hex 4)"

echo -e "${GREEN}✅ Basic authentication configured${NC}"
echo -e "${YELLOW}   ⚠️  Change default passwords in:${NC}"
echo "   - /etc/nginx/.htpasswd_ops"
echo "   - /etc/nginx/.htpasswd_executive"

# Final nginx reload
echo ""
echo -e "${YELLOW}🔄 Final nginx reload...${NC}"
systemctl reload nginx || service nginx reload

# Display summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SSL/TLS Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "📍 ${YELLOW}Access Points:${NC}"
echo -e "   Main Site:      https://$DOMAIN"
echo -e "   Operations:     https://$DOMAIN/ops"
echo -e "   Executive:      https://$DOMAIN/executive"
echo -e "   API:            https://$DOMAIN/api"
echo -e "   Health Check:   https://$DOMAIN/health"
echo ""
echo -e "🔐 ${YELLOW}SSL Certificate:${NC}"
echo -e "   Issuer:         Let's Encrypt"
echo -e "   Valid for:      90 days"
echo -e "   Auto-renewal:   Daily at 3:00 AM"
echo ""
echo -e "🔑 ${YELLOW}Basic Auth Credentials:${NC}"
echo -e "   Username:       admin"
echo -e "   Password files: /etc/nginx/.htpasswd_*"
echo -e "   ${RED}⚠️  CHANGE DEFAULT PASSWORDS!${NC}"
echo ""
echo -e "📚 ${YELLOW}Next Steps:${NC}"
echo "   1. Update password files with secure passwords"
echo "   2. Test access to all endpoints"
echo "   3. Configure firewall (allow ports 80, 443)"
echo "   4. Monitor certificate renewal logs"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
