## 项目介绍

这是一个基于uiautomator2实现的 Android APP自动遍历测试项目，是一个Android APP动态测试工具，项目需要本地部署完成后才可使用。

特点：

1. **app_dfs（主要功能）**：给定一个APP，自动进行动态测试，以达到尽可能进入APP不同的页面，进行不同的行为。
2. apk_spider（次要功能）：指定一个APP，从Google 商店中爬取对应的APK文件。
3. mitmproxy（次要功能）：在进行app_dfs动态测试时，劫持app流量，从中提取一些被加密的数据信息。

### 项目部署

1. 安装相关python包

   ```shell
   pip install -r requirements.txt
   ```

2. 安装 Android 模拟器

   市面上有很多模拟器，本项目在开发时采用的是MuMu模拟器，推荐使用，也可根据个人对项目的理解，开发出适配于其它模拟器的模块（已经预留接口）

   **模拟器配置**

   - 植入证书（可选）：若需要对流量进行解密，则需要将中间人的证书植入到Android信任的证书列表里，方法见：https://docs.mitmproxy.org/stable/howto-install-system-trusted-ca-android/。在进行测试前，在模拟器的“设置->网络和互联网->互联网->wifi设置->编辑”  进行手动配置代理，ip地址为主机的地址，端口号为 mitmproxy监听的端口如：

     ```shell
     主机ip 192.168.31.10
     ~$: mitmproxy -p 18080
     ```

     那么配置即为：

     <img src="https://www.helloimg.com/i/2025/02/11/67aae5c9c3147.png" alt="image-20250211121532930" style="zoom:30%;" />

3. 其它配置

   项目运行会用到一些 Android SDK工具，主要有 `adb, aptt2`等指令。可以通过安装Android Studio，其会包含Android开发工具包，也可自行独立安装。

4. 运行

   **APK 爬取**

   - 给定APP名称/名称列表，自动下载APK并存储到指定位置

     ```shell
     python .\spider\google_spider.py -n app_name -s save_path
     ```

     或，指定一个文件，要包含 app_name 列

     ```shell
     python .\spider\google_spider.py -f filename -s save_dir
     ```

   - 自动爬取Google商店中 APP rank列表

     ```shell
     python .\spider\google_spider.py -r -s save_path
     ```

   **APP自动动态测试**

   - 该测试需要准备好需要测试APP的APK文件

   - 单个APP测试

     ```shell
     python .\main.py -a test.apk -p pcapfile -k sslkey.log -d device
     ```

     该指令会在 device 上执行 test.apk的动态测试，流量会存储在 pcapfile 中，绘画密钥会存储在 sslkey.log中

   - 批量APP测试

     与单个APP测试不同，批量测试不支持指定每个 pcapfile 的名称以及 sslkey.log的名称，它们会被默认命名为 `<app的包名>.pcap <app的包名>.log`

     ```shell
     python .\main.py --apkdir apks_dir --pcapdir pcap_dir --keydir sslkey_dir -d device
     ```

     该指令会提取 `<apks_dir>`下的所有 `.apk`后缀的文件，依次进行动态测试。每个app产生一个 `pcap` 文件和一个 `sslkey.log` 文件，存储在 `<pcap_dir>` 和 `<sslkey_dir>` 目录下

     其它测试参数可使用 `python .\main.py -h` 获取

     ```shell
     usage: APPs AUTO CONTOL [-h] [-a APK] [--apkdir APKDIR] [-p PCAPFILE] [-k SSLKEYLOG]
                             [--pcapdir PCAPDIR] [--keydir KEYDIR] [-t TIMEOUT] [--round ROUND]
                             [--depth DEPTH] [-d DEVICE] [-s SCRIPT]
     
     本工具为APP自动测试工具，它会连接本地的MuMu模拟器默认127.0.0.1:7555端口，安装指定的APP，并自动产生尽可能多和不同的点击行为
     
     options:
       -h, --help            show this help message and exit
       -a APK, --apk APK     apk, 待测试APP安装包的位置
       --apkdir APKDIR       当进行多个APP测试时，指定apk存放的文件夹
       -p PCAPFILE, --pcapfile PCAPFILE
                             apk产生的流量存储路径，默认值<package_name>.pcap
       -k SSLKEYLOG, --sslkeylog SSLKEYLOG
                             sslkeylog文件路径，默认值<package_name>.keylog
       --pcapdir PCAPDIR     进行多个APP测量时，产生的pcap文件的存储路径，默认值./results/pcap/
       --keydir KEYDIR       进行多个APP测量时，产生的sslkeylog文件的存储路径，默认值./results/sslkeylog/
       -t TIMEOUT, --timeout TIMEOUT
                             APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成，默认值 300 秒       
       --round ROUND         APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成，默认值 1
       --depth DEPTH         APP测试测试时的遍历深度
       -d DEVICE, --device DEVICE
                             device, 模拟器adb服务的运行端口，<ip_addr>:<port>，默认值127.0.0.1:7555     
       -s SCRIPT, --script SCRIPT
                             中间人的处理脚本路径，默认值值E:\work\app_dfs\mitmproxy\mitmproxy_script.py
     ```

### 项目设计介绍

```shell
├─auto_control
├─common
├─mitmproxy
├─results
├─spider
└─main.py
```

项目开发的目标是能够针对任意APP实现自动的动态测试，并且收集APP的流量行为，因为可能涉及到流量的解密，因此本项目还借助了 [@mitmproxy]([mitmproxy/mitmproxy: An interactive TLS-capable intercepting HTTP proxy for penetration testers and software developers.](https://github.com/mitmproxy/mitmproxy)) 工具实现流量密钥的捕获。

总共分为3个部分：

1. APK收集：APP自动测试需要有被测APP的APK文件，spider模块负责收集APK。实现思路是，借助uiautomator2，实现模拟人手动搜索下载APP的行为，再使用 `adb shell pm list packages` 指令，找到对应的 apk文件存储位置，传输到本机目标位置
2. mitmrpoxy：本项目中的 mitmproxy 部分只是实现了一个 [@mitmproxy]([mitmproxy/mitmproxy: An interactive TLS-capable intercepting HTTP proxy for penetration testers and software developers.](https://github.com/mitmproxy/mitmproxy)) 工具需要的脚本，可以再使用中间人代理时，从流量中实时提取一些信息存储到数据库中，流量解密暂时不属于此部分实现。[@mitmproxy]([mitmproxy/mitmproxy: An interactive TLS-capable intercepting HTTP proxy for penetration testers and software developers.](https://github.com/mitmproxy/mitmproxy)) 工具会将密钥自动导入到环境变量 `SSLKEYLOG` 指定的文件中，解密`pcap`需要结合对应`sslkeylog`文件。
3. APP自动动态测试：输入APK文件/包含多个APK的文件夹，此部分会对每个 APK执行以下操作
   - 将 apk 安装到模拟器上
   - 在主机开启进程，运行`mitmproxy` 工具，并监听特定端口
   - 在主机上开启进程，启动`tcpdump`抓包程序
   - APP进行自动动态测试
   - 收集结果

`.\auto_control` 实现APP自动动态测试的控制逻辑

`.\common` 封装一些控制模拟器操作的函数，方便使用的数据结构

`.\mitmrpoxy` 实现了一个 `mitmproxy` 脚本，用于实时从流量中提取一些信息

`.\results` 默认的文件输出位置

`.\spider` 对应 app rank列表获取和 apk文件自动获取功能

`main.py` 协调进行APP动态测试时的逻辑，自动初始化测试环境，如自动打开中间人代理、抓包进程，然后才进行测试，对结果进行收集。
