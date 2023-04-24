import socket
import contextlib
import dns.resolver
import threading

""" ##查询子域名域名 2023-04-19 by wuqiang """

# 定义子域名字典文件路径
subdomain_file = "next_sub_full.txt"
source_file = "non_wildcard_domains.txt"
out_file = "live_subdomains.txt"

# 定义要探测的域名列表
target_domains = []

# 从文件中读取要探测的域名
with open(source_file, "r", encoding='utf-8-sig') as f:
    target_domains.extend(line.strip() for line in f)

# 定义DNS解析器
resolver = dns.resolver.Resolver()

# 请调整 可以设置一个dns服务器的列表，查询时候可以随机从dns服务器列表里面去查询
resolver.nameservers = ['223.5.5.5', '119.29.29.29', '180.76.76.76', '114.114.114.114']

# 定义存活的子域名列表
alive_subdomains = []

# 定义探测子域名的函数
def check_subdomain(subdomains, target_domain):
    sub_alive_subdomains = []
    for subdomain in subdomains:
        domain = f"{subdomain}.{target_domain}"
        try:
            # 解析域名，获取解析记录
            answers = resolver.resolve(domain)
            # 如果有解析记录，则域名存活
            if not domain.startswith(('pop.', 'pop3.', 'smtp.', 'mail.','imap.')):
                if len(answers) == 1 and not answers[0].to_text().startswith('127.0.0.'):
                    sub_alive_subdomains.append(domain)
                elif len(answers) > 1:
                    for rdata in answers:
                        if rdata.to_text().startswith('127.0.0.'):
                            break
                    else:
                        sub_alive_subdomains.append(domain)
                else:
                    # 增加判断，如果answers为空，判断是否为127.0.0.1
                    ip = socket.gethostbyname(domain)
                    if not ip.startswith('127.0.0.'):
                        sub_alive_subdomains.append(domain)
        except Exception as e:
            #print(f"Error: {e}")
            continue
    # 加锁，避免多线程写入文件时出现冲突
    with lock:
        alive_subdomains.extend(sub_alive_subdomains)
    # 把存活的子域名写入文件
    with open(out_file, "a", encoding='utf-8-sig') as f:
        for domain in sub_alive_subdomains:
            print(f'{domain}--- alive')
            f.write(domain + "\n")

# 读取子域名字典文件，生成子域名列表
subdomains = []
with open(subdomain_file, "r") as f:
    subdomains.extend(line.strip() for line in f)

# 修改代码，调整线程数量为100 并且可修改
num_threads = 30

# 创建多个线程，同时探测子域名
threads = []
lock = threading.Lock()
for target_domain in target_domains:
    print(f'正在查询域名：{target_domain}')
    subdomains_list = [subdomains[i::num_threads] for i in range(num_threads)]
    for subdomains_chunk in subdomains_list:
        thread = threading.Thread(target=check_subdomain, args=(subdomains_chunk, target_domain))
        threads.append(thread)
        thread.start()

# 等待所有线程执行完毕
for thread in threads:
    thread.join()
