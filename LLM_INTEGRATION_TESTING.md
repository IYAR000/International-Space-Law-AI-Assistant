# LLM Integration Testing

This document explains how to test the LLM integration with your API keys.

## Quick Start

1. **Get your API key:**
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Claude/Anthropic**: https://console.anthropic.com/

2. **Update the test script:**
   
   Open `test_llm_integration.py` and set your API key:
   
   ```python
   # For OpenAI
   OPENAI_API_KEY = "sk-your-actual-key-here"
   
   # For Claude
   CLAUDE_API_KEY = "sk-ant-your-actual-key-here"
   ```

3. **Run the test:**
   
   ```powershell
   python test_llm_integration.py
   ```

## What the Test Does

### 1. API Health Checks
- Tests both Space Law APIs (Data Collection & Legal Analysis)
- Verifies they are running and responding

### 2. Analysis Endpoint Test
- Calls the legal analysis API
- Gets back structured legal analysis data (with mock data)

### 3. API Key Validation (No Tokens Used)
- **Validates OpenAI key format** (must start with `sk-`)
- **Validates Claude key format** (must start with `sk-ant-`)
- **Attempts mock authentication** without consuming tokens
- Shows which keys are valid and which need updating

### 4. Full LLM Integration (If Keys Valid)
- Sends legal analysis to the LLM
- Gets back comprehensive legal opinions
- **Only runs if API keys are properly validated**

## Test Output Example

```
============================================================
Validating OpenAI API Key
============================================================
✓ API key format is valid
✓ Key length: 48 characters
✓ Key prefix: sk-proj-...

Attempting mock authentication (no tokens used)...
✓ Authentication successful!
✓ Response status: 200

============================================================
Testing LLM Integration (OpenAI)
============================================================
✓ LLM Response Received

Legal Opinion from GPT-4:
[Full legal opinion from the LLM...]
```

## Important Notes

- **Mock Authentication Only**: The validation tests authenticate your API key WITHOUT making actual LLM calls or consuming tokens
- **Real LLM Calls**: Only happen after successful authentication
- **Environment Variables**: For production, store API keys in environment variables instead of the script:
  
  ```powershell
  $env:OPENAI_API_KEY="sk-..."
  $env:CLAUDE_API_KEY="sk-ant-..."
  ```

## Troubleshooting

### "Authentication failed - Invalid API key"
- Check that your API key is correctly copied
- Ensure there are no extra spaces or special characters
- Verify the key format:
  - OpenAI: starts with `sk-`
  - Claude: starts with `sk-ant-`

### "Request timeout"
- Check your internet connection
- Verify you can access the APIs:
  - https://api.openai.com/ (for OpenAI)
  - https://api.anthropic.com/ (for Claude)

### "Connection refused"
- Make sure the Space Law APIs are running
- Data Collection API: http://localhost:8001
- Legal Analysis API: http://localhost:8002

## API Endpoints

### Data Collection API
- **Health**: `GET http://localhost:8001/health`
- **Docs**: `http://localhost:8001/docs`

### Legal Analysis API
- **Health**: `GET http://localhost:8002/health`
- **Analyze**: `POST http://localhost:8002/analyze/customary-vs-treaty`
- **Docs**: `http://localhost:8002/docs`

## Next Steps

After validating your API keys:

1. Implement the full LLM integration in your application
2. Handle API rate limits and retries
3. Cache frequently analyzed documents
4. Set up logging for audit trails
5. Implement error handling for LLM failures
