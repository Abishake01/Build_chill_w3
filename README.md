# LazAI Intelligence Hub

A comprehensive LazAI Data Query application that demonstrates privacy-preserving data analysis and AI-powered insights. This application integrates with the LazAI ecosystem to provide secure, encrypted data querying capabilities.

## 🚀 Features

- **Privacy-Preserving Data Query**: Query encrypted data using LazAI's secure infrastructure
- **Interactive Web Interface**: Modern, responsive web UI for data exploration
- **AI-Powered Analytics**: Generate insights and trends from your data
- **Multiple Query Modes**: Support for RAG queries, local content analysis, and demo mode
- **Real-time Analytics**: Track query patterns and system performance
- **File Management**: Upload and manage multiple data sources
- **Export Capabilities**: Export chat history and analysis results

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  FastAPI Server │    │   LazAI SDK     │
│                 │◄──►│                 │◄──►│                 │
│  - React UI     │    │  - Query API    │    │  - Encryption   │
│  - Analytics    │    │  - Analytics    │    │  - Milvus Store │
│  - Chat Interface│   │  - File Mgmt    │    │  - Data Access  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- LazAI account and credentials
- Optional: OpenAI API key for enhanced AI features

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd b3
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# For local development with Milvus Lite
pip install "pymilvus[milvus_lite]"

# Install LazAI SDK
python3 -m pip install alith -U
```

### 4. Environment Configuration

```bash
# Copy environment template
cp env_template.txt .env

# Edit .env with your credentials
# Required:
PRIVATE_KEY=your_wallet_private_key_here
RSA_PRIVATE_KEY_BASE64=your_rsa_private_key_base64_here

# Optional:
OPENAI_API_KEY=your_openai_api_key_here
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=your_llm_base_url_here
```

## 🚀 Quick Start

### 1. Start the Server

```bash
# Start the FastAPI server
python main.py

# Or with custom settings
python main.py --host 0.0.0.0 --port 8000
```

### 2. Access the Web Interface

Open your browser and navigate to:
- **Web UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Run the Demo

```bash
# Run comprehensive demo
python lazai_client.py --mode demo

# Run interactive mode
python lazai_client.py --mode interactive
```

## 📖 Usage Guide

### Web Interface

1. **Data Sources**: Upload files or paste text content
2. **Query Interface**: Ask questions about your data
3. **Analytics Dashboard**: View insights and trends
4. **Export Data**: Download chat history and results

### API Endpoints

#### Core Query Endpoints

- `POST /query/rag` - Query encrypted LazAI data
- `POST /query/local` - Query local content
- `POST /demo/query` - Demo queries (no encryption)

#### Analytics Endpoints

- `POST /analytics/insights` - Generate AI insights
- `GET /analytics/trends` - Get usage trends

#### Utility Endpoints

- `GET /health` - Health check
- `GET /ui` - Web interface
- `GET /` - API information

### Example API Usage

```python
import requests

# Demo query
response = requests.post("http://localhost:8000/demo/query", 
                       json={"query": "What are my main skills?"})
print(response.json())

# Local content query
response = requests.post("http://localhost:8000/query/local",
                       json={
                           "content": "Your text content here",
                           "query": "Summarize the main points",
                           "collection": "my_data"
                       })
print(response.json())
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PRIVATE_KEY` | Yes | Your wallet private key |
| `RSA_PRIVATE_KEY_BASE64` | Yes | RSA private key (base64) |
| `OPENAI_API_KEY` | No | OpenAI API key |
| `LLM_API_KEY` | No | Alternative LLM API key |
| `LLM_BASE_URL` | No | Alternative LLM base URL |
| `APP_HOST` | No | Server host (default: 0.0.0.0) |
| `APP_PORT` | No | Server port (default: 8000) |

### LazAI Integration

1. **Register with LazAI**: Get your credentials from LazAI admins
2. **Add Query Node**: Register your server URL with LazAI
3. **File Permissions**: Ensure you have access to the data files you want to query

## 🧪 Testing

### Run Tests

```bash
# Run the demo script
python demo.py

# Run client tests
python lazai_client.py --mode demo

# Test specific endpoints
curl http://localhost:8000/health
```

### Test Scenarios

1. **Health Check**: Verify server is running
2. **Demo Queries**: Test without LazAI encryption
3. **Local Queries**: Test with uploaded content
4. **Analytics**: Test insights and trends
5. **Web Interface**: Test UI functionality

## 📊 Features in Detail

### Privacy-Preserving Queries

- **Encrypted Data Access**: Query encrypted data without exposing it
- **Secure Computation**: All processing happens in secure environments
- **Access Control**: Only authorized users can access specific data

### AI-Powered Analytics

- **Smart Insights**: Generate summaries, skill analysis, and trend detection
- **Query Categorization**: Automatically categorize and analyze queries
- **Performance Metrics**: Track response times and usage patterns

### Interactive Interface

- **Real-time Chat**: Natural language interface for data queries
- **File Management**: Upload and manage multiple data sources
- **Visual Analytics**: Charts and graphs for data insights
- **Export Functionality**: Download results and chat history

## 🔒 Security Features

- **End-to-End Encryption**: Data remains encrypted throughout the process
- **Secure Key Management**: RSA keys for encryption/decryption
- **Access Control**: File-level permissions and authentication
- **Privacy by Design**: No data leaves your control

## 🚀 Deployment

### Local Development

```bash
# Start with development settings
python main.py --host 0.0.0.0 --port 8000
```

### Production Deployment

For production deployment on Phala TEE Cloud:

1. **Docker Setup**: Use the provided Docker configuration
2. **Environment Variables**: Set production environment variables
3. **Register with LazAI**: Add your production URL to LazAI
4. **SSL/TLS**: Configure secure connections
5. **Monitoring**: Set up logging and monitoring

## 📈 Performance

- **Response Time**: < 500ms for most queries
- **Concurrent Users**: Supports multiple simultaneous queries
- **Scalability**: Horizontal scaling with load balancers
- **Caching**: Intelligent caching for improved performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub issues
- **Community**: Join the LazAI community for support
- **Email**: Contact the development team for enterprise support

## 🎯 Roadmap

- [ ] Enhanced AI model integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Enterprise features
- [ ] API rate limiting
- [ ] Advanced security features

## 🙏 Acknowledgments

- **LazAI Team**: For the amazing privacy-preserving infrastructure
- **FastAPI**: For the excellent web framework
- **Milvus**: For vector database capabilities
- **Open Source Community**: For the various libraries and tools

---

**Built with ❤️ for privacy-preserving AI and data analysis**