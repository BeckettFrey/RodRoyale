# File: generate_ssl_cert.sh
#!/bin/bash
# Generate self-signed SSL certificate for development

echo "🔐 Generating self-signed SSL certificate for development..."

# Create certificates directory
mkdir -p certificates

# Generate private key
openssl genrsa -out certificates/private.key 2048

# Generate certificate signing request
openssl req -new -key certificates/private.key -out certificates/cert.csr \
    -subj "/C=US/ST=State/L=City/O=Rod Royale/OU=Development/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in certificates/cert.csr \
    -signkey certificates/private.key -out certificates/cert.pem

# Clean up CSR file
rm certificates/cert.csr

echo "✅ SSL certificate generated!"
echo "   Private key: certificates/private.key"
echo "   Certificate: certificates/cert.pem"
echo ""
echo "⚠️  Note: This is a self-signed certificate for development only."
echo "   Browsers will show security warnings that you can bypass."
echo "   For production, use a proper SSL certificate from a CA."
