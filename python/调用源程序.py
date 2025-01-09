import sys
import subprocess
from pathlib import Path

def process_files_in_directory(directory, tool_exe):
    """
    遍历指定目录及其子目录下的所有.vndat和.mcdat文件，并使用指定工具处理。
    
    :param directory: 要遍历的根目录
    :param tool_exe: 外部工具的路径或名称
    """
    # 获取所有符合条件的文件路径
    target_extensions = ['.vndat', '.mcdat']
    files_to_process = [f for f in Path(directory).rglob('*') if f.suffix.lower() in target_extensions]

    # 如果没有找到任何文件，直接返回
    if not files_to_process:
        print(f"在 {directory} 中没有找到任何.vndat或.mcdat文件。")
        return

    # 分批处理文件，这里我们假设每次处理50个文件
    batch_size = 50
    for i in range(0, len(files_to_process), batch_size):
        batch = files_to_process[i:i + batch_size]
        print(f"正在处理第 {i // batch_size + 1} 批文件...")

        # 构建命令行参数
        args = [str(tool_exe)] + [str(file) for file in batch]

        try:
            # 调用外部工具
            result = subprocess.run(args, check=True)
            print("成功处理了一批文件。")
        except subprocess.CalledProcessError as e:
            print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    # 获取当前脚本所在的目录
    script_dir = Path(__file__).parent.absolute()

    # 定义外部工具的路径（假设在同一目录）
    tool_path = script_dir / "LightvnTools.exe"

    # 检查是否有文件夹被拖放到脚本上
    if len(sys.argv) < 2:
        print("请将一个文件夹拖放到此脚本上以进行处理。")
        sys.exit(1)

    # 获取传递的第一个参数作为要处理的文件夹路径
    folder_path = Path(sys.argv[1])

    # 检查是否为有效的文件夹
    if folder_path.is_dir():
        process_files_in_directory(folder_path, tool_path)
    else:
        print(f"路径 {folder_path} 不是有效的文件夹。")