from PyInquirer import prompt
from examples import custom_style_2
import zipfile
import os


questions = [
    {
        'type': 'list',
        'name': 'project_name',
        'message': '请选择项目：',
        'choices': ["multi_robot", "multi_robot_load", "dense_storge", "multi_task"]
    },
]


def main():
    answers = prompt(questions, style=custom_style_2)
    a = answers.get("project_name")
    createZip(a)


def createZip(name):
    zipPath = '../dist/%s.zip' % (name)
    # # 打开一个 ZIP 文件（以w覆盖的方式写入）
    ZipFile = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)

    adddirfile('../bundle', ZipFile, bundle_ignore_fun(name))
    adddirfile('../algorithm/%s/python_demo' % name, ZipFile, algo_ignore_fun)
    adddirfile('../algorithm/%s/java_demo' % name, ZipFile, algo_ignore_fun)

    ZipFile.close()


# 打包文件夹
def adddirfile(dir_path, zip_file, ignore_fun):
    pre_len = len(os.path.dirname(dir_path))
    for dirpath, dirnames, filenames in os.walk(dir_path):
        if(ignore_fun(dirpath, 'dir', '')):
            continue

        for filename in filenames:
            if(ignore_fun(dirpath, 'file', filename)):
                continue

            pathfile = os.path.join(dirpath, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            print(arcname)
            zip_file.write(pathfile, arcname)


def bundle_ignore_fun(name):
    def ignore_fun(path, type, file_name):
        if(type == 'dir'):
            if('__pycache__' in path):
                return True
            if('simulator' in path and not path.endswith(name)):
                return True

        if(type == 'file'):
            if('.DS_Store' in file_name):
                return True
            if('../bundle' == path and file_name.endswith(".py")):
                if(('%s.py' % name) != file_name):
                    return True

    return ignore_fun


def algo_ignore_fun(path, type, file_name):
    if(type == 'dir'):
        if('__pycache__' in path or 'target' in path or '.idea' in path or '.settings' in path):
            return True

    if(type == 'file'):
        if('.DS_Store' in file_name or '.project' in file_name or '.classpath' in file_name):
            return True


if __name__ == "__main__":
    main()
