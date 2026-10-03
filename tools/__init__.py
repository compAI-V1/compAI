from .code_execution import execute_python
from .file_access import list_files, read_file, write_file
from .pdf_generator import generate_pdf
from .web_search import web_search
from .voice import synthesize_speech

TOOL_SCHEMAS = [
 {"name":"web_search","description":"Search the web; use multiple sources for non-trivial facts.","input_schema":{"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer","default":5}},"required":["query"]}},
 {"name":"execute_python","description":"Execute Python in a temporary process with a strict timeout. Local personal use only.","input_schema":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}},
 {"name":"list_files","description":"List files confined to the user files root.","input_schema":{"type":"object","properties":{}}},
 {"name":"read_file","description":"Read a file confined to the user files root.","input_schema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}},
 {"name":"write_file","description":"Write a text file in the user files root, backing up an existing file.","input_schema":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}},
 {"name":"generate_pdf","description":"Generate a structured PDF report.","input_schema":{"type":"object","properties":{"title":{"type":"string"},"subtitle":{"type":"string"},"sections":{"type":"array"},"sources":{"type":"array"}},"required":["title","sections"]}},
]
DISPATCH = {"web_search": web_search, "execute_python": execute_python, "list_files": lambda **_: list_files(), "read_file": read_file, "write_file": write_file, "generate_pdf": generate_pdf}
