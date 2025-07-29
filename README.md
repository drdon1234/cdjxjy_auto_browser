# 📚 成都市中小学教师继续教育网自动刷课脚本

自动化完成课程学习、视频播放与学习记录提交，解放双手



## 🚀 功能简介

- 自动登录（通过 cookie）
- 自动点击播放按钮，保持视频播放不中断
- 自动处理弹窗和验证码
- 自动填写并提交学习记录
- 支持多课程轮询刷课，省时高效



## 📝 使用指南

### 1️⃣ 获取 Cookie

1. 进入 [成都市中小学教师继续教育网首页](https://www.cdjxjy.com/IndexMain.aspx) 并完成手动登录
2. 按下 F12 打开 **开发者工具**，切换至「网络」面板，找到 `cookie`
3. 复制 `IndexMain.aspx` 页面的全部 cookie（**须包含 `ASP.NET_SessionId` 和 `logincookie` 两项**）
4. 粘贴到项目根目录的 `cookie.txt` 文件中，**内容示例如下：**
   
   ```
   ASP.NET_SessionId=xxxxxx; logincookie=xxxxxx
   ```

### 2️⃣ 启动脚本

1. 安装最新版 [Chrome 浏览器](https://www.google.com/chrome/)
2. 确保已安装 **Python 3**  
3. 安装以下依赖：
   
    ```
    pip install selenium
    ```
4. 运行刷课主脚本：
   
    ```
    main.py
    ```

## ⚠️ 注意事项

- **cookie 有效期有限**，如遇脚本登录无效，请重新获取新 cookie 并覆盖 `cookie.txt`
- 刷课期间电脑请勿断网、Chrome 浏览器窗体请勿频繁最小化/关闭
- 脚本仅供学习交流，请勿用于非授权用途
- 本工具依赖网站 DOM 结构，如遇页面改版需手动适配

## 📧 联系与反馈

如遇脚本失效或有优化建议，欢迎交流
本项目仅供技术交流用途
