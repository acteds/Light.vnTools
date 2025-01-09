import os
import struct
from pathlib import Path
import zipfile
import sys
import shutil
import filetype

# 定义常量
PKZIP_SIGNATURE = b'\x50\x4B\x03\x04'
KEY = b'd6c5fKI3GgBWpZF3Tz6ia3kF0'
REVERSED_KEY = KEY[::-1]

def xor_data(data, key, reversed_key):
    """根据指定的规则对数据执行XOR操作"""
    data_length = len(data)
    
    # Convert bytes to bytearray for mutability
    data = bytearray(data)

    if data_length < 100:
        if data_length <= 0:
            return data

        # XOR entire bytes for files less than 100 bytes
        for i in range(data_length):
            data[i] ^= reversed_key[i % len(key)]
    else:
        # XOR the first 100 bytes with KEY
        for i in range(100):
            data[i] ^= key[i % len(key)]

        # XOR the last 99 bytes with REVERSED_KEY
        for i in range(99):
            if data_length - 99 + i < data_length:  # 确保索引不超出范围
                data[data_length - 99 + i] ^= reversed_key[i % len(key)]

    # Return as bytes
    return bytes(data)
        
def is_vndat(file_path):
    """检查给定文件是否为.vndat文件（即ZIP格式）"""
    with open(file_path, 'rb') as f:
        header = f.read(4)
        return header == PKZIP_SIGNATURE

def unpack_vndat(vndat_file, output_folder, password=None):
    """解包.vndat文件"""
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with zipfile.ZipFile(vndat_file, 'r') as zip_ref:
            if password:
                zip_ref.setpassword(password.encode('utf-8'))
            
            # 提取所有文件
            for member in zip_ref.infolist():
                try:
                    zip_ref.extract(member, output_folder)
                    print(f"已提取 {member.filename}")
                except Exception as e:
                    print(f"提取 {member.filename} 时出错: {e}")

        # 如果ZIP文件未加密，则对内容进行XOR解密
        if not password:
            for root, _, files in os.walk(output_folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    if data:
                        xorred_data = xor_data(data,KEY, REVERSED_KEY)
                        with open(file_path, 'wb') as f:
                            f.write(xorred_data)
                        print(f"已XOR解密 {file_path}")
        
        print("解包完成。")
    except Exception as e:
        print(f"解包文件 {vndat_file} 时出错: {e}")

def decrypt_mcdat(mcdat_file, output_file):
    """解密.mcdat文件"""
    try:
        with open(mcdat_file, 'rb') as f:
            data = f.read()
        xorred_data = xor_data(data, KEY, REVERSED_KEY)
        with open(output_file, 'wb') as f:
            f.write(xorred_data)
        print(f"已解密 {mcdat_file} 到 {output_file}")
    except Exception as e:
        print(f"解密文件 {mcdat_file} 时出错: {e}")

def process_files_in_directory(directory, output_root_dir):
    """
    遍历指定目录及其子目录下的所有.vndat和.mcdat文件，并进行解包或解密。
    
    :param directory: 要遍历的根目录
    :param output_root_dir: 输出根目录
    """
    target_extensions = ['.vndat', '.mcdat']
    files_to_process = [f for f in Path(directory).rglob('*') if f.suffix.lower() in target_extensions]

    if not files_to_process:
        print(f"在 {directory} 中没有找到任何.vndat或.mcdat文件。")
        return

    for file_path in files_to_process:
        relative_path = file_path.relative_to(directory)
        output_dir = os.path.join(output_root_dir, relative_path.parent)
        os.makedirs(output_dir, exist_ok=True)
        
        if file_path.suffix.lower() == '.vndat':
            print(f"正在解包 {file_path} 到 {output_dir}")
            unpack_vndat(str(file_path), output_dir, password=KEY.decode('utf-8'))
        elif file_path.suffix.lower() == '.mcdat':
            output_file = os.path.join(output_dir, file_path.stem + '.dec')
            print(f"正在解密 {file_path} 到 {output_file}")
            decrypt_mcdat(str(file_path), output_file)
    

def get_file_extension(file_path):
    """使用filetype库读取文件头并返回对应的扩展名"""
    try:
        kind = filetype.guess(file_path)
        if kind is None:
            print(f'无法识别的文件类型: {file_path}')
            return None
        print(f'文件类型: {kind.mime}, 扩展名: {kind.extension}')
        return f'.{kind.extension}'
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
    return None

def create_directory_if_not_exists(directory, ext):
    """根据扩展名创建子文件夹（如果不存在）"""
    ext_dir = os.path.join(directory, ext.lstrip('.'))
    if not os.path.exists(ext_dir):
        os.makedirs(ext_dir)
    return ext_dir

def move_file_to_directory(file_path, new_ext_dir):
    """将文件移动到新的子文件夹中"""
    filename = os.path.basename(file_path)
    new_file_path = os.path.join(new_ext_dir, filename)
    try:
        shutil.move(file_path, new_file_path)
        print(f'已移动文件 {file_path} 到 {new_file_path}')
    except Exception as e:
        print(f"无法移动文件 {file_path}: {e}")

def rename_and_organize_files_in_directory(directory):
    """遍历目录及其子目录中的所有文件，重命名文件扩展名并根据扩展名组织文件"""
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = get_file_extension(file_path)
            if ext is not None and not filename.lower().endswith(ext):
                # 重命名文件
                new_file_path = os.path.splitext(file_path)[0] + ext
                print(f'正在重命名 {file_path} 到 {new_file_path}')
                try:
                    shutil.move(file_path, new_file_path)
                    file_path = new_file_path
                except Exception as e:
                    print(f"无法重命名文件 {file_path}: {e}")
                    continue
            
            # 根据扩展名组织文件
            if ext:
                ext_dir = create_directory_if_not_exists(directory, ext)
                move_file_to_directory(file_path, ext_dir)

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="解包指定目录下的所有.vndat和.mcdat文件",
        epilog="示例: python 开始处理2.py input_folder [output_folder]"
    )
    parser.add_argument('input_directory', type=str, help='要处理的文件夹路径')
    parser.add_argument('output_directory', nargs='?', default=None, type=str, help='解包后的文件存放路径（可选）')

    args = parser.parse_args()

    # 获取当前脚本所在的目录
    script_directory = Path(__file__).parent

    # 如果没有提供输出目录，则默认为脚本所在目录下的ExtractFiles文件夹
    if args.output_directory is None:
        output_directory = script_directory / 'ExtractFiles'
    else:
        output_directory = Path(args.output_directory)

    input_directory = Path(args.input_directory)

    if not input_directory.is_dir():
        print(f"路径 {input_directory} 不是有效的文件夹。")
        sys.exit(1)

    if not output_directory.exists():
        output_directory.mkdir(parents=True, exist_ok=True)

    print(f"开始处理文件夹: {input_directory}")
    process_files_in_directory(input_directory, output_directory)
    rename_and_organize_files_in_directory(output_directory)  # 解密后重命名并组织文件
    print("处理完成。")