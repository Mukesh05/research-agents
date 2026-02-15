from tools.pptx_export import save_to_pptx

test_data = '''
# Introduction to AI
AI is transforming technology.
## Machine Learning
ML enables computers to learn from data.
- Classification algorithms
- Neural networks
'''

print("Testing PPTX...")
try:
    result = save_to_pptx.invoke(
        {"data": test_data, "title": "AI Overview", "filename": "test_ai.pptx"})
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
