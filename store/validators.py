from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kb = 500
     
    if file.size > max_size_kb * 1024:  #file.size是b
        raise ValidationError(f'文件不可超过{max_size_kb}KB')
