import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class AutoBrowser():
    def __init__(self):
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--mute-audio')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        )
        self.driver = webdriver.Chrome(options=options)

    def quit(self, method):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        wh_then = self.driver.window_handles
        for _ in range(int(timeout * 2)):
            wh_now = self.driver.window_handles
            if len(wh_now) > len(wh_then):
                return list(set(wh_now).difference(set(wh_then)))[0]
            time.sleep(0.5)
        raise Exception("等待课程窗口超时")

    def try_accept_js_alert(self):
        try:
            alert = self.driver.switch_to.alert
            logging.info(f'检测到alert弹窗: {alert.text}')
            alert.accept()
            logging.info("已自动点击alert确定")
            time.sleep(1)
            return True
        except Exception:
            return False

    def inject_focus_js(self):
        try:
            self.driver.execute_script("""
                try {
                    Object.defineProperty(document, 'hidden', {get: function(){return false;}});
                } catch(e){}
                try {
                    Object.defineProperty(document, 'visibilityState', {get: function(){return 'visible';}});
                } catch(e){}
                document.hasFocus = function(){return true;};
                window.onblur = null;
                document.onvisibilitychange = null;
                window.addEventListener('visibilitychange', function(e){e.stopImmediatePropagation();}, true);
                window.addEventListener('blur', function(e){e.stopImmediatePropagation();}, true);
            """)
        except Exception:
            pass

    def try_click_big_play_btn(self):
        try:
            btns = self.driver.find_elements(By.CSS_SELECTOR, "div.prism-big-play-btn")
            for btn in btns:
                style = btn.get_attribute('style')
                if btn.is_displayed() and 'display: none' not in style:
                    ActionChains(self.driver).move_to_element(btn).perform()
                    time.sleep(0.3)
                    btn.click()
                    logging.info('已点击大播放按钮')
                    time.sleep(1)
                    return True
        except Exception:
            pass
        return False

    def try_resume_video(self):
        try:
            is_paused = self.driver.execute_script(
                "var v=document.querySelector('video'); return v ? v.paused : false;"
            )
            if not is_paused:
                return
            player_area = self.driver.find_element(By.CLASS_NAME, "prism-player")
            ActionChains(self.driver).move_to_element(player_area).perform()
            for _ in range(6):
                controlbar = self.driver.find_element(By.ID, "J_prismPlayer_component_73C05521-E3AB-44A9-8703-B135D67C5BF2")
                disp = controlbar.value_of_css_property('display')
                if disp and disp.lower() == "block":
                    play_btn = controlbar.find_element(By.CLASS_NAME, "prism-play-btn")
                    ActionChains(self.driver).move_to_element(play_btn).perform()
                    time.sleep(0.3)
                    play_btn.click()
                    logging.info("已点击小播放按钮恢复播放")
                    break
                time.sleep(2)
                ActionChains(self.driver).move_to_element(player_area).perform()
        except Exception:
            pass

    def check_and_solve_captcha(self, max_retry=5):
        for i in range(max_retry):
            try:
                layers = self.driver.find_elements(By.XPATH, "//*[starts-with(@id, 'layui-layer')]")
                visible_layers = [l for l in layers if l.is_displayed()]
                if not visible_layers:
                    return False
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "checkCode"))
                )
                code_element = self.driver.find_element(By.ID, "checkCode")
                code = code_element.text.strip()
                logging.info(f"第{i+1}次尝试，验证码是：{code}")
                input_box = self.driver.find_element(By.ID, "yz")
                input_box.clear()
                input_box.send_keys(code)
                time.sleep(0.5)
                self.driver.find_element(By.CSS_SELECTOR, "button.yzsubmit").click()
                logging.info("验证码已填写并提交")
                time.sleep(2)
                layers = self.driver.find_elements(By.XPATH, "//*[starts-with(@id, 'layui-layer')]")
                visible_layers = [l for l in layers if l.is_displayed()]
                if not visible_layers:
                    logging.info('验证码窗口关闭，验证通过')
                    return True
                else:
                    logging.warning('验证码校验失败，准备重试或刷新验证码')
                    self.driver.find_element(By.CLASS_NAME, "yz").click()
                    time.sleep(1)
                    continue
            except StaleElementReferenceException:
                logging.warning("检测到StaleElementReferenceException，刷新元素重试。")
                continue
            except NoSuchElementException:
                logging.warning("验证码相关元素未找到，可能验证码弹窗已关闭。")
                return False
            except Exception as e:
                logging.error(f"验证码处理异常: {e}")
                break
        return False

    def run(self):
        try:
            with open('cookie.txt', 'r', encoding='utf-8') as f:
                cookies_str = f.read().strip()
        except Exception as e:
            logging.error(f"cookie.txt读取失败！{e}")
            return
        self.driver.get('https://www.cdjxjy.com/IndexMain.aspx')
        self.driver.delete_all_cookies()
        for pair in cookies_str.split('; '):
            if '=' in pair:
                name, value = pair.split('=', 1)
                self.driver.add_cookie({'name': name, 'value': value, 'domain': '.cdjxjy.com'})
        self.driver.get('https://www.cdjxjy.com/IndexMain.aspx')
        time.sleep(2)
        logging.info("页面已打开并带cookie登录。")
        self.driver.find_element(By.ID, "RegionPanel1_leftPanel_accordionMenu_ctl01_header_hd-textEl").click()
        logging.info('进入课程主菜单')
        for i in range(80):
            logging.info(f'第{i}次切换课程')
            self.driver.find_element(By.LINK_TEXT, "未完成课程").click()
            logging.info('点击-未完成课程')
            self.driver.switch_to.frame(1)
            logging.info('切换frame1')
            handles0 = self.driver.window_handles
            time.sleep(2)
            self.driver.find_element(By.LINK_TEXT, "课程学习").click()
            logging.info('点击 课程学习')
            for t in range(20):
                handles = self.driver.window_handles
                if len(handles) > len(handles0):
                    break
                time.sleep(0.5)
            else:
                logging.error('未发现新课程窗口')
                return
            new_window = list(set(handles) - set(handles0))[0]
            self.driver.switch_to.window(new_window)
            logging.info(f'切到新课程窗口: {new_window}')
            time.sleep(2)
            self.try_accept_js_alert()
            self.inject_focus_js()
            last_print_time = 0
            while True:
                self.try_click_big_play_btn()
                self.try_resume_video()
                self.check_and_solve_captcha()
                try:
                    time_str = self.driver.find_element(By.ID, 'labstudenttime').text
                    match = re.search(r'还差(\d+)分钟', time_str)
                    if match:
                        left_minutes = int(match.group(1))
                        now = time.time()
                        if now - last_print_time > 300:
                            logging.info(f'还需学习时间（分钟）：{left_minutes}')
                            last_print_time = now
                        time.sleep(5)
                        continue
                    elif '已学满' in time_str:
                        logging.info('已学满，自动提交学习记录')
                        try:
                            try:
                                self.driver.find_element(By.LINK_TEXT, "学习记录").click()
                            except Exception:
                                self.driver.find_element(
                                    By.XPATH,
                                    "//div[contains(text(), '学习记录') and contains(@class, 'courseToggle_hook')]"
                                ).click()
                            time.sleep(1)
                            good_str = "好" * 50
                            self.driver.find_element(By.ID, "txtareainnertContents").clear()
                            self.driver.find_element(By.ID, "txtareainnertContents").send_keys(good_str)
                            self.driver.find_element(By.ID, "txtareaExperience").clear()
                            self.driver.find_element(By.ID, "txtareaExperience").send_keys(good_str)
                            time.sleep(1)
                            self.driver.find_element(By.ID, "AddRecord").click()
                            logging.info("学习记录已自动填写并提交")
                            time.sleep(2)
                        except Exception:
                            logging.error("学习记录填写或提交失败")
                        try:
                            self.driver.close()
                        except Exception:
                            pass
                        try:
                            self.driver.switch_to.window(handles0[0])
                        except Exception:
                            pass
                        try:
                            self.driver.refresh()
                        except Exception:
                            pass
                        time.sleep(2)
                        break
                    else:
                        logging.info('进度未学满，5秒后重试')
                        time.sleep(5)
                except Exception:
                    logging.error('获取学习进度失败，5秒后重试')
                    time.sleep(5)

if __name__ == "__main__":
    browser = AutoBrowser()
    try:
        browser.run()
    finally:
        browser.quit('')
        logging.info("程序已退出。")
