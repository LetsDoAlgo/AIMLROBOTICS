"""Export notebook code + output images and append to report as appendix."""
import json, base64
from pathlib import Path

nb_path = Path(r'c:\Users\INAYGUP1\OneDrive - ABB\Ayushi_M\SEM3\Robotics\Ass-1\Part_A_Motion_Model.ipynb')
report_path = Path(r'c:\Users\INAYGUP1\OneDrive - ABB\Ayushi_M\SEM3\Robotics\Ass-1\Part_A_Report.md')
img_dir = nb_path.parent / 'report_images'
img_dir.mkdir(exist_ok=True)

nb = json.loads(nb_path.read_text(encoding='utf-8'))

appendix_md = "\n\n---\n\n## Appendix: Notebook Code & Simulation Outputs\n\n"
img_count = 0
cell_num = 0

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        cell_num += 1
        source = ''.join(cell['source'])
        appendix_md += f"### Code Cell {cell_num}\n\n```python\n{source}\n```\n\n"
        
        # Extract image outputs
        if 'outputs' in cell:
            for output in cell['outputs']:
                if 'data' in output:
                    if 'image/png' in output['data']:
                        img_count += 1
                        img_data = output['data']['image/png']
                        img_bytes = base64.b64decode(img_data)
                        img_name = f"output_{img_count}.png"
                        (img_dir / img_name).write_bytes(img_bytes)
                        appendix_md += f"**Output {img_count}:**\n\n![Simulation Output {img_count}](report_images/{img_name})\n\n"
                
                # Text output
                if output.get('output_type') == 'stream' and 'text' in output:
                    text = ''.join(output['text']).strip()
                    if text:
                        appendix_md += f"```\n{text}\n```\n\n"

# Append to report
current_report = report_path.read_text(encoding='utf-8')
report_path.write_text(current_report + appendix_md, encoding='utf-8')

print(f"Done! Appended {cell_num} code cells and {img_count} output images to Part_A_Report.md")
print(f"Images saved in: report_images/")
