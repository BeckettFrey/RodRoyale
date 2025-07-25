# 🌤️ Cloudinary Integration Documentation

This document explains the Cloudinary integration in the Rod Royale Backend API, which replaces local file storage with cloud-based image management.

## 🔧 Setup Requirements

### 1. Cloudinary Account
- Sign up for a free account at [cloudinary.com](https://cloudinary.com)
- Navigate to your dashboard to get:
  - **Cloud Name**: Your unique identifier
  - **API Key**: Public key for API access
  - **API Secret**: Private key for API access

### 2. Environment Variables
Add these to your `.env` file:
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Package Installation
The cloudinary package is included in `requirements.txt`:
```bash
pip install cloudinary==1.36.0
```

## 📸 Features

### Image Upload
- **Direct Upload**: Upload images directly to Cloudinary
- **Automatic Optimization**: Images are automatically optimized for web delivery
- **Format Conversion**: Auto-detects best format (WebP, AVIF, etc.)
- **Quality Adjustment**: Automatic quality optimization

### Dynamic Transformations
- **Thumbnails**: Generate thumbnails with custom dimensions
- **Resizing**: Resize images while maintaining aspect ratio
- **Cropping**: Smart cropping with face detection
- **Optimization**: Real-time optimization based on device and network

### Image Management
- **Organized Storage**: Images stored in folders (Rod Royale/catches, etc.)
- **Public IDs**: Unique identifiers for each image
- **Programmatic Deletion**: Delete images via API
- **Analytics**: Usage tracking and analytics via Cloudinary dashboard

## 🚀 API Endpoints

### Image Upload
```http
POST /api/v1/upload/image
Content-Type: multipart/form-data

file: <image_file>
folder: Rod Royale/catches (optional)
```

**Response:**
```json
{
  "url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/Rod Royale/catches/uuid.jpg",
  "public_id": "Rod Royale/catches/uuid",
  "original_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/Rod Royale/catches/uuid.jpg",
  "thumbnail_url": "https://res.cloudinary.com/your-cloud/image/upload/c_fill,h_300,w_300/Rod Royale/catches/uuid.jpg"
}
```

### Catch with Image Upload
```http
POST /api/v1/catches/upload-with-image
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <image_file>
species: "Largemouth Bass"
weight: 8.5
lat: 34.0522
lng: -118.2437
shared_with_followers: true
```

**Response:**
```json
{
  "id": "ObjectId",
  "user_id": "ObjectId",
  "species": "Largemouth Bass",
  "weight": 8.5,
  "photo_url": "https://res.cloudinary.com/your-cloud/image/upload/.../uuid.jpg",
  "photo_public_id": "Rod Royale/catches/uuid",
  "thumbnail_url": "https://res.cloudinary.com/.../c_fill,h_300,w_300/.../uuid.jpg",
  "location": {
    "lat": 34.0522,
    "lng": -118.2437
  },
  "shared_with_followers": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Generate Thumbnail
```http
GET /api/v1/upload/image/{public_id}/thumbnail?width=200&height=200
```

### Generate Optimized URL
```http
GET /api/v1/upload/image/{public_id}/optimized?width=800&height=600
```

### Delete Image
```http
DELETE /api/v1/upload/image/{public_id}
```

## 🏗️ Architecture

### Service Layer
The `CloudinaryService` class handles all Cloudinary operations:
- Image validation (file type, size)
- Upload with transformations
- URL generation for thumbnails and optimized versions
- Image deletion

### Database Integration
Catch records now include additional Cloudinary fields:
- `photo_public_id`: Cloudinary public ID for image management
- `thumbnail_url`: Pre-generated thumbnail URL for optimized loading

### Error Handling
- Validates file types (png, jpg, jpeg, gif, webp)
- Enforces size limits (10MB max)
- Graceful error handling with proper HTTP status codes
- Detailed error messages for debugging

## 🔒 Security

### API Keys
- API keys are stored as environment variables
- Never committed to version control
- Separate keys for development/production

### Access Control
- Image uploads require JWT authentication
- Users can only delete their own images
- Cloudinary URLs are publicly accessible but unpredictable

### File Validation
- File type validation before upload
- Size limits enforced
- Malicious file detection by Cloudinary

## ⚡ Performance Benefits

### Over Local Storage
- **CDN Delivery**: Global content delivery network
- **Automatic Optimization**: Format and quality optimization
- **Caching**: Built-in caching and edge delivery
- **Scalability**: No server storage limitations

### Dynamic Transformations
- **On-the-fly**: Generate thumbnails without pre-processing
- **Device Optimization**: Serve appropriate sizes for different devices
- **Bandwidth Savings**: Automatically optimize for network conditions

## 🧪 Testing

Run the comprehensive test script:
```bash
python test_cloudinary_upload.py
```

This tests:
- Direct image upload
- Catch creation with image
- Thumbnail generation
- Optimized URL generation
- Image deletion

## 🚨 Migration from Local Storage

### For Existing Images
If you have existing images in the `uploads/` folder:

1. **Backup**: Ensure you have backups of existing images
2. **Migration Script**: Create a script to upload existing images to Cloudinary
3. **Update Database**: Update catch records with new Cloudinary URLs
4. **Cleanup**: Remove local `uploads/` folder after verification

### Database Updates
Update existing catch records to include Cloudinary fields:
```javascript
// MongoDB update to add new fields
db.catches.updateMany(
  { photo_public_id: { $exists: false } },
  { 
    $set: { 
      photo_public_id: null,
      thumbnail_url: null
    }
  }
)
```

## 📊 Monitoring

### Cloudinary Dashboard
Monitor usage via the Cloudinary dashboard:
- **Usage Statistics**: Bandwidth, transformations, storage
- **Analytics**: Popular images, access patterns
- **Optimization Reports**: Format adoption, size savings

### API Monitoring
Track API performance:
- Upload success/failure rates
- Response times
- Error patterns

## 🔧 Advanced Configuration

### Custom Transformations
Modify default transformations in `cloudinary_service.py`:
```python
default_transformation = {
    'quality': 'auto:good',
    'fetch_format': 'auto',
    'width': 1200,
    'height': 1200,
    'crop': 'limit'
}
```

### Folder Organization
Organize images by type:
- `Rod Royale/catches/` - Fishing catch photos
- `Rod Royale/profiles/` - User profile images
- `Rod Royale/pins/` - Map pin images

### Environment-Specific Config
Use different Cloudinary accounts for environments:
```bash
# Development
CLOUDINARY_CLOUD_NAME=Rod Royale-dev

# Production  
CLOUDINARY_CLOUD_NAME=Rod Royale-prod
```

## 🆘 Troubleshooting

### Common Issues

**"Cloudinary configuration missing"**
- Ensure all three environment variables are set
- Check for typos in variable names
- Verify values are correct from Cloudinary dashboard

**"File type not allowed"**
- Check allowed extensions in `cloudinary_service.py`
- Ensure file has proper extension

**"Upload failed"**
- Check network connectivity
- Verify Cloudinary credentials
- Check file size limits

**"Image not found during deletion"**
- Verify public_id is correct
- Check if image exists in Cloudinary dashboard
- Ensure proper URL encoding for nested folder IDs

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Resources

- [Cloudinary Documentation](https://cloudinary.com/documentation)
- [Python SDK Guide](https://cloudinary.com/documentation/django_integration)
- [Image Transformation Reference](https://cloudinary.com/documentation/image_transformation_reference)
- [API Reference](https://cloudinary.com/documentation/image_upload_api_reference)
