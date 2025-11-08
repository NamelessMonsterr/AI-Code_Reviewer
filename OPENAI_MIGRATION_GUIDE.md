# OpenAI API Migration Guide

## Overview
OpenAI has deprecated the old `openai.ChatCompletion.create()` API in favor of the new client-based approach in SDK v1.0+. This guide helps migrate your codebase.

## What Changed

### Old API (Deprecated)
```python
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

response = openai.ChatCompletion.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Hello'}],
    temperature=0.2
)

result = response.choices[0].message.content
```

### New API (Required)
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'Hello'}],
    temperature=0.2
)

result = response.choices[0].message.content
```

## Key Differences

### 1. **Client Initialization**
- **Old**: Global `openai.api_key` configuration
- **New**: Create `OpenAI()` client instance

### 2. **Method Names**
- **Old**: `openai.ChatCompletion.create()`
- **New**: `client.chat.completions.create()`

### 3. **Response Access**
- Response structure remains the same
- Still access: `response.choices[0].message.content`

### 4. **Embeddings**
- **Old**: `openai.Embedding.create()`
- **New**: `client.embeddings.create()`

### 5. **File Operations**
- **Old**: `openai.File.create()`
- **New**: `client.files.create()`

### 6. **Fine-tuning**
- **Old**: `openai.FineTuningJob.create()`
- **New**: `client.fine_tuning.jobs.create()`

## Files That Need Migration

### ✅ Already Fixed
- `src/autofix/code_fixer.py`

### ⚠️ Need Migration
1. **src/documentation/doc_generator.py**
2. **src/interactive/chat_interface.py**
3. **src/performance/profiler.py**
4. **src/testing/test_generator.py**
5. **src/search/semantic_search.py**
6. **src/training/model_finetuner.py**

## Step-by-Step Migration

### Step 1: Update imports
```python
# Before
import openai

# After
from openai import OpenAI
```

### Step 2: Initialize client in __init__
```python
class YourClass:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        # Old way
        # openai.api_key = self.api_key
        
        # New way
        self.client = OpenAI(api_key=self.api_key)
```

### Step 3: Update method calls
```python
# Old
response = openai.ChatCompletion.create(
    model='gpt-4',
    messages=[...]
)

# New
response = self.client.chat.completions.create(
    model='gpt-4',
    messages=[...]
)
```

### Step 4: Update embeddings
```python
# Old
response = openai.Embedding.create(
    model='text-embedding-ada-002',
    input=text
)

# New
response = self.client.embeddings.create(
    model='text-embedding-ada-002',
    input=text
)
```

### Step 5: Update fine-tuning
```python
# Old
job = openai.FineTuningJob.create(
    training_file=file_id,
    model='gpt-3.5-turbo'
)

# New
job = self.client.fine_tuning.jobs.create(
    training_file=file_id,
    model='gpt-3.5-turbo'
)
```

## Example: Complete Class Migration

### Before
```python
import openai
import os

class DocumentationGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
    
    def generate_docstring(self, code: str) -> str:
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': f'Document: {code}'}],
            temperature=0.2
        )
        return response.choices[0].message.content
```

### After
```python
from openai import OpenAI
import os

class DocumentationGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_docstring(self, code: str) -> str:
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': f'Document: {code}'}],
            temperature=0.2
        )
        return response.choices[0].message.content
```

## Error Handling

### Old API Errors
```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.RateLimitError as e:
    print("Rate limited")
```

### New API Errors
```python
from openai import RateLimitError, APIError

try:
    response = self.client.chat.completions.create(...)
except RateLimitError as e:
    print("Rate limited")
except APIError as e:
    print(f"API error: {e}")
```

## Testing Migration

After migrating, test with:

```python
# test_openai_migration.py
from openai import OpenAI
import os

def test_basic_completion():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Say hello'}],
        max_tokens=10
    )
    
    assert response.choices[0].message.content
    print("✓ Migration successful!")

if __name__ == '__main__':
    test_basic_completion()
```

## Breaking Changes Checklist

- [ ] Replace `import openai` with `from openai import OpenAI`
- [ ] Remove `openai.api_key = ...` lines
- [ ] Create `self.client = OpenAI(...)` in `__init__`
- [ ] Update `openai.ChatCompletion.create` → `client.chat.completions.create`
- [ ] Update `openai.Embedding.create` → `client.embeddings.create`
- [ ] Update `openai.File.create` → `client.files.create`
- [ ] Update `openai.FineTuningJob.create` → `client.fine_tuning.jobs.create`
- [ ] Update error handling imports
- [ ] Test all affected endpoints

## Compatibility

- **Minimum SDK Version**: `openai>=1.0.0`
- **Python Version**: Python 3.7+
- **Breaking Change**: SDK v0.x methods will not work

## Rollout Strategy

1. **Update requirements.txt**: `openai>=1.3.0`
2. **Migrate one file at a time** (use checklist above)
3. **Test each file** after migration
4. **Update CI/CD** to use new SDK
5. **Monitor for errors** in production

## Support

- OpenAI API Docs: https://platform.openai.com/docs/api-reference
- Migration Guide: https://github.com/openai/openai-python/discussions/742
- SDK Changelog: https://github.com/openai/openai-python/releases
