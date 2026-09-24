"""Export notebook to editable markdown, then convert to docx via pandoc."""
import json
from pathlib import Path
import subprocess

nb_path = Path(r'c:\Users\INAYGUP1\OneDrive - ABB\Ayushi_M\SEM3\Robotics\Ass-1\Part_A_Motion_Model.ipynb')
md_path = nb_path.parent / 'Part_A_Motion_Model_Editable.md'
docx_path = nb_path.parent / 'Part_A_Motion_Model_Editable.docx'

nb = json.loads(nb_path.read_text(encoding='utf-8'))
md_out = []

for cell in nb['cells']:
    source = ''.join(cell['source'])
    if cell['cell_type'] == 'markdown':
        # Remove leading --- that pandoc interprets as YAML
        source = source.lstrip('-').lstrip('\n')
        md_out.append(source)
    elif cell['cell_type'] == 'code':
        md_out.append('```python\n' + source + '\n```')
    md_out.append('')

md_path.write_text('\n'.join(md_out), encoding='utf-8')
print(f"Editable markdown: {md_path.name}")

# Convert to docx using pandoc
result = subprocess.run(
    ['pandoc', str(md_path), '-o', str(docx_path), '--standalone'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print(f"Editable Word doc: {docx_path.name}")
    print("-> Edit in Word, then Save As PDF when done.")
else:
    print(f"pandoc error: {result.stderr}")
