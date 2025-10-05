# LazAI Intelligence Hub

A comprehensive AI-powered data analytics and query application built on the LazAI platform. This application showcases how an intelligent agent can interact with encrypted datasets in a useful and meaningful way.

## 🚀 Features

### 🤖 AI-Powered Data Assistant
- **Intelligent Chat Interface**: Natural language queries against your encrypted data
- **Real-time Processing**: Instant responses with loading indicators
- **Context-Aware Responses**: Smart formatting and error handling

### 📊 Advanced Analytics Dashboard
- **Query Analytics**: Track total queries, response times, and usage patterns
- **Data Visualization**: Interactive charts showing query categories and trends
- **AI Insights**: Automated analysis of your data content and patterns
- **Performance Metrics**: Real-time monitoring of system performance

### 🔒 Secure Data Management
- **Encrypted Data Sources**: Query your LazAI encrypted files securely
- **File Management**: Upload and manage multiple data sources
- **Permission Control**: Secure access to encrypted data via LazAI permissions

### 💬 Interactive Features
- **Chat History**: Persistent conversation history with export functionality
- **Quick Actions**: Pre-defined query templates for common tasks
- **Smart Suggestions**: AI-powered query recommendations
- **File Upload**: Support for text files, direct text input, and URL sources

### 🎨 Modern User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Professional dark theme with smooth animations
- **Intuitive Navigation**: Clean, modern interface with clear visual hierarchy
- **Accessibility**: Keyboard navigation and screen reader support

## 🛠️ Technical Architecture

### Backend (FastAPI)
- **RESTful API**: Clean, well-documented endpoints
- **CORS Support**: Cross-origin resource sharing for web applications
- **Error Handling**: Comprehensive error handling and logging
- **Analytics Endpoints**: Advanced data analysis and insights generation

### Frontend (Vanilla JavaScript)
- **Modular Architecture**: Clean, maintainable code structure
- **Real-time Updates**: Dynamic UI updates without page refreshes
- **Local Storage**: Persistent user preferences and query history
- **Chart Integration**: Interactive data visualization with Chart.js

### Data Processing
- **Vector Search**: Efficient similarity search using Milvus
- **Text Chunking**: Intelligent text segmentation for better search
- **Caching**: In-memory caching for improved performance
- **Fallback Store**: Simple in-memory store when Milvus is unavailable

## 📋 API Endpoints

### Core Query Endpoints
- `POST /query/rag` - Query encrypted LazAI data
- `POST /query/local` - Query local text data (for testing)

### Analytics Endpoints
- `POST /analytics/insights` - Generate AI-powered insights
- `GET /analytics/trends` - Get query trends and patterns

### Utility Endpoints
- `GET /health` - Health check
- `GET /ui` - Serve the web interface
- `GET /` - API information

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- LazAI account and private key
- IPFS JWT token (optional, for file uploads)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd b3
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   PRIVATE_KEY=your_lazai_private_key
   IPFS_JWT=your_ipfs_jwt_token  # Optional
   LLM_BASE_URL=your_llm_base_url  # Optional
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the web interface**
   Open your browser and navigate to `http://localhost:8000/ui`

## 💡 Usage Examples

### Basic Query
```javascript
// Query your encrypted data
const response = await fetch('/query/rag', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: 2346,
    query: "What are my main skills?",
    limit: 3
  })
});
```

### Analytics Insights
```javascript
// Get AI-powered insights
const insights = await fetch('/analytics/insights', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: 2346,
    analysis_type: "skills"
  })
});
```

### Local Data Testing
```javascript
// Test with local data
const response = await fetch('/query/local', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: "Your text content here...",
    query: "Summarize the main points",
    collection: "test_collection"
  })
});
```

## 🔧 Configuration

### Environment Variables
- `PRIVATE_KEY`: Your LazAI private key (required)
- `IPFS_JWT`: IPFS JWT token for file uploads (optional)
- `LLM_BASE_URL`: Custom LLM endpoint (optional)

### Server Configuration
```python
# Run with custom settings
python main.py --host 0.0.0.0 --port 8000
```

## 📊 Analytics Features

### Query Analytics
- Total queries processed
- Average response time
- Query success rate
- Popular query patterns

### Data Insights
- Content analysis and summarization
- Skills and expertise extraction
- Technology stack identification
- Interest and passion mapping

### Usage Patterns
- Peak usage hours
- Most active days
- Query category distribution
- User engagement metrics

## 🔒 Security Features

### Data Encryption
- All data encrypted using LazAI encryption
- Secure key management
- Permission-based access control

### API Security
- CORS protection
- Input validation
- Error handling without data leakage
- Rate limiting (configurable)

## 🎨 Customization

### UI Themes
- Dark theme (default)
- Light theme support
- Custom color schemes
- Responsive breakpoints

### Query Templates
- Pre-defined quick actions
- Custom query suggestions
- Smart query recommendations
- Context-aware suggestions

## 📈 Performance Optimization

### Caching Strategy
- In-memory query caching
- Collection-based caching
- Response time optimization
- Memory usage monitoring

### Database Optimization
- Milvus vector database
- Efficient similarity search
- Text chunking optimization
- Index management

## 🐛 Troubleshooting

### Common Issues

1. **"None of PyTorch, TensorFlow >= 2.0, or Flax have been found"**
   - This is normal for the current setup
   - The application uses alternative text processing methods

2. **CORS errors**
   - Ensure the server is running on the correct port
   - Check CORS configuration in main.py

3. **File upload issues**
   - Verify IPFS_JWT token is set
   - Check file format compatibility

### Debug Mode
```bash
# Run with debug logging
python main.py --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LazAI platform for encrypted data management
- FastAPI for the robust backend framework
- Chart.js for data visualization
- Font Awesome for icons
- The open-source community for inspiration

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

---

**Built with ❤️ using LazAI, FastAPI, and modern web technologies**
