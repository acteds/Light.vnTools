import os
import struct
from pathlib import Path
import zipfile

# 定义常量
PKZIP_SIGNATURE = b'\x50\x4B\x03\x04'
KEY = b'd6c5fKI3GgBWpZF3Tz6ia3kF0'
REVERSED_KEY = KEY[::-1]

def xor_data(data, key, reversed_key):
    """根据指定的规则对数据执行XOR操作"""
    if len(data) < 100:
        if len(data) <= 0:
            return data

        # XOR entire bytes for files less than 100 bytes
        return bytes([data[i] ^ reversed_key[i % len(key)] for i in range(len(data))])
    else:
        # XOR the first 100 bytes
        xorred_first = bytes([data[i] ^ key[i % len(key)] for i in range(100)])
        
        # XOR the last 99 bytes
        xorred_last = bytes([data[len(data) - 99 + i] ^ reversed_key[i % len(key)] for i in range(99)])
        
        # Combine the parts: unchanged middle part + xorred first and last parts
        middle_part = data[100:-99] if len(data) > 198 else b''
        return xorred_first + middle_part + xorred_last

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
    print("处理完成。")