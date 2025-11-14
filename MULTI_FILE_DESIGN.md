# Multi-File Upload Design

## Approach
To keep the UI simple while supporting multiple files:

1. **Upload Multiple Files** - Users can select multiple files at once
2. **File Selector** - Show a dropdown/radio to select which file to work with
3. **Process Selected File** - Convert/analyze the currently selected file
4. **Switch Between Files** - User can change selection to process different files

## Benefits
- Simple UI (no major redesign needed)
- Reuses existing single-file processing logic
- User can batch upload, then process individually
- Clear which file is being processed

## Implementation
```python
# Upload multiple files
uploaded_files = st.file_uploader(..., accept_multiple_files=True)

if uploaded_files:
    # Show file selector
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("Select file to process:", file_names)

    # Get selected file
    selected_file = next(f for f in uploaded_files if f.name == selected_file_name)

    # Process as normal (existing code)
    ...
```
