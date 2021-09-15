import re
import docker
import time
import os
import tarfile
client = docker.from_env()

regex = r"(?<=\(score:\s).*?(?=\))"

# image = client.images.build(
#     path='/Users/zhanglei/code/geekplus/judger/Multi-robot/')
# print(image[0])
cli = client.containers.run(
    # image[0].short_id,
    '07d902323454',
    command='/bin/bash',
    stdin_open=True,
    tty=True,
    detach=True,
    cpuset_cpus=1
)

# cli = client.containers.get('619de5cbb123')

# def copy_to(src, dst):
#     name, dst = dst.split(':')
#     container = client.containers.get(name)
#     os.chdir(os.path.dirname(src))
#     srcname = os.path.basename(src)
#     tar = tarfile.open(src + '.tar', mode='w')
#     try:
#         tar.add(srcname)
#     finally:
#         tar.close()
#     data = open(src + '.tar', 'rb').read()
#     print(container.put_archive(os.path.dirname(dst), data))


def setTar(src, name='Archive'):
    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)
    tar = tarfile.open(name + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()
    return tar


def copy_to_container(tar, container, toPath):
    data = open(tar, 'rb').read()
    return container.put_archive(os.path.dirname(toPath), data)


# result = cli.exec_run('sh /root/resource/resource/run_py.sh')
# print(result)
# if(result.exit_code == 0):
#     output = str(result.output, encoding="utf-8")
#     matches = re.findall(regex, output, re.MULTILINE)
#     if len(matches) > 0:
#         score = matches[-1]
#         print(score)
