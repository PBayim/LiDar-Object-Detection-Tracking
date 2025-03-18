#!/usr/bin/python3 

from typing import List

class TextFileReader:
    
    def __init__(self, file_path: str):
        
        self.file_path = file_path
    
    def read_lines(self) -> List[str]:
        
        lines_list : List[str] = []
        with open(self.file_path) as file:
            for line in file:
                line_stripped = line.strip()
                if line_stripped:
                    lines_list.append()
        return lines_list