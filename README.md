# Light.vnTools

## 实用程序  

### 解密与解包工具使用说明

#### 程序概述

此[程序](python\直接使用python解密并指定正确的扩展名.py)用于解密和解包特定格式的文件（`.vndat` 和 `.mcdat`），并根据文件内容自动重命名其扩展名。程序还能够根据文件类型将解密后的文件组织到相应的子文件夹中。对于长度小于100字节的文件，整个文件都会进行XOR操作；而对于长度大于等于100字节的文件，则仅对前100字节和最后99字节进行XOR操作。

#### 使用前提

- **Python环境**：确保已安装Python 3.x版本。
- **依赖库**：本程序依赖于`filetype`库来识别文件类型。可以通过运行`pip install filetype`来安装该库。
- **权限**：确保程序有读取输入目录和写入输出目录的权限。

#### 安装依赖

在命令行中执行以下命令以安装所需的依赖：

```bash
pip install filetype
```

#### 命令行用法

##### 基本用法

程序通过命令行参数指定输入和输出目录。如果未提供输出目录，默认会在脚本所在目录下创建名为`ExtractFiles`的文件夹作为输出目录。

```bash
python 直接使用python解密并指定正确的扩展名.py [input_directory] [output_directory]
```

- `[input_directory]`：必选参数，指定包含待处理文件的根目录路径。
- `[output_directory]`：可选参数，指定解密后文件存放的根目录路径。如果不提供，默认为脚本同级目录下的`ExtractFiles`文件夹。

##### 示例

1. **提供两个参数**：
   ```bash
   python "直接使用python解密并指定正确的扩展名.py" "D:\game\Data\" "D:\output"
   ```

2. **仅提供一个参数**（输出目录自动设置为与脚本同级的`ExtractFiles`文件夹）：
   ```bash
   python "直接使用python解密并指定正确的扩展名.py" "D:\game\Data\"
   ```

#### 功能描述

1. **解密与解包**：
   - 遍历指定目录及其子目录中的所有`.vndat`和`.mcdat`文件。
   - 对`.vndat`文件进行解包，并对解包后的文件内容进行XOR解密。
   - 对`.mcdat`文件直接进行XOR解密。

2. **重命名与组织**：
   - 使用`filetype`库识别解密后文件的真实类型，并根据识别结果重命名文件扩展名。
   - 根据文件类型创建对应的子文件夹，并将文件移动到相应的子文件夹中。

---

### 技术细节

#### 解密逻辑

- **KEY**：用于XOR解密的密钥。
- **REVERSED_KEY**：`KEY`的逆序版本，用于对文件末尾部分进行XOR解密。
- **xor_data函数**：根据文件长度选择不同的XOR解密策略：
  - 对于长度小于100字节的文件，整个文件进行XOR操作。
  - 对于长度大于等于100字节的文件，仅对前100字节和最后99字节进行XOR操作。

#### 文件处理流程

1. **遍历目录**：从根目录开始递归遍历所有子目录，查找`.vndat`和`.mcdat`文件。
2. **解密/解包**：对找到的文件进行解密或解包操作。
3. **重命名与组织**：解密完成后，检查文件类型并重命名文件扩展名，然后根据文件类型将其组织到相应子文件夹中。



> 
>
> ## Overview
>
> Light.vnTools is an unpack/decrypt and repack/encrypt tool for game made with [Light.vn](https://lightvn.net "Light.vn") (Visual Novel) game engine.
>
> ## Requirements
>
> - [.NET 7.0 SDK](https://dotnet.microsoft.com/download/dotnet/7.0 "Download .NET 7.0 SDK") / [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0 "Download .NET 8.0 SDK")
>
> ## Usage
>
> > [!IMPORTANT]  
> > The "new" encryption scheme that works on the newer Light.vn version is stripping the original file name,
> > so I can't recover it.
> >
> > We're missing the original file extension, but we can guess it by reading the file header and set the extension based on that,
> >
> > For the time being you need to do it yourself by grabbing a hex editor program like [ImHex](https://github.com/WerWolv/ImHex "Visit ImHex GitHub repository"), find the **magic header**, do some Googling then rename the file.
>
> - Download Light.vnTools at [Releases](https://github.com/kiraio-moe/Light.vnTools/releases "Light.vnTools Releases").
> - Unpack/Decrypt:  
>   Drag and drop `.vndat` / `.mcdat` file(s) to the `LightvnTools.exe`.
> - Repack/Encrypt:  
>   Drag and drop **unpacked folder/file(s)** to the `LightvnTools.exe`.
>
> ## Credits
>
> Thanks to [takase1121](https://github.com/takase1121 "Visit takase1121 GitHub profile") by providing proof of concept at: <https://github.com/morkt/GARbro/issues/440>
>
> ## License
>
> This project is licensed under GNU GPL 3.0.
>
> For more information about the GNU General Public License version 3.0 (GNU GPL 3.0), please refer to the official GNU website: <https://www.gnu.org/licenses/gpl-3.0.html>
>
> ## Disclaimer
>
> This tool is intentionally created as a modding tool to translate the visual novel game created with Light.vn game engine. I didn't condone any piracy in any forms such as taking the game visual and sell it illegally which harm the developer. Use the tool at your own risk (DWYOR - Do What You Own Risk).
