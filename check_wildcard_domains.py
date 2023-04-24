import subprocess
import random
import string
import platform
import time

"""
    ##查询域名是否做了泛解析
    2023-04-19 by wuqiang
    
"""
def is_wildcard_dns(domain):
    # 随机生成两个不存在的子域名
    subdomain1 = ''.join(random.choices(string.ascii_lowercase, k=16))
    subdomain2 = ''.join(random.choices(string.ascii_lowercase, k=16))

    # 判断系统平台，选择合适的命令
    if platform.system() == 'Windows':
        cmd1 = f"nslookup -type=A {subdomain1}.{domain} 223.5.5.5"
        cmd2 = f"nslookup -type=A {subdomain2}.{domain} 119.29.29.29"
    else:
        cmd1 = f"dig +noall +answer {subdomain1}.{domain}"
        cmd2 = f"dig +noall +answer {subdomain2}.{domain}"

    # 执行命令查询两个子域名的解析结果
    try:
        output1 = subprocess.check_output(cmd1, shell=True, universal_newlines=True, timeout=3)
        output2 = subprocess.check_output(cmd2, shell=True, universal_newlines=True, timeout=3)
    except subprocess.TimeoutExpired:
        print(f"Timeout checking domain {domain}")
        return False
    
    # 解析命令的输出结果，判断是否存在多个 IP 地址
    ips1 = {
        line.split()[-1]
        for line in output1.strip().split('\n')
        if line.strip().startswith('Address')
    }
    ips2 = {
        line.split()[-1]
        for line in output2.strip().split('\n')
        if line.strip().startswith('Address')
    }

    return len(ips1) > 1 or len(ips2) > 1



if __name__ == '__main__':
    input_file = 'target_domains.txt'  # 输入文件名
    wildcard_file = 'wildcard_domains.txt'  # 输出泛解析域名文件名
    non_wildcard_file = 'non_wildcard_domains.txt'  # 输出非泛解析域名文件名

    wildcard_domains = []
    non_wildcard_domains = []

    with open(input_file, 'r',encoding='utf-8-sig') as f:
        for line in f:
            domain = line.strip()
            if is_wildcard_dns(domain):
                wildcard_domains.append(domain)
            else:
                non_wildcard_domains.append(domain)
            with open(wildcard_file, 'a',encoding='utf-8-sig') as wf:
                if is_wildcard_dns(domain):
                    wf.write(domain+'\n')
            with open(non_wildcard_file, 'a',encoding='utf-8-sig') as nwf:
                if not is_wildcard_dns(domain):
                    nwf.write(domain+'\n')
            time.sleep(0.5)

    print(f"Done. Found {len(wildcard_domains)} wildcard domains and {len(non_wildcard_domains)} non-wildcard domains.")

